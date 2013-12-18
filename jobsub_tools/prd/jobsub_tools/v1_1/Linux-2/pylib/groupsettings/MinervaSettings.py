#!/usr/bin/env python
# $Id$
from JobSettings import JobSettings
from optparse import OptionGroup
import os
from datetime import datetime

class MinervaSettings(JobSettings):
    def __init__(self):
        super(MinervaSettings,self).__init__()
        #print "MinervaSettings init: parser=%s generic=%s file=%s"%(self.parser,self.generic_group,self.file_group)

        self.settings['minerva_condor'] = os.environ.get("MINERVA_CONDOR")

        self.settings['defaultrelarea']="/grid/fermiapp/minerva/software_releases"

        self.settings['msopt']=''
        self.settings['rel']=''
        self.settings['reldir']=''
        self.settings['testreldir']=''
        self.settings['prefix']=''
        self.settings['cmtconfig']= os.environ.get("CMTCONFIG")
        if self.settings['cmtconfig']== None:
            self.settings['cmtconfig']=''

        self.settings['enstorefiles']=""

    def initParser(self):
        #print "MinervaSettings initParser"
        parser = self.parser
        self.minerva_group = OptionGroup(self.parser, "Minerva Specific Options")
        self.parser.add_option_group(self.minerva_group)

        #print "MinervaSettings initParser parser=%s"%self.parser
        #print "MinervaSettings initParser file_group=%s"%self.file_group
        #return
    
        
        self.minerva_group.add_option("-i", dest="reldir",
                                 action="store",type="string",
                                 help="release_directory for Minerva Software ")

        self.minerva_group.add_option("-t", dest="testreldir",
                                 action="store",type="string",
                                 help="release_directory for test Minerva Software ")
              
        self.minerva_group.add_option("-r", dest="rel",
                                 action="store",type="string",
                                 help="release_version for  Minerva Software ")
                
        self.minerva_group.add_option("-y", dest="enstorefiles",
                                 action="append",
                                 help="enstore files ")
            
        self.minerva_group.add_option("-O", dest="msopt",
                                 action="store_const",const="-O",
                                 help="optimize flag")
        self.minerva_group.add_option("--prefix", dest="prefix",
                                 action="store",
                                 help="The jobs and files created by this scrip will be PREFIX_<timestamp>.  Default is executable name.")

        self.minerva_group.add_option("--cmtconfig", dest="cmtconfig",
                                 action="store",
                                 help="Set up minervasoft release built with cmt configuration. default is $CMTCONFIG")


        return super(MinervaSettings,self).initParser()


    def makeWrapFile(self):
        super(MinervaSettings,self).makeWrapFile()
        
        f = open(self.settings['wrapfile'], 'a')
        
        settings=self.settings
        rel_version=0
        r=settings['rel']
        if r.find('v')>=0:
            #print "searching r=",r
            rel_version=int(r[r.find('v')+1:r.find('r')])
            
            
        # this part sets up the Minerva software environment for submitting framework exectuables directly
        
        if self.settings['reldir'] != "":
            f.write("\n")
            if rel_version < 10:
                f.write("source %s/setup.sh %s %s %s\n"%\
                        (settings['reldir'],settings['rel'],
                         settings['reldir'],settings['cmtconfig']))
            else:
                f.write("source %s/setup.sh -c %s\n"%\
                        (settings['reldir'],settings['cmtconfig']))
                
            f.write("\n")
            if self.settings['testreldir'] != "":

                f.write("cd %s/cmt/\n" % settings['testreldir'])    # users working package
                f.write("cmt config\n")
                f.write("source setup.sh\n")

            f.write("\n")
        f.close()
        
    def print_usage(self):
        usage = """      Minossoft and enstore:
          -O             Set up optimized minossoft (requires -r or -t).

          -r <rel>       Set up minervasoft release <rel> at the beginning
                         of the job.

          -i <dir>       Directory where base release <rel> is installed

          -t <dir>       Set up a local test release in <dir> at the
                         beginning of the job.  -r is needed.
                         -t $PACKAGEROOT

          -y <file>      Get <file> (usually of the form /pnfs/...) from
                         Enstore, point $FROM_ENSTORE to it, and clean up
                         when finished.  You can use multiple -y options
                         if you want $FROM_ENSTORE to point to multiple
                         files.  You can also specify non-Enstore files if
                         you want.  (Perhaps you have a mixture of input.)
                         Requires either -r or -t to get access to dccp.


        """ 
        super(MinervaSettings,self).print_usage()
        print usage

    def makeCondorFiles(self):
        settings=self.settings
        a = settings['exe_script'].split("/")
        prefix=a[-1]
        if settings['prefix'] != "":
            prefix=settings['prefix']
            
        ow = datetime.now()
	pid=os.getpid()
    
        filebase = "%s_%s%02d%02d_%02d%02d%02d_%s"%(prefix,ow.year,
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

                
            self.makeDAGFile()
            self.makeSAMBeginFiles()
            self.makeSAMEndFiles()


    def checkSanity(self):
        return super(MinervaSettings,self).checkSanity()
        
