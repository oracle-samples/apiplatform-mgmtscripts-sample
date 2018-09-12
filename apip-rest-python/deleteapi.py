# -*- coding: utf-8 -*-
#!/usr/bin/python3
#Copyright © 2018, Oracle and/or its affiliates. All rights reserved.
#The Universal Permissive License (UPL), Version 1.0
import os
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
    apiid= None
    if len(mainargs) == 0 : 
        parser = argparse.ArgumentParser(description='Deletes an Api from APICS by providing its api-id; When no API ID is provided deletes all APIs and can be used to cleanup')
        parser.add_argument('-cf','--configfile', dest='configfile', help='config file specifying server, auth, proxy and other details in json format;', default='apipcs_config.json', required=False)
        parser.add_argument('--apiid', dest='apiid', help='apiid to be deleted from API Platform server, warning - deletes all API when omitted', required=False)
        parser.add_argument('--force', dest='force', help='flag to force the deletion of applications', action='store_true', required=True)

        cmdargs = parser.parse_args()
        logging.info(cmdargs)
        serverargs = (cmdargs.configfile,)
        if (cmdargs.apiid): apiid = cmdargs.apiid #if (cmdargs.apifile) if (cmdargs.apifile) 
    else:
        logging.info(mainargs)
        numargs = len(mainargs)
        if numargs in  (3,4): pass
        else: raise TypeError("Number of arguments expected is 3 or 4 ; got {} !".format(numargs)) 
        serverargs = mainargs[0:3]
        if numargs==4 : apiid = mainargs[3:4] [0]
        
    if(apiid):
        apisvr = apipserver(serverargs)
        #export before delete
        apisvr.persistdetails(apiid, 'api')
        apisvr.deleteapi(apiid)
    else: #deleteall
        apisvr = apipserver(serverargs)
        apisvr.createdirectories()
        #allapis = apisvr.retrieveallapis()
        allapis = apisvr.retrieveall('api')()
        for apiid in loopapis(allapis): #Loop through all json files in CWD and import them
            logging.info('*** Deleting API - {}'.format(apiid))
            #export before delete
            apisvr.persistdetails(apiid, 'api')
            apisvr.deleteapi(apiid)
    return 'deleted'
                      
def loopapis(allapis): #generator func
    for k,v in allapis.items():
        count = None
        if k == "count": count=v
        if k == "items": 
            items=allapis[k]
            logging.info('***Found {} APIs defined on the apipcs server'.format(count))
            for element in items: 
                for m,n in element.items(): 
                    if m == 'id': yield n
 
 
if __name__ == "__main__": main()



