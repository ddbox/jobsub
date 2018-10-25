
"""Module: request_headers
   Purpose: retrieve various information from http/cherrypy request headers
   Author:  Dennis Box, dbox@fnal.gov
"""
import cherrypy
from jobsub.lib.logger import logger


def slashify(a_dn):
    """
    if a_dn is of the form CN=UID:dbox,CN=Dennis Box,OU=People,yada yada yada
    reformat it and return as
    /yada yada yada/OU=People/CN=Dennis Box/CN=UID:dbox
    """
    if a_dn is None:
        return a_dn
    if '/' in a_dn:
        return a_dn
    lst = a_dn.split(',')
    lst.reverse()
    new_dn = '/' + '/'.join(lst)
    return new_dn

def get_client_dn():
    """
    Identify the client DN based on if the client is using a X509 cert-key
    pair or an X509 proxy. Currently only works with a single proxy chain.
    Wont work if the proxy is derieved from the proxy itself.
    """

    issuer_dn = slashify(cherrypy.request.headers.get('Ssl-Client-I-Dn'))
    client_dn = slashify(cherrypy.request.headers.get('Ssl-Client-S-Dn'))
    # In case of proxy additional last part will be of the form /CN=[0-9]*
    # In other words, issuer_dn is a substring of the client_dn
    if client_dn:
        if issuer_dn:
            if client_dn.startswith(issuer_dn):
                client_dn = issuer_dn
    return client_dn

def uid_from_client_dn():
    """
    return uid from a dn of the form
    /DC=yak/DC=yak/UID:uid/
    """
    uid = None
    cdn = get_client_dn()
    parts = cdn.split('/')
    for part in parts:
        if 'UID:' in part:
            uid_parts = part.split(':')
            uid = uid_parts[-1]
    #if not cherrypy.request.username:
    #    cherrpy.request.username = uid
    return uid


def path_info():
    """
    Returns a list of the path elements
    /jobsub/acctgroups/nova/jobs
    returns ['jobsub','acctgroups','nova','jobs']
    """
    path = cherrypy.request.path_info
    path = path.strip('/')
    p_list = path.split('/')
    return p_list


def path_end():
    """
    Returns last element in the path
    /jobsub/acctgroups/nova/jobs
    returns 'jobs'
     """

    p_list = path_info()
    return p_list[-1]
