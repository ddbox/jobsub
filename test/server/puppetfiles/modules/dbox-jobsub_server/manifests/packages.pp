class jobsub_server::packages {
    yumrepo { 'jenkins':
      baseurl  => 'http://pkg.jenkins-ci.org/redhat',
      descr    => 'Jenkins',
      enabled  => 1,
      gpgcheck => 1,
      gpgkey   => 'http://pkg.jenkins-ci.org/redhat/jenkins-ci.org.key',
    }
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


    package {'git': ensure => present}
    package { 'httpd': ensure => present}
    package {'java-1.8.0-openjdk': ensure =>present}
    package { 'jenkins': ensure => present, }
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
    $ins = ' upd install jobsub_tools '
    $ver =  $jobsub_server::vars::jobsub_tools_version
    $flv = ' -f Linux+2 '
    $cur = ' ups declare -c jobsub_tools '

    exec { 'install_jobsub_tools':#                                            #
      command => "${cmd} \"${ups} ${ins} ${ver} ${flv};${cur} ${ver} ${flv}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist jobsub_tools ${ver} \" " ,
    }

}
