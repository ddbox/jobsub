#!/usr/bin/env python
# $Id$
import os
import sys
import datetime
from JobUtils import JobUtils
from optparse import OptionParser
from optparse import OptionGroup
from JobsubConfigParser import JobsubConfigParser


class UnknownInputError(Exception):pass

class IllegalInputError(Exception):pass

class InitializationError(Exception):pass

class MyCmdParser(OptionParser):
		
	def print_help(self):
		OptionParser.print_help(self)
		#OptionParser.epilog doesn't work in v python 2.4, here is my workaround
		epilog="""
	NOTES
	You can have as many instances of -c, -d, -e, -f, -l and -y as you need.

	The -d directory mapping works on non-Grid nodes, too.

	export IFDH_VERSION=some_version then use -e IFDH_VERSION to use 
        the (some_version) release of ifdh for copying files in and out 
        with -d and -f flags instead of the current ifdh version in KITS

	More documentation is available at 
	https://cdcvs.fnal.gov/redmine/projects/ifront/wiki/UsingJobSub
	and on this machine at 
	$JOBSUB_TOOLS_DIR/docs/
	

		
		"""
		print epilog
	 
class JobSettings(object):
	def __init__(self):
		#print "JobSettings.__init__"

		if hasattr(self, 'cmdParser'):
			pass
		else:
			usage = "usage: %prog [options] your_script [your_script_args]\n"
			usage +="submit your_script to local batch or to the OSG grid "
			
			
			self.cmdParser = MyCmdParser(usage=usage, version=os.environ.get("SETUP_JOBSUB_TOOLS","NO_UPS_DIR"))
			self.cmdParser.disable_interspersed_args()
			self.generic_group = OptionGroup(self.cmdParser, "Generic Options")
			self.cmdParser.add_option_group(self.generic_group)
			
			self.file_group= OptionGroup(self.cmdParser, "File Options")
			self.cmdParser.add_option_group(self.file_group)

			self.sam_group= OptionGroup(self.cmdParser, "SAM Options")
			self.cmdParser.add_option_group(self.sam_group)
			

		self.initCmdParser()
		self.initFileParser()
		self.settings = {}
		self.settings['submit_host']=os.environ.get("SUBMIT_HOST")
		if self.settings['submit_host'] == None:
			self.settings['submit_host'] = "gpsn01.fnal.gov"
		##self.settings['local_host']=os.environ.get("HOSTNAME")
		commands=JobUtils()
		(retVal,rslt)=commands.getstatusoutput("/bin/hostname")
		self.settings['local_host']=rslt
			
		self.settings['condor_tmp'] = os.environ.get("CONDOR_TMP","/tmp")
		if self.settings['condor_tmp'] == None:
			raise InitializationError("CONDOR_TMP not defined! setup_condor and try again")
			
		self.settings['condor_exec'] = os.environ.get("CONDOR_EXEC","/tmp")
		self.settings['condor_config'] = os.environ.get("CONDOR_CONFIG")
		self.settings['local_condor'] = os.environ.get("LOCAL_CONDOR","/opt/condor/bin")
		self.settings['group_condor'] = os.environ.get("GROUP_CONDOR","/this/is/bogus")

		self.settings['x509_user_proxy'] = os.environ.get("X509_USER_PROXY")
		if self.settings['x509_user_proxy'] == None:
			user=os.environ.get("USER")
			group=os.environ.get("GROUP","common")
			if group=="common":
				self.settings['x509_user_proxy'] = "/scratch/"+user+"/grid/"+user+".proxy"
			else:
				self.settings['x509_user_proxy'] = "/scratch/"+user+"/grid/"+user+"."+group+".proxy"

		self.settings['ifdh_base_uri'] = os.environ.get("IFDH_BASE_URI")
		if self.settings['ifdh_base_uri'] == None:
			group=os.environ.get("GROUP","common")
			self.settings['ifdh_base_uri'] = "http://samweb.fnal.gov:8480/sam/"+group+"/api"

		self.settings['output_tag_array']={}
		self.settings['input_dir_array'] = []
		self.settings['output_dir_array'] = []
		
		self.settings['istestjob']=False
		self.settings['needafs']=False
		self.settings['notify']=1
		self.settings['submit']=True
		self.settings['grid']=False

		self.settings['usepwd']=True
		self.settings['forceparrot']=False
		self.settings['forcenoparrot']=True
		self.settings['useparrot']=False
		self.settings['usedagman']=False
		self.settings['requirements']='((Arch==\"X86_64\") || (Arch==\"INTEL\"))'
		self.settings['environment']='CLUSTER=$(Cluster);PROCESS=$(Process);CONDOR_TMP='+\
						  self.settings['condor_tmp']+';CONDOR_EXEC='+\
						  self.settings['condor_exec']
		self.settings['lines']=[]
		self.settings['group']=os.environ.get("GROUP","common")
		self.settings['storage_group']=os.environ.get("STORAGE_GROUP")
		self.settings['accountinggroup']=self.settings['group']
		self.settings['user']=os.environ.get("USER")
		self.settings['version']=os.environ.get("SETUP_JOBSUB_TOOLS","NO_UPS_VERSION")
		self.settings['output_tag_counter']=0
		self.settings['input_tag_counter']=0
		self.settings['queuecount']=1
		self.settings['joblogfile']=""
		self.settings['override_x509']=False
		self.settings['use_gftp']=False
		self.settings['filebase']=''
		self.settings['filetag']=''
		self.settings['wrapfile']=''
		self.settings['parrotfile']=''
		self.settings['cmdfile']=''
		self.settings['dagfile']=''
		self.settings['sambeginfile']=''
		self.settings['samendfile']=''
		self.settings['processtag']=''
		self.settings['logfile']=''
		self.settings['opportunistic']=False
		self.settings['nowrapfile']=False
		self.settings['errfile']=''
		self.settings['outfile']=''
		self.settings['exe_script']=''
		self.settings['script_args']=[]
		self.settings['verbose'] = False
		self.settings['nologbuffer'] = False
		self.settings['wrapper_cmd_array']=[]
		self.settings['msopt']=""
		self.settings['added_environment']=""
		self.settings['generated_by']=self.settings['version']+" "+self.settings['local_host']
		self.settings['input_tar_dir']=False
		self.settings['tar_file_name']=""
		self.settings['overwrite_tar_file']=False
		self.settings['site']=False
		self.settings['dataset_definition']=""
		self.settings['project_name']=""
		self.settings['cmd_file_list']=[]
		self.settings['jobsub_tools_dir']=os.environ.get("JOBSUB_TOOLS_DIR","/tmp")
		self.settings['ups_shell']=os.environ.get("UPS_SHELL")
		self.settings['gftp_funcs']=commands.gftpString()
		#self.settings['condor_setup_cmd']='. /opt/condor/condor.sh; '
		self.settings['downtime_file']='/grid/fermiapp/common/jobsub_MOTD/JOBSUB_UNAVAILABLE'
		self.settings['motd_file']='/grid/fermiapp/common/jobsub_MOTD/MOTD'
		self.settings['wn_ifdh_location']=os.environ.get("WN_IFDH_LOCATION",'/grid/fermiapp/products/common/etc/setups.sh')
		self.settings['desired_os']=''
		self.settings['default_grid_site']=False
		self.settings['resource_list']=[]
                self.settings['transfer_executable']=False
                self.settings['transfer_input_files']=os.environ.get("TRANSFER_INPUT_FILES","")
                self.settings['needs_appending']=True
                self.settings['ifdh_cmd']='${JSB_TMP}/ifdh.sh'
		self.settings['jobsub_max_log_size']=5000000

		#for w in sorted(self.settings,key=self.settings.get,reverse=True):
		#	print "%s : %s"%(w,self.settings[w])
		#sys.exit


	def runCmdParser(self,a=None,b=None):
		(options, args) = self.cmdParser.parse_args(a,b)
		
		new_settings=vars(options)
		if new_settings.has_key('verbose') and new_settings['verbose']:
			print "new_settings = ",new_settings
		for x in new_settings.keys():
			if new_settings[x] is not None:
				self.settings[x]=new_settings[x]
		self.runFileParser()
                settings=self.settings
		#for w in sorted(self.settings,key=self.settings.get,reverse=True):
		#	print "%s : %s"%(w,self.settings[w])
		#sys.exit
		if 'override' in new_settings:
			(a,b)=new_settings['override']
			self.settings[a]=b

		if(len(args)<1):
			print "error, you must supply a script to run"
			print "jobsub -h for help"
			sys.exit(1)
		self.settings['exe_script']=args[0]
		executable_ok=os.access(self.settings['exe_script'],os.X_OK)
		if not executable_ok and os.path.exists(self.settings['exe_script']):
			os.chmod(self.settings['exe_script'],0775)
		
		
		#yuck
		if(len(args)>1):
			self.settings['script_args']=args[1:]
                for x in settings.keys():
                        if settings[x] in ['True','true','TRUE']:
                            settings[x]=True
                        if settings[x] in ['False','false','FALSE']:
                            settings[x]=False
                if settings.has_key('transfer_wrapfile'):
                    settings['tranfer_executable']=settings['transfer_wrapfile']
                if settings.has_key('always_run_on_grid') and settings['always_run_on_grid']:
                    settings['grid']=True
	def findConfigFile(self):
            if self.settings.has_key('jobsub_ini_file'):
                cnf=self.settings['jobsub_ini_file']
            else:
		cnf = self.fileParser.findConfigFile()
                self.settings['jobsub_ini_file']=cnf
	    return cnf
	
	def runFileParser(self):
		grp=os.environ.get("GROUP")
		commands=JobUtils()
                pairs = []
		if grp is None:
			(stat,grp)=commands.getstatusoutput("id -gn")
			user=os.environ.get("USER","fermilab")
		exps = self.fileParser.sections()
		if grp not in exps:
			grp = "fermilab"
                if self.fileParser.has_section('default'):
                        pairs.extend(self.fileParser.items('default'))
                if self.fileParser.has_section(grp):
                        pairs.extend(self.fileParser.items(grp))
                sbhst=os.environ.get("SUBMIT_HOST")
                if sbhst is None:
                        sbhst = self.settings['submit_host']
                if self.fileParser.has_section(sbhst):
                        pairs.extend(self.fileParser.items(sbhst))
                use_these=dict(pairs)
		for (x,y) in pairs:
			eval=os.environ.get(x.upper(),None)
			if eval is not None:
				self.settings[x]=eval
			else:
                                yp = use_these[x]
				cmd = "echo %s"%yp
				(stat,rslt)=commands.getstatusoutput(cmd) 
				self.settings[x]=rslt

			
        def resource_callback(self,option, opt, value, p):
            #print "callback opt=%s val=%s"%(opt,value)
            self.settings['resource_list'].append(value)


	def initFileParser(self):
		self.fileParser=JobsubConfigParser()
		

				
	def initCmdParser(self):
		#print "JobSettings initCmdParser"
		cmdParser = self.cmdParser
		
		generic_group=self.generic_group
		file_group=self.file_group
		sam_group=self.sam_group
		

		file_group.add_option("-l", "--lines", dest="lines",action="append",type="string",
							  help="[Expert option]  Add the line <line> to the\
							  Condor submission (.cmd) file.  See Condor\
							  help for more.")

		
##		 file_group.add_option("-o", "--output", dest="output",action="append",type="string",
##							   help="output file  ")

		
		file_group.add_option("-a", "--needafs", dest="needafs",action="store_true",default=False,
							  help="run on afs using parrot (this is discouraged)  ")

		#file_group.add_option("--tar_directory", dest="tar_directory",action="store",
		#					  help="put contents of TAR_DIRECTORY into self extracting tarfile.  On worker node, untar and then run your_script with your_script_arguments")

		
		sam_group.add_option("--dataset_definition", dest="dataset_definition",
								action="store",type="string",
								help="SAM dataset definition used in a Directed Acyclic Graph (DAG)")
		
		sam_group.add_option("--project_name", dest="project_name",
								action="store",type="string",
								help="optional project name for SAM DAG ")
		
		
		generic_group.add_option("--OS", dest="os",
								 action="store",type="string",default="SL5",
								 help="specify OS version of worker node. Default is SL5,  and SL6 is supported.  Comma seperated list '--OS=SL4,SL5,SL6' works as well ")

		generic_group.add_option("-G","--group", dest="accountinggroup",
								 action="store",type="string",
								 help="Group/Experiment/Subgroup for priorities and accounting")

		generic_group.add_option("-v", "--verbose", dest="verbose",action="store_true",default=False,
							  help="dump internal state of program (useful for debugging)")
		generic_group.add_option("--resource-provides", type="string", action="callback",callback=self.resource_callback,
                        help="request specific resources by changing condor jdf file.  For example: --resource-provides=CVMFS=OSG will add +CVMFS=\"OSG\" to the job classad attributes and '&&(CVMFS==\"OSG\")' to the job requirements")

		generic_group.add_option("-M","--mail_always", dest="notify",
								 action="store_const",const=2,
								 help="send mail when job completes or fails")
		
		generic_group.add_option("-q","--mail_on_error", dest="notify",
								 action="store_const",const=1,
								 help="send mail only when job fails due to error (default)")
		
		generic_group.add_option("-Q","--mail_never", dest="notify",
								 action="store_const",const=0,
								 help="never send mail (default is to send mail on error)")

		generic_group.add_option("-T","--test_queue", dest="istestjob",
								 action="store_true",default=False,
								 help="Submit as a test job.  Job will run with highest\
								 possible priority, but you can only have one such\
								 job in the queue at a time.")

		file_group.add_option("-L","--log_file", dest="joblogfile",action="store",
							  help="Log file to hold log output from job.")
		
		file_group.add_option("--no_log_buffer", dest="nologbuffer",action="store_true",
							  help="write log file directly to disk. Default is to copy it back after job is completed.  This option is useful for debugging but can be VERY DANGEROUS as joblogfile typically is sent to bluearc.  Using this option incorrectly can cause all grid submission systems at FNAL to become overwhelmed resulting in angry admins hunting you down, so USE SPARINGLY. ")

		generic_group.add_option("-g","--grid", dest="grid",action="store_true",
							  help="run job on the FNAL GP  grid. Other flags can modify target sites to include other areas of the Open Science Grid")
		
		generic_group.add_option("--nowrapfile", dest="nowrapfile",action="store_true",
							  help="do not generate shell wrapper for fermigrid operations. (default is to generate a wrapfile)")
		

		file_group.add_option("--use_gftp", dest="use_gftp",action="store_true",default=False,
							  help="use grid-ftp to transfer file back")

		generic_group.add_option("-c","--append_condor_requirements", dest="append_requirements",action="append",
							  help="append condor requirements")

		generic_group.add_option("--overwrite_condor_requirements", dest="overwriterequirements",action="store",
							  help="overwrite default condor requirements with supplied requirements")

		generic_group.add_option("--override", dest="override",nargs=2, action="store",default=(1,1),
							  help="override some other value: --override 'requirements' 'gack==TRUE' would produce the same condor command file as --overwrite_condor_requirements 'gack==TRUE' if you want to use this option, test it first with -n to see what you get as output ")


		generic_group.add_option("-C",dest="usepwd",action="store_true",default=False,
							  help="execute on grid from directory you are currently in")

		generic_group.add_option("-e","--environment", dest="added_environment",action="append",
							  help="""-e ADDED_ENVIRONMENT exports this variable and its local value to worker node environment. For example export FOO="BAR"; jobsub -e FOO <more stuff> guarantees that the value of $FOO on the worker node is "BAR" .  Can use this option as many times as desired""")


		generic_group.add_option("--submit_host", dest="submit_host",action="store",
							  help="submit to different host")

		generic_group.add_option("--site", dest="site",action="store",
							  help="submit jobs to this site ")

		file_group.add_option("--input_tar_dir", dest="input_tar_dir",action="store",
							  help="create self extracting tarball from contents of INPUT_TAR_DIR.  This tarball will be run on the worker node with arguments you give to your_script")

		file_group.add_option("--tar_file_name", dest="tar_file_name",action="store",
							  help="name of tarball to submit, created from --input_tar_dir if specified")

		file_group.add_option("--overwrite_tar_file", dest="overwrite_tar_file",action="store_true",
							  help="overwrite TAR_FILE_NAME when creating tarfile using --input_tar_dir")
		
		generic_group.add_option("-p", dest="forceparrot",
								 action="store_true",default=False,
								 help="use parrot to run on afs (only makes sense with -a flag)")

		generic_group.add_option("--pOff", dest="forcenoparrot",
								 action="store_true",default=False,
								 help="turn parrot off explicitly (this is the default)")


		generic_group.add_option("-n","--no_submit", dest="submit",action="store_false",default=True,
							  help="generate condor_command file but do not submit")


		generic_group.add_option("--opportunistic", dest="opportunistic",action="store_true",default=False,
							  help="submit opportunistically to Fermigrid GP Grid and CDF Grid.  This option will allow you to potentially get more slots than your Fermigrid quota, but these slots are subject to preemption")

		generic_group.add_option("-N", dest="queuecount",action="store",default=1,type="int",
							  help="""submit N copies of this job. Each job will
						 have access to the environment variable
						 $PROCESS that provides the job number (0 to
						 <num>-1), equivalent to the decimal point in
						 the job ID (the '2' in 134567.2). """)


		file_group.add_option("-f", dest="input_dir_array",action="append",type="string",
							  help="""-f <file>	  input file <file> will be copied to directory  
						 $CONDOR_DIR_INPUT on the execution node.  
						 Example :-f /grid/data/minerva/my/input/file.xxx  
						 will be copied to $CONDOR_DIR_INPUT/file.xxx 
						 Specify as many -f file1 -f file2 args as you need.""")
		
		file_group.add_option("-d", dest="output_dir_array",action="append",type="string",
							  nargs=2,
							  help=""" -d<tag> <dir>  Writable directory $CONDOR_DIR_<tag> will
						 exist on the execution node.  After job completion,
						 its contents will be moved to <dir> automatically
						 Specify as many <tag>/<dir> pairs as you need. """)

		generic_group.add_option("-x","--X509_USER_PROXY", dest="x509_user_proxy",action="store",type="string",
							  help="location of X509_USER_PROXY (expert mode)")



	def checkSanity(self):
		settings = self.settings
		for arg in settings['added_environment']:
			if os.environ.has_key(arg)==False:
				err = "you used -e %s , but $%s must be set first for this to work!"%(arg,arg)
                                raise InitializationError(err)
                                                    
                if settings['istestjob'] and settings['queuecount'] > 1:
			err = "you may only send one test job at a time, -N=%d not allowed" % settings['queuecount']
			raise InitializationError(err)
			
		#if settings['nologbuffer'] and settings['queuecount'] > 1:
		#	err = " --nologbuffer and -N=%d (where N>1) options are not allowed together " % settings['queuecount']
		#	raise InitializationError(err)
			
		if settings['nologbuffer'] and settings['use_gftp']:
			err = " --use_gftp and --no_log_buffer together make no sense"
			raise InitializationError(err)
	
	
		if settings['nologbuffer'] and settings['joblogfile'] == "":
			err = "you must specify an input value for the log file with -L if you use --no_log_buffer"
			raise InitializationError(err)
		
		if settings['input_tar_dir'] and settings['tar_file_name'] == "":
			err = "you must specify a --tar_file_name if you create a tar file using --input_tar_dir"
			raise InitializationError(err)

		if settings['nowrapfile']:

			if len(settings['output_dir_array'])>0:
				err = "-d file transfers are done in the wrapfile, using with --nowrapfile does not make sense"
				raise InitializationError(err)

			if len(settings['input_dir_array'])>0:
				err = "-f file transfers are done in the wrapfile, using with --nowrapfile does not make sense"
				raise InitializationError(err)
			
			if settings['use_gftp']:
				err = "--use_gftp file transfers are done in the wrapfile, using with --nowrapfile does not make sense"
				raise InitializationError(err)
			
		return True



	def makeParrotFile(self):
		# print "makeParrotFile"
		settings = self.settings
		commands = JobUtils()
		glob = commands.parrotString()

		glob = glob.replace('WRAPFILETAG', settings['wrapfile'])
		f = open(settings['parrotfile'], 'w')
		f.write(glob)
		f.close()

	def makeWrapFilePreamble(self):
		#print "jobsettings makeWrapFilePreamble"
		settings=self.settings
		f = open(settings['wrapfile'], 'a')
		f.write("#!/bin/sh\n")
		f.write("#\n")
                f.write("umask 002\n")
		f.write("# %s\n"%settings['wrapfile'])
		f.write("# Automatically generated by: \n")
		ln=int(len(sys.argv))
		f.write("#	  %s %s \n" % \
				( os.path.basename(sys.argv[0]) ," ".join( sys.argv[1:]) ) )

		f.write("\n")
		
		#f.write(settings['gftp_funcs'])
		f.write("# Hold and clear arg list\n")
		f.write("args=\"$@\"\n")
		f.write("set - \"\"\n")
		f.write("\n")
		f.write("# To prevent output files from being transferred back\n")
		f.write("export JSB_TMP=$_CONDOR_SCRATCH_DIR/jsb_tmp\n")
                f.write("mkdir -p $JSB_TMP\n")
		f.write("export _CONDOR_SCRATCH_DIR=$_CONDOR_SCRATCH_DIR/no_xfer\n")
		f.write("export TMP=$_CONDOR_SCRATCH_DIR\n")
		f.write("export TEMP=$_CONDOR_SCRATCH_DIR\n")
		f.write("export TMPDIR=$_CONDOR_SCRATCH_DIR\n")
		f.write("export OSG_WN_TMP=$TMPDIR\n")
		f.write("mkdir -p $_CONDOR_SCRATCH_DIR\n")
		f.write("""if [ "${JOBSUB_MAX_LOG_SIZE}" = "" ] ; then JOBSUB_MAX_LOG_SIZE=%s ; fi \n"""%settings['jobsub_max_log_size'])
                f.write("""exec 7>&1; exec >${JSB_TMP}/JOBSUB_LOG_FILE; exec 8>&2; exec 2>${JSB_TMP}/JOBSUB_ERR_FILE\n""")


		f.write("\n")
                #ifdh_setup=JobUtils().ifdhString()%settings['wn_ifdh_location']
                #f.write(ifdh_setup)
                ifdh_pgm_text=JobUtils().ifdhString()%(settings['ifdh_cmd'],settings['wn_ifdh_location'],settings['ifdh_cmd'])
                f.write(ifdh_pgm_text)


	def makeWrapFilePostamble(self):
		#print "makeWrapFilePostamble"
		settings=self.settings
		ifdh_cmd=settings['ifdh_cmd']
                exe_script=settings['exe_script']
                if settings['transfer_executable']:
                    exe_script=os.path.basename(settings['exe_script'])
		script_args=''
		f = open(settings['wrapfile'], 'a')
		for x in settings['script_args']:
			script_args = script_args+x+" "
		log_cmd = """%s log "%s:BEGIN EXECUTION %s %s "\n"""%(ifdh_cmd,settings['user'],os.path.basename(exe_script),script_args)
		f.write(log_cmd)
		if settings['joblogfile'] != "":
			if settings['nologbuffer']==False:
				f.write("%s %s > $_CONDOR_SCRATCH_DIR/tmp_job_log_file 2>&1\n" % (exe_script,script_args))
			else:
				f.write("%s %s > %s  2>&1\n" % (exe_script,script_args,settings['joblogfile']))

		else:
			f.write("%s %s  \n" % \
						(exe_script,script_args))
 

		f.write("JOB_RET_STATUS=$?\n")

		log_cmd = """%s log "%s:%s COMPLETED with return code $JOB_RET_STATUS" \n"""%(ifdh_cmd,settings['user'],os.path.basename(exe_script))
		f.write(log_cmd)
		
		copy_cmd=log_cmd1=log_cmd2=cnt=append_cmd=''
		if len(settings['output_dir_array'])>0:
			my_tag="%s:%s"%(settings['user'],os.path.basename(exe_script))
                        if settings['use_gftp']:
                                copy_cmd="""\t%s cp --force=expgridftp -r -D  """%ifdh_cmd
                        else:
                                copy_cmd="""\t%s cp  -D  """%ifdh_cmd


			for tag in settings['output_dir_array']:
				f.write("if [ \"$(ls -A ${CONDOR_DIR_%s})\" ]; then\n" %(tag[0]))
				f.write("\tchmod a+rwx ${CONDOR_DIR_%s}/*\n" % tag[0])
				f.write("\tmkdir -p %s\n" % tag[1])
				f.write("fi\n")

				if settings['use_gftp']:
					copy_cmd=copy_cmd+""" %s  ${CONDOR_DIR_%s}/ %s """%(cnt, tag[0],tag[1])
				else:
					copy_cmd=copy_cmd+""" %s   ${CONDOR_DIR_%s}/* %s """%(cnt,tag[0],tag[1])
					#append_cmd=append_cmd+"""; chmod g+w %s/*"""%tag[1]
				cnt='\;'
					
			log_cmd1 = """\t%s log "%s BEGIN %s "\n"""%(ifdh_cmd,my_tag,copy_cmd)
			log_cmd2 = """\t%s log "%s FINISHED %s "\n"""%(ifdh_cmd,my_tag,copy_cmd)				
	
		f.write(log_cmd1)
		f.write("%s %s\n"%(copy_cmd,append_cmd))
		f.write(log_cmd2)

			
		if settings['joblogfile'] != "":
			f.write("%s cp  $_CONDOR_SCRATCH_DIR/tmp_job_log_file %s\n"%(ifdh_cmd,settings['joblogfile']))
                f.write("""exec 1>&7 7>&- ; exec 2>&8 8>&- ; tail -c ${JOBSUB_MAX_LOG_SIZE} ${JSB_TMP}/JOBSUB_ERR_FILE 1>&2 ; tail -c ${JOBSUB_MAX_LOG_SIZE} ${JSB_TMP}/JOBSUB_LOG_FILE \n""") 

		f.write("exit $JOB_RET_STATUS\n")
		f.close
		cmd = "chmod +x %s" % settings['wrapfile'] 
		commands=JobUtils()
		(retVal,rslt)=commands.getstatusoutput(cmd)

		
	def makeWrapFile(self):
		#print "makeWrapFile"
		settings=self.settings
		ifdh_cmd=settings['ifdh_cmd']
		f = open(settings['wrapfile'], 'a')


		f.write("export PATH=\"${PATH}:.\"\n")
		f.write("\n")
		for tag in settings['output_dir_array']:
			f.write("export CONDOR_DIR_%s=${_CONDOR_SCRATCH_DIR}/${PROCESS}/%s\n" %\
					(tag[0],tag[0]))
			f.write("export CONDOR_DEST_DIR_%s=%s\n" %\
					(tag[0],tag[1]))
			f.write("mkdir -p $CONDOR_DIR_%s\n" % tag[0])
			#f.write("mkdir -p $CONDOR_DEST_DIR_%s\n" % tag[0])
			f.write("echo ${CONDOR_DIR_%s}\n" % tag[0] )
			f.write("ls -lrt ${CONDOR_DIR_%s}\n" % tag[0])
			f.write("chmod g+rwx $CONDOR_DIR_%s\n\n" % tag[0])


		f.write("export CONDOR_DIR_INPUT=${_CONDOR_SCRATCH_DIR}/${PROCESS}/TRANSFERRED_INPUT_FILES\n")
		f.write("mkdir -p ${_CONDOR_SCRATCH_DIR}/${PROCESS}\n")
		f.write("mkdir -p ${CONDOR_DIR_INPUT}\n")
		#f.write("CPN=/grid/fermiapp/common/tools/cpn \n")
                if settings['use_gftp']:
                    cmd="""%s cp --force=expgridftp  """%ifdh_cmd
                else:
                    cmd="""%s  cp  -D  """%ifdh_cmd
		cnt=""
		for idir in settings['input_dir_array']:
			cmd=cmd+""" %s %s ${CONDOR_DIR_INPUT}/""" % (cnt,idir)
			cnt="\;"
		if len(settings['input_dir_array'])>0:
			f.write("""%s  log "%s BEGIN %s"\n"""%(ifdh_cmd,settings['user'],cmd))
			f.write("%s\n"%cmd)
			f.write("""%s  log "%s FINISHED %s"\n"""%(ifdh_cmd,settings['user'],cmd))
			
		f.write("\n")


                if settings['transfer_executable']==False:
		    targetdir='/bin/pwd'
		    commands=JobUtils()
		    retVal,rslt=commands.getstatusoutput(targetdir)
		    f.write("if [ -d %s ]\nthen\n" % rslt)
		    f.write("  cd %s\nelse\n" %rslt)
		    f.write("  echo Cannot change to submission directory %s\n" % rslt )
		    f.write("  echo ...Working dir is thus `/bin/pwd`\n")
		    f.write("fi\n")

		

		f.close()


	def makeTarDir(self):
		settings=self.settings
		ju=JobUtils()
		if os.path.exists(settings['tar_file_name']) and not settings['overwrite_tar_file']:
			raise IllegalInputError("%s already exists! if you want to overwrite it use --overwrite_tar_file "%\
						settings['tar_file_name'])
		f = open(settings['tar_file_name'], 'w')
		if not os.path.isdir(settings['input_tar_dir']):
			raise IllegalInputError("%s does not exist or is not a directory "%\
						settings['input_tar_dir'])
		base=os.path.basename(settings['input_tar_dir'])
		iret,tmpdir=ju.getstatusoutput("/bin/mktemp -d")
		cwd = os.getcwd()
		os.chdir(settings['input_tar_dir'])
		iret,ires=ju.getstatusoutput("tar czvf %s/%s.tgz * "%(tmpdir,base))
		if iret:
			raise Exception(ires)
		f = open('%s/xtract.sh'%tmpdir ,'w')
		f.write(ju.untar_sh())
		f.close()
		iret,ires=ju.getstatusoutput("cat %s/xtract.sh %s/%s.tgz > %s/%s.sh"%(tmpdir,tmpdir,base,tmpdir,base))
		if iret:
			raise Exception(ires)
		
		iret,ires=ju.getstatusoutput("mv %s/%s.sh %s"%(tmpdir,base,settings['tar_file_name']))
		if iret:
			raise Exception(ires)
		
		iret,ires=ju.getstatusoutput("chmod +x %s"%(settings['tar_file_name']))
		if iret:
			raise Exception(ires)
		
		
		

	def makeCondorFiles(self):
		self.checkSanity()
		settings=self.settings
		if settings['input_tar_dir']:
			self.makeTarDir()
			
		a = settings['exe_script'].split("/")
		ow = datetime.datetime.now()
		pid=os.getpid()
		filebase = "%s_%s%02d%02d_%02d%02d%02d_%s"%(a[-1],ow.year,
							    ow.month,ow.day,ow.hour,
							    ow.minute,ow.second,pid)
		settings['filetag']=filebase
		if settings['dataset_definition']=="":
			self.makeCondorFiles2()
		else:
			if settings['project_name']=="":
				settings['project_name']="%s-%s"%(settings['user'],settings['filetag'])
			job_count=settings['queuecount']
			settings['queuecount']=1
			job_iter=1
			while (job_iter <= job_count):
				#print "calling self.makeCondorFiles2(%d)"%job_iter
				self.makeCondorFiles2(job_iter)
	    			job_iter += 1
                                settings['needs_appending']=False

				
			self.makeDAGFile()
			self.makeSAMBeginFiles()
			self.makeSAMEndFiles()


	def makeSAMBeginFiles(self):
		settings = self.settings
		sambeginexe = "%s/%s.sambegin.sh"%(settings['condor_exec'],settings['filetag'])
		f = open(sambeginexe,'wx')
		f.write("#!/bin/sh -x\n")
		f.write("EXPERIMENT=$1\n")
		f.write("DEFN=$2\n")
		f.write("PRJ_NAME=$3\n")
		f.write("SAM_USER=$4\n")
		f.write("export JSB_TMP=$_CONDOR_SCRATCH_DIR/jsb_tmp\n")
                f.write("mkdir -p $JSB_TMP\n")
                ifdh_pgm_text=JobUtils().ifdhString()%(settings['ifdh_cmd'],settings['wn_ifdh_location'],settings['ifdh_cmd'])
                f.write(ifdh_pgm_text)
		f.write("""export IFDH_BASE_URI=%s\n"""%settings['ifdh_base_uri'])
		f.write("ifdh describeDefinition $DEFN\n")
		f.write("""if [ "$SAM_STATION" = "" ]; then\n""")
		f.write("""SAM_STATION=$EXPERIMENT\n""")
		f.write("fi\n")
		f.write("ifdh startProject $PRJ_NAME $SAM_STATION $DEFN  $SAM_USER $EXPERIMENT\n")		   
		f.close()
		cmd = "chmod +x %s" % sambeginexe
		commands=JobUtils()
		(retVal,rslt)=commands.getstatusoutput(cmd)
		
		f = open(settings['sambeginfile'], 'w')
		f.write("universe	  = vanilla\n")
		f.write("executable	= %s\n"%sambeginexe)
		f.write("arguments	 = %s %s %s %s\n"%(settings['group'],
							   settings['dataset_definition'],
							   settings['project_name'],settings['user']))
		
		f.write("output		= %s/sambegin-%s.out\n"%(settings['condor_tmp'],settings['filetag']))
		f.write("error		 = %s/sambegin-%s.err\n"%(settings['condor_tmp'],settings['filetag']))
		f.write("log		   = %s/sambegin-%s.log\n"%(settings['condor_tmp'],settings['filetag']))
		#f.write("environment   = CLUSTER=$(Cluster);PROCESS=$(Process);CONDOR_TMP=%s;CONDOR_EXEC=%s;IFDH_BASE_URI=%s;\n"%\

		#		(settings['condor_tmp'],settings['condor_exec'],settings['ifdh_base_uri']))
		f.write("environment = %s\n"%settings['environment'])
		f.write("rank		  = Mips / 2 + Memory\n")
		f.write("notification  = Error\n")
		#f.write("x509userproxy = %s\n" % settings['x509_user_proxy'])
		f.write("+RUN_ON_HEADNODE= True\n")
                f.write("transfer_executable     = True\n")
                self.handleResourceProvides(f)

		#f.write("requirements  = ((Arch==\"X86_64\") || (Arch==\"INTEL\"))  \n")
                f.write("requirements  = %s\n"%self.condorRequirements())

		#f.write("+GeneratedBy =\"%s\"\n"%settings['version'])
		f.write("queue 1\n")	 
		f.close()
				
		#print "makeSamBeginFiles created %s\n%s\n"%(sambeginexe,settings['sambeginfile'])
	
	def makeSAMEndFiles(self):
		settings = self.settings
		samendexe = "%s/%s.samend.sh"%(settings['condor_exec'],settings['filetag'])
		f = open(samendexe,'wx')
		f.write("#!/bin/sh -x\n")
		f.write("EXPERIMENT=$1\n")
		f.write("PRJ_NAME=$2\n")
		f.write("export JSB_TMP=$_CONDOR_SCRATCH_DIR/jsb_tmp\n")
                f.write("mkdir -p $JSB_TMP\n")
                ifdh_pgm_text=JobUtils().ifdhString()%(settings['ifdh_cmd'],settings['wn_ifdh_location'],settings['ifdh_cmd'])
                f.write(ifdh_pgm_text)
		f.write("""export IFDH_BASE_URI=%s\n"""%settings['ifdh_base_uri'])
		f.write("CPURL=`ifdh findProject $PRJ_NAME ''` \n")
		f.write("%s  endProject $CPURL\n"%settings['ifdh_cmd'])		   
		f.close()
		f = open(settings['samendfile'], 'w')
		f.write("universe	  = vanilla\n")
		f.write("executable	= %s\n"%samendexe)
		f.write("arguments	 = %s %s\n"%(settings['group'],
												 settings['project_name']))
		f.write("output		= %s/samend-%s.out\n"%(settings['condor_tmp'],settings['filetag']))
		f.write("error		 = %s/samend-%s.err\n"%(settings['condor_tmp'],settings['filetag']))
		f.write("log		   = %s/samend-%s.log\n"%(settings['condor_tmp'],settings['filetag']))
		#f.write("environment   = CLUSTER=$(Cluster);PROCESS=$(Process);CONDOR_TMP=%s;CONDOR_EXEC=%s;IFDH_BASE_URI=%s;\n"%\
		#			(settings['condor_tmp'],settings['condor_exec'],settings['ifdh_base_uri']))
		f.write("environment = %si\n"%settings['environment'])
		f.write("rank		  = Mips / 2 + Memory\n")
		f.write("notification  = Error\n")
		#f.write("x509userproxy = %s\n" % settings['x509_user_proxy'])
		f.write("+RUN_ON_HEADNODE= True\n")
                f.write("transfer_executable     = True\n")
                self.handleResourceProvides(f)
                f.write("requirements  = %s\n"%self.condorRequirements())
		#f.write("+GeneratedBy =\"%s\"\n"%settings['version'])
		f.write("queue 1\n")	 

		f.close()
		cmd = "chmod +x %s" % samendexe
		commands=JobUtils()
		(retVal,rslt)=commands.getstatusoutput(cmd)


		
		#print "makeSamEndFiles created %s\n%s\n"%(samendexe,settings['samendfile'])
		

	def makeDAGFile(self):
		#print "JobSettings.makeDAGFile()"
		settings=self.settings
		print settings['dagfile']

		f = open(settings['dagfile'], 'w')
		f.write("DOT %s.dot UPDATE\n"%settings['dagfile'])
		f.write("JOB SAM_START %s\n"%settings['sambeginfile'])
		n=1
		exe=os.path.basename(settings['exe_script'])
		for x in settings['cmd_file_list']:
			f.write("JOB %s_%d %s\n"%(exe,n,x))
			n+=1
		f.write("JOB SAM_END %s\n"%settings['samendfile'])
		f.write("Parent SAM_START child ")
		n1=1
		while (n1 <n):
			f.write("%s_%d "%(exe,n1))
			n1+=1
		f.write("\n")
		f.write("Parent ")
		n1=1
		while (n1 <n):
			f.write("%s_%d "%(exe,n1))
			n1+=1
		f.write("child SAM_END\n")
		
		f.close()
	
	 
	def makeCondorFiles2(self,job_iter=0):
		#makeCondorFiles2(%s)"%job_iter
		settings=self.settings
		filebase="%s_%s"%(settings['filetag'],job_iter)
		if settings['dagfile']=='':
			settings['dagfile']="%s/%s.dag" % (settings['condor_tmp'],filebase)
			settings['sambeginfile']="%s/%s.sambegin.cmd" % (settings['condor_tmp'],filebase)
			settings['samendfile']="%s/%s.samend.cmd" % (settings['condor_tmp'],filebase)
		uniquer=0
		retVal = 0
		while (retVal == 0):
			uniquer = uniquer + 1
			cmd = "ls %s/%s_%d.cmd" % (settings['condor_tmp'],filebase, uniquer) 
			commands=JobUtils()
			(retVal,rslt)=commands.getstatusoutput(cmd)
			if settings['verbose']:
				print "%s returns %s - %s " % (cmd, retVal, rslt)


			settings['wrapfile'] ="%s/%s_%s_wrap.sh" % \
			(settings['condor_exec'],filebase,uniquer)
			settings['parrotfile'] ="%s/%s_%s_parrot.sh" % \
			(settings['condor_exec'],filebase,uniquer)
			settings['filebase'] ="%s/%s_%s" % \
			(settings['condor_tmp'],filebase,uniquer)
			settings['cmdfile'] = settings['filebase']+".cmd"

			if settings['verbose']:
				print "settings['wrapfile'] =",settings['wrapfile']
				print "settings['parrotfile'] =",settings['parrotfile']
				print "settings['filebase'] =",settings['filebase']
				print "settings['cmdfile'] =",settings['cmdfile']

			if settings['queuecount']>1:
				settings['processtag'] = "_$(Process)"

			#settings['logfile']=settings['filebase']+settings['processtag']+".log"
			settings['logfile']=settings['filebase']+".log"
			settings['errfile']=settings['filebase']+settings['processtag']+".err"
			settings['outfile']=settings['filebase']+settings['processtag']+".out"

			##if (settings['joblogfile']=="" and settings['grid']==0):
				##settings['joblogfile']=settings['filebase']+settings['processtag']+".joblog"

			if settings['verbose']:
				print "settings['logfile'] =",settings['logfile']
				print "settings['errfile'] =",settings['errfile']
				print "settings['outfile'] =",settings['outfile']
				print "settings['joblogfile'] =",settings['joblogfile']


			for tag in settings['output_tag_array'].keys():
				cmd1 = "mkdir -p %s " % settings['output_tag_array'][tag]
				settings['wrapper_cmd_array'].append(cmd1)
				if settings['verbose']:
					print cmd1
				cmd2 = "chmod g+rw %s " % settings['output_tag_array'][tag]
				settings['wrapper_cmd_array'].append(cmd2)
				if settings['verbose']:
					print cmd2
				cmd3 = "export CONDOR_DIR_${%s}=\${CONDOR_SCRATCH_DIR/\${PROCESS}/${%s}" % (tag,tag)
				settings['wrapper_cmd_array'].append(cmd3)
				if settings['verbose']:
					print cmd3
            #pid=os.getpid()
			#print"pid=%s \n"%(pid)
			if settings['dataset_definition']=="":
				print"%s"%(settings['cmdfile'])
			#print "uniquer=%s calling self.makeCommandFile(%s)"%(uniquer,job_iter)
			if uniquer==1:
				self.makeCommandFile(job_iter)
				if settings['nowrapfile']==False:
					if settings['useparrot']==False:
						self.makeWrapFilePreamble()
						self.makeWrapFile()
						self.makeWrapFilePostamble()
					else:
						self.makeParrotFile()

	   

	def makeCommandFile(self, job_iter=0 ):
		#print "testing for submit host:%s"%self.settings['submit_host']
		if self.settings['submit_host'].find("gpsn01")>=0:
			self.makeGPSN01CommandFile(job_iter)
		else:
			self.makeOtherCommandFile(job_iter)

        def shouldTransferInput(self):
            settings=self.settings
            rsp="transfer_executable	 = False\n" 
	    if settings['nowrapfile']\
                    or settings['tar_file_name']\
                    or settings['transfer_executable']:
	        rsp="transfer_executable	 = True\n"
            tInputFiles=settings['transfer_input_files']
            eScript=settings['exe_script']
            if settings['transfer_executable']:
                if eScript not in tInputFiles and os.path.exists(eScript):
                    if len(tInputFiles)>0:
                        tInputFiles=tInputFiles+",%s" % eScript
                    else:
                        tInputFiles=eScript
            if len(tInputFiles)>0:
                rsp=rsp+"transfer_input_files = %s\n" % tInputFiles

            return rsp

        def addToLineSetting(self,thingy):
            
            settings=self.settings
            if settings['needs_appending']:
                if 'lines' not in settings:
                    settings['lines']=[]
                settings['lines'].append(thingy)

        def handleResourceProvides(self,f,job_iter=0):
            settings=self.settings 
            submit_host=settings['submit_host'] 
            fp=self.fileParser 
	    if 'lines' in settings and len(settings['lines']) >0:			
		#print("lines setting=%s"%settings['lines'])
		for thingy in settings['lines']:
                    f.write("%s\n" % thingy)
	    if 'os' in settings:
		f.write("+DesiredOS =\"%s\"\n"%settings['os'])
	    if settings['site']:
		if settings['site']!='LOCAL':
                    f.write("+DESIRED_Sites = \"%s\"\n" % settings['site'])
            f.write("+GeneratedBy =\"%s\"\n"%settings['generated_by'])
            for res in settings['resource_list']: 
                parts=res.split('=')
                if len(parts)>1: 
                    opt=parts[0]
                    val=parts[1]
                    has_opt=opt
                    if opt.lower().find('has_')<0:
                        has_opt="has_%s"%opt
                    if not fp.has_option(submit_host,has_opt): 
                        err="illegal --resource-provides option: %s is not supported on %s according to config file %s.\nSupported options will be under the [%s] section and start with 'has_',\nthe condor admin must add a 'has_%s' section and properly configure condor to use it for this option value to be valid"%(opt,submit_host,self.findConfigFile(),submit_host,opt)
                        raise InitializationError(err)
                    else: 
                        allowed_vals=fp.get(submit_host,has_opt)
                        vals_ok=False
                        val_list=val.split(',')
                        for check_val in val_list:
                            if allowed_vals.upper().find(check_val.upper())>=0:
                                vals_ok=True
                        if not vals_ok: 
                            err="illegal --resource-provides value: %s for option: %s is not supported on %s according to your config file %s.  Legal values are:%s"%(val,opt,submit_host,self.findConfigFile(),allowed_vals)
                            raise InitializationError(err)
                        else:
                            f.write("""+DESIRED_%s = "%s"\n"""%(opt,val))
			
        def condorRequirements(self):
            #print "condorRequirements needs_appending=%s"%self.settings['needs_appending']
            settings=self.settings
            if settings['needs_appending']:
                self.makeCondorRequirements()
            return settings['requirements']



        def makeCondorRequirements(self):     
            settings = self.settings
            if not settings['needs_appending']:
                return settings['requirements']
            settings['needs_appending']=False
            requirements=settings['requirements']
	    if 'overwriterequirements' in settings:
		settings['requirements']=settings['overwriterequirements']
                return settings['requirements']
            if settings['grid']:
                settings['requirements']=settings['requirements'] + '&& (target.IS_Glidein==true) '
            if settings['site']:
	        desired_site_req=' && (stringListIMember(target.GLIDEIN_Site,my.DESIRED_Sites)) '	
                settings['requirements']=settings['requirements'] +  desired_site_req
            if 'desired_os' in settings and len(settings['desired_os'])>0:
                settings['requirements']=settings['requirements'] + settings['desired_os'] 
            for x in settings['resource_list']:
                (opt,val)=x.split('=')
                settings['requirements']=settings['requirements']+\
                     """ && (stringListsIntersect(toUpper(target.HAS_%s), toUpper(my.DESIRED_%s)))"""%(opt,opt)
            if 'append_requirements' in settings:
		for req in settings['append_requirements']:
		    settings['requirements'] = settings['requirements'] + " && %s " % req
            return settings['requirements']

	def makeOtherCommandFile(self, job_iter=0 ):
		#print "self.makeOtherCommandFile"
		settings = self.settings
		settings['cmd_file_list'].append(settings['cmdfile'])
		f = open(settings['cmdfile'], 'w')
		f.write("universe	  = vanilla\n")

		if settings['tar_file_name']!="":
			settings['useparrot']=False
			f.write("executable	= %s\n"%settings['tar_file_name'])
			
		elif settings['nowrapfile']:
			settings['useparrot']=False
			f.write("executable	= %s\n"%settings['exe_script'])
		else:
			settings['useparrot']=False
			f.write("executable	= %s\n"%settings['wrapfile'])
		args = ""
		if settings['tar_file_name']!="":
			args = "./"+os.path.basename(settings['exe_script'])+ " "
		for arg in settings['script_args']:
			args = args+" "+arg+" "
		if job_iter <=1:
			for arg in settings['added_environment']:
				settings['environment'] = settings['environment']+";"+\
										  arg+'='+os.environ.get(arg)
			settings['environment']=settings['environment']+\
									 ";GRID_USER=%s"%settings['user']
			settings['environment']=settings['environment']+\
									 ";EXPERIMENT=%s"%settings['group']
		
			settings['environment']=settings['environment']+\
									 ";IFDH_BASE_URI=%s"%\
									 (settings['ifdh_base_uri'])
			#print "testing project name(=%s)"%settings['project_name']
			if settings['project_name'] != "":
				settings['environment']=settings['environment']+\
										 ';SAM_PROJECT_NAME=%s'%\
										 settings['project_name']
		#print "after environment=%s"%settings['environment']
		f.write("arguments	 = %s\n"%args)
		f.write("output		= %s\n"%settings['outfile'])
		f.write("error		 = %s\n"%settings['errfile'])
		f.write("log		   = %s\n"%settings['logfile'])
		f.write("environment   = %s\n"%settings['environment'])
		f.write("rank		  = Mips / 2 + Memory\n")
		f.write("job_lease_duration = 21600\n")

		if settings['notify']==0:
			f.write("notification  = Never\n")
		elif settings['notify']==1:
			f.write("notification  = Error\n")
		else:
			f.write("notification  = Always\n")
		f.write("when_to_transfer_output = ON_EXIT\n")
		f.write("transfer_output		 = True\n")
		f.write("transfer_error		  = True\n")
                tval=self.shouldTransferInput()
                f.write(tval)

		if settings['grid']:
			self.addToLineSetting("x509userproxy = %s" % settings['x509_user_proxy'])
			self.addToLineSetting("+RunOnGrid			  = True")

                        if not settings['site']: 
                            if settings['default_grid_site']:
                                settings['site']=settings['default_grid_site']
                        


					 


		if settings['istestjob'] == True:
			self.addToLineSetting("+AccountingGroup = \"group_testjobs\"")

		if settings['group'] != "" and settings['istestjob'] == False:			
			self.addToLineSetting("+AccountingGroup = \"group_%s.%s\""%(settings['accountinggroup'],settings['user']))

                self.handleResourceProvides(f,job_iter)
		f.write("requirements  = %s\n"%self.condorRequirements())

		f.write("\n")
		f.write("\n")
		f.write("queue %s"%settings['queuecount'])

		f.close

	
		
	def makeGPSN01CommandFile(self, job_iter=0 ):
		#print "self.makeGPSN01CommandFile(%s)"%job_iter
		settings = self.settings
                if job_iter <=1:
		    if settings['grid']:
			settings['requirements'] = settings['requirements'] + settings['desired_os'] + ' && (target.IS_Glidein==true) '
		    else:
			settings['requirements'] = settings['requirements'] + ' && (target.IS_Glidein=?=UNDEFINED) '
		settings['cmd_file_list'].append(settings['cmdfile'])
		f = open(settings['cmdfile'], 'w')
		f.write("universe	  = vanilla\n")
		if settings['grid'] and settings['forcenoparrot'] \
			   and settings['needafs'] and settings['forceparrot']:
			settings['useparrot']=True
			f.write("executable	= %s\n"%settings['parrotfile'])
		elif settings['tar_file_name']!="":
			settings['useparrot']=False
			f.write("executable	= %s\n"%settings['tar_file_name'])
			
		elif settings['nowrapfile']:
			settings['useparrot']=False
			f.write("executable	= %s\n"%settings['exe_script'])
		else:
			settings['useparrot']=False
			f.write("executable	= %s\n"%settings['wrapfile'])
		args = ""
		if settings['tar_file_name']!="":
			args = "./"+os.path.basename(settings['exe_script'])+ " "
		for arg in settings['script_args']:
			args = args+" "+arg+" "
		if job_iter <=1:
			for arg in settings['added_environment']:
				settings['environment'] = settings['environment']+";"+\
										  arg+'='+os.environ.get(arg)
			settings['environment']=settings['environment']+\
									 ";GRID_USER=%s"%settings['user']
			settings['environment']=settings['environment']+\
									 ";EXPERIMENT=%s"%settings['group']
		
			settings['environment']=settings['environment']+\
									 ";IFDH_BASE_URI=%s"%\
									 (settings['ifdh_base_uri'])
			#print "testing project name(=%s)"%settings['project_name']
			if settings['project_name'] != "":
				settings['environment']=settings['environment']+\
										 ';SAM_PROJECT_NAME=%s'%\
										 settings['project_name']
		#print "after environment=%s"%settings['environment']
		f.write("arguments	 = %s\n"%args)
		f.write("output		= %s\n"%settings['outfile'])
		f.write("error		 = %s\n"%settings['errfile'])
		f.write("log		   = %s\n"%settings['logfile'])
		f.write("environment   = %s\n"%settings['environment'])
		f.write("rank		  = Mips / 2 + Memory\n")
		f.write("job_lease_duration = 21600\n")

		if settings['notify']==0:
			f.write("notification  = Never\n")
		elif settings['notify']==1:
			f.write("notification  = Error\n")
		else:
			f.write("notification  = Always\n")
		f.write("when_to_transfer_output = ON_EXIT\n")
		f.write("transfer_output		 = True\n")
		f.write("transfer_error		  = True\n")
                tval=self.shouldTransferInput()
                f.write(tval)

                if job_iter <=1:
                    for x in settings['resource_list']:
                        (opt,val)=x.split('=')
                        settings['requirements']=settings['requirements']+\
                         """&&(stringListsIntersect(toUpper(target.HAS_%s), toUpper(my.DESIRED_%s)))"""%(opt,opt)
		if settings['grid']:

                        if job_iter<=1:
			    self.addToLineSetting("x509userproxy = %s" % settings['x509_user_proxy'])
			    self.addToLineSetting("+RunOnGrid			  = True")
			    settings['requirements']=settings['requirements'] + \
				          '  && (stringListIMember(target.GLIDEIN_Site,my.DESIRED_Sites))'


			if not settings['site']:
			    if job_iter <= 1:
			        settings['requirements']=settings['requirements'] + \
				  '  && (target.AGroup==my.AGroup)'
                        
			    if settings['opportunistic']==0:
				settings['site']="FNAL_%s" % settings['group']
			    else:
				settings['site']="FNAL_%s,FNAL_%s_opportunistic" % (settings['group'],settings['group'])

			if job_iter <=1 and  'append_requirements' in settings:
				for req in settings['append_requirements']:
					settings['requirements'] = settings['requirements'] + " && %s " % req
	

		else:
			if job_iter <=1:
				settings['requirements']=settings['requirements'] + ' && (target.GLIDEIN_Site=?=UNDEFINED)'
		if settings['istestjob'] == True:
			f.write("+AccountingGroup = \"group_testjobs\"\n")

		if settings['group'] != "" and settings['istestjob'] == False:			
			f.write("+AccountingGroup = \"group_%s.%s\"\n"%(settings['accountinggroup'],settings['user']))

		self.addToLineSetting("+Agroup = \"group_%s\""%settings['group'])

                self.handleResourceProvides(f,job_iter)

                if 'overwriterequirements' in settings:

                        f.write("requirements  = %s\n"%settings['overwriterequirements'])
                else:
                        f.write("requirements  = %s\n"%settings['requirements'])





		#f.write("%s"%settings['lines'])
		f.write("\n")
		f.write("\n")
		f.write("queue %s"%settings['queuecount'])

		f.close
