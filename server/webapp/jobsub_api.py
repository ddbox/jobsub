"""
 Description:
   This module starts the ROOTURL of the jobsub server

 Project:
   JobSub

 Author:
   Nick Palumbo

"""
import cherrypy
import os
import getpass
import traceback
from distutils import spawn

from accounting_group import AccountingGroupsResource
from queued_jobs import QueuedJobsResource
from users_jobs import UsersJobsResource
from version import VersionResource
from scheddload import ScheddLoadResource
from util import mkdir_p
from subprocessSupport import iexe_priv_cmd
from threading import current_thread
from format import format_response
from jobsub.lib.parser import JobsubConfigParser
import jmod


class ApplicationInitializationError(Exception):

    def __init__(self, err):
        self.err = err

    def __str__(self):
        return "JobSub server initialization failed: %s" % (self.err)


class Root(object):
    """
    Root class of API
    /jobsub
    """

    def __init__(self):

        self.acctgroups = AccountingGroupsResource()
        self.jobs = QueuedJobsResource()
        self.users = UsersJobsResource()
        self.version = VersionResource()
        self.scheddload = ScheddLoadResource()

    @cherrypy.expose
    @format_response
    def index(self, **kwargs):
        """
        index.html for /jobsub/
        """
        if cherrypy.request.method == 'GET':
            out = ['Jobsub Server',
                   ['<a href=version/>Version</a>',
                    '<a href=acctgroups/>Browse Accounting Groups</a>',
                    '<a href=users/>User Information</a>',
                    '<a href=scheddload/>Schedd Load </a>',
                    ]
                   ]

            r_code = {'out': out}
            return r_code
        else:
            r_code = 'Unsupported method: %s' % cherrypy.request.method
            return r_code


class RDirect(object):
    """A redirect class to direct / to /jobsub
    """
    @cherrypy.expose
    def index(self, **kwargs):
        """
        the actual redirect
        """
        raise cherrypy.HTTPRedirect('/jobsub')
        #cherrypy.tree.mount(RDirect, '/')


ROOTURL = Root()
cherrypy.tree.mount(RDirect(), '/')


def create_statedir(log):
    """
    Create Application statedir(s)
    /var/lib/jobsub             : rexbatch : 755
    /var/lib/jobsub/tmp         : rexbatch : 700
    """

    jobsub_config = jmod.JobsubConfig()
    state_dir = jobsub_config.state_dir
    err = ''
    path = '%s:%s:%s' % (os.environ['PATH'], '.', '/opt/jobsub/server/webapp')
    exe = spawn.find_executable('jobsub_priv', path=path)

    for s_dir in jobsub_config.state_dir_layout():
        if not os.path.isdir(s_dir[0]):
            try:
                cmd = '%s mkdirsAsUser %s %s %s %s' % (
                    exe,
                    os.path.dirname(dir[0]),
                    os.path.basename(dir[0]),
                    getpass.getuser(),
                    s_dir[1])
                out, err = iexe_priv_cmd(cmd)
                log.error('Created statedir/subdirectories' % s_dir[0])
            except Exception:
                err = 'Failed creating internal state directory %s' % state_dir
                log.error(err)
                log.error(traceback.format_exc())
                raise ApplicationInitializationError(err)


def initialize(log):
    create_statedir(log)


def application(environ, start_response):
    os.environ['JOBSUB_INI_FILE'] = environ['JOBSUB_INI_FILE']
    os.environ['JOBSUB_ENV_RUNNER'] = environ['JOBSUB_ENV_RUNNER']
    os.environ['JOBSUB_UPS_LOCATION'] = environ['JOBSUB_UPS_LOCATION']
    os.environ['JOBSUB_CREDENTIALS_DIR'] = \
        os.path.expanduser(environ['JOBSUB_CREDENTIALS_DIR'])
    os.environ['KCA_DN_PATTERN_LIST'] = environ['KCA_DN_PATTERN_LIST']
    os.environ['KADMIN_PASSWD_FILE'] = \
        os.path.expanduser(environ['KADMIN_PASSWD_FILE'])
    os.environ['JOBSUB_SERVER_VERSION'] = "1.2.9.0.1.rc0"
    os.environ['JOBSUB_SERVER_X509_CERT'] = environ['JOBSUB_SERVER_X509_CERT']
    os.environ['JOBSUB_SERVER_X509_KEY'] = environ['JOBSUB_SERVER_X509_KEY']
    if environ.get('JOBSUB_SET_X509_CERT'):
        os.environ['X509_USER_CERT'] = environ['JOBSUB_SERVER_X509_CERT']
        os.environ['X509_USER_KEY'] = environ['JOBSUB_SERVER_X509_KEY']
    script_name = ''
    appname = environ.get('JOBSUB_APP_NAME')
    if appname is not None:
        script_name = os.path.join('/', appname)
        version = environ.get('JOBSUB_VERSION')
        if version is not None:
            script_name = os.path.join(script_name, appname)
    app = cherrypy.tree.mount(ROOTURL, script_name=script_name, config=None)

    log_dir = environ['JOBSUB_LOG_DIR']
    mkdir_p(log_dir)
    access_log = os.path.join(log_dir, 'access.log')
    error_log = os.path.join(log_dir, 'debug.log')
    jcp = JobsubConfigParser()
    cache_on = False
    cache_duration = 120
    try:
        jcp_c = jcp.get('default', 'enable_http_cache')
        if jcp_c:
            if jcp_c == True or jcp_c.lower() == 'true':
                cache_on = True
        jcp_d = jcp.get('default', 'http_cache_duration')
        if jcp_d:
            cache_duration = int(jcp_d)
    except Exception:
        pass

    cherrypy.config.update({
        'environment': 'embedded',
        'log.screen': False,
        'log.error_file': error_log,
        'log.access_file': access_log,
        'tools.caching.on': cache_on,
        'tools.caching.delay': cache_duration,
    })

    app.log.error('[%s]: jobsub_api.py starting: JOBSUB_INI_FILE:%s cacheing:%s cache_duration:%s seconds' %
                  (current_thread().ident,
                   os.environ.get('JOBSUB_INI_FILE'), cache_on, cache_duration))

    initialize(app.log)

    return cherrypy.tree(environ, start_response)


if __name__ == '__main__':
    cherrypy.quickstart(ROOTURL, '/jobsub')
