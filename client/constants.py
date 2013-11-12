################################################################################
# Project:
#   JobSub
#
# Author:
#   Parag Mhashilkar
#
# Description:
#   This module implements constants used by the JobSub Client
#
################################################################################

################################################################################
# JOBSUB Constants
################################################################################

# Default JobSub Server
JOBSUB_SERVER = 'https://jobsub.fnal.gov'

# Default JobSub job submission url pattern
# https://server.com/jobsub/api/<api-version>/experiments/<exp-name>/jobs

#JOBSUB_JOB_SUBMIT_URL_PATTERN = '%s/jobsub/api/%s/experiments/%s/jobs'
JOBSUB_JOB_SUBMIT_URL_PATTERN = '%s/jobsub/experiments/%s/jobs/'

################################################################################
# HTTP/REST API Constants
################################################################################

# HTTP Verbs/Actions
HTTP_GET = 'GET'
HTTP_POST = 'POST'
