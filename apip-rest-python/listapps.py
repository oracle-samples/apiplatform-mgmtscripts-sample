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
    logging.debug(sys.argv)
    appid= None
    if len(mainargs) == 0 : 
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        parser = argparse.ArgumentParser(description='Lists all Applications from APICS and writes to console. Only writes to the console, use exportallapps to persist details in File system')
        parser.add_argument('-cf','--configfile', dest='configfile', help='config file specifying server, auth, proxy and other details in json format;', default='apipcs_config.json', required=False)
        cmdargs = parser.parse_args()
        logging.info(cmdargs)
        serverargs = (cmdargs.configfile,)
    elif len(mainargs) == 1: #REPL
        serverargs = mainargs[0]
    else:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logging.info(mainargs)
        numargs = len(mainargs)
        if numargs==3: pass
        else: raise TypeError("Number of arguments expected is 3; got {} !".format(numargs)) 
        serverargs = mainargs[0:3]
    apisvr = apipserver(serverargs)
    allapps = apisvr.retrieveall('application')()
    prettyprint(allapps)
    #allapps = apisvr.retrieveallapps()
    #for appid in loopapps(allapps): 
    #    logging.info('*** APP id - {}'.format(appid))
    return 'success'
    
                      
def loopapps(allapps): #generator func
    for k,v in allapps.items():
        if k == "count": count=v
        if k == "items": 
            items=allapps[k]
            for element in items: 
                for m,n in element.items(): 
                    if m == 'id': yield n
    logging.info('***Found {} Apps defined on the apipcs server'.format(count))
 
def prettyprint(allapis): #generator func
    for k,v in allapis.items():
       if k == "count": count=v
       if k == "items": 
           items=allapis[k]
           logging.info("==============listapps===============")
           header =  ["ID", "Name", "State", 'Created By', 'Created At' ]
           logging.info(header)
           for element in items: 
                appinfo = [element.get('id'), element.get('name'), element.get('state'), element.get('createdBy'), element.get('createdAt') ]
                logging.info(appinfo)

    logging.info('***Found {} Applications defined on the apipcs server'.format(count))
    logging.info("==============listapps===============")

 
if __name__ == "__main__": main()



