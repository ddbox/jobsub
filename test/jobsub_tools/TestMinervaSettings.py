#!/usr/bin/env python
# $Id$

import unittest
#from JobSettings import JobSettings
from MinervaSettings import MinervaSettings
from TestJobSettings import JobTest

 
class MinervaTest(JobTest):


    def setUp(self):
        super(MinervaTest,self).ioSetUp()
        self.ns = MinervaSettings()
        super(MinervaTest,self).stdioON()
        super(MinervaTest,self).setUp()


    def testMinervaConstructor(self):
        """exercise MinervaSettings constructor"""
        ns = self.ns
    
        self.assertEqual(ns.settings['defaultrelarea'],
                         '/grid/fermiapp/minerva/software_releases')
        self.assertEqual(ns.settings['msopt'],'')
        self.assertEqual(ns.settings['enstorefiles'],'')


    def testMinervaGoodInput(self):
        """exercise Minervsettings against good input """
        ns = self.ns
        ns.runCmdParser(['-ilalalala','a_script'])
        self.assertEqual(ns.settings['reldir'],'lalalala')
        ns.runCmdParser(['-tlalalala','a_script'])
        self.assertEqual(ns.settings['testreldir'],'lalalala')
        ns.runCmdParser(['-rlalalala','a_script'])
        self.assertEqual(ns.settings['rel'],'lalalala')
        
        ns.runCmdParser(['-yenstore1','a_script'])
        self.assertEqual(ns.settings['enstorefiles'],['enstore1'])
        ns.runCmdParser(['-yenstore1', '-yenstore2','a_script'])
        self.assertEqual(ns.settings['enstorefiles'],['enstore1', 'enstore2'])
        
        ns.runCmdParser(['-O','a_script'])
        self.assertEqual(ns.settings['msopt'],'-O')
        

        
    def testMinervaBadInput(self):

        """excercise MinervaSettings against bad input -- should complain"""
        ns = self.ns
        self.stdioOFF()
        self.assertRaises(SystemExit,ns.runCmdParser,
                          ['--deliberately_bogus_option=lalalala','some_stupid_script'],2)
        self.stdioON()
                         


if __name__ == "__main__":
    suite = unittest.makeSuite(MinervaTest)
    unittest.TextTestRunner(verbosity=10).run(suite)
