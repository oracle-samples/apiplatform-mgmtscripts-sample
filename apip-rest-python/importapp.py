# -*- coding: utf-8 -*-
#!/usr/bin/python3
#Copyright © 2018, Oracle and/or its affiliates. All rights reserved.
#The Universal Permissive License (UPL), Version 1.0
import os
import sys
import requests
import json
from textwrap import indent
from APIPCSmodule import apipserver
from pathlib import Path
import argparse
import datetime
import logging
                  
def main(*mainargs):
    logging.basicConfig(filename='logs/apip-session-{:%Y%m%d-%H%M%S}.log'.format(datetime.datetime.now()), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)    
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info(sys.argv)
    appfilepath= None
    if len(mainargs) == 0 : #if len(sys.argv)>1 and len(sys.argv)<5:
        parser = argparse.ArgumentParser(description='Import an Application into APICS by providing a json file;')
        parser.add_argument('-cf','--configfile', dest='configfile', help='config file specifying server, auth, proxy and other details in json format;', default='apipcs_config.json', required=False)
        parser.add_argument('--apifile', dest='apifile', help='full path of file to be imported;', required=True)
        cmdargs = parser.parse_args()
        logging.info(cmdargs)
        serverargs = (cmdargs.configfile,)
        if (cmdargs.apifile): appfilepath = cmdargs.apifile  
    else:
        logging.info(type(mainargs))
        #Feature specific args parse
        numargs = len(mainargs)
        logging.info(numargs)
        if numargs==4: pass
        else: raise TypeError("Number of arguments expected is 4 ; got {} !".format(numargs)) 
        serverargs = mainargs[0:3]
        appfilepath = mainargs[3:4] [0]

    apisvr = apipserver(serverargs)
    apisvr.importapplication(appfilepath)
    return 'success'
 
if __name__ == "__main__": main() 



