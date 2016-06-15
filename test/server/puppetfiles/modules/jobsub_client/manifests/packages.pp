class jobsub_client::packages {

#  yumrepo { 'jenkins':
#    baseurl  => 'http://pkg.jenkins-ci.org/redhat',
#    descr    => 'Jenkins',
#    enabled  => 1,
#    gpgcheck => 1,
#    gpgkey   => 'http://pkg.jenkins-ci.org/redhat/jenkins-ci.org.key',
#  }
#   yumrepo { 'jobsub':
#     baseurl  => 'http://web1.fnal.gov/files/jobsub/dev/6/x86_64/',
#     descr    => 'Jobsub',
#     enabled  => 1,
#     gpgcheck => 0,
#   }


    package { 'osg-release':
      ensure   => 'installed',
      provider => 'rpm',
      source   => '/root/osg-3.2-el5-release-latest.rpm',
    }

    file { '/root/osg-3.2-el5-release-latest.rpm':
      require => Exec['osg-3.2-el5-release-latest.rpm'],
    }

    exec { 'osg-3.2-el5-release-latest.rpm':
      command => "/usr/bin/wget --no-check-certificate https://repo.grid.iu.edu/osg/3.2/osg-3.2-el5-release-latest.rpm -O /root/osg-3.2-el5-release-latest.rpm",
      creates => '/root/osg-3.2-el5-release-latest.rpm',
    }

    package { 'fermilab-util_kx509.noarch' :
      ensure => 'absent',
    }

    package {'yum-priorities': ensure => present,}
    package { 'httpd': ensure => present}
    package { 'upsupdbootstrap-fnal': ensure => present }
    package { 'curl': ensure => present }
    package { 'krb5-fermi-getcert': ensure => present }


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



    package { 'osg-ca-certs':
      ensure          => present,
      install_options => '--enablerepo=osg',
    }

    #install ups products and make them current
    $cmd = '/bin/su products -c '
    $ups = '. /fnal/ups/etc/setups.sh; setup ups; setup upd; '
    $install = ' upd install '
    $flv = $jobsub_client::vars::ups_flavor
    $declare = ' ups declare -c '

    $jver = $jobsub_client::vars::jobsub_client_version
    $jt_ver = "jobsub_client ${jver} -f NULL"
    
    $ups_version = "ups ${jobsub_client::vars::ups_version} -f ${flv}"

    exec { 'install_ups_version':#                                            #
      command => "${cmd} \"${ups} ${install} ${ups_version};${declare} ${ups_version}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${ups_version} \" " ,
    }
    exec { 'install_jobsub_client':#                                            #
      command => "${cmd} \"${ups} ${install} ${jt_ver};${declare} ${jt_ver}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${jt_ver} \" " ,
    }
    
    $ifdh_v = "ifdhc ${jobsub_client::vars::ifdhc_version} -f ${flv} -q python27"
    exec { 'install_ifdhc':
      command => "${cmd} \"${ups} ${install} ${ifdh_v};${declare} ${ifdh_v}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${ifdh_v} \" " ,
    }
  
    $cigetcertlibs = "cigetcertlibs ${jobsub_client::vars::cigetcert_libs_version} -f ${flv} "
    exec { 'install_cigetcertlibs':
      command => "${cmd} \"${ups} ${install} ${cigetcertlibs};${declare} ${cigetcertlibs}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${cigetcertlibs} \" " ,
    }

    $cigetcert = "cigetcert ${jobsub_client::vars::cigetcert_version} -f ${flv} "
    exec { 'install_cigetcert':
      command => "${cmd} \"${ups} ${install} ${cigetcert};${declare} ${cigetcert}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${cigetcert} \" " ,
    }

    $python = "python ${jobsub_client::vars::python_version} -f ${flv} "
    exec { 'install_python':
      command => "${cmd} \"${ups} ${install} ${python};${declare} ${python}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${python} \" " ,
    }

    $pycurl = "pycurl ${jobsub_client::vars::pycurl_version} -f ${flv} "
    exec { 'install_pycurl':
      command => "${cmd} \"${ups} ${install} ${pycurl};${declare} ${pycurl}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${pycurl} \" " ,
    }

    $kx509 = "kx509 ${jobsub_client::vars::kx509_version} -f NULL "
    exec { 'install_kx509':
      command => "${cmd} \"${ups} ${install} ${kx509};${declare} ${kx509}\" ",
      require => [ Package['upsupdbootstrap-fnal'], ],
      unless  => "${cmd} \"${ups} ups exist ${kx509} \" " ,
    }


}
