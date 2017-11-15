# author Dennis Box, dbox@fnal.gov
class osg_client::vars{
    $osg_client_version = 'latest'
    $release_major = $::os['release']['major']
    case $::os['release']['major']{
      '5' : {
        $epel_release = 'epel-release-5'
        $epel_url = 'https://dl.fedoraproject.org/pub/epel/epel-release-latest-5.noarch.rpm'
        $osg_release = 'osg-release.noarch'
        $osg_url = 'https://repo.grid.iu.edu/osg/3.2/osg-3.2-el5-release-latest.rpm'
        $wget_opt = '--no-check-certificate'
        $yum_priorities = 'yum-priorities'
      }
      '6' : {
        $epel_release = 'epel-release-6'
        $epel_url = 'https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm'
        $osg_release = 'osg-release.noarch'
        $osg_url = 'https://repo.grid.iu.edu/osg/3.4/osg-3.4-el6-release-latest.rpm'
        $wget_opt = ''
        $yum_priorities = 'yum-plugin-priorities'
        $ssl_conf = 'ssl.conf.erb'
      }
      '7' : {
        $epel_release = 'epel-release-7'
        $epel_url = 'https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm'
        $osg_release = 'osg-release.noarch'
        $osg_url = 'https://repo.grid.iu.edu/osg/3.4/osg-3.4-el7-release-latest.rpm'
        $wget_opt = ''
        $yum_priorities = 'yum-plugin-priorities'
        $ssl_conf = 'ssl.conf.7.erb'
      }
      default: {
        $ups_flavor = 'NULL'
        $epel_url = 'NULL'
        $osg_url = 'NULL'
        $wget_opt = 'NULL'
      }
    }

}
