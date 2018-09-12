# -*- coding: utf-8 -*-
#!/usr/bin/python3
#Copyright © 2018, Oracle and/or its affiliates. All rights reserved.
#The Universal Permissive License (UPL), Version 1.0
import os
import sys
import requests
import json
import cmd
from APIPCSmodule import apipserver
from pathlib import Path
import argparse
import datetime
import logging
                  
import listapis                  
import listapps
import listplans
import listgateways
#import exportallapis
import importapis_fromdir
import importapplications_fromdir
import importplans_fromdir
                  
class APIREPL(cmd.Cmd):
    prompt = 'APIPCS: > '
            
    def __init__(self, argv):
        super().__init__()
        logging.basicConfig(filename='logs/repl-apip-session-{:%Y%m%d-%H%M%S}.log'.format(datetime.datetime.now()), filemode='w', format='%(asctime)s %(message)s', level=logging.INFO)
        #logging.getLogger('urllib3').setLevel(logging.CRITICAL)        
        logging.getLogger("requests.packages.urllib3").setLevel(logging.CRITICAL)
        #repl logging only goes to file, use print() for interactive messages    
        #logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        #logging.info(sys.argv)
        parser = argparse.ArgumentParser(description='REPL for API Platform Cloud Service')
        parser.add_argument('-cf','--configfile', dest='configfile', help='config file specifying server, auth, proxy and other details in json format;', default='apipcs_config.json', required=False)
        cmdargs = parser.parse_args()
        #logging.info(cmdargs)
        self.serverargs = (cmdargs.configfile,)
        logging.info('done initing repl')
    
    def cmdloop(self, intro=None):
        cmd.Cmd.cmdloop(self, intro=intro)
        
    def emptyline(self):
        print('Try one of the commands')
        return False
                      
    def do_listapis(self, arg):
        if self.serverargs: 
            listapis.main(self.serverargs)
        else:
            logging.info('Not Connected, check config json file and try again !')
        return
                          
    def do_listapps(self, arg):
        if self.serverargs: 
            listapps.main(self.serverargs)
        else:
            logging.info('Not Connected, check config json file and try again !')
        return

    def do_listgateways(self, arg):
        if self.serverargs: 
            listgateways.main(self.serverargs)
        else:
            logging.info('Not Connected, check config json file and try again !')
        return

    def do_listplans(self, arg):
        if self.serverargs: 
            listplans.main(self.serverargs)
        else:
            logging.info('Not Connected, check config json file and try again !')
        return

    def do_exportallapis(self, arg):
        if self.serverargs: 
            self.exportartifacts(arg, 'api')
        else:
            logging.info('Not Connected, check config json file and try again !')
        return
    
    def do_exportallapps(self, arg):
        if self.serverargs: 
            self.exportartifacts(arg, 'application')
        else:
            logging.info('Not Connected, check config json file and try again !')
        return

    def do_exportallplans(self, arg):
        if self.serverargs: 
            self.exportartifacts(arg, 'plan')
        else:
            logging.info('Not Connected, check config json file and try again !')
        return

    def exportartifacts(self, arg, artifact):
        parser = NoExitArgumentParser(description='exportallapps repl command', prog='exportall{}s'.format(artifact), usage='exportall{}s [--destdir <path>]'.format(artifact)) 
        parser.add_argument('--destdir', dest='destdir', default='./', help='directory path on local file system where all the exported artifacts will be saved to; defaults to current directory', required=False )
        cmdargs, errors = parser.parse_args(arg.split())
        print(cmdargs)
        print(errors)
        if errors == 1:
            #print('Error in REPL command, check usage and try again')
            return
        destdir = cmdargs.destdir   #default CWD
        logging.info('-->destdir = '+destdir)    

        apisvr = apipserver(self.serverargs)
        exportf = apisvr.getall(artifact)
        exportf(destdir)
        return 'success'

    def do_importapis_fromdir(self, arg):
        if self.serverargs: 
            parser = NoExitArgumentParser(description='importapis_fromdir repl command', prog='importapis_fromdir', usage='importapis_fromdir [--dirpath <path>]') 
            parser.add_argument('--dirpath', dest='dirpath', help='directory path; All json files from this directory will be imported', required=True )
            cmdargs, _error = parser.parse_args(arg.split())
            #cmdargs = parser.parse_args(arg.split())
            if _error == '1': return
            print('noErrors')
            dirpath = cmdargs.dirpath   #default CWD
            logging.info('-->dirpath = '+dirpath)    
    
            importapis_fromdir.main(self.serverargs, dirpath)
        else:
            logging.info('Not Connected, check config json file and try again !')
        return
    
    def do_importplans_fromdir(self, arg):
        if self.serverargs: 
            parser = NoExitArgumentParser(description='importplans_fromdir repl command', prog='importplans_fromdir', usage='importplans_fromdir [--dirpath <path>]') 
            parser.add_argument('--dirpath', dest='dirpath', help='directory path; All json files from this directory will be imported', required=True )
            cmdargs, _error = parser.parse_args(arg.split())
            #cmdargs = parser.parse_args(arg.split())
            if _error == '1': return
            print('noErrors')
            dirpath = cmdargs.dirpath   #default CWD
            logging.info('-->dirpath = '+dirpath)    
    
            importplans_fromdir.main(self.serverargs, dirpath)
        else:
            logging.info('Not Connected, check config json file and try again !')
        return

    def do_importapps_fromdir(self, arg):
        if self.serverargs: 
            parser = NoExitArgumentParser(description='importapps_fromdir repl command', prog='importapps_fromdir', usage='importapps_fromdir [--dirpath <path>]') 
            parser.add_argument('--dirpath', dest='dirpath', help='directory path; All json files from this directory will be imported', required=True )
            cmdargs, _error = parser.parse_args(arg.split())
            #cmdargs = parser.parse_args(arg.split())
            if _error == '1': return
            print('noErrors')
            dirpath = cmdargs.dirpath   #default CWD
            logging.info('-->dirpath = '+dirpath)    
    
            importapplications_fromdir.main(self.serverargs, dirpath)
        else:
            logging.info('Not Connected, check config json file and try again !')
        return
    
    def do_exit(self, arg):
        print('Have a nice day!')
        sys.exit()


class NoExitArgumentParser(argparse.ArgumentParser):
    onError = '0'
    def error(self, message):
        self.onError = '1'
        print('Error in REPL command, check usage and try again')
        self.print_usage(sys.stderr)
        if message: pass#logging.info(message, sys.stderr)            
        return

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            msg ='unrecognized arguments: '
            self.error('unrecognized arguments !')
        return args, self.onError
    
             
if __name__ == "__main__": APIREPL(sys.argv).cmdloop()
    


