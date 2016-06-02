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
$jobsub_ha_servicename = $hostname
$jobsub_git_dir = "/var/tmp/jobsub"

yumrepo { "jenkins":
   baseurl  => "http://pkg.jenkins-ci.org/redhat",
   descr    => "Jenkins",
   enabled  => 1,
   gpgcheck => 1,
   gpgkey   => "http://pkg.jenkins-ci.org/redhat/jenkins-ci.org.key",
}

yumrepo { "jobsub":
   baseurl  => "http://web1.fnal.gov/files/jobsub/dev/6/x86_64/",
   descr    => "Jobsub",
   enabled  => 1,
   gpgcheck => 0,
}

vcsrepo { $jobsub_git_dir :
  provider => git,
  ensure => present,
  source  => 'http://cdcvs.fnal.gov/projects/jobsub',
  require => User[$jobsub_user],
  owner  => $jobsub_user,
  group  => $jobsub_group,
  revision => $jobsub_git_branch,
}

package { 'epel-release-6':
   provider => 'rpm',
   ensure => 'installed',
   source => 'https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm',
}

package { 'osg-release-3.3-5.osg33.el6.noarch':
   provider => 'rpm',
   ensure => 'installed',
   source => 'https://repo.grid.iu.edu/osg/3.3/osg-3.3-el6-release-latest.rpm',
}


package {'git': ensure => present}
package { 'httpd': ensure => present }
package { 'upsupdbootstrap-fnal': ensure => present }

package { 'llrun':
  ensure          => present,
  install_options => "--enablerepo=osg-development",
}

package { 'lcmaps-plugins-gums-client':
  ensure          => present,
  install_options => "--enablerepo=osg-development",
}

package { 'lcmaps-without-gsi':
  ensure          => present,
  install_options => "--enablerepo=epel",
}

package { 'myproxy':
  ensure          => present,
  install_options => "--enablerepo=osg",
}

package { 'condor':
  ensure          => present,
  install_options => "--enablerepo=osg",
}

package { 'jobsub':
  ensure          => $jobsub_server_version,
  install_options => "--enablerepo=jobsub",
}

package { 'osg-ca-scripts':
  ensure          => present,
  install_options => "--enablerepo=osg",
}

exec { 'setupCA':
  command => "/usr/sbin/osg-ca-manage setupCA --location root --url osg",
  require => [ Package['osg-ca-scripts'] ],
  unless => "/usr/bin/test -e /etc/grid-security/certificates/FNAL-SLCS.pem",
}

exec { 'makebasedir':
  command => "/bin/mkdir -p ${jobsub_basejobsdir}",
  unless => "/usr/bin/test -e ${jobsub_basejobsdir}",
}

exec { 'gitpull':
  command => "cd $jobsub_git_dir ; git checkout master; git pull; git checkout $jobsub_git_branch ; git pull",
  require => File[$jobsub_git_dir],
} 

exec { 'jobsub_hostcert':
  command => "cp /etc/grid-security/hostcert.pem /etc/grid-security/jobsub/${jobsub_ha_servicename}-hostcert.pem",
  require => File['/etc/grid-security/jobsub'],
  unless => "test -e /etc/grid-security/jobsub/${jobsub_ha_servicename}-hostcert.pem",
} 

exec { 'jobsub_hostkey':
  command => "cp /etc/grid-security/hostkey.pem /etc/grid-security/jobsub/${jobsub_ha_servicename}-hostkey.pem",
  require => File['/etc/grid-security/jobsub'],
  unless => "test -e /etc/grid-security/jobsub/${jobsub_ha_servicename}-hostkey.pem",
} 

exec { 'install_jobsub_tools':
  command => "/bin/su products -c \" . /fnal/ups/etc/setups.sh; setup ups; setup upd; upd install jobsub_tools ${jobsub_tools_version} -f Linux+2; ups declare -c jobsub_tools ${jobsub_tools_version} -f Linux+2 \"  ",
  require => [ Package['jobsub'], Package['upsupdbootstrap-fnal'], Package['condor'], Package['httpd'] ],
  unless  => "/bin/su products -c \" . /fnal/ups/etc/setups.sh; setup ups; setup upd; ups exist jobsub_tools ${jobsub_tools_version} \" " ,
}

group { $jobsub_group:
  gid    => $jobsub_user_gid,
  ensure => present
}
user { $jobsub_user:
  ensure     => present,
  groups     => $jobsub_group,
  home       => "${jobsub_user_home}",
  managehome => true,
  uid        => $jobsub_user_uid,
  gid        => $jobsub_user_gid,
  shell      => '/bin/bash',
  require    => Group[$jobsub_group]
}

  file { "${jobsub_basejobsdir}":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { "${jobsub_basejobsdir}/proxies":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '700'
  }
  file { "${jobsub_basejobsdir}/uploads":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '775'
  }
  file { "${jobsub_basejobsdir}/history":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '775'
  }
  file { "${jobsub_basejobsdir}/history/work":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '775'
  }

  file { "/var/lib/jobsub":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { "/var/lib/jobsub/tmp":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { "/var/lib/jobsub/creds":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { "/var/lib/jobsub/creds/certs":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { "/var/lib/jobsub/creds/keytabs":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { "/var/lib/jobsub/creds/krb5cc":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { "/var/lib/jobsub/creds/proxies":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { "${jobsub_basejobsdir}/dropbox":
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { "${jobsub_basejobsdir}/uploads/job.log":
    ensure => file,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '775'
  }
  # Setup logrotation
#  file { '/etc/logrotate.d/jobsub':
#    ensure  => file,
#    mode    => '644',
#    source  => 'puppet:///modules/jobsub/etc/logrotate.d/jobsub',
#  }
#  file { '/etc/logrotate.d/httpd':
#    ensure  => file,
#    mode    => '644',
#    source  => 'puppet:///modules/jobsub/etc/logrotate.d/httpd',
#  }
  file { 'jobsublogsdir':
    name   => $jobsub_logsbasedir,
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file { '/var/log/jobsub':
    ensure => link,
    target => $jobsub_logsbasedir
  }
  file { '/etc/httpd':
    ensure => directory,
    owner  => 'root',
    group  => 'root',
    mode   => '755'
  }
  file { '/etc/httpd/conf.d':
    ensure => directory,
    owner  => 'root',
    group  => 'root',
    mode   => '755'
  }
  file { '/etc/sysconfig/httpd':
    ensure => file,
    owner  => 'root',
    group  => 'root',
    mode   => '644'
  }
  file_line {
    'allow_proxy_certs':
      ensure  => 'present',
      path    => '/etc/sysconfig/httpd',
      line    => 'export OPENSSL_ALLOW_PROXY_CERTS=1',
  }
  file { '/etc/httpd/conf.d/jobsub_api.conf':            # need to have this symlink in place on fifebatch nodes before condor is installed
    ensure   => 'link',
    target   => '/opt/jobsub/server/conf/jobsub_api.conf',
    require  => [ Package['jobsub']],
  }
  file { '/opt/jobsub/server/conf/jobsub.ini':
    ensure  => file,
    owner   => $jobsub_user,
    group   => $jobsub_group,
    mode    => '644',
    content => template("/var/tmp/jobsub/test/server/puppetfiles/jobsub.ini.erb")
  }
  file { '/var/www/html/cigetcertopts.txt':
    ensure  => file,
    owner   => $jobsub_user,
    group   => $jobsub_group,
    mode    => '644',
    content => template("/var/tmp/jobsub/test/server/puppetfiles/cigetcertopts.txt.erb")
  }
  file { '/etc/httpd/conf.d/ssl.conf':
    ensure  => file,
    owner   => $jobsub_user,
    group   => $jobsub_group,
    mode    => '644',
    content => template("/var/tmp/jobsub/test/server/puppetfiles/ssl.conf.erb")
  }
  file { '/opt/jobsub/server/conf/jobsub_api.conf':
    ensure  => file,
    owner   => $jobsub_user,
    group   => $jobsub_group,
    mode    => '644',
    content => template("/var/tmp/jobsub/test/server/puppetfiles/jobsub_api.conf.erb")
  }
  file {'/etc/grid-security/jobsub':
    ensure => directory,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '755'
  }
  file {'fifebatch-hacert.pem':
    path   => "/etc/grid-security/jobsub/${jobsub_ha_servicename}-hostcert.pem",
    ensure => file,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '644',
    source => "puppet:///modules/jobsub/etc/grid-security/jobsub/${jobsub_ha_servicename}-hostcert.pem"
  }
  file {'fifebatch-hakey.pem':
    path   => "/etc/grid-security/jobsub/${jobsub_ha_servicename}-hostkey.pem",
    ensure => file,
    owner  => $jobsub_user,
    group  => $jobsub_group,
    mode   => '400',
    source => "puppet:///modules/jobsub/etc/grid-security/jobsub/${jobsub_ha_servicename}-hostkey.pem"
  }
  file { '/opt/jobsub/server/admin/krbrefresh.sh':
    ensure  => present,
    owner   => $jobsub_user,
    group   => $jobsub_group,
    mode    => '744'
  }
  file { '/opt/jobsub/server/admin/jobsub_preen.sh':
    ensure  => present,
    owner   => $jobsub_user,
    group   => $jobsub_group,
    mode    => '744'
  }
  file {'/etc/lcmaps':
    ensure  => 'directory',
    mode    => '755'
  }
  file { '/etc/lcmaps/lcmaps.db':
    ensure   => 'link',
    target   => '/etc/lcmaps.db',
    require  => Package['lcmaps-plugins-gums-client']
  }
  file { '/etc/lcmaps.db':
    ensure  => file,
    mode    => '644',
    content => template("/var/tmp/jobsub/etc/lcmaps.db.erb")
  }
  service{'httpd':
    ensure     => true,
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
    subscribe  => File["/etc/grid-security/jobsub/${jobsub_ha_servicename}-hostcert.pem", "/etc/grid-security/jobsub/${jobsub_ha_servicename}-hostkey.pem", '/opt/jobsub/server/conf/jobsub_api.conf', '/opt/jobsub/server/conf/jobsub.ini']
  }
  cron {'Refresh the kerberos proxies of users in queue that have kerberos principal older than 3600 seconds (default)':
    ensure  => present,
    command => '/opt/jobsub/server/admin/krbrefresh.sh --refresh-proxies 10800',
    user    => rexbatch,
    minute  => 54,
    hour    => [4,16],
    require => File['/opt/jobsub/server/admin/krbrefresh.sh']
  }
  cron {'Copy jobs out of condor history file into jobsub_history database':
    ensure  => present,
    command => '/opt/jobsub/server/admin/fill_jobsub_history.sh --keepUp',
    user    => rexbatch,
    minute  => [07,17,27,37,47,57],
  }
  cron { "Cleanup files for jobs that were last modified ${jobsub_jobhistory_count} days ago, logs to LOG_DIR/jobsub_preen.log":
    ensure  => present,
    command => "/opt/jobsub/server/admin/jobsub_preen.sh ${jobsub_basejobsdir}/uploads  ${jobsub_jobhistory_count} >/tmp/jobsub_preen.out 2>&1",
    hour    => '10',
    minute  => '30',
    require => File['/opt/jobsub/server/admin/jobsub_preen.sh']
  }
  cron {'clean the dropbox directories of old jobs':
    ensure  => present,
    command => "/opt/jobsub/server/admin/jobsub_preen.sh ${jobsub_basejobsdir}/dropbox  ${jobsub_jobhistory_count} >/tmp/jobsub_preen.out 2>&1",
    user    => root,
    hour => '10',
    minute  => '34',
  }
  cron {'clean /var/lib/jobsub/tmp of leftover files from failed authentications':
    ensure  => present,
    command => "/opt/jobsub/server/admin/jobsub_preen.sh /var/lib/jobsub/tmp ${jobsub_jobhistory_count}  thisDirOnly >/tmp/jobsub_preen.out 2>&1",
    user    => root,
    hour    => '10',
    minute  => '44',
  }
  cron {'clean /var/lib/jobsub/creds/proxies of expired proxies and cruft from failed authentications':
    ensure  => present,
    command => "/opt/jobsub/server/admin/jobsub_preen.sh /var/lib/jobsub/creds/proxies/ ${jobsub_jobhistory_count} rmEmptySubdirs  >/tmp/jobsub_preen.out 2>&1",
    user    => root,
    hour    => '10',
    minute  => '54',
  }

