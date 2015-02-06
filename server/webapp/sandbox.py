import os
import cherrypy
import logger
import math
import subprocessSupport

from cherrypy.lib.static import serve_file

from util import create_zipfile, create_tarfile
from auth import check_auth
from jobsub import is_supported_accountinggroup, get_command_path_root
from jobsub import JobsubConfig
from jobsub import move_file_as_user
from format import format_response
from datetime import datetime


condor_job_status = {
    1: 'Idle',
    2: 'Running',
    3: 'Removed',
    4: 'Completed',
    5: 'Held',
    6: 'Transferring Output',
}




def cleanup(zip_file, outfilename=None):
    """ Hook function to cleanup sandbox files after request has been processed
    """
             
    if outfilename is not None:
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


    def __init__(self):
        self.role = None
        self.username = None
        self.vomsProxy = None

    def findSandbox(self, path):
	if os.path.exists(path):
	    return path
	jobid=os.path.basename(path)
	logger.log('jobid:%s'%jobid)
	uid = '/%s/' % self.username
        cmd1=""" -format '%s' iwd -constraint """ 
        cmd2="""'jobsubjobid=="%s"' """%(jobid)
	for cmd0 in ['condor_history ','condor_q ']:
		cmd=cmd0+cmd1+cmd2
		logger.log(cmd)
		newpath, cmd_err = subprocessSupport.iexe_cmd(cmd)
        	logger.log('result:%s status:%s'%(newpath,cmd_err))
        	if newpath and\
                   len(newpath)>0 and\
                   os.path.exists(newpath) and\
                    uid in newpath:
	    		return newpath
	return False



    #@format_response
    def doGET(self, acctgroup, job_id, kwargs):
        jobsubConfig = JobsubConfig()
        sbx_create_dir = jobsubConfig.commandPathAcctgroup(acctgroup)
        sbx_final_dir = jobsubConfig.commandPathUser(acctgroup, self.username)

        command_path_root = get_command_path_root()
        if job_id is None:
             job_id='I_am_planning_on_failing'
        #else:
        #    job_tokens = job_id.split('.')
        #job_id = '%s.0' % job_tokens[0]
        zip_path = os.path.join(sbx_final_dir, job_id)
	zip_path = self.findSandbox(zip_path)
        if zip_path:
            ts = datetime.now().strftime("%Y-%m-%d_%H%M%S.%f")
            format = kwargs.get('archive_format')
            logger.log('archive_format:%s'%format)
            zip_file_tmp = None
            if format and format=='zip':
                zip_file_tmp = os.path.join(sbx_create_dir,
                                            '%s.%s.zip'%(job_id,ts))
                create_zipfile(zip_file_tmp, zip_path, job_id)
            else:           
                zip_file_tmp = os.path.join(sbx_create_dir,
                                            '%s.%s.tgz'%(job_id,ts))
                create_tarfile(zip_file_tmp, zip_path, job_id)

            # Moving the file to user dir and changing the ownership
            # prevents cherrypy from doing the cleanup. Keep the files in
            # in acctgroup area to allow for cleanup
            zip_file = zip_file_tmp
            rc = {'out': zip_file}
            cherrypy.request.hooks.attach('on_end_request', cleanup,
                                          zip_file=zip_file)
            logger.log('returning %s'%zip_file)
            return serve_file(zip_file, 'application/x-download','attachment')

        else:
            # TODO: PM
            # Do we need this logic anymore? fetchlog now supports a much
            # cleaner option --list-sandboxes
            # return error for no data found
            err = 'No sandbox data found for user: %s, acctgroup: %s, job_id %s' % (self.username, acctgroup, job_id)
            logger.log(err)
            #rc = {'err': err}
            cherrypy.response.status = 404
            sandbox_cluster_ids = list()
            if os.path.exists(sbx_final_dir):
		logger.log('Looking for available sandboxes %s'%sbx_final_dir)
                dirs = os.listdir(sbx_final_dir)
                for dir in dirs:
                    if os.path.islink(os.path.join(sbx_final_dir, dir)) and dir.find('@')>0:
			frag="""<a href="../../%s/sandbox/">%s</a>"""%(dir,dir)
                        sandbox_cluster_ids.append(frag)
                sandbox_cluster_ids.sort()
	    outmsg = "For user %s, accounting group %s, the server can retrieve information for these job_ids:"% (self.username, acctgroup)
	    sandbox_cluster_ids.insert(0,outmsg)
            rc = {'out': sandbox_cluster_ids , 'err':err }

        return rc

    @cherrypy.expose
    @format_response
    @check_auth
    def index(self, acctgroup, job_id, **kwargs):
        logger.log('job_id:%s'%job_id)
        self.role = kwargs.get('role')
        self.username = kwargs.get('username')
        self.vomsProxy = kwargs.get('voms_proxy')

        try:
            if job_id is None:
                raise

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
            err = 'Exception on SandboxResource.index'
            cherrypy.response.status = 500
            logger.log(err, traceback=True)
            rc = {'err': err}
            cherrypy.response.status = 500
  
        return rc


