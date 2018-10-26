"""Module:
        by_user
   Purpose
        implements condor_q <username>
        API /jobsub/acctgroups/<group_id>/jobs/user/<username>/
        API /jobsub/acctgroups/<group_id>/jobs/user/<username>/<jobsubjobid>
"""
import cherrypy
import logging
from jobsub.lib.logger import logger
from .util import doDELETE
from .util import doPUT
from .auth import check_auth
from .jmod import is_supported_accountinggroup
from .format import format_response


@cherrypy.popargs('action_user', 'job_id')
class AccountJobsByUserResource(object):
    """Class that implements above URLS
       Only responds to http GET, only
       index.html implemented
    """

    @cherrypy.expose
    @format_response
    @check_auth
    def index(self, acctgroup, action_user=None, job_id=None, **kwargs):
        """implementation of index.html
           no point in putting anything here for pydoc
           as decorators seem to eat it in python 2
           hopefully 3 will be better
        """
        try:
            if kwargs.get('role'):
                cherrypy.request.role = kwargs.get('role')
            if kwargs.get('username'):
                cherrypy.request.username = kwargs.get('username')
            if kwargs.get('voms_proxy'):
                cherrypy.request.vomsProxy = kwargs.get('voms_proxy')
            logger.log('action_user=%s' % (action_user))
            logger.log('kwargs=%s' % kwargs)
            if is_supported_accountinggroup(acctgroup):
                if cherrypy.request.method == 'DELETE':
                    # remove job
                    rc = doDELETE(
                        acctgroup, user=action_user, job_id=job_id, **kwargs)
                elif cherrypy.request.method == 'PUT':
                    # hold/release
                    rc = doPUT(acctgroup, user=action_user,
                               job_id=job_id, **kwargs)
                else:
                    err = 'Unsupported method: %s' % cherrypy.request.method
                    logger.log(err, severity=logging.ERROR)
                    logger.log(err, severity=logging.ERROR, logfile='error')
                    rc = {'err': err}
            else:
                # return error for unsupported acctgroup
                err = 'AccountingGroup %s is not configured in jobsub' % acctgroup
                logger.log(err, severity=logging.ERROR)
                logger.log(err, severity=logging.ERROR, logfile='error')
                rc = {'err': err}
        except Exception:
            cherrypy.response.status = 500
            err = 'Exception on AccountJobsByUserResource.index'
            logger.log(err, severity=logging.ERROR, traceback=True)
            logger.log(err, severity=logging.ERROR,
                       logfile='error', traceback=True)
            rc = {'err': err}
        if rc.get('err'):
            cherrypy.response.status = 500
        return rc
