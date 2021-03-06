#!/bin/sh
if [ "$1" = "" ]; then
    echo "usage: $0 server [joblist] "
    echo " hold and relieve list of jobs on server"
    exit 0
fi
source ./setup_env.sh
JOBLIST=`echo "$@"|sed 's/\s\+/,/g'`
GUSER=${GROUP}pro
echo before
$EXEPATH/jobsub_q --user $GUSER $GROUP_SPEC $SERVER_SPEC  
T1=$?
echo T1=$T1
echo holding joblist=${JOBLIST}
$EXEPATH/jobsub_hold --role Production $GROUP_SPEC $SERVER_SPEC  --jobid $JOBLIST --debug
T2=$?
echo T2=$T2
echo after hold
$EXEPATH/jobsub_q  --user $GUSER  $GROUP_SPEC $SERVER_SPEC  
T3=$?
echo T3=$T3
echo releasing joblist=${JOBLIST}
$EXEPATH/jobsub_release --role Production $GROUP_SPEC $SERVER_SPEC  --jobid $JOBLIST --debug
T4=$?
echo T4=$T4
echo after release
$EXEPATH/jobsub_q --user $GUSER  $GROUP_SPEC $SERVER_SPEC  
T5=$?
echo T5=$T5
echo holding joblist=${JOBLIST} with a bogus role
$EXEPATH/jobsub_hold --role production $GROUP_SPEC $SERVER_SPEC  --jobid $JOBLIST --debug
test $? -ne 0
T6=$?
echo releasing joblist=${JOBLIST} with a bogus role
$EXEPATH/jobsub_release --role production $GROUP_SPEC $SERVER_SPEC  --jobid $JOBLIST --debug
test $? -ne 0
T7=$?
! (( $T1 || $T2 || $T3 || $T4 || $T5 || $T6 || $T7 ))
TFINAL=$?

echo $0 exiting with status $TFINAL
exit $TFINAL
