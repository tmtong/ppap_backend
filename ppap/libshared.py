import hashlib
import random
import os
import platform
import re
from datetime import datetime, timedelta
import sys
import pytz
from subprocess import PIPE, Popen
from bson import json_util
from bson.json_util import JSONOptions
from bson.json_util import loads, dumps


import requests
# undetected-chromedriver fails to work with perfs, thus cannot download pdf automatically
# from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions
# from seleniumwire.undetected_chromedriver import Chrome, ChromeOptions

import platform
import os
import re
import shutil, zipfile, time, json, traceback

#################################
hospital = 'TMHv1'

#################################
# Bus related
PACKET_TYPE_REGISTER = 0
PACKET_TYPE_LOGIN1 = 1
PACKET_TYPE_LOGIN2 = 2
PACKET_TYPE_LOGIN3 = 3
PACKET_TYPE_LOGIN4 = 4
PACKET_TYPE_DATA = 5
PACKET_TYPE_REGISTER_RESULT = 6
PACKET_TYPE_FAIL = 7
PACKET_TYPE_CONNECTED = 8
PACKET_TYPE_CHANGEPASSWORD = 9
PACKET_TYPE_PING = 10
PACKET_TYPE_REFRESHTOKEN = 11
PACKET_TYPE_REFRESHREPLY = 12
PACKET_TYPE_LOGOUT = 13
PACKET_TYPE_LOGOUTREPLY = 14
PACKET_TYPE_PINGREPLY = 15
PACKET_TYPE_UNREGISTER = 16

#bufsize = 65536
bufsize = 256
numconsumer = 1

lengthsize = 4
headerlength = lengthsize + 2
busport = 1801
bushost = ""  # set later according to hostid
#########################################

symmetrykey = ""  # used to encrypt data
passwordkey = ""  # key used to hash password and salt for user
lifekey = b'hcMlHuPVHOk3RIH24wFeYABiuP6O20TEqtlZI3SQUS0='  # use to encrypt hn
#################################
dbversion = "v002"
dbipaddr = ""


#################################
def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_timenow():

    now = datetime.now(tz=pytz.timezone('Asia/Hong_Kong'))
    now = now.replace(tzinfo=None)
    # now = datetime(2022, 4, 9, 9, 0, 0)
    return now


def get_stdtimestr(date):
    return date.strftime("%d/%m-%H:%M")
def get_darttimestr(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

def clean_time(t):
    return t.replace(tzinfo=None)


def log(message):
    message = str(message)
    message = message.rstrip()
    if message == "":
        return
    now = get_timenow()
    nowstr = now.strftime("[%d/%m-%H:%M]")
    message = nowstr + " " + message
    print(message)


def read_jsonfromfile(fullpath):
    if os.path.isfile(fullpath):
        options = JSONOptions(tzinfo=None, tz_aware=False)
        with open(fullpath) as f:
            s = f.read()
            if len(s) == 0:
                return []
            d = loads(s, json_options=options)
            # d = json.load(f,  object_hook=json_util.object_hook)

        return d
    else:
        return []


def dump_jsontofile(json_dict):
    fullpath = json_dict['fullpath']
    options = JSONOptions(tzinfo=None, tz_aware=False)
    with open(fullpath, 'w') as outfile:
        # json.dump(json_dict, outfile, indent=4, default=json_util.default, sort_keys=True)
        j = dumps(json_dict, json_options=options, indent=4, sort_keys=True)
        outfile.write(j)
        outfile.flush()



#######################################
## WEB CODE
#######################################

pythondir = ""
if 'PYTHONDIR' in os.environ:
    pythondir = os.environ['PYTHONDIR']
uname = platform.uname()
osname = uname[0]
hostname = uname[1]
if not os.path.exists('./hostid'):
    log("libshared: file hostid not found")
    sys.exit(1)
hostid = open('./hostid', 'r').read().rstrip()
log("libshared: hostid is " + hostid + ", osname is " + osname)



driver_path = None
linuxwebdocspath = None
with open('./sec/terence.epr.sec') as f:
    lines = f.readlines()
    cms_username = lines[0].rstrip()
    cms_password = lines[1].rstrip()
cms_proxy_server = 'proxy.ha.org.hk'
cms_proxy_port = '8080'
ha_proxy_str = 'http://' + cms_username + ':' + cms_password + '@' + cms_proxy_server + ':' + cms_proxy_port
ha_no_proxy_str = 'enquiry.epr.ha.org.hk,ailab-api-trim-app-ailab-corp-web-dev-1.cldpaast71.server.ha.org.hk,tmh.home,ntwc.home,ntwccorpis01,haho-webmail,ha.home,epr.home,tmhicupc022,tmhicupc018,poh-icu05,tmhicupc023,localhost,127.0.0.1,ivm-home.server.ha.org.hk,epr-gateway-cms-epr-prd.cldpaasp61.server.ha.org.hk,epr-gateway-cms-epr-prd.cldpaasp71.server.ha.org.hk,*.server.ha.org.hk'


# For home
if osname == "Linux" and hostid == 'homelaptop':
    download_directory = os.getcwd() + '/temp/'
    bushost = "127.0.0.1"
    busport = 8801
    dbipaddr = "127.0.0.1"
    hostplatform = 'home'
    ha_computer = False



# For production
elif osname == "Linux" and hostid == 'tmhicupc022':
    download_directory = os.getcwd() + '/temp/'
    bushost = "127.0.0.1"
    dbipaddr = "127.0.0.1"
    hostplatform = 'tmhicupc022-docker'
    ha_computer = True


# For TMH
elif osname == "Linux" and hostid == 'tmhicupc018':
    download_directory = os.getcwd() + '/temp/'
    bushost = "127.0.0.1"  # May need tmhicupc018
    dbipaddr = "127.0.0.1"
    hostplatform = 'tmhicupc018-docker'
    ha_computer = True


elif osname == "Linux" and hostid == 'tmhicupc023':
    download_directory = os.getcwd() + '/temp/'
    bushost = "127.0.0.1"  # May need tmhicupc018
    dbipaddr = "127.0.0.1"
    hostplatform = 'tmhicupc018-docker'
    ha_computer = True


# For POH
elif osname == "Linux" and hostid == 'poh-icu05':
    download_directory = os.getcwd() + '/temp/'
    bushost = "127.0.0.1"  # May need tmhicupc018
    dbipaddr = "127.0.0.1"
    hostplatform = 'tmhicupc018-docker'
    ha_computer = True



# cygwin
elif 'cygdrive' in pythondir:
    pythondir = re.sub(r'/cygdrive/(\w)/', r'\1:\\', pythondir)
    pythondir = re.sub(r'/', r'\\', pythondir)
    download_directory = 'C:\\Users\\tmc877\\Documents\\mimo_backend\\temp'
    bushost = "127.0.0.1"
    dbipaddr = "127.0.0.1"
    hostplatform = 'cygwin'  # vscode, windows


else:  # for vs code
    # need to be in downloads, not temp
    download_directory = 'C:\\Users\\tmc877\\Documents\\mimo_backend\\temp'
    bushost = "127.0.0.1"
    dbipaddr = "127.0.0.1"
    hostplatform = 'vscode'


log("libshared: platform is " + hostplatform)



def requests_proxy(internet):
    if ha_computer and internet:
        proxies = {
            'http': ha_proxy_str,
            'https': ha_proxy_str
        }
    else:
        proxies = {
            'http': None,
            'https': None
        }

    return proxies

def requests_get(url, internet, cookies = None, headers = None):
    proxies = requests_proxy(internet)
    return requests.get(url, cookies = cookies, headers = headers, proxies=proxies, verify=False)

def requests_post(url, internet, json_dict, headers = None, cookies = None, files = None):
    proxies = requests_proxy(internet)
    return requests.post(url, cookies = cookies, headers = headers, json = json_dict, proxies=proxies, files = files, verify=False)


def requests_put(url, internet, json_dict, cookies = None, headers = None, files = None):
    proxies = requests_proxy(internet)
    return requests.put(url, headers = headers, cookies = cookies, json = json_dict, proxies=proxies, verify=False, files = files)


#######################################



