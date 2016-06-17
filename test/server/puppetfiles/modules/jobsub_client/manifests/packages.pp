class jobsub_client::packages( String $ups_flavor = $jobsub_client::vars::ups_flavor) {

    $osg_rpm = 'osg-3.2-el5-release-latest.rpm'

    package { 'osg-release':
      ensure   => 'installed',
      provider => 'rpm',
      source   => "/root/${osg_rpm}",
    }

    file { "/root/${osg_rpm}":
      require => Exec["${osg_rpm}"],
    }


    exec { "${osg_rpm}":
      command => "/usr/bin/wget --no-check-certificate https://repo.grid.iu.edu/osg/3.2/${osg_rpm} -O /root/${osg_rpm}",
      require => Package['wget'],
      creates => "/root/${osg_rpm}",
    }

    package { 'wget': ensure => present }
    package { 'fermilab-util_kx509.noarch' : ensure => absent }
    package { 'yum-priorities': ensure => present,}

    package { 'upsupdbootstrap-fnal': ensure => present }
    file {'/fnal/ups/.k5login':
      owner => 'products',
      content => 'dbox@FNAL.GOV',
      require => Package['upsupdbootstrap-fnal'],
    }

    package { 'curl': ensure => present }
    package { 'krb5-fermi-getcert': ensure => present }
      
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

   jobsub_client::ups::product { 
     'ups'          : version => $jobsub_client::vars::ups_version, qualifier => "-f ${ups_flavor}";
     'kx509'        : version => $jobsub_client::vars::kx509_version ;
     'jobsub_client': version => $jobsub_client::vars::jobsub_client_version ;
     'ifdhc'        : version => $jobsub_client::vars::ifdhc_version, qualifier => "-f ${ups_flavor} -q python27";
     'git'          : version => 'v1_8_5_3', qualifier => "-f ${ups_flavor}" ; 
     'pycurl'       : version => $jobsub_client::vars::pycurl_version, qualifier=> "-f ${ups_flavor}";
     'python'       : version => $jobsub_client::vars::python_version, qualifier=> "-f ${ups_flavor}";
     'cigetcertlibs': version => $jobsub_client::vars::cigetcert_libs_version, qualifier=> "-f ${ups_flavor}";
     'cigetcert'    : version => $jobsub_client::vars::cigetcert_version , qualifier=> "-f ${ups_flavor}";
   }
}
