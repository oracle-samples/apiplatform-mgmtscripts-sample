
# <a name="apiplatform-mgmtscripts-sample"></a>apiplatform-mgmtscripts-sample
   * [apiplatform-mgmtscripts-sample](#apiplatform-mgmtscripts-sample)
      * [Introduction](#introduction)
         * [Why](#why)
      * [Prerequisites](#prerequisites)
      * [Common Administrative Operations:](#common-administrative-operations)
         * [Exporting all APIs from an API Platform (exportallapis.py)](#exporting-all-apis-from-an-api-platform-exportallapispy)
         * [Exporting all Applications from an API Platform (exportallapplications.py)](#exporting-all-applications-from-an-api-platform-exportallapplicationspy)
         * [Exporting all Plans from an API Platform (exportallplans.py)](#exporting-all-plans-from-an-api-platform-exportallplanspy)
         * [Importing APIs into an API Platform (importapis_fromdir.py)](#importing-apis-into-an-api-platform-importapis_fromdirpy)
         * [Importing Applications into an API Platform (importapplications_fromdir.py)](#importing-applications-into-an-api-platform-importapplications_fromdirpy)
         * [Importing Plans into an API Platform (importplans_fromdir.py)](#importing-plans-into-an-api-platform-importplans_fromdirpy)
         * [Other Utility commands](#other-utility-commands)
      * [REPL interface](#repl-interface)
         * [A note about grants](#a-note-about-grants)
         * [Logs](#logs)

## <a name="introduction"></a> Introduction

This blog introduces a few useful Python scripts written to repeatedly perform common administrative tasks and development operations on an API Platform Cloud Service instance.

The scripts are written in Python and can be executed on all Python 3.6+ supported platforms

### <a name="why"></a> Why

These scripts are written keeping in mind a few real life use cases, such as –

- Migration of API Platform artifacts between different API server environments
- Export of API Platform artifacts for source control

The scripts require familiarity with API Platform Cloud Service. Knowledge of Python programming language is not essential to execute the scripts and the interactive REPL, but will come in handy to customize or extend the functionality of the scripts to suite any specific needs.

## <a name="prerequisites"></a> Prerequisites

The scripts require Python version 3.6+ and ‘requests’ module installed.

The API Platform Cloud Service (APIPCS) REST API documentation is available here.   
Autonomous APIPCS - http://docs.oracle.com/en/cloud/paas/api-platform-cloud   
User Managed APIPCS- https://docs.oracle.com/en/cloud/paas/api-platform-cloud-um


The python scripts zip pack can be downloaded FROM **[here](https://github.com/oracle/apiplatform-mgmtscripts-sample/archive/refs/heads/master.zip).**

Extract the zip archive. All python scripts are found within the apip-rest-python directory.

Usage information: Use ‘—help’ to get the usage of every script

For example, python listapis.py –help

> `['listapis.py', '--help']`
> `usage: listapis.py [-h] [-cf CONFIGFILE]`
>
> `Lists all APIs from APICS and writes to console. Only writes to the console, ``use exportallapis to persist details in File system`
>
> `optional arguments:`
> `-h, --help            show this help message and exit`
> `-cf CONFIGFILE, --configfile CONFIGFILE config file specifying server, auth, proxy and other details in json format;`

All scripts accept a common config file as argument which contains the details required to connect to and authenticate against the API Platform Cloud service. The file is in json format and defaults to apipcs_config.json when not provided.   

Note that API Platform Cloud Service - User Managed (APIPCS UM) uses basic auth and requires the username, password credentials of an APIPCS user for authentication. Here is an example of how the file would appear for APIPCS UM.

**APICS User Managed - sample json config file using basic auth** :
> `apipcs_config.json:`   
> `{   `   
> `    "server": "http://host:7201/apiplatform" ,   `   
> `    "auth": ["weblogic"],`   
> `}`   

Provide only the username for authentication. The scripts will prompt for a password during execution !
>`Password for APIPCS user- weblogic:`

Oracle Autonomous API Platform Cloud Service (APIPCS) uses Oauth and requires an access token issued by Oracle Identity Cloud Service for APIPCS user, in order to be authenticated.   
Refer here for 
<a name="https://docs.oracle.com/en/cloud/paas/api-platform-cloud/apfrm/Authentication.html">**generating access tokens for APIPCS**</a>   
Here is a sample json config file to be used for Autonomous APIPCS. Specify a marker element for 'oauth' with an empty value. The script will prompt for access token during execution !

**Autonomous APIPCS - sample json config file using oauth**:
> `apipcs_config.json:`   
>`{`   
>`	"server": "http://localhost:7201/apiplatform" ,`   
>`	"oauth" : []`   
>`}`   

Note - the script will prompt for the oauth access token during execution!
> `oauth access token for accessing APIPCS :`   

Additionally, proxy infomation can also be provided when a http/https proxy server is required to connect to the API platform Cloud Service. Shown below are sample proxy configurations.

> `{`
> `    "server": "https://host/apiplatform" ,`  
> `    "auth": ["weblogic"],`  
> `    "proxy": {`  
> `        "http": "proxy.xxx.yyy.com:80", `   
> `        "https": "proxy.xxx.yyy.com:80"`   
> `    }`
> `}`


## <a name="common-administrative-operations"></a> Common Administrative Operations:

### 

### <a name="exporting-all-apis-from-an-api-platform-exportallapispy"></a> Exporting all APIs from an API Platform (exportallapis.py)

This script will export the metadata of all APIs defined in API platform Cloud Service.

The metadata in json format will be persisted within the destination directory specified in the client file system.  In addition to the API metadata, the following additional artifacts are also fetched and persisted to the file system –

- API resources like files used to specify the Overview and Documentation content of APIs
- API Grants that have been issued to every API
- API Contracts associated with every API

> `Usage:`
> `    python exportallapis.py --help`
> `    exportallapis.py [-h] [-cf CONFIGFILE] [--destdir DESTDIR]`
>
> `    This program exports all APIs and its associated artifacts from APICS and` `persist them on the file system`   
> `    optional arguments:`   
> `      -h, --help       show this help message and exit`   
> `      -cf CONFIGFILE, --configfile CONFIGFILE    config file specifying server,`   
>   
> `auth, proxy and other otails in json format;`   
> `--destdir DESTDIR     directory path on local file system where all the exported API artifacts will be saved to; defaults to current directory`   

### 

### <a name="exporting-all-applications-from-an-api-platform-exportallapplicationspy"></a> Exporting all Applications from an API Platform (exportallapplications.py)

This script will export the metadata of all Applications created on API platform Cloud Service.

The metadata in json format will be persisted within the destination directory specified in the client file system. In addition to the Applications’ metadata, the following additional artifacts are also fetched and persisted to the file system –

- Application registrations associated with every Application being exported

> `usage:`
> `exportallapplications.py [-h] [-cf CONFIGFILE] [--destdir DESTDIR]`   
> `This program exports all Applications from APICS and persist them on the file system`   
>   
> `optional arguments:`   
> `  -h, --help       show this help message and exit`   
> `  -cf CONFIGFILE, --configfile CONFIGFILE    config file specifying server, auth, proxy and other`   
> `                        details in json format;`   
> `  --destdir DESTDIR     directory path on local file system where all the exported Apps and artifacts will be saved to; defaults to current directory`   

 

### <a name="exporting-all-plans-from-an-api-platform-exportallplanspy"></a> Exporting all Plans from an API Platform (exportallplans.py)

This script will export the metadata of all Plans created on API platform Cloud Service.

The metadata in json format will be persisted within the destination directory specified in the client file system. In addition to the plans' metadata, the following additional artifacts are also fetched and persisted to the file system –

- Plan Grants associated with the plans
- Plan Entitlements 
- Plan Subscriptions

> `usage: exportallplans.py [-h] [-cf CONFIGFILE] [--destdir DESTDIR]This program exports all plans' metadata from APICS and persist them on the file system`     
>   
> `optional arguments:`   
> `  -h, --help        show this help message and exit`   
> `  -cf CONFIGFILE, --configfile CONFIGFILE    config file specifying server, auth, proxy and other details in json format;`   
> `  --destdir DESTDIR     directory path on local file system where all the exported gateway details will be saved to; defaults to current directory`   

 

### <a name="importing-apis-into-an-api-platform-importapis_fromdirpy"></a> Importing APIs into an API Platform (importapis_fromdir.py)

This script scans through all the API metadata jsons in a specified directory and creates them on the target API Platform server. The script also reads any resources referenced, like files used to specify the Overview and Documentation content from the same directory and includes their content when creating the API on the target API Platform server

Note that API grants and contracts are not used when importing. The new APIs will be created on target server with default grants and no contracts.

> `Usage`   
> `importapis_fromdir.py [-h] [-cf CONFIGFILE] --dirpath DIRPATH`   
>   
> `Import APIs into APICS by reading all json files in specified dirpath;`   
>   
> `optional arguments:`   
> `  -h, --help       show this help message and exit`   
> `  -cf CONFIGFILE, --configfile CONFIGFILE config file specifying server, auth, proxy and other details in json format;`      
> `  --dirpath DIRPATH     directory path; All json files from this directory will be imported`    

If any of the APIs have references to gateways or credentials in their policies, then such policies will be in draft mode after import. These should be completed prior to publishing these APIs on the target APIPCS server.

 

### <a name="importing-applications-into-an-api-platform-importapplications_fromdirpy"></a> Importing Applications into an API Platform (importapplications_fromdir.py)

This script scans through all the Application metadata json files in a specified directory and creates them on the target API Platform server. Note that Application registrations will not be used when importing. The new Applications will be created on target server with no registrations.

> `Usage: importapplications_fromdir.py [-h] [-cf CONFIGFILE] --dirpath DIRPATHImport Applications into APICS by reading all json files in specified dirpath;`   
>      
> `optional arguments:`   
> `-h, –help            show this help message and exit`   
> `-cf CONFIGFILE, –configfile CONFIGFILE config file specifying server, auth, proxy and other details in json format;`   
> `–dirpath DIRPATH     directory path; All json files from this directory will be imported`   

 
### <a name="importing-plans-into-an-api-platform-importplans_fromdirpy"></a> Importing Plans into an API Platform (importplans_fromdir.py)

This script scans through all the plan jsons in the specified directory and creates them on the target API Platform server. The script also recreates the entitlements and subscriptions associated with the plans. For this reason the order of importing artifacts is important.   
**Note**: Ensure that artifacts are imported in the following order   
    1) Api, 2) Apps and then 3) Plans   
The plan metadata contains the relations between APIs-Plans-Apps in the form of entitlements and subscriptions.   
The script assumes that APIs and Apps are already imported prior to importing the plans and attempts to recreate the relations as they existed in the original API Platform CS instance.

Note that Plan grants are not used when importing. The new Plans will be created on target server with default grants.

> `Usage`   
> `importplans_fromdir.py [-h] [-cf CONFIGFILE] --dirpath DIRPATH`   
>     
> `Import Plans into APICS by reading all json files in specified dirpath;`   
>     
> `optional arguments:`   
> `  -h, --help       show this help message and exit`   
> `  -cf CONFIGFILE, --configfile CONFIGFILE config file specifying server, auth, proxy and other details in json format;`    
> `  --dirpath DIRPATH     directory path; All json files from this directory will be imported`    

If any of the APIs have references to gateways or credentials in their policies, then such policies will be in draft mode after import. These should be completed prior to publishing these APIs on the target APIPCS server.


### <a name="other-utility-commands"></a> Other Utility commands

The script bundle comes with few other utiity commands which may be useful for administrative and developer tasks. Given below is a brief overview of all the scripts including the ones discussed above.

- listapis.py – lists all API IDs to the console. Note- nothing is persisted to file system
- listapps.py – lists Application IDs, Gateways defined on API Platform
- listgateways.py – lists Gateway IDs, Gateways defined on API Platform
- export_api_byid – export one API by specifying its API ID
- exportallapis.py – export all APIs from an API Platform
- exportallapplications.py – export all applications from an API Platform
- importapi.py – import one API into API Platform. Requires full path of API metadata json file
- importapis_fromdir.py – import all API from a specified directory to target API Platform
- importapplications_fromdir.py –  import all applications from a specified directory to target API Platform
- importapp.py – import one Application into APi Platform. Takes full path of Application metadata json file as argument
- deleteapi-py – deletes an API when ID specified; Deletes all APIs when no API ID is specified. Useful for cleanup of environment. Use with caution.
- deleteapplication.py – similar to deleteapi.py above. Useful for cleanup tasks. Use with caution

## <a name="repl-interface"></a> REPL interface

The scripts also provide an interactive REPL interface for some of the above operations. The REPL shell can be started by invoking the repl.py and optionally passing the config file as below.

> `python repl.py [-cf CONFIGFILE]`   

The REPL also takes the same common config file as argument as before which contains the details required to connect to and authenticate against the API Platform Cloud service. It defaults to apipcs_config.json when not provided.

**Autonomous APIPCS - sample json config file using oauth**:
> **`apipcs_config.json:`**   
> `{`
> `    "server": "https://host:port/apiplatform" ,`   
> `    "oauth": [],`   
> `    "proxy": {`   
> `        "http": "proxy.xxx.yyy.com:80",`   
> `        "https": "proxy.xxx.yyy.com:80"`   
> `    }`
> `}`

**APICS User Managed - sample json config file using basic auth** :
> **`apipcs_config.json:`**   
> `{   `   
> `    "server": "http://host:port/apiplatform" ,   `   
> `    "auth": ["weblogic"],`   
> `}`   

Starting the REPL   

> `bash-4.1$ python repl.py -cf apipcs_config.json`   
> `done initing repl`   
> `APIPCS: >`   

The following commands are available from the REPL prompt. All commands connect to and execute operations on the API Platform CS server specified in the config json file.

- listapis
- listgateways
- listapps
- exportallapis [–destdir <dirpath>]
- exportallapps [–destdir <dirpath>]
- exportallplans [–destdir <dirpath>]
- importapis_fromdir [–dirpath <dirpath>]
- importapps_fromdir [–dirpath <dirpath>]
- importplans_fromdir [–dirpath <dirpath>]

The commands are self explanatory and they perform the same functions as their script counterparts.   

Here is a sample REPL session extract for reference   

> `>python repl.py -cf apipcs_exportfrom.json`      
> `done initing repl`   
> `APIPCS: >`   
> `APIPCS: > help`   
> `Documented commands (type help ):`   
> `========================================`   
> `help`   
> `Undocumented commands:`   
> `======================`   
> `exit           exportallplans      importplans_fromdir  listgateways`   
> `exportallapis  importapis_fromdir  listapis             listplans`   
> `exportallapps  importapps_fromdir  listapps`   
> `APIPCS: >`   
> `APIPCS: >`   
> `APIPCS: > listapis`   
> `Reading Config from - apipcs_config.json`   
> `Password for APIPCS user- weblogic:`   
> `==============listapis===============`   
> `['ID', 'Name', 'State', 'Created By', 'Created At']`   
> `['104', 'AreaList', 'ALPHA', 'weblogic', '2018-08-17T10:23:05+0000']`   
> `['105', 'AreaListPositive', 'ALPHA', 'weblogic', '2018-08-17T13:01:30+0000']`   
> `['103', '1825API', 'ALPHA', 'weblogic', '2018-07-22T07:01:56+0000']`   
> `***Found 3 APIs defined on the apipcs server`   
> `==============listapis===============`   
 

### <a name="a-note-about-grants"></a> A note about grants

Note that the output of most of the above list*/export* commands depends on the grants available for the user provided in the config json! For instance, if the user has no grants on any APIs, then the exportallapis.py will return no apis although there may be apis configured and visible to other users. 

### <a name="logs"></a> Logs

All script files and the REPL sessions write to log files within the apip-rest-python/logs directory. The log levels are set to default within the script .py files and the repl.py as shown below.

> `logging.basicConfig(filename='logs/repl-apip-session-{:%Y%m%d-%H%M%S}.log'.format(datetime.datetime.now()), filemode='w', format='%(asctime)s %(message)s', **level=logging.INFO**)`

Increasing the log level to debug will write more diagnostic information and raw REST responses to the console and the log files.

## Contributing

This project is not accepting external contributions at this time. For bugs or enhancement requests, please file a GitHub issue unless it’s security related. When filing a bug remember that the better written the bug is, the more likely it is to be fixed. If you think you’ve found a security vulnerability, do not raise a GitHub issue and follow the instructions in our [security policy](./SECURITY.md).

## Security

Please consult the [security guide](./SECURITY.md) for our responsible security vulnerability disclosure process

## License

Copyright (c) 2018, 2023 Oracle and/or its affiliates.

Released under the Universal Permissive License v1.0 as shown at
<https://oss.oracle.com/licenses/upl/>.
