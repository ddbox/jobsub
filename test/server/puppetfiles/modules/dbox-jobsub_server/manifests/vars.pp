# author Dennis Box, dbox@fnal.gov
class jobsub_server::vars{
    $jobsub_server_version = '1.2-3'
    $jobsub_tools_version = 'v1_4_5'
    $jobsub_user = 'rexbatch'
    $jobsub_user_uid = 47535
    $jobsub_group = 'fife'
    $jobsub_user_gid = 9239
    $jobsub_user_home = '/home/rexbatch'
    $jobsub_basejobsdir = '/fife/local/scratch'
    $jobsub_logsbasedir = '/fife/local/scratch/logs'
    $jobsub_jobhistory_count = '30'
    $jobsub_git_branch = 'puppetized_ci'
    $jobsub_git_dir = '/var/tmp/jobsub'
    $jobsub_cert = '/etc/grid-security/jobsub/jobsubcert.pem'
    $jobsub_key = '/etc/grid-security/jobsub/jobsubkey.pem'
    ######################################################
    $jenkins_user = 'jenkins'
    $jenkins_home = '/var/lib/jenkins'
    $jenkins_cert = '/etc/grid-security/jenkins/jenkinscert.pem'
    $jenkins_key = '/etc/grid-security/jenkins/jenkinskey.pem'
    $jenkins_admin_email = 'dbox@fnal.gov'
}
