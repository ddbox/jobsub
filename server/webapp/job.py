import base64
import threading
import os
import re
import platform
import cherrypy
import logger
import math

from util import encode_multipart_formdata

if platform.system() == 'Linux':
    try:
        import htcondor as condor
        import classad
    except:
        logger.log('Cannot import htcondor. Have the condor python bindings been installed?')

from datetime import datetime
from shutil import copyfileobj

from cherrypy.lib.static import serve_file

from util import get_uid, mkdir_p, create_zipfile
from auth import check_auth
from jobsub import is_supported_accountinggroup, execute_jobsub_command, get_command_path_root
from format import format_response


condor_job_status = {
    1: 'Idle',
    2: 'Running',
    3: 'Removed',
    4: 'Completed',
    5: 'Held',
    6: 'Transferring Output',
}


def get_condor_queue(acctgroup, uid, convert=False):
    """ Uses the Condor Python bindings to get information for scheduled jobs.
        Returns a map of objects with the Cluster Id as the key
    """
    schedd = condor.Schedd()
    # Filter by user
    results = schedd.query('Owner =?= "%s"' % uid)
    all_jobs = dict()
    for classad in results:
        # Split the Env data into a dictionary
        env = dict([x.split('=') for x in classad['Env'].split(';')])
        # Filter by accounting group
        if env.get('EXPERIMENT') == acctgroup:
            key = classad['ClusterId']
            # Converting from ClassAd object to dictionary is optional
            # since sometime we are only seeking one value
            if convert is True:
                classad = classad_to_dict(classad)
            all_jobs[key] = classad
    return all_jobs


def classad_to_dict(classad):
    """ Converts a ClassAd object to a dictionary. Used for serialization to JSON.
    """
    job_dict = dict()
    for k, v in classad.items():
        job_dict[repr(k)] = repr(v)
    return job_dict


def cleanup(zip_file, outfilename):
    """ Hook function to cleanup sandbox files after request has been processed
    """
    try:
        os.remove(outfilename)
    except:
        err = 'Failed to remove encoded file at %s' % outfilename
        logger.log(err)
    try:
        os.remove(zip_file)
    except:
        err = 'Failed to remove zip file at %s' % zip_file
        logger.log(err)


class SandboxResource(object):
    """ Download compressed output sandbox for a given job
        API is /jobsub/acctgroups/<group_id>/jobs/<job_id>/sandbox/
    """
    def doGET(self, acctgroup, job_id, kwargs):
        subject_dn = cherrypy.request.headers.get('Auth-User')
        uid = get_uid(subject_dn)
        command_path_root = get_command_path_root()
        if job_id is not None:
            # Get the job status to return with the sandbox
            job_status = None
            # Get the queue of scheduled jobs
            all_jobs = get_condor_queue(acctgroup, uid)
            # Find the ClassAd for the job id
            classad = all_jobs.get(math.trunc(float(job_id)))
            if classad is not None:
                # Use the map to get a readable name for the job status value
                job_status = condor_job_status.get(classad.get('JobStatus'))
            job_tokens = job_id.split('.')
            # Disregard anything past the decimal point in job id
            if len(job_tokens) == 1 or (len(job_tokens) > 1 and job_tokens[-1].isdigit() is False):
                job_id = '%s.0' % job_id
            zip_path = os.path.join(command_path_root, acctgroup, uid, job_id)
            if os.path.exists(zip_path):
                # found the path, zip data and return
                # If there is no job status then it was not found in the queue. Assume completed
                if job_status is None:
                    job_status = 'Completed'
                zip_file = os.path.join(command_path_root, acctgroup, uid, '%s.zip' % job_id)
                create_zipfile(zip_file, zip_path, job_id)

                rc = {'job_status': job_status}

                # Create the multipart response and return
                with open(zip_file, 'rb') as fh:
                    fields = [('rc', rc)]
                    files = [('zip_file', zip_file, fh.read())]
                    outfilename = os.path.join(command_path_root, acctgroup, uid, '%s.encoded' % job_id)
                    with open(outfilename, 'wb') as outfile:
                        content_type = encode_multipart_formdata(fields, files, outfile)
                    # attach a hook function to cleanup when the request is done
                    cherrypy.request.hooks.attach('on_end_request', cleanup, zip_file=zip_file, outfilename=outfilename)
                    return serve_file(outfilename, 'application/x-download')

            else:
                # return error for no data found
                err = 'No sandbox data found for user: %s, acctgroup: %s, job_id %s' % (uid, acctgroup, job_id)
                logger.log(err)
                rc = {'job_status': job_status, 'err': err}
                cherrypy.response.status = 404
        else:
            jobs_file_path = os.path.join(command_path_root, acctgroup, uid)
            sandbox_cluster_ids = list()
            if os.path.exists(jobs_file_path):
                root, dirs, files = os.walk(jobs_file_path, followlinks=False)
                for dir in dirs:
                    if os.path.islink(os.path.join(jobs_file_path, dir)):
                        sandbox_cluster_ids.append(dir)
                rc = {'out': sandbox_cluster_ids}
            else:
                # return error for no data found
                err = 'No sandbox data found for user: %s, acctgroup: %s' % (uid, acctgroup)
                logger.log(err)
                rc = {'err': err}
                cherrypy.response.status = 404

        return rc

    @cherrypy.expose
    @format_response
    @check_auth
    def index(self, acctgroup, job_id, **kwargs):
        try:
            if is_supported_accountinggroup(acctgroup):
                if cherrypy.request.method == 'GET':
                    rc = self.doGET(acctgroup, job_id, kwargs)
                else:
                    err = 'Unsupported method: %s' % cherrypy.request.method
                    logger.log(err)
                    rc = {'err': err}
                    cherrypy.response.status = 500
            else:
                # return error for unsupported acctgroup
                err = 'AccountingGroup %s is not configured in jobsub' % acctgroup
                logger.log(err)
                rc = {'err': err}
                cherrypy.response.status = 500
        except:
            err = 'Exception on AccountJobsResouce.index'
            logger.log(err, traceback=True)
            rc = {'err': err}
            cherrypy.response.status = 500
  
        return rc


@cherrypy.popargs('job_id')
class AccountJobsResource(object):

    def __init__(self):
        self.sandbox = SandboxResource()

    def doGET(self, acctgroup, job_id):
        """ Serves the following APIs:

            Query a single job. Returns a JSON map of the ClassAd object that matches the job id
            API is /jobsub/acctgroups/<group_id>/jobs/<job_id>/

            Query list of jobs. Returns a JSON map of all the ClassAd objects in the queue
            API is /jobsub/acctgroups/<group_id>/jobs/
        """
        subject_dn = cherrypy.request.headers.get('Auth-User')
        uid = get_uid(subject_dn)
        if job_id is not None:
            all_jobs = get_condor_queue(acctgroup, uid)
            classad = all_jobs.get(int(job_id))
            if classad is not None:
                # Convert from ClassAd object to dict for JSON dump
                job_dict = classad_to_dict(classad)
                rc = {'out': job_dict}
            else:
                err = 'Job with id %s not found in condor queue' % job_id
                logger.log(err)
                rc = {'err': err}
        else:
            all_jobs = get_condor_queue(acctgroup, uid, True)
            rc = {'out': all_jobs}

        return rc

    def doPOST(self, acctgroup, job_id, kwargs):
        """ Create/Submit a new job. Returns the output from the jobsub tools.
            API is /jobsub/acctgroups/<group_id>/jobs/<job_id>/
        """
        if job_id is None:
            logger.log('kwargs: %s' % str(kwargs))
            jobsub_args = kwargs.get('jobsub_args_base64')
            if jobsub_args is not None:
                jobsub_args = base64.b64decode(jobsub_args).rstrip()
                logger.log('jobsub_args: %s' % jobsub_args)
                jobsub_command = kwargs.get('jobsub_command')
                logger.log('jobsub_command: %s' % jobsub_command)
                subject_dn = cherrypy.request.headers.get('Auth-User')
                uid = get_uid(subject_dn)
                command_path_root = get_command_path_root()
                ts = datetime.now().strftime("%Y-%m-%d_%H%M%S") # add request id
                thread_id = threading.current_thread().ident
                workdir_id = '%s_%s' % (ts, thread_id)
                command_path = os.path.join(command_path_root, acctgroup, uid, workdir_id)
                logger.log('command_path: %s' % command_path)
                mkdir_p(command_path)
                if jobsub_command is not None:
                    command_file_path = os.path.join(command_path, jobsub_command.filename)
                    logger.log('command_file_path: %s' % command_file_path)
                    with open(command_file_path, 'wb') as dst_file:
                        copyfileobj(jobsub_command.file, dst_file)
                    # replace the command file name in the arguments with the path on the local machine
                    command_tag = '@(.*)%s' % jobsub_command.filename
                    jobsub_args = re.sub(command_tag, command_file_path, jobsub_args)
                    logger.log('jobsub_args (subbed): %s' % jobsub_args)

                jobsub_args = jobsub_args.split(' ')

                rc = execute_jobsub_command(acctgroup, uid, jobsub_args, workdir_id)
            else:
                # return an error because no command was supplied
                err = 'User must supply jobsub command'
                logger.log(err)
                rc = {'err': err}
        else:
            # return an error because job_id has been supplied but POST is for creating new jobs
            err = 'User has supplied job_id but POST is for creating new jobs'
            logger.log(err)
            rc = {'err': err}

        return rc

    @cherrypy.expose
    @format_response
    @check_auth
    def index(self, acctgroup, job_id=None, **kwargs):
        try:
            if is_supported_accountinggroup(acctgroup):
                if cherrypy.request.method == 'POST':
                    rc = self.doPOST(acctgroup, job_id, kwargs)
                elif cherrypy.request.method == 'GET':
                    rc = self.doGET(acctgroup, job_id)
                else:
                    err = 'Unsupported method: %s' % cherrypy.request.method
                    logger.log(err)
                    rc = {'err': err}
            else:
                # return error for unsupported acctgroup
                err = 'AccountingGroup %s is not configured in jobsub' % acctgroup
                logger.log(err)
                rc = {'err': err}
        except:
            err = 'Exception on AccountJobsResouce.index'
            logger.log(err, traceback=True)
            rc = {'err': err}

        return rc


