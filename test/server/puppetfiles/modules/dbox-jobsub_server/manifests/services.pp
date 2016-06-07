class jobsub_server::services{
  service{'httpd':
    ensure     => true,
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
  }
  service{'condor':
    ensure     => true,
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
  }
  service{'jenkins':
    ensure     => true,
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
  }
}

