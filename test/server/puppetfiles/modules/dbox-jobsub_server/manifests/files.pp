class jobsub_server::files{
  
     $jobsub_server_version = $jobsub_server::vars::jobsub_server_version
     $jobsub_tools_version = $jobsub_server::vars::jobsub_tools_version
     $jobsub_user = $jobsub_server::vars::jobsub_user
     $jobsub_user_uid = $jobsub_server::vars::jobsub_user_uid
     $jobsub_group = $jobsub_server::vars::jobsub_group
     $jobsub_user_gid = $jobsub_server::vars::jobsub_user_gid
     $jobsub_user_home = $jobsub_server::vars::jobsub_user_home
     $jobsub_basejobsdir = $jobsub_server::vars::jobsub_basejobsdir
     $jobsub_logsbasedir = $jobsub_server::vars::jobsub_logsbasedir
     $jobsub_jobhistory_count = $jobsub_server::vars::jobsub_jobhistory_count
     $jobsub_git_branch = $jobsub_server::vars::jobsub_git_branch
     $jobsub_git_dir = $jobsub_server::vars::jobsub_git_dir
     $jobsub_ha_servicename = $jobsub_server::vars::jobsub_ha_servicename

     $esg = '/etc/grid-security'
 
     exec { 'setupCA':
       command => "/usr/sbin/osg-ca-manage setupCA --location root --url osg",
       require => [ Package['osg-ca-scripts'] ],
       creates => "$esg/certificates/FNAL-SLCS.pem",
     }
     
     exec { 'makebasedir':
       command => "/bin/mkdir -p ${jobsub_basejobsdir}",
       creates => "${jobsub_basejobsdir}",
     }
     
     exec { "$esg/jobsub":
       command => "/bin/mkdir -p $esg/jobsub",
       creates => "$esg/jobsub",
     }
     
     file {"$esg/jobsub/${jobsub_ha_servicename}-hostcert.pem" :
         owner  => $jobsub_user,
         group  => $jobsub_group,
         mode   => '755',
         require   => Exec['jobsub_hostcert'],
     }
     
     exec { 'jobsub_hostcert':
       command => "/bin/cp $esg/hostcert.pem $esg/jobsub/${jobsub_ha_servicename}-hostcert.pem",
       require => Exec["$esg/jobsub"],
       creates => "$esg/jobsub/${jobsub_ha_servicename}-hostcert.pem",
     } 
     
     file {"$esg/jobsub/${jobsub_ha_servicename}-hostkey.pem" :
         owner  => $jobsub_user,
         group  => $jobsub_group,
         mode   => '700',
         require   => Exec['jobsub_hostkey'],
     }

     exec { 'jobsub_hostkey':
       command => "/bin/cp $esg/hostkey.pem $esg/jobsub/${jobsub_ha_servicename}-hostkey.pem",
       require => Exec["$esg/jobsub"],
       creates  => "$esg/jobsub/${jobsub_ha_servicename}-hostkey.pem",
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

      file { '/etc/httpd/conf.d/jobsub_api.conf':            
        ensure   => 'link',
        target   => '/opt/jobsub/server/conf/jobsub_api.conf',
        require  => [ Package['jobsub']],
      }
    
      file { '/opt/jobsub/server/conf/jobsub.ini':
        ensure  => file,
        owner   => $jobsub_user,
        group   => $jobsub_group,
        mode    => '644',
        content => template("jobsub_server/jobsub.ini.erb"),
      }

      file { '/var/www/html/cigetcertopts.txt':
        ensure  => file,
        owner   => $jobsub_user,
        group   => $jobsub_group,
        mode    => '644',
        content => template("jobsub_server/cigetcertopts.txt.erb"),
      }

      file { '/etc/httpd/conf.d/ssl.conf':
        ensure  => file,
        owner   => $jobsub_user,
        group   => $jobsub_group,
        mode    => '644',
        content => template("jobsub_server/ssl.conf.erb"),
      }

      file { '/opt/jobsub/server/conf/jobsub_api.conf':
        ensure  => file,
        owner   => $jobsub_user,
        group   => $jobsub_group,
        mode    => '644',
        content => template("jobsub_server/jobsub_api.conf.erb"),
      }

      file { '/etc/lcmaps.db':
        ensure  => file,
        mode    => '644',
        content => template("jobsub_server/lcmaps.db.erb")
      }
    
      file {"$esg/jobsub":
        ensure => directory,
        owner  => $jobsub_user,
        group  => $jobsub_group,
        mode   => '755'
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
}
