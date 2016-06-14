class jobsub_server::packages {
#   yumrepo { 'jenkins':
#     baseurl  => 'http://pkg.jenkins-ci.org/redhat',
#     descr    => 'Jenkins',
#     enabled  => 1,
#     gpgcheck => 1,
#     gpgkey   => 'http://pkg.jenkins-ci.org/redhat/jenkins-ci.org.key',
#   }
    yumrepo { 'jobsub':
      baseurl  => 'http://web1.fnal.gov/files/jobsub/dev/6/x86_64/',
      descr    => 'Jobsub',
      enabled  => 1,
      gpgcheck => 0,
    }

    package { 'epel-release-6':
      ensure   => 'installed',
      provider => 'rpm',
      source   => 'https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm',
    }

    package { 'osg-release-3.3-5.osg33.el6.noarch':
      ensure   => 'installed',
      provider => 'rpm',
      source   => 'https://repo.grid.iu.edu/osg/3.3/osg-3.3-el6-release-latest.rpm',
    }

    package { 'fermilab-util_kx509.noarch' :
      ensure => 'absent',
    }

    package {'git': ensure => present}
    package { 'httpd': ensure => present}
#   package {'java-1.8.0-openjdk': ensure =>present}
#   package { 'jenkins': ensure => present, }
    package { 'upsupdbootstrap-fnal': ensure => present }

    package { 'llrun':
      ensure          => present,
      install_options => '--enablerepo=osg-development',
    }

    package { 'lcmaps-plugins-gums-client':
      ensure          => present,
      install_options => '--enablerepo=osg-development',
    }

    package { 'lcmaps-without-gsi':
      ensure          => present,
      install_options => '--enablerepo=epel',
    }

    package { 'myproxy':
      ensure          => present,
      install_options => '--enablerepo=osg',
    }

    #package { 'dcache-srmclient.noarch':
    #  ensure          => present,
    #  install_options => '--enablerepo=osg',
    #}
      
    package { 'uberftp':
      ensure          => present,
      install_options => '--enablerepo=osg',
    }

    package { 'globus-ftp-client':
      ensure          => present,
      install_options => '--enablerepo=osg',
    }

#   package { 'bestman2-client':
#     ensure          => present,
#     install_options => '--enablerepo=osg',
#   }

    package { 'condor':
      ensure          => present,
      install_options => '--enablerepo=osg',
    }

    package { 'jobsub':
      ensure          => $jobsub_server::vars::jobsub_server_version,
      install_options => '--enablerepo=jobsub',
    }

    package { 'osg-ca-scripts':
      ensure          => present,
      install_options => '--enablerepo=osg',
    }

    #install jobsub_tools version and make it current
    $cmd = '/bin/su products -c '
    $ups = '. /fnal/ups/etc/setups.sh; setup ups; setup upd; '
    $install = ' upd install '
    $ver = $jobsub_server::vars::jobsub_tools_version
    $jt_ver = "jobsub_tools ${ver} -f Linux+2"
    $declare = ' ups declare -c '

    exec { 'install_jobsub_tools':#                                            #
      command => "${cmd} \"${ups} ${install} ${jt_ver};${declare} ${jt_ver}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${jt_ver} \" " ,
    }

    $ifdh_v = "ifdhc v1_8_5 -f Linux64bit+2.6-2.12 -q python27"
    exec { 'install_ifdhc':
      command => "${cmd} \"${ups} ${install} ${ifdh_v};${declare} ${ifdh_v}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${ifdh_v} \" " ,
    }
  

}
