import cherrypy
import logger
import uuid
import os

from util import get_uid
from auth import check_auth
from job import AccountJobsResource
from format import format_response
from jobsub import get_supported_accountinggroups
from jobsub import execute_jobsub_command
from jobsub import get_dropbox_path_root
from util import mkdir_p

from cherrypy.lib.static import serve_file

from shutil import copyfileobj


class HelpResource(object):
    def doGET(self, acctgroup):
        jobsub_args = ['--help']
        subject_dn = cherrypy.request.headers.get('Auth-User')
        uid = get_uid(subject_dn)
        rc = execute_jobsub_command(acctgroup, uid, jobsub_args)

        return rc


    @cherrypy.expose
    @format_response
    def index(self, acctgroup, **kwargs):
        try:
            subject_dn = cherrypy.request.headers.get('Auth-User')
            if subject_dn is not None:
                logger.log('subject_dn: %s' % subject_dn)
                if cherrypy.request.method == 'GET':
                    rc = self.doGET(acctgroup)
                else:
                    err = 'Unsupported method: %s' % cherrypy.request.method
                    logger.log(err)
                    rc = {'err': err}
            else:
                # return error for no subject_dn
                err = 'User has not supplied subject dn'
                logger.log(err)
                rc = {'err': err}
        except:
            err = 'Exception on JobsResouce.index'
            logger.log(err, traceback=True)
            rc = {'err': err}

        return rc


@cherrypy.popargs('file_id')
class DropboxResource(object):
    def doGET(self, acctgroup, file_id):
        subject_dn = cherrypy.request.headers.get('Auth-User')
        uid = get_uid(subject_dn)
        dropbox_path_root = get_dropbox_path_root()
        dropbox_path = os.path.join(dropbox_path_root, acctgroup, uid)
        dropbox_file_path = os.path.join(dropbox_path, file_id)
        return serve_file(dropbox_file_path, "application/x-download", "attachment")

    def doPOST(self, acctgroup, kwargs):
        subject_dn = cherrypy.request.headers.get('Auth-User')
        uid = get_uid(subject_dn)
        dropbox_path_root = get_dropbox_path_root()
        dropbox_path = os.path.join(dropbox_path_root, acctgroup, uid)
        mkdir_p(dropbox_path)
        file_map = dict()
        for arg_name, arg_value in kwargs:
            if hasattr(arg_value, 'file'):
                file_id = str(uuid.uuid4())
                dropbox_file_path = os.path.join(dropbox_path, file_id)
                logger.log('dropbox_file_path: %s' % dropbox_file_path)
                with open(dropbox_file_path, 'wb') as dst_file:
                    copyfileobj(arg_value.file, dst_file)
                    file_map[arg_name] = file_id

        return file_map

    @cherrypy.expose
    @format_response
    @check_auth
    def index(self, acctgroup, file_id=None, **kwargs):
        try:
            subject_dn = cherrypy.request.headers.get('Auth-User')
            if subject_dn is not None:
                logger.log('subject_dn: %s' % subject_dn)
                if cherrypy.request.method == 'POST':
                    if file_id is None:
                        rc = self.doPOST(acctgroup, kwargs)
                    else:
                        err = 'User has supplied file_id but POST is for adding files'
                        logger.log(err)
                        rc = {'err': err}
                elif cherrypy.request.method == 'GET':
                    if file_id is not None:
                        rc = self.doGET(acctgroup, file_id)
                    else:
                        err = 'User has must supply file_id for GET'
                        logger.log(err)
                        rc = {'err': err}
                else:
                    err = 'Unsupported method: %s' % cherrypy.request.method
                    logger.log(err)
                    rc = {'err': err}
            else:
                # return error for no subject_dn
                err = 'User has not supplied subject dn'
                logger.log(err)
                rc = {'err': err}
        except:
            err = 'Exception on JobsResouce.index'
            logger.log(err, traceback=True)
            rc = {'err': err}

        return rc


@cherrypy.popargs('acctgroup')
class AccountingGroupsResource(object):
    def __init__(self):
        self.jobs = AccountJobsResource()
        self.help = HelpResource()
        self.dropbox = DropboxResource()

    def doGET(self, acctgroup):
        if acctgroup is None:
            return {'out': get_supported_accountinggroups()}

    @cherrypy.expose
    @format_response
    def index(self, acctgroup, **kwargs):
        try:
            subject_dn = cherrypy.request.headers.get('Auth-User')
            if subject_dn is not None:
                logger.log('subject_dn: %s' % subject_dn)
                if cherrypy.request.method == 'GET':
                    rc = self.doGET(acctgroup)
                else:
                    err = 'Unsupported method: %s' % cherrypy.request.method
                    logger.log(err)
                    rc = {'err': err}
            else:
                # return error for no subject_dn
                err = 'User has not supplied subject dn'
                logger.log(err)
                rc = {'err': err}
        except:
            err = 'Exception on JobsResouce.index'
            logger.log(err, traceback=True)
            rc = {'err': err}

        return rc
