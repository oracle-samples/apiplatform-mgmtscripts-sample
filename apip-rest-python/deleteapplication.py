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
    appid= None
    if len(mainargs) == 0 : 
        parser = argparse.ArgumentParser(description='Deletes an Application from APICS by providing its app-id; When no App ID is provided deletes all Apps and can be used to cleanup')
        parser.add_argument('-cf','--configfile', dest='configfile', help='config file specifying server, auth, proxy and other details in json format;', default='apipcs_config.json', required=False)
        parser.add_argument('--appid', dest='appid', help='appid to be deleted from API Platform server, warning - deletes all Apps when omitted', required=False)
        parser.add_argument('--force', dest='force', help='flag to force the deletion of applications', action='store_true', required=True)

        cmdargs = parser.parse_args()
        logging.info(cmdargs)
        serverargs = (cmdargs.configfile,)
        if (cmdargs.appid): appid = cmdargs.appid  
    else:
        logging.info(mainargs)
        numargs = len(mainargs)
        if numargs in  (3,4): pass
        else: raise TypeError("Number of arguments expected is 3 or 4 ; got {} !".format(numargs)) 
        serverargs = mainargs[0:3]
        if numargs==4 : appid = mainargs[3:4] [0]
        
    if(appid):
        apisvr = apipserver(serverargs)
        #export before delete
        apisvr.persistdetails(appid, 'application')
        apisvr.deleteapp(apiid)
    else: #deleteall
        apisvr = apipserver(serverargs)
        allapps = apisvr.retrieveall('application')()
        for appid in loopapps(allapps): #Loop through all json files in CWD and import them
            logging.info('*** Deleting Application - {}'.format(appid))
            #export before delete
            apisvr.persistdetails(appid, 'application')
            apisvr.deleteapp(appid)
    return 'deleted'
                      
def loopapps(allapps): #generator func
    count = None
    for k,v in allapps.items():
        if k == "count": count=v
        if k == "items":
            items=allapps[k]
            for element in items: 
                for m,n in element.items(): 
                    if m == 'id': yield n
    logging.info('***Found {} Apps defined on the apipcs server'.format(count)) 
    
 
 
if __name__ == "__main__": main()




