# -*- coding: utf-8 -*-
#!/usr/bin/python3
#Copyright © 2018, Oracle and/or its affiliates. All rights reserved.
#The Universal Permissive License (UPL), Version 1.0
import os
import sys
import requests
import json
from test import test_getargs2
from pathlib import Path
from APIPCSmodule import apipserver
import argparse
import datetime
import logging
                  
def main(*mainargs):
    logging.basicConfig(filename='logs/apip-session-{:%Y%m%d-%H%M%S}.log'.format(datetime.datetime.now()), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)    
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info(sys.argv)
    if len(mainargs) == 0 : #if len(sys.argv)>1 and len(sys.argv)<5:
        parser = argparse.ArgumentParser(description='This program exports all Gateways\' metadata from APICS and persist them on the file system') 
        parser.add_argument('-cf','--configfile', dest='configfile', help='config file specifying server, auth, proxy and other details in json format;', default='apipcs_config.json', required=False)
        parser.add_argument('--destdir', dest='destdir', default='./', help='directory path on local file system where all the exported gateway details will be saved to; defaults to current directory', required=False )
        cmdargs = parser.parse_args()
        logging.info(type(cmdargs))
        logging.info(cmdargs)
        #Feature specific args parse
        serverargs = (cmdargs.configfile,)
        logging.info(serverargs) 
        destdir = cmdargs.destdir   #default CWD
        logging.info(destdir)
    else:
        #Feature specific args parse
        numargs = len(mainargs)
        logging.info(numargs)
        if numargs in  (3,4): pass
        else: raise TypeError("Number of arguments expected is 3 or 4 ; got {} !".format(numargs)) 
        serverargs = mainargs[0:3]
        destdir = mainargs[3:4][0] if (numargs==4) else './'   #default CWD
        logging.info(destdir)
            
    apisvr = apipserver(serverargs)
    savethegatewaysto = apisvr.getall('gateway') #get the real method
    savethegatewaysto(destdir) # and execute it
    return 'success'
                  
if __name__ == "__main__": main()




