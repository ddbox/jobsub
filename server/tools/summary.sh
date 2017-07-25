#!/bin/sh
CMDFILE=$1
CONDOR_TMP=`dirname $CMDFILE`
DAGFILE=`basename $2`
#PYTHONPATH=$JOBSUB_TOOLS_DIR/pylib/DAGParser/
OUTFILE=$CONDOR_TMP/$DAGFILE.summary.out
DAGLOGFILE=$DAGFILE.nodes.log
DAGPARENTLOGFILE=$DAGFILE.dagman.log
MAILTO=`grep -m1 notify_user $CMDFILE | sed -e 's/notify_user//' -e 's/=//' `
export CMDFILE CONDOR_TMP OUTFILE DAGLOGFILE DAGPARENTLOGFILE MAILTO
JOBSUBPARENTJOBID=`grep -m1 ^000 ${DAGPARENTLOGFILE} | sed -e 's/000 (//' | sed -e 's/\.00.*/\.0\@/'`
SCHEDD=$(grep -m1 +JobsubParentJobId $CMDFILE | cut -d '@' -f2- | sed s/\"//)
export SCHEDD
HOST=`hostname`
JOBSUBPARENTJOBID="${JOBSUBPARENTJOBID}${SCHEDD}"
export JOBSUBPARENTJOBID
SUBJECT="Job $JOBSUBPARENTJOBID Status Summary"
export SUBJECT
/bin/echo ''> $OUTFILE
/bin/echo "$SUBJECT" >> $OUTFILE
/bin/echo "--------------------------" >> $OUTFILE
/bin/echo '' >> $OUTFILE
python /opt/jobsub/lib/DAGParser/PrintSummary.py $DAGLOGFILE >> $OUTFILE 2>&1

mail -s "$SUBJECT" $MAILTO < $OUTFILE
exit 0
