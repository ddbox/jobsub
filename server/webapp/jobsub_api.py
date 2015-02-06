import cherrypy
import os

from accounting_group import AccountingGroupsResource
from queued_jobs import QueuedJobsResource
from users_jobs import UsersJobsResource
from version import VersionResource
from util import mkdir_p


class Root(object):
    pass


root = Root()
root.acctgroups = AccountingGroupsResource()
root.jobs = QueuedJobsResource()
root.users = UsersJobsResource()
root.version = VersionResource()


def application(environ, start_response):
    os.environ['JOBSUB_INI_FILE'] = environ['JOBSUB_INI_FILE']
    os.environ['JOBSUB_ENV_RUNNER'] = environ['JOBSUB_ENV_RUNNER']
    os.environ['JOBSUB_UPS_LOCATION'] = environ['JOBSUB_UPS_LOCATION']
    os.environ['JOBSUB_CREDENTIALS_DIR'] = \
            os.path.expanduser(environ['JOBSUB_CREDENTIALS_DIR'])
    os.environ['KCA_DN_PATTERN_LIST'] = environ['KCA_DN_PATTERN_LIST']
    os.environ['KADMIN_PASSWD_FILE'] = \
            os.path.expanduser(environ['KADMIN_PASSWD_FILE'])
    os.environ['JOBSUB_SERVER_VERSION'] = environ['JOBSUB_SERVER_VERSION']
    script_name = ''
    appname = environ.get('JOBSUB_APP_NAME')
    if appname is not None:
        script_name = os.path.join('/', appname)
        version = environ.get('JOBSUB_VERSION')
        if version is not None:
            script_name = os.path.join(script_name, appname)
    app = cherrypy.tree.mount(root, script_name=script_name, config=None)

    log_dir = environ['JOBSUB_LOG_DIR']
    mkdir_p(log_dir)
    access_log = os.path.join(log_dir, 'access.log')
    error_log = os.path.join(log_dir, 'error.log')

    cherrypy.config.update({
        'environment': 'embedded',
        'log.screen': False,
        'log.error_file': error_log,
        'log.access_file': access_log
    })

    app.log.error('jobsub_api.py: starting api: JOBSUB_INI_FILE: %s' % \
            os.environ.get('JOBSUB_INI_FILE'))

    return cherrypy.tree(environ, start_response)

if __name__ == '__main__':
    cherrypy.quickstart(root, '/jobsub')
