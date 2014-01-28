#!/bin/sh 
VERS=v0_1_2
REV='_1'

if [ "$1" ==  "" ]; then
	echo "usage $0 target_machine"
	echo "tars up jobsub_client and distributes it to /fnal/ups/prd"
	exit -1
fi

./make_tablefile.py $VERS$REV
cd ups_db
tar cvf db.jobsub_client.tar jobsub_client 
scp db.jobsub_client.tar products@$1.fnal.gov:/fnal/ups/db
ssh products@$1.fnal.gov "cd /fnal/ups/db;  tar xvf db.jobsub_client.tar; rm db.jobsub_client.tar; "
rm  db.jobsub_client.tar
cd -
#wget https://cdcvs.fnal.gov/redmine/attachments/download/15054/jobsub-client-v0.1.2.tar.gz
#tar xzvf jobsub-client-v0.1.2.tar.gz
#rm jobsub-client-v0.1.2.tar.gz
#mv jobsub/client jobsub/jobsub_client
mkdir -p jobsub/jobsub_client
cp ../client/* jobsub/jobsub_client
cd jobsub
tar cvf prd.jobsub_client.tar jobsub_client 

scp prd.jobsub_client.tar products@$1.fnal.gov:/fnal/ups/prd
CMD="cd /fnal/ups/prd; mkdir -p jobsub_client/$VERS$REV; rm -rf jobsub_client/$VERS$REV/* ; mkdir -p tmp; cd tmp; rm -rf *; tar xvf ../prd.jobsub_client.tar ; cd ..; mv tmp/jobsub_client jobsub_client/$VERS$REV/NULL; chmod -R g+w jobsub_client/$VERS$REV;rm prd.jobsub_client.tar; rm -rf tmp "
echo "performing $CMD on $1"
ssh products@$1.fnal.gov $CMD 
rm prd.jobsub_client.tar
cd ..

