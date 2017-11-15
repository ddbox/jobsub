#!/bin/sh

function help() {
    echo
    echo "usage:"
    echo 
    echo "$prog somehost.fnal.gov        install osg_client on somehost.fnal.gov"
    echo "                                                  use 'create_fermicloud_vm.sh' to create "
    echo "                                                  somehost.fnal.gov on fermicloud if desired "
    echo ""
    echo "$prog --help                   Print this help message and exit"
    echo
    exit 0
}
prog=`basename $0`
if [ $# -ne 1 ]; then
    help
fi
if [ "$1" = "--help" ]; then
    help
fi
export REMOTE_HOST=$1
export REMOTE_SCRIPT=osg_client_host_puppet_apply.sh
puppet module build osg_client
scp osg_client/pkg/gwms-osg_client-0.0.1.tar.gz root@${REMOTE_HOST}:gwms-osg_client-0.0.1.tar.gz
echo "puppet module list | grep gwms-osg_client" > $REMOTE_SCRIPT
echo "if [ \$? -eq 0 ]; then" >> $REMOTE_SCRIPT
echo "    puppet module uninstall gwms-osg_client" >> $REMOTE_SCRIPT
echo "fi" >> $REMOTE_SCRIPT
echo "puppet module install gwms-osg_client-0.0.1.tar.gz" >>$REMOTE_SCRIPT
echo "puppet apply -e \"class { 'osg_client' : }\"" >> $REMOTE_SCRIPT
echo "" >> $REMOTE_SCRIPT
scp $REMOTE_SCRIPT root@${REMOTE_HOST}:$REMOTE_SCRIPT
ssh root@${REMOTE_HOST} bash $REMOTE_SCRIPT
rm $REMOTE_SCRIPT
