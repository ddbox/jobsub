"""
 Description:
   Query dropbox size to use for an experiment to drop tarballs and other files.
   Written as a part of the transition to unmount Bluearc from the grid worker nodes.

   API is /acctgroups/<group>/dropboxsize/

 Project:
   JobSub

 Author:
   Shreyas Bhat

"""
import cherrypy
from jobsub.lib.logger import logger
import logging
import jmod
from format import format_response


class DropboxSizeResource(object):
    """see module documentation, only one class in file
    """

    def doGET(self, kwargs):
        """ http GET request on index.html of API
            Query max dropbox size. Returns a JSON list object.
            API is /acctgroups/<group>/dropboxsize/
        """
        acctgroup = kwargs.get('acctgroup')
        logger.log('acctgroup=%s' % acctgroup)
        dropbox = jmod.get_dropbox_max_size(acctgroup)
        if dropbox == False:
            cherrypy.response.status = 403
            return {'err': 'Dropbox size is NOT available for %s'
                    % acctgroup}
        elif not dropbox:
            cherrypy.response.status = 404
            return {'err': 'Dropbox size is NOT found for %s'
                    % acctgroup}
        return {'out': dropbox}

    @cherrypy.expose
    @format_response
    def index(self, **kwargs):
        """index.html, only GET implemented
        """
        try:
            logger.log("kwargs %s" % kwargs)

            if cherrypy.request.method == 'GET':
                rc = self.doGET(kwargs)
            else:
                err = 'Unsupported method: %s' % cherrypy.request.method
                logger.log(err, severity=logging.ERROR)
                logger.log(err, severity=logging.ERROR, logfile='error')
                rc = {'err': err}
        except Exception:
            err = 'Exception on DropboxSizeResource.index'
            cherrypy.response.status = 500
            logger.log(err, severity=logging.ERROR, traceback=True)
            logger.log(err, severity=logging.ERROR,
                       logfile='error', traceback=True)
            rc = {'err': err}

        return rc
