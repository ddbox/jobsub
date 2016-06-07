class jobsub_server::users{

     group { $jobsub_server::vars::jobsub_group:
       gid    => $jobsub_server::vars::jobsub_user_gid,
       ensure => present
     }

     user { $jobsub_server::vars::jobsub_user:
       ensure     => present,
       groups     => $jobsub_server::vars::jobsub_group,
       home       => "${jobsub_server::vars::jobsub_user_home}",
       managehome => true,
       uid        => $jobsub_server::vars::jobsub_user_uid,
       gid        => $jobsub_server::vars::jobsub_user_gid,
       shell      => '/bin/bash',
       require    => Group[$jobsub_server::vars::jobsub_group]
     }
}
