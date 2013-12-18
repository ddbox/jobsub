#!/usr/bin/env python
# $Id$

import unittest
import sys
import os
import commands
#from test import test_support

from JobSettings import JobSettings




class JobTest(unittest.TestCase):

##     def __init__(self):
        
##         #super(JobTest,self).__init__()
##         self.ns=None
        
    def setUp(self):
        """set up JobSettings"""
        self.ns=JobSettings()
##         if self.ns == None:
##             print "constructing"
##             self.ns = JobSettings()
        
    def testConstructor(self):
        """test that JobSettings constructor initializes correctly"""
        #self.setUp()
        ns = self.ns
    
        self.assertEqual(ns.settings['output_tag_array'],{})

        self.assertNotEqual(ns.settings['condor_tmp'],None)
        self.assertNotEqual(ns.settings['condor_exec'],None)
        self.assertEqual(ns.settings['condor_config'],None)
        self.assertNotEqual(ns.settings['local_condor'],None)
        self.assertNotEqual(ns.settings['group_condor'],None)
        self.assertNotEqual(ns.settings['x509userproxy'],None)
        
        self.assertEqual(ns.settings['input_dir_array'],[])
        self.assertEqual(ns.settings['istestjob'],False)
        self.assertEqual(ns.settings['needafs'],False)
        self.assertEqual(ns.settings['notify'],1)
        self.assertEqual(ns.settings['submit'],True)
        self.assertEqual(ns.settings['grid'],False)
        self.assertEqual(ns.settings['usepwd'],True)
        self.assertEqual(ns.settings['forceparrot'],False)
        self.assertEqual(ns.settings['forcenoparrot'],True)
        self.assertEqual(ns.settings['usedagman'],False)
        self.assertNotEqual(ns.settings['requirements'],None)
        self.assertNotEqual(ns.settings['environment'],None)
        self.assertEqual(ns.settings['lines'],"")
        self.assertNotEqual(ns.settings['group'],None)
        self.assertNotEqual(ns.settings['user'],None)
        self.assertEqual(ns.settings['output_tag_counter'],0)
        self.assertEqual(ns.settings['input_tag_counter'],0)
        self.assertEqual(ns.settings['queuecount'],1)
        self.assertEqual(ns.settings['joblogfile'],"")
        self.assertEqual(ns.settings['override_x509'],False)
        self.assertEqual(ns.settings['use_gftp'],0)
        self.assertEqual(ns.settings['filebase'],'')
        self.assertEqual(ns.settings['wrapfile'],'')
        self.assertEqual(ns.settings['parrotfile'],'')
        self.assertEqual(ns.settings['cmdfile'],'')
        self.assertEqual(ns.settings['processtag'],'')
        self.assertEqual(ns.settings['logfile'],'')
        self.assertEqual(ns.settings['opportunistic'],0)
        self.assertEqual(ns.settings['errfile'],'')
        self.assertEqual(ns.settings['outfile'],'')
        self.assertEqual(ns.settings['msopt'],"")
        self.assertEqual(ns.settings['exe_script'],'')
        self.assertEqual(ns.settings['script_args'],[])
        self.assertEqual(ns.settings['verbose'], False)
        self.assertEqual(ns.settings['wrapper_cmd_array'],[])
        self.assertEqual(ns.settings['msopt'],"")
        self.assertNotEqual(ns.settings['generated_by'],"")
        self.assertEqual(ns.checkSanity(),True)
    
        
    def testGoodInput(self):

        
        """test  JobSettings correct  input flags"""
        #self.setUp()

        ns = self.ns
        #ns = JobSettings()
        
        #ns.runParser(["-ooutput_dir1","--output=output_dir2","my_script"],None)
        #self.assertEqual(ns.settings['output'],['output_dir1','output_dir2'])
        ns.runParser(["-a","my_script"], None)
        self.assertEqual(ns.settings['needafs'],True)
        ns.runParser(['-p','dummy_script'])
        self.assertEqual(ns.settings['forceparrot'],True)
        ns.runParser(['-Glalalala','some_script'])
        self.assertEqual(ns.settings['accountinggroup'],'lalalala')
        ns.runParser(['--group=thats_a_silly_group_name','some_script'])
        self.assertEqual(ns.settings['accountinggroup'],'thats_a_silly_group_name')
        ns.runParser(['-N 10','shhhhh.sh'])
        self.assertEqual(ns.settings['queuecount'],10)
        ns.runParser(['-q','shhhhh.sh'])
        self.assertEqual(ns.settings['notify'],1)
        ns.runParser(['-Q','SSSSHHHHH.sh'])
        self.assertEqual(ns.settings['notify'],0)
        ns.runParser(['-T','huh'])
        self.assertEqual(ns.settings['istestjob'],True)
        logfile = ns.settings['condor_tmp']+'/testlogfile'
        ns.runParser(["-L%s"%logfile, 'some_script'])
        self.assertEqual(ns.settings['joblogfile'],logfile)
        ns.runParser(['-g','some_script'])
        self.assertEqual(ns.settings['grid'],True)
        #del ns
        
    def testBadInput(self):
        """give JobSettings some bad input -- should complain"""
        #self.setUp()
        ns = self.ns
        #ns = JobSettings()
        sys.stdout =  open('/dev/null', 'w')
        self.assertRaises(SystemExit,ns.runParser,
                          ['--deliberately_bogus_option','lalalala'],2)
    
        sys.stdout.close()
        #del ns
        
    def testMakingDagFiles(self):
        """test whether DAG files for SAM made correctly"""
        #self.assertTrue(True)
        """test that JobSettings creates cmdfile, wrapfile, parrotfile"""
        ns = self.ns
        #ns = JobSettings()
        
        #print "%s"%ns.settings
        sys.stdout = open('/dev/null', 'w')
        ns.settings['dataset_definition']="mwm_test_1"
        ns.settings['queuecount']=3
        ns.settings['accountinggroup']="group_w"
        ns.settings['exe_script']=ns.__class__.__name__+"_samtest.sh"
        ns.settings['grid']=True
        ns.makeCondorFiles()
        sys.stdout.close()

        self.assertEqual(os.path.isfile(ns.settings['dagfile']),True,ns.settings['dagfile'])
        self.assertEqual(os.path.isfile(ns.settings['sambeginfile']),True,ns.settings['sambeginfile'])
        self.assertEqual(os.path.isfile(ns.settings['samendfile']),True,ns.settings['samendfile'])
        
        (retVal,output)=commands.getstatusoutput("grep RunOnGrid  %s"%ns.settings['cmdfile'])
        self.assertEqual(retVal,0)


        (retVal,output)=commands.getstatusoutput("grep RUN_ON_HEADNODE %s"%ns.settings['sambeginfile'])
        self.assertEqual(retVal,0)
        
        (retVal,output)=commands.getstatusoutput("grep RUN_ON_HEADNODE %s"%ns.settings['samendfile'])
        self.assertEqual(retVal,0)

        (retVal,output)=commands.getstatusoutput("wc -l %s"%ns.settings['dagfile'])
        response="8 %s"%ns.settings['dagfile']
        self.assertEqual(retVal,0)
        self.assertEqual(output,response)
        #del ns
        
    def testMakingCommandFiles(self):
        """test that JobSettings creates cmdfile, wrapfile, parrotfile"""
        ns = self.ns
        #ns = JobSettings()
        
        #print "%s"%ns.settings
        sys.stdout = open('/dev/null', 'w')
        ns.settings['queuecount']=11
        ns.settings['accountinggroup']="group_w"
        ns.settings['exe_script']=ns.__class__.__name__+"_MakeCommandFiles.sh"
        ns.makeCondorFiles()
        ns.makeParrotFile()
        sys.stdout.close()

        self.assertEqual(os.path.isfile(ns.settings['cmdfile']),True,ns.settings['cmdfile'])
        self.assertEqual(os.path.isfile(ns.settings['wrapfile']),True,ns.settings['wrapfile'])
        self.assertEqual(os.path.isfile(ns.settings['parrotfile']),True,ns.settings['parrotfile'])
        (retVal,output)=commands.getstatusoutput("grep group_group_w %s"%ns.settings['cmdfile'])
        self.assertEqual(retVal,0)
        
        self.assertEqual(output.find('+AccountingGroup = "group_group_w'),0)
        (retVal,output)=commands.getstatusoutput("grep 'queue 11' %s"%ns.settings['cmdfile'])
        self.assertEqual(retVal,0)
        
        (retVal,output)=commands.getstatusoutput("grep RunOnGrid  %s"%ns.settings['cmdfile'])
        self.assertNotEqual(retVal,0)
        #del ns

    def testCPNCommands(self):
        """test CPN i/o from -d and -f flags"""
        ##jobsub -f input_file_1 -f input_file_2 -d FOO this_is_the_foo_dir -d BAR this_is_the_bar_dir (some_subclass)_CPNtest.sh
        ns = self.ns
        sys.stdout = open('/dev/null', 'w')
        ns.settings['input_dir_array']=['input_file_1', 'input_file_2']
        ns.settings['output_dir_array']=[('FOO', 'this_is_the_foo_dir'),('BAR', 'this_is_the_bar_dir')]
        ns.settings['accountinggroup']="group_w"
        ns.settings['exe_script']=ns.__class__.__name__+"_CPNtest.sh"
        ns.makeCondorFiles()
        sys.stdout.close()
        (retVal,output)=commands.getstatusoutput("grep 'ifdh cp --force=cpn -D    input_file_1 ${CONDOR_DIR_INPUT}/ \\\; input_file_2 ${CONDOR_DIR_INPUT}/'  %s"%ns.settings['wrapfile'])
        self.assertEqual(retVal,0,'cpn cant find input_file_1 in '+ns.settings['wrapfile'])
        (retVal,output)=commands.getstatusoutput("grep 'ifdh cp --force=cpn       ${CONDOR_DIR_FOO}/\* this_is_the_foo_dir  \\\;   ${CONDOR_DIR_BAR}/\* this_is_the_bar_dir' %s"%ns.settings['wrapfile'])
        self.assertEqual(retVal,0,'cpn cant transfer out CONDOR_DIR_FOO in file '+ns.settings['wrapfile'])
        
        
    def testGFTPCommands(self):
        """test gridFTP i/o from -d and -f flags"""
        ##jobsub --use_gftp  -f input_file_1 -f input_file_2 -d FOO this_is_the_foo_dir -d BAR this_is_the_bar_dir (some_subclass)_GFTPtest.sh
        ns = self.ns
        sys.stdout = open('/dev/null', 'w')
        ns.settings['input_dir_array']=['input_file_1', 'input_file_2']
        ns.settings['output_dir_array']=[('FOO', 'this_is_the_foo_dir'),('BAR', 'this_is_the_bar_dir')]
        ns.settings['accountinggroup']="group_w"
        ns.settings['exe_script']=ns.__class__.__name__+"_GFTPtest.sh"
        ns.settings['use_gftp']=True
        ns.makeCondorFiles()
        sys.stdout.close()
        (retVal,output)=commands.getstatusoutput("grep 'ifdh cp --force=cpn -D    input_file_1 ${CONDOR_DIR_INPUT}/ \\\; input_file_2 ${CONDOR_DIR_INPUT}/' %s"%\
                                                 (ns.settings['wrapfile']))

        self.assertEqual(retVal,0,'gftp cant find input_file_1 in '+ns.settings['wrapfile'])
        
        (retVal,output)=commands.getstatusoutput("grep 'ifdh cp --force=expgridftp -r -D     ${CONDOR_DIR_FOO}/ this_is_the_foo_dir  \\\;  ${CONDOR_DIR_BAR}/ this_is_the_bar_dir' %s"%\
                                                 (ns.settings['wrapfile']))
        self.assertEqual(retVal,0,'gftp cant transfer out CONDOR_DIR_BAR in file '+ns.settings['wrapfile'])
        
       
        

if __name__ == "__main__":
    
    #unittest.main()
    suite = unittest.makeSuite(JobTest)
    unittest.TextTestRunner(verbosity=10).run(suite)

