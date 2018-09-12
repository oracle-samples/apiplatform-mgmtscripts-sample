# -*- coding: utf-8 -*-
#!/usr/bin/python3
#Copyright © 2018, Oracle and/or its affiliates. All rights reserved.
#The Universal Permissive License (UPL), Version 1.0
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
    if len(mainargs) == 0 : #if len(sys.argv)>1 and len(sys.argv)<5:
        parser = argparse.ArgumentParser(description='This program exports all specified type of artifact (api, plan, application, gateway..) from APICS and persist them on the file system') 
        parser.add_argument('-cf','--configfile', dest='configfile', help='config file specifying server, auth, proxy and other details in json format;', default='apipcs_config.json', required=False)
        parser.add_argument('--destdir', dest='destdir', default='./', help='directory path on local file system where all the exported API artifacts will be saved to; defaults to current directory', required=False )
        parser.add_argument('-i','--item', dest='item', help='type of artifacts (api, plan, application, gateway..) to be exported', required=True )
        cmdargs = parser.parse_args()
        #Feature specific args parse
        serverargs = (cmdargs.configfile,)
        destdir = cmdargs.destdir   #default CWD
        item = cmdargs.item
    else:
        #Feature specific args parse
        numargs = len(mainargs)
        if numargs in  (4,5): pass
        else: raise TypeError("Number of arguments expected is 4 or 5 ; got {} !".format(numargs)) 
        serverargs = mainargs[0:3]
        destdir = mainargs[3:4][0] if (numargs==5) else './'   #default CWD
        item = mainargs[4:5][0] if (numargs==5) else './'   #default CWD
            
    apisvr = apipserver(serverargs)
    getanyandstoreat = apisvr.getall(item)
    getanyandstoreat(destdir)

if __name__ == "__main__": main()



