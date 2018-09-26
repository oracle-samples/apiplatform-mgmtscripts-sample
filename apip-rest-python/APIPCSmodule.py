# -*- coding: utf-8 -*-
#!/usr/bin/python3
#Copyright © 2018, Oracle and/or its affiliates. All rights reserved.
#The Universal Permissive License (UPL), Version 1.0
import os
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import datetime
from pathlib import Path
import base64
import logging
#from _overlapped import NULL
import getpass


class apipserver(object):
    def __init__(self, serverargs):
        numargs = len(serverargs)
        if numargs==1: # we have a config file !
            logging.info("Reading Config from - {}".format(serverargs[0]))
            _configinited= self.readconfig(serverargs[0])
        elif numargs==3: # coming from main args / unit tests
            logging.debug("Reading Config from default apipcs_config.json")
            _configinited= self.readconfig()
            #Override default config using supplied arguments
            #getpass#
            passwd = getpass.getpass(prompt='Please enter APIPCS password:', stream=None)
            #self._serverurl, self._auth = serverargs[0], serverargs[1:3] 
            self._serverurl, self._auth = serverargs[0], serverargs[1:2], passwd
            #getpass#
        else: raise TypeError("apipsvr needs 3 arguments ; got {} !".format(numargs))

        now = datetime.datetime.now()
        sessiondirname = 'apip-session-{:%Y%m%d-%H%M%S}'.format(now)
        self._sessiondir = Path(sessiondirname) #Path().absolute() #default- use where meaningful
        #sessiondir = Path(sessiondirname) 
        #self._basedirname = './' #default base dir name 
        self._mgmt_uri = "/management/v1/" # Todo get rid of this and use specific uris
        self._apis_uri = self._serverurl+"/management/v1/apis"
        self._api_uri = self._serverurl+"/management/v1/apis/{}"
        self._apps_uri = self._serverurl+"/management/v1/applications"
        self._app_uri = self._serverurl+"/management/v1/applications/{}"
        self._plans_uri = self._serverurl+"/management/v1/plans"
        self._plan_uri = self._serverurl+"/management/v1/plans/{}"
        self._gateways_uri = self._serverurl+"/management/v1/gateways"
        self._gateway_uri = self._serverurl+"/management/v1/gateways/{}"
        self._plan_subs_uri = self._serverurl+"/management/v1/plans/{}/subscriptions"
        self._plan_ents_uri = self._serverurl+"/management/v1/plans/{}/entitlements"
        self._plan_sub_detail_uri = self._serverurl+"/management/v1/plans/{}/subscriptions/{}"
        self._plan_ent_detail_uri = self._serverurl+"/management/v1/plans/{}/entitlements/{}"
        #All Grants to be exported! No Import
        self._api_grants_uri = self._serverurl+"/management/v1/apis/{}/grants"
        self._app_grants_uri = self._serverurl+"/management/v1/applications/{}/grants"
        self._plan_grants_uri = self._serverurl+"/management/v1/plans/{}/grants"
        self._gateway_grants_uri = self._serverurl+"/management/v1/gateways/{}/grants"
        #self._api_grant_uri = self._serverurl+"/management/v1/apis/{}/grants/{}"    # doesnt exist
    #Api contracts deprecated in 18.2.1 --START        
        self._api_contracts_uri = self._serverurl+"/management/v1/apis/{}/contracts"
        self._api_contract_uri = self._serverurl+"/management/v1/apis/{}/contracts/{}"
            #App Registrations deprecated in 18.2.1 --END
    #Api Contracts deprecated in 18.2.1 --START
        self._app_regs_uri = self._serverurl+"/management/v1/applications/{}/registrations??fields=state,application.description,application.key,application.contact.firstName"
        self._app_reg_uri = self._serverurl+"/management/v1/applications/{}/registrations/{}"#exists, not using for now; above gw_deps is good enough
    #App Registrations deprecated in 18.2.1 --END
        self._gw_deps_uri = self._serverurl+"/management/v1/gateways/{}/deployments?fields=api.description,api.vanityName,api.state"
        self._gw_dep_uri = self._serverurl+"/management/v1/gateways/{}/deployments/{}" #exists, not using for now; above gw_deps is good enough
        self._api_resources_uri = self._serverurl+"/management/v1/apis/{}/resources"
        self._api_resources_uri = self._serverurl+"/management/v1/apis/{}/resources/{}"
        self._level1uris = dict(api=self._apis_uri, application=self._apps_uri, plan=self._plans_uri, gateway=self._gateways_uri)
        self._level2uris = dict(api=self._api_uri, application=self._app_uri, plan=self._plan_uri, gateway=self._gateway_uri)
        self._level3uris = dict(apigrants=self._api_grants_uri, apicontracts=self._api_contracts_uri, apicontract=self._api_contract_uri, appregistrations=self._app_regs_uri, 
                                gatewaydeployments=self._gw_deps_uri, apiresource=self._api_resources_uri, gatewaygrants=self._gateway_grants_uri, appgrants=self._app_grants_uri, 
                                plangrants=self._plan_grants_uri, plansubscriptions=self._plan_subs_uri, planentitlements=self._plan_ents_uri)
        self._level4uris = dict(plansubscriptiondetail=self._plan_sub_detail_uri, planentitlementdetail=self._plan_ent_detail_uri)
        self._base_url = self._serverurl+self._mgmt_uri #Todo get rid of this and use specific



        #self._content_headers = {'Content-Type':'application/json', 'Accept':'application/json', 'X-RESOURCE-SERVICE-INSTANCE-GUID':'apics-e0918830-75ec-444d-8f9c-749918c8c8c3'}
        self._content_headers = {'Content-Type':'application/json', 'Accept':'application/json'}
        self._timeout_tuple = (20,100) #(60,300) 
        #Finally create a session
        self._s = requests.Session()
         # and set proxy on the session if available
        self._s.proxies =self._proxies if (self._proxies) else None
        logging.debug(self._s.proxies )
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        logging.debug('apipserver::init created http session for {}'.format(self._serverurl))
        self.apimappings = {}
        self.printconfig()
        
    def readconfig(self, configfile='apipcs_config.json'):
        with open(configfile, mode='rt') as config: 
            config = json.loads(config.read())
            self._serverurl = config.get('server')
            #getpass#
            #self._auth = tuple(config.get('auth'))
            if config.get('auth'):
                user = config.get('auth')[0]
                passwd = getpass.getpass(prompt='Password for APIPCS user- {}:'.format(user), stream=None)
                self._auth = (user, passwd)
                #getpass#
            elif 'oauth' in config.keys():
                #accesstoken = config.get('accesstoken')[0]
                accesstoken = getpass.getpass(prompt='oauth access token for accessing APIPCS :', stream=None)
                self._auth = TokenAuth(accesstoken)
            else:
                raise TypeError("Supply either basic-auth with username or oauth empty element in config file. \n Example : {}  !".
                                format(' "auth": ["weblogic"] or "accesstoken": [] '))
            self._proxies = config.get('proxy')
            self._basedirname = config.get('basedir')
            return True
            
    def printconfig(self):
        logging.debug('Using '+self._serverurl+' ;'+str(self._proxies)+' ;'+str(self._basedirname))
            
    def createdirectories(self, basedirname='./'):
        self._basedirname = basedirname # override if provided
        #Update default sessondir with desired one
        self._sessiondir = Path(os.path.join(self._basedirname,str(self._sessiondir)))
        self._sessiondir.mkdir(parents=True,exist_ok=True) #make it idempotently
        logging.debug('***All artifacts will go here - '+str(self._sessiondir))
        
    def validateargs(self):
        logging.info('Looks good for now, real validation happens when we curl !')
        
    def persistapiartifacts_ifany(self, api_id, apimd):
        logging.debug("Checking if there are artifacts to be retrieved..")
        artfs = apimd.get("artifacts")
        if len(artfs) > 0 :
            logging.debug("We have artifacts..")
            for artf in artfs:
                self.exportapiartifact(api_id, artf.get("pathname"), artf.get("content-type"))
        else: pass    

    def exportapiartifact(self, api_id, pathname, contenttype):
        logging.debug("getting artifacts from -"+pathname)
        resturi= self._level3uris.get('apiresource')
        resp = self._s.get(url=resturi.format(api_id, pathname), timeout=self._timeout_tuple, auth=self._auth, headers={'Content-Type':contenttype}, verify=False)
        saverawresponsetofile(resp, os.path.join(str(self._sessiondir),pathname ))
        logging.debug('*** api artifact Status code = '+str(resp.status_code))
        logging.debug('*** get artifact response = '+resp.text) 

        
    def importapi_populateartifacts(self, apifilepath): #Todo -  use when artifact upload is sorted out
        api = self.getpersistedapi(apifilepath)
        logging.debug(type(api))
        #for k, v in api.items():
        #    logging.info('API KEY {} :: APi VALUE {}'.format(k,v))
        try:
            logging.debug("SHR:: Outside Old Api before adding artifact contents :"+str(api))
            newapi = self.populateartifactcontents_ifany(apifilepath, api) #dict(api) #self.stripartifacts_ifany(apifilepath, api)
            logging.debug("SHR:: New Api after adding artifacts :"+str(newapi))
            #for k, v in api.items():
            #    logging.info('newapi KEY {} :: newapi VALUE {}'.format(k,v))
        except Exception as mye:
            logging.info('Error during populating artifact for this API- {}! Skipping import of this API'.format(apifilepath))
            logging.info('Root Cause - {}'.format(str(mye)))
            return
            #try to load the API anyway 
            #newapi = api
            
        logging.debug('python decoded to dictapi = '+str(api))
        resp = self._s.post(url=self._base_url+'apis/', data=str(newapi), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)
        logging.info('apipsvr::importapi response = '+resp.text) 
        oldapiid = api.get('id')
        apiname = api.get('name')
        logging.info('apipsvr::importapi Status code = '+str(resp.status_code))
        if resp.status_code==201:
            newapiid = resp.json().get("id")
            logging.info("Imported API successfully, API ID = {}".format(newapiid))
            self.addapimapping(oldapiid, newapiid, apiname)
            self.loadgrants(apifilepath, oldapiid, newapiid, 'apigrants')
        return resp.status_code

#This function Loads Grants for MM
    def loadgrants(self, filepath, oldid, newid, granttype): #relationtype
        postrawdata = '{{\"type\":\"{}\",\"{}\":{{\"id\":\"{}\"}} }}' #usergrant
        mappingfile = 'apimappings.json'
        try:
            for filename in os.listdir(os.path.join(os.path.dirname(filepath), granttype)): 
                try:
                    logging.info('Processing grant file - {}'.format(filename))
                    if filename.endswith('.json') and (oldid in filename) : 
                        with open(os.path.join(os.path.dirname(filepath), granttype,filename), mode='rt', buffering=1024, encoding='utf_8') as fd:
                            planents = json.load(fd)
                            grantcount = planents.get('count')
                            print('*** SHR:: import {} count = {} ****'.format(granttype, grantcount))
                            if grantcount > 0:
                                for k,v in planents.items():
                                    if k == "items": 
                                        items=planents[k]
                                        grantname=grantsubject=grantsubjid = None
                                        for element in items:        
                                            svalue = str(element)
                                            jvalue = json.loads(svalue.replace("'",'"'))
                                            tuser = jvalue.get('user')
                                            tgroup = jvalue.get('group')
                                            grantname = jvalue.get('type')
                                            grantsubject = "group" if  (tuser is None) else "user"
                                            grantsubjid = tgroup.get('id') if  (tuser is None) else tuser.get('id')
                                            
                                            logging.info('Grant Info: {}::{}::{}::{}'.format(granttype,grantname, grantsubject,grantsubjid))
                                            
                                            postdata = postrawdata.format(grantname, grantsubject, grantsubjid)
                                            logging.info('{} POST payload = {} '.format(granttype, postdata))
            
                                            resturi= self._level3uris.get(granttype).format(newid)
                                            resp = self._s.post(url=resturi, data=str(postdata), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)
                                            logging.info('apipsvr::{} POST response = {}'.format(granttype, resp.text)) 
                                            logging.info('apipsvr::{} POST Status code = '.format(granttype,str(resp.status_code)))
                    else:
                        logging.info('Skipping Processing grant file - {}'.format(filename))
                except FileNotFoundError as fne:
                    logging.info('Error - Incorrect location specified - {}'.format(filepath))
                    logging.info('Root Cause - {}'.format(str(fne)))
                    logging.info('Error processing file {} - Proceed to process next file'.format(filename))
        except FileNotFoundError as fne:
            logging.info('Error - Incorrect location specified - {}'.format(filepath))
            logging.info('Root Cause - {}'.format(str(fne)))
    
    def importplanX(self, apifilepath): #Todo -  use when artifact upload is sorted out
        plan = self.getpersistedapi(apifilepath)
        logging.debug('this is the file path passed on - {}'.format(apifilepath))
        logging.debug('this is the file path type pased on - {}'.format(type(apifilepath)))
        logging.debug('python decoded to dictapi = '+str(plan))
        resp = self._s.post(url=self._base_url+'plans/', data=str(plan), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)
        logging.debug('apipsvr::import Plan response = '+resp.text) 
        logging.debug('apipsvr::import Plan Status code = '+str(resp.status_code))
        if resp.status_code==201:
            logging.info("Imported Plan successfully, Plan ID = {}".format(resp.json().get("id")))
            newplan = json.loads(resp.text)   
            newplanId = newplan.get('id')
            oldplanid = apifilepath[apifilepath.find('plan-details-')+13:apifilepath.index('.json')]
            logging.info("old persisted plan id {}".format(oldplanid))
            logging.info("new created plan id {}".format(newplanId))
            
            self.loadPlanRelationships(apifilepath, oldplanid, newplanId, 'planentitlements')
            self.loadPlanRelationships(apifilepath, oldplanid, newplanId, 'plansubscriptions')
            self.loadgrants(apifilepath, oldplanid, newplanId, "plangrants")
        return resp.status_code

#This function recreates plan relationships for the newly created plan (newPlanId)
#relationships are plan entitlement (plan<->api) and plan subscription (plan<->app)
#Caution - recheck if the correct api/apps arte targetted as the script is reusing Ids from older export
    def loadPlanRelationships(self, apifilepath, oldplanid, newplanId, relationtype):
        deppattern = 'api' if (relationtype == 'planentitlements') else 'application'
        #postrawdata = '{{\"apiId\": \"{}\" }}' if (relationtype == 'planentitlements') else '{{\"applicationId\": \"{}\", \"state\": \"SUBSCRIBED\" }}'
        postrawdata = '{{\"apiId\": \"{}\", "publication": {{ \"state\": \"{}\"}} }}' if (relationtype == 'planentitlements') else '{{\"applicationId\": \"{}\", \"state\": \"{}\" }}'
        mappingfile = 'apimappings.json' if (relationtype == 'planentitlements') else 'appmappings.json'
        try:
            for filename in os.listdir(os.path.join(os.path.dirname(apifilepath), relationtype)): 
                try:
                    logging.info('Processing plan relationship file - {}'.format(filename))
                    if filename.endswith('.json') and (oldplanid in filename) : 
                        with open(os.path.join(os.path.dirname(apifilepath), relationtype,filename), mode='rt', buffering=1024, encoding='utf_8') as fd:
                            planents = json.load(fd)
                            planentscount = planents.get('count')
                            logging.info('*** SHR:: import {} count = {} ****'.format(relationtype, planentscount))
                            if planentscount > 0:
                                for k,v in planents.items():
                                    if k == "items": 
                                        items=planents[k]
                                        for jvalue in items:
                                            #jvalue = json.loads(element) #(element.replace("'",'"'))   
                                            tapi = jvalue.get(deppattern)
                                            entapiid = tapi.get('id')
                                            tstate = None
                                            if relationtype == 'planentitlements':  
                                                tpub = jvalue.get('publication')
                                                tstate = tpub.get('state')
                                                logging.info('planentitlements to be added: apiid ={}:: publication state={}'.format(entapiid, tstate))
                                            elif relationtype == 'plansubscriptions':
                                                tstate = jvalue.get('state')
                                                logging.info('plansubscriptions to be added: appid ={}:: entitlement state={}'.format(entapiid, tstate))

                                            if relationtype == 'planentitlements':
                                                mappedid = getmappedapiid(entapiid, mappingfile)
                                            elif relationtype == 'plansubscriptions':
                                                mappedid = getmappedappid(entapiid, mappingfile)
                                            
                                            #mappedid = getmappedapiid(entapiid, mappingfile)
                                            postdata = postrawdata.format(mappedid, tstate)

                                            logging.info('{} POST payload = {} '.format(relationtype, postdata))
                                            resturi= self._level3uris.get(relationtype).format(newplanId)
                                            resp = self._s.post(url=resturi, data=str(postdata), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)
                                            logging.info('apipsvr::{} create response = {}'.format(relationtype, resp.text)) 
                                            logging.info('apipsvr::{} create Status code = '.format(relationtype,str(resp.status_code)))
                    else:
                        logging.info('Skipping Processing plan relationship file - {}'.format(filename))
                except FileNotFoundError as fne:
                    logging.info('Error - Incorrect location specified - {}'.format(apifilepath))
                    logging.info('Root Cause - {}'.format(str(fne)))
                    logging.info('Error processing file {} - Proceed to process next file'.format(filename))
        except FileNotFoundError as fne:
            logging.info('Error - Incorrect location specified - {}'.format(apifilepath))
            logging.info('Root Cause - {}'.format(str(fne)))
        
        
    def addapimapping(self, oldapiid, newapiid, apiname):
        apimapping = '{{"oldapiid":"{}","newapiid":"{}","apiname":"{}"}}'.format(oldapiid, newapiid, apiname)
        logging.info("api mapping entry = {}".format(apimapping))
        fullfilename = os.path.join(os.curdir, str('apimappings.json'))
        logging.info("api mapping folder -{}".format(fullfilename))
        if not os.path.isfile(fullfilename):
            feeds = []
            feeds.append(apimapping)
            with open(fullfilename, mode='w') as f1:
                f1.write(json.dumps(feeds, indent=2))
        else:
            with open(fullfilename) as feedsjson:
                feeds = json.load(feedsjson)
                feeds.append(apimapping)

            with open(fullfilename, mode='w') as f2:
                f2.write(json.dumps(feeds, indent=2))        

        logging.debug('Building mappings file content - ***{}***'.format(apimapping))
        
    def addappmapping(self, oldappid, newappid, appname):
        appmapping = '{{"oldappid":"{}","newappid":"{}","appname":"{}"}}'.format(oldappid, newappid, appname)
        logging.info("app mapping entry = {}".format(appmapping))
        fullfilename = os.path.join(os.curdir, os.path.dirname(str('logs')), str('appmappings.json'))
        logging.info("app mapping folder -{}".format(fullfilename))
        if not os.path.isfile(fullfilename):
            feeds = []
            feeds.append(appmapping)
            with open(fullfilename, mode='w') as f1:
                f1.write(json.dumps(feeds, indent=2))
        else:
            with open(fullfilename) as feedsjson:
                feeds = json.load(feedsjson)
                feeds.append(appmapping)

            with open(fullfilename, mode='w') as f2:
                f2.write(json.dumps(feeds, indent=2))        

        logging.debug('Building mappings file content - ***{}***'.format(appmapping))
        
    def populateartifactcontents_ifany(self, apifilepath, api):
        newapi = dict(api)

        logging.debug("Checking if there are artifacts in the API..")
        artfs = newapi.get("artifacts")
        logging.debug(type(artfs))
        if len(artfs) > 0 :
            logging.debug("We have artifacts, which will be processed..")
            for artf in artfs:
                artifactfile = os.path.join(os.path.dirname(apifilepath), artf.get("pathname")) # artf.get("pathname")
                acontent = self.getartifactcontent(artifactfile, artf.get("pathname"), artf.get("content-type"))
                #bcontent = base64.urlsafe_b64encode(acontent) #base64.urlsafe_b64encode(bytes(acontent, 'utf_8')) #fails for APi custom icons!
                #standard_b64encode
                bcontent = base64.standard_b64encode(acontent) #base64 encoded bytes
                artf.update({"content": bcontent.decode()}) #base64 encoded string
        else: pass 
        return newapi   

    def getartifactcontent(self, artifactfile, artifactname, contenttype):
        logging.debug("processing artifact -{} of type - {} from file - {}".format(artifactname, contenttype, artifactfile))
        #read as bytes
        with open(artifactfile, mode='rb') as fd: #buffering=1024, 
            artifactcontent = fd.read()
            #logging.info("Contents of artifact file = "+artifactcontent)
            logging.debug(type(artifactcontent))
        return artifactcontent       
    
    def getpersistedapi(self, apifilepath):
        with open(apifilepath, mode='rt', buffering=1024, encoding='utf_8') as fd:
            api = json.load(fd)
        logging.debug("apisvr::getpersistedapi retrieved api from file - {}".format(apifilepath))
        return api  
        
                   
    def deleteapi(self, apiid): 
        resp = self._s.delete(url=self._base_url+'apis/'+apiid, timeout=self._timeout_tuple, auth=self._auth, verify=False)  
        logging.debug('*** deleteapi Status code = '+str(resp.status_code))
        logging.debug('*** deleteapi response = '+resp.text) 

    def deleteplan(self, apiid): 
        resp = self._s.delete(url=self._base_url+'plans/'+apiid, timeout=self._timeout_tuple, auth=self._auth, verify=False)  
        logging.debug('*** deleteplan Status code = '+str(resp.status_code))
        logging.debug('*** delete Plan response = '+resp.text) 

    def __del__(self):
        try:
            self._s.close()
            #logging.info('*** http session closed!')
        except Exception as e:
            logging.info('*** Error closing http session -'+str(e))
        #logging.info('*** http session cleanup complete!')
        
#====================
# Closures
#====================
    
    def getall(self, stufftype):
        stufftypes = self._level1uris.keys()#("api", "application", "plan", "gateway")
        if stufftype in stufftypes: pass
        else: raise TypeError("This method can be called only for {} - got {} !".format(stufftypes, stufftype))
        
        def getallstuff(basedirname='./'):
            logging.debug("inside name not important with {} and {}".format(self, basedirname))
            #self.createdirectories(basedirname) defer to latest
            resturi = self._level1uris.get(stufftype)
            resp = self._s.get(url=resturi, timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
            logging.debug('*** getall {} Status code = {}'.format(stufftype, str(resp.status_code)) )
            logging.debug('*** getall {} json response = {}'.format(stufftype, resp.text) )
            dict_res = json.loads(resp.text)  # for now this is good #@@Todo make pretty
            self.disembleresponse(dict_res, stufftype, basedirname)
        return getallstuff 
    
    def disembleresponse(self, dictres, stufftype, basedirname):
        count=0
        for k,v in dictres.items():
            if k == "count": count=v
            if k == "items": 
                items=dictres[k]
                for element in items:        
                    for m,n in element.items():
                        if m == 'id': id=n
                    self.persistdetails(id, stufftype, basedirname)
        logging.info('***Found {} {}s defined on the apipcs server'.format(count, stufftype))
        logging.info('***{} export complete!'.format(stufftype)) 
        
    def persistdetails(self, id, stufftype, basedirname='./'):
        self.createdirectories(basedirname) #use default
        logging.debug(stufftype)
        resturi = self._level2uris.get(stufftype)
        logging.debug('persistdetails using uri - {}'.format(resturi.format(id)))
        resp = self._s.get(url=resturi.format(id), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)
        logging.debug('*** get {} details Status code = {}'.format(stufftype, str(resp.status_code)))
        logging.debug('*** get {} details json response = {}'.format(stufftype, str(resp.text)))
        dict_res = json.loads(resp.text)  
        if resp.status_code==200:
            if stufftype == 'api': 
                self.persistapiartifacts_ifany(id, dict_res)
                self.savegrants('apigrants',id) 
                #self.persistapicontracts_ifany(id) 
            elif stufftype == 'application':
                self.savegrants('appgrants',id)
                #self.saveappregistrations(id) #Deprecated 
            elif stufftype == 'plan':
                self.savegrants('plangrants',id)
                #self.saveplansubscriptions(id)
                self.saveplanrelations(id, 'planentitlements')
                self.saveplanrelations(id, 'plansubscriptions') 
            elif stufftype == 'gateway':
                self.savegatewaygrants(id) 
                self.savegatewaydeployments(id)
            saveprettyreponsetofile(dict_res, os.path.join(str(self._sessiondir),'{}-details-{}.json'.format(stufftype, id)))
        else:
            saveprettyreponsetofile(dict_res, os.path.join(str(self._sessiondir),'{}-get-ERROR-details-{}.err'.format(stufftype, id)))
            logging.info("Unable to get {} details for {}. Check REST API response above".format(stufftype, id))        

    #Todo
    def importstuff(self, apifilepath):
        api = self.getpersistedapi(apifilepath)
        logging.debug(type(api))
        logging.debug('python decoded to dictapi = '+str(api))
        resp = self._s.post(url=self._base_url+'apis/', data=str(api), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)
        logging.debug('apipsvr::importapi Status code = '+str(resp.status_code))
        if resp.status_code==200:
            logging.info("Imported API successfully, API ID = {}".format(resp.json().get("id")))
        logging.debug('apipsvr::importapi json resonse = '+resp.text) 

    def listall(self, stufftype):
        stufftypes = self._level1uris.keys()
        if stufftype in stufftypes: pass
        else: raise TypeError("This method can be called only for {} - got {} !".format(stufftypes, stufftype))

        def listallstuff(): 
            resturi = self._level1uris.get(stufftype)
            resp = self._s.get(url=resturi, timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
            logging.debug('*** retrieve all {} Status code = {}'.format(stufftype, str(resp.status_code)))
            logging.debug('*** retrieve all {} response = {}'.format(stufftype, resp.text))
            allitems = json.loads(resp.text) #Todo hanndle non 200 response
            for iid in loopit(allitems, stufftype): 
                logging.info('*** {} id - {}'.format(stufftype, iid))            
        
        return listallstuff
    
    def retrieveall(self, stufftype):
        stufftypes = self._level1uris.keys()
        if stufftype in stufftypes: pass
        else: raise TypeError("This method can be called only for {} - got {} !".format(stufftypes, stufftype))
    
        def retrieveallstuff(): 
            resturi = self._level1uris.get(stufftype)
            resp = self._s.get(url=resturi, timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
            logging.debug('*** retrieve all {} Status code = {}'.format(stufftype, str(resp.status_code)))
            #logging.info('*** retrieve all {} response = {}'.format(stufftype, resp.text))
            allitems = json.loads(resp.text) #Todo hanndle non 200 response
            return allitems          
        
        return retrieveallstuff
#====================
#Application methods
#====================

 

    def importapplication(self, appfilepath): 
        app = self.getpersistedapi(appfilepath)
        logging.debug(type(app))
        logging.debug('python decoded to dictapi = '+str(app))
        resp = self._s.post(url=self._base_url+'applications/', data=str(app), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)
        logging.debug('apipsvr::importapp response = '+resp.text) 
        logging.debug('apipsvr::importapp Status code = '+str(resp.status_code))
        oldappid = app.get('id')
        appname = app.get('name')
        #if resp.status_code==200:
        #    logging.info("Imported Application successfully, Application ID = {}".format(resp.json().get("id")))
        #return resp.status_code
        if resp.status_code==201:
            newappid = resp.json().get("id")
            logging.info("Imported Application successfully, App ID = {}".format(newappid))
            self.addappmapping(oldappid, newappid, appname)
            self.loadgrants(appfilepath, oldappid, newappid, 'appgrants')
        return resp.status_code


    def retrieveallapps(self): 
        resp = self._s.get(url=self._base_url+'applications', timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
        logging.debug('*** retrieve allapps Status code = '+str(resp.status_code))
        #logging.info('*** retrieve allapps response = '+resp.text) 
        allapps = json.loads(resp.text) #Todo hanndle non 200 response
        return allapps

    def retrieveallgateways(self): 
        resp = self._s.get(url=self._base_url+'gateways', timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
        logging.debug('*** retrieve allgateways Status code = '+str(resp.status_code))
        #logging.info('*** retrieve allgateways response = '+resp.text) 
        allgws = json.loads(resp.text) #Todo hanndle non 200 response
        return allgws

    def deleteapp(self, appid): 
        resp = self._s.delete(url=self._base_url+'applications/'+appid, timeout=self._timeout_tuple, auth=self._auth, verify=False)  
        logging.debug('*** delete app Status code = '+str(resp.status_code))
        #logging.info('*** delete app response = '+resp.text) 

    def saveprettyresponsetonewdirfile(self, response, foldername, filename):
        folder = Path(os.path.join(str(self._sessiondir)), foldername )
        folder.mkdir(parents=True,exist_ok=True) #make it idempotently
        filetoopen =  os.path.join(str(folder),filename)
        logging.debug(filetoopen)
        with open(filetoopen, 'wt') as fd:
            #json.dump(getapidetailsresponse, fd, cls=CustomJsonEncoder, indent=4,  )
            json.dump(response, fd, indent=4,  )
        logging.info("***Check {} for exported details.".format(str(filetoopen)))     


#===================
# new v3
#===================
    def savegrants(self, stufftype, artid):  # done
        resourceuri = self._level3uris.get(stufftype) 
        resp = self._s.get(url=resourceuri.format(artid), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
        logging.debug('*** get all {} Status code = '.format(stufftype, str(resp.status_code)) )
        logging.debug('*** get all {} response = '.format(stufftype, resp.text)) 
        apigrants = json.loads(resp.text)  # for now this is good #@@Todo make pretty

        logging.debug(str(self._sessiondir))
        if resp.status_code==200: 
            self.saveprettyresponsetonewdirfile(apigrants, stufftype,'{}-details-{}.json'.format(stufftype, artid))
        else:
            self.saveprettyreponsetofile(dict_res, os.path.join(str(self._sessiondir),'{}-get-ERROR-details-{}.err'.format(stufftype, artid)))
            logging.info("Unable to get {} details for {}. Check REST API response above".format(stufftype, id))        
        
    def savegatewaygrants(self, gwid, stufftype='gatewaygrants'): 
        resourceuri = self._level3uris.get('gatewaygrants')      
        logging.debug('*** Retrieving {} using URI - '.format(stufftype, resourceuri.format(gwid)))
        
        resp = self._s.get(url=resourceuri.format(gwid), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
        logging.debug('*** get all {} Status code = {}'.format(stufftype, str(resp.status_code)))
        logging.debug('*** get all {} response = {}'.format(stufftype, resp.text)) 
        gwgrants = json.loads(resp.text) 
        logging.debug(str(self._sessiondir))
        if resp.status_code==200: 
            self.saveprettyresponsetonewdirfile(gwgrants, 'gatewaygrants','{}-details-{}.json'.format(stufftype, gwid))
        else:
            self.saveprettyreponsetofile(resp.text, os.path.join(str(self._sessiondir),'{}-get-ERROR-details-{}.err'.format(stufftype, gwid)))
            logging.info("Unable to get {} details for {}. Check REST API response above".format(stufftype, id))        

    def savegatewaydeployments(self, gwid, stufftype='gatewaydeployments'): 
        resourceuri = self._level3uris.get('gatewaydeployments')      
        logging.debug('*** Retrieving {} using URI - '.format(stufftype, resourceuri.format(gwid)))
        
        resp = self._s.get(url=resourceuri.format(gwid), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
        logging.debug('*** get all {} Status code = {}'.format(stufftype, str(resp.status_code)))
        logging.debug('*** get all {} response = {}'.format(stufftype, resp.text)) 
        gwgrants = json.loads(resp.text) 
        logging.debug(str(self._sessiondir))
        if resp.status_code==200: 
            self.saveprettyresponsetonewdirfile(gwgrants, 'gatewaydeployments','{}-details-{}.json'.format(stufftype, gwid))
        else:
            self.saveprettyreponsetofile(resp.text, os.path.join(str(self._sessiondir),'{}-get-ERROR-details-{}.err'.format(stufftype, gwid)))
            logging.info("Unable to get {} details for {}. Check REST API response above".format(stufftype, id))        

    #appregistrations
    def saveappregistrations(self, appid, stufftype='appregistrations'): 
        resourceuri = self._level3uris.get('appregistrations')      
        logging.debug('*** Retrieving {} using URI - '.format(stufftype, resourceuri.format(appid)))
        
        resp = self._s.get(url=resourceuri.format(appid), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
        logging.debug('*** get all {} Status code = {}'.format(stufftype, str(resp.status_code)))
        logging.debug('*** get all {} response = {}'.format(stufftype, resp.text)) 
        appregs = json.loads(resp.text) 
        logging.debug(str(self._sessiondir))
        if resp.status_code==200: 
            self.saveprettyresponsetonewdirfile(appregs, 'appregistrations','{}-details-{}.json'.format(stufftype, appid))
        else:
            saveprettyreponsetofile(resp.text, os.path.join(str(self._sessiondir),'{}-get-ERROR-details-{}.err'.format(stufftype, appid)))
            logging.info("Unable to get {} details for {}. Check REST API response above".format(stufftype, id))        
    
    
    def persistapicontracts_ifany(self, apiid, stufftype='apicontracts', subdirname='apicontracts'):
        #todo get from map
        resourceuri = self._level3uris.get('apicontracts')
        logging.debug('*** Retrieving {} using URI - '.format(stufftype, resourceuri.format(apiid)))

        resp = self._s.get(url=resourceuri.format(apiid), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
        logging.debug('*** get all {} Status code = {}'.format(stufftype, str(resp.status_code)))
        logging.debug('*** get all {} response = {}'.format(stufftype, resp.text)) 
        apicontracts = json.loads(resp.text)  # for now this is good #@@Todo make pretty
        #loop thru using a generator
        for contractid in loopidsfromresponse(apicontracts):
            resturi= self._level3uris.get('apicontract')
            logging.debug('*** Retrieving {} using URI - {}'.format(stufftype, resturi.format(apiid, contractid)))
            response = self._s.get(url=resturi.format(apiid, contractid), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)
            logging.debug('*** GET {} Status code = {}'.format(stufftype,str(response.status_code)))
            logging.debug('*** GET {} response = {}'.format(stufftype,response.text)) 
            logging.debug(str(self._sessiondir))
            if response.status_code==200: 
                contract = json.loads(response.text)  # for now this is good #@@Todo make pretty
                self.saveprettyresponsetonewdirfile(contract, 'apicontracts','api-{}-{}-details-{}.json'.format(apiid, stufftype, contractid))
            else:
                self.saveprettyreponsetofile(response.text, os.path.join(str(self._sessiondir),'api-{}-{}-get-ERROR-details-{}.err'.format(stufftype, apiid, contractid)))
                logging.info("Unable to get {} details for api-{}-{}-{}. Check REST API response above".format(stufftype, apiid, stufftype, contractid ))        
        
#==================
#Plan Methods
#==================
    #plansubscriptions todo remove and refactor make generic
    def saveplansubscriptions(self, planid, stufftype='plansubscriptions'): 
        resourceuri = self._level3uris.get('plansubscriptions')      
        logging.debug('*** Retrieving {} using URI - '.format(stufftype, resourceuri.format(planid)))
        
        resp = self._s.get(url=resourceuri.format(planid), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
        logging.debug('*** get all {} Status code = {}'.format(stufftype, str(resp.status_code)))
        logging.debug('*** get all {} response = {}'.format(stufftype, resp.text)) 
        plansubs = json.loads(resp.text) 
        logging.debug(str(self._sessiondir))
        if resp.status_code==200:
            #Since we have plansubs, now get plan subscription details for each plansub
            plansubscount = plansubs.get('count')
            logging.info('*** SHR:: plan subscriptions count = {} ****'.format(plansubscount))
            if plansubscount > 0:
                for k,v in planents.items():
                    if k == "items": 
                        items=planents[k]
                        for element in items:        
                            for m,n in element.items():
                                if m == 'api': 
                                    logging.info('Plan Entitlement API Id = {} '.format(n))
                self.saveprettyresponsetonewdirfile(plansubs, 'plansubscriptions','{}-details-{}.json'.format(stufftype, planid))
        else:
            self.saveprettyreponsetofile(resp.text, os.path.join(str(self._sessiondir),'{}-get-ERROR-details-{}.err'.format(stufftype, planid)))
            logging.info("Unable to get {} details for {}. Check REST API response above".format(stufftype, id))        

            
    #method to fetch 'planentitlements' and 'plansubscriptions'
    def saveplanrelations(self, planid, stufftype):  
        resourceuri = self._level3uris.get(stufftype)      
        logging.debug('*** Retrieving {} using URI - '.format(stufftype, resourceuri.format(planid)))
        
        resp = self._s.get(url=resourceuri.format(planid), timeout=self._timeout_tuple, auth=self._auth, headers=self._content_headers, verify=False)  
        logging.debug('*** get all {} Status code = {}'.format(stufftype, str(resp.status_code)))
        logging.debug('*** get all {} response = {}'.format(stufftype, resp.text)) 
        planents = json.loads(resp.text) 
        logging.debug(str(self._sessiondir))
        if resp.status_code==200:
            #Since we have planents, now get plan entitlement details for each planent
            planentscount = planents.get('count')
            logging.info('*** {} count = {} ****'.format(stufftype,planentscount))
            if planentscount > 0:
                for k,v in planents.items():
                    if k == "items": 
                        items=planents[k]
                        for element in items:        
                            for m,n in element.items():
                                if m == 'api': 
                                    logging.info('{} API Id = {} '.format(stufftype,n))
                self.saveprettyresponsetonewdirfile(planents, stufftype,'{}-details-{}.json'.format(stufftype, planid))
        else:
            self.saveprettyreponsetofile(resp.text, os.path.join(str(self._sessiondir),'{}-get-ERROR-details-{}.err'.format(stufftype, planid)))
            logging.info("Unable to get {} details for {}. Check REST API response above".format(stufftype, id))        

class TokenAuth(requests.auth.AuthBase):
    
    def __init__(self, accesscode):
        self.accesscode = accesscode
        
        
    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer '+self.accesscode
        #print_request(r)
        return r
#=====================
#Utility methods
#=====================      
def print_request(req):
    
    print('SHREE:: HTTP/1.1 {method} {url}\n{headers}\n\n{body}'.format(
        method=req.method,
        url=req.url,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        body="NONE",
    ))

def loopidsfromresponse(dictres): #generator func
    count=0
    for k,v in dictres.items():
        if k == "count": count=v
        if k == "items": 
            items=dictres[k]
            for element in items:        
                for m,n in element.items():
                    if m == 'id': yield n
    logging.info('*** Found {} items defined on the API platform server'.format(count))

def saverawresponsetofile(rawresponse, fullfilename):
    with open(fullfilename, 'wb') as fd:
        for chunk in rawresponse.iter_content(chunk_size=128):
            fd.write(chunk)
    logging.info("***Check file {} for details".format(fullfilename))                   

def saveprettyreponsetofile(response, fullfilename):  
    with open(fullfilename, 'w+') as fd:
        #json.dump(getapidetailsresponse, fd, cls=CustomJsonEncoder, indent=4,  )
        json.dump(response, fd, indent=4,  )
    logging.info("***Check {} for exported api details.".format(fullfilename))      

def loopit(allitems, stufftype): #generator func
    for k,v in allitems.items():
        if k == "count": count=v
        if k == "items": 
            items=allitems[k]
            for element in items: 
                for m,n in element.items(): 
                    if m == 'id': yield n
            logging.info('***Found (loopit) {} {}s defined on the apipcs server'.format(count, stufftype))

def getmappedapiid(oldapiid, mappingfile):
    #mappingfile = 'apimappings.json'
    with open(mappingfile) as feedsjson:
        map={}
        feeds = json.load(feedsjson)
        for mapping in feeds:
            map = json.loads(mapping)
            if map.get('oldapiid') == str(oldapiid):
                logging.info('oldapiid ='+map.get('oldapiid') )
                logging.info('newapiid ='+map.get('newapiid') )
                return map.get('newapiid')


def getmappedappid(oldappid, mappingfile):
    #mappingfile = 'appmappings.json'
    with open(mappingfile) as feedsjson:
        map={}
        feeds = json.load(feedsjson)
        for mapping in feeds:
            map = json.loads(mapping)
            if map.get('oldappid') == str(oldappid):
                logging.info('oldappid ='+map.get('oldappid') )
                logging.info('newappid ='+map.get('newappid') )
                return map.get('newappid')
         
def main(*mainargs):
    # Can only be called internally for testing    
    apisvr = apipserver(mainargs)
    apisvr.validateargs()
                  
if __name__ == "__main__": main()



