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
    apifilepath= None
    if len(mainargs) == 0 : #if len(sys.argv)>1 and len(sys.argv)<5:
        parser = argparse.ArgumentParser(description='Import an API into APICS by providing a json file; When not provided, loops through all json files in the current directory and imports them')
        parser.add_argument('-cf','--configfile', dest='configfile', help='config file specifying server, auth, proxy and other details in json format;', default='apipcs_config.json', required=False)
        parser.add_argument('--apifile', dest='apifile', help='full path of file to be imported', required=True)
        cmdargs = parser.parse_args()
        logging.info(cmdargs)
        #serverargs = (cmdargs.server, cmdargs.user, cmdargs.passwd)
        serverargs = (cmdargs.configfile,)
        if (cmdargs.apifile): apifilepath = cmdargs.apifile #if (cmdargs.apifile) if (cmdargs.apifile) 
    else:
        logging.info(type(mainargs))
        #Feature specific args parse
        numargs = len(mainargs)
        logging.info(numargs)
        if numargs == 4: pass
        else: raise TypeError("Number of arguments expected is  4 ; got {} !".format(numargs)) 
        serverargs = mainargs[0:3]
        apifilepath = mainargs[3:4] [0]

    if(apifilepath):
        apisvr = apipserver(serverargs)
        apisvr.importapi_populateartifacts(apifilepath)
    else:
        for jsonfile in findalljsonfiles(): #Loop through all json files in CWD and import them
            logging.info('*** Processing json file {} found in current working directory '.format(jsonfile))
            apisvr = apipserver(serverargs)
            logging.info(jsonfile)
            apisvr.importapi_populateartifacts(jsonfile)
    return 'success'
                      
def findalljsonfiles(): #generator func
    for filename in os.listdir(): 
        if filename.endswith('.json'): yield filename
 
if __name__ == "__main__": main() 



