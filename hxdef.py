"""
Here are just some functions I am using for different HyperFlex REST API Scripts.

This solution is tested on HyperFlex 4.0.2a.

You can change this script to have it working anyway you want.
THIS SCRIPT IS NOT IDIOT PROOF

Author : Joost van der Made 2020
IAmJoost.com
"""

import requests
import json
import os
from HXBoostSettings import *

# What model is the HyperFlex node ?
# 1 = All Flash
# 2 = All NVMe
# 0 = The rest.

def hx_in_list(hxmodel):
    #hxflashcores = 12
    #hxnvmecores = 16
    #hxallflash = [['HXAF220C-M5SX', 'HXAF240C-M5SX'],hxflashcores]
    #hxallnvme =[['HXAF220C-M5SN'],hxnvmecores]
    if hxmodel in hxallflash[0]:
        return 1,hxallflash[1]
    else:
        if hxmodel in hxallnvme[0]:
            return 2,hxallnvme[1]
    return 0,0

# HX Exit if not testing
def hxexit(testing):
    if testing == True:
        print ("Testing is enabled. Continue the script.")
    else:
        os._exit(1)

# Generate HyperFlex API Token.
def get_hxtoken(hxip, hxuser, hxpasswd):
    payload = {'username': hxuser, 'password': hxpasswd}

    headers = {
        "Content-type": "application/json",
        "Accept": "application/json"}

    url = 'https://' + hxip + '/aaa/v1/auth?grant_type=password'

    hxauth = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    if hxauth.status_code == 201:
        return (hxauth)
    else:
        print ("There was an error getting the Token.")
        print ("You should be on HyperFlex Data Platform 4.0 or Higher !")
        print("HTTP Error Code: ",hxauth.status_code)
        print ("Message: ",hxauth.text)

        os._exit(1)

# Get HyperFlex UUID of the Cluster
def get_hxuuid(hxip, hxtoken):
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = 'https://' + hxip + '/coreapi/v1/clusters'
    response = requests.get(url, headers=headers, verify=False)
    for item in response.json():
        hxuuid = item['uuid']

    return hxuuid

# Get the HyperFlex Version
#https://10.1.15.13/coreapi/v1/clusters/1525837625288471367%3A5577340641586887964/about
def get_hxversion(hxip, hxtoken,hxuuid):
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = 'https://' + hxip + '/coreapi/v1/clusters/' + hxuuid + '/about'
    response = requests.get(url, headers=headers, verify=False)
    hx_response = json.loads(response.text)
    hxversion = hx_response['displayVersion']

    return hxversion

#Get the Datastores from HyperFLex Cluster
def get_ds(hxip,hxtoken,hxuuid):
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = "https://" + hxip + "/coreapi/v1/clusters/" + hxuuid + "/datastores"
    return(requests.get(url, headers=headers, verify=False))

#Create Datastore on the HyperFlex Cluster.
def create_ds(hxip,hxtoken,hxuuid,dsname,dssize,blocksize):
    payload = {"name": dsname, "sizeInBytes": dssize, "dataBlockSizeInBytes": blocksize}
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = "https://" + hxip + "/coreapi/v1/clusters/" + hxuuid + "/datastores"
    hxds = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    if hxds.status_code == 200:
        return True
    else:
        print ("There was an error")
        print ("Message: ",hxds.text)
        os._exit(1)

#Delete a Datastore on the HyperFLex Cluster
def delete_ds(hxip,hxtoken,hxuuid,dsuuid):
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = "https://" + hxip + "/coreapi/v1/clusters/" + hxuuid + "/datastores/"+dsuuid
    hxds = requests.delete(url, headers=headers, verify=False)
    if hxds.status_code == 200:
        return True
    else:
        print ("There was an error")
        print ("Message: ",hxds.text)
        os._exit(1)

#HyperFlex Status
# Is the HyperFlex Cluster Healthy ?
def get_hxstatus(hxip, hxtoken, clusteruuid):
    # https://10.1.15.13/coreapi/v1/clusters/6326623497596061830%3A7687534548531484521/status

    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}
    # https://10.1.15.13/coreapi/v1/clusters/6326623497596061830%3A7687534548531484521/health
    url = 'https://' + hxip + '/coreapi/v1/clusters/' + clusteruuid + '/health'
    response = requests.get(url, headers=headers, verify=False)

    hx_response = json.loads(response.text)
    # print (hx_response)
    json_data = hx_response['resiliencyDetails']
    # print (json_data)
    hxhealthmessage = json_data.get("messages")
    # print (hxhealthmessage[0])
    if hxhealthmessage[0] != 'Storage cluster is healthy. ':
        # print ('Cluster is Unhealthy')
        return False
    # else:
    #    print ('Cluster Healthy.')

    return True

# Get Controller IP
def get_hx_stcvm (hxip,hxtoken, huuid):
    # https://10.1.15.13/coreapi/v1/hypervisor/hosts/62d62a1d-14fb-1c46-b44b-f0025d92cea5/controllervm
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = 'https://' + hxip + '/coreapi/v1/hypervisor/hosts/' + huuid + '/controllervm'

    response = requests.get(url, headers=headers, verify=False)
    hxitem = response.json()
    hxstcvm = hxitem['mgmtIp']['ip']
    return hxstcvm



# Get the serial, model, huuid of the nodes
def get_hx_ser(hxip,hxtoken):
    # https://10.1.15.13/coreapi/v1/hypervisor/hosts
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = 'https://' + hxip + '/coreapi/v1/hypervisor/hosts'

    response = requests.get(url, headers=headers, verify=False)
    c = 0
    L = []

    for hxitem in response.json():

        huuid = hxitem['identity']['uuid']
        hxmodel = hxitem['modelNumber']
        hxser = hxitem['serialNumber']
        hxstatus = hxitem['status']
        L.append([])
        L[c].append(huuid)
        L[c].append(hxser)
        L[c].append(hxmodel)
        L[c].append(hxstatus)
        # Get Controller IP.
        L[c].append(get_hx_stcvm(hxip,hxtoken,huuid))
        c = c + 1

    return L

# Get the Serial numbers of the nodes.
def get_hx_ser_old(hxip, hxtoken,hxuuid):
    # https://10.1.15.13/coreapi/v1/clusters/1525837625288471367%3A5577340641586887964/about
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = 'https://' + hxip + '/coreapi/v1/clusters/' + hxuuid + '/about'

    response = requests.get(url, headers=headers, verify=False)
    c = 0
    hxseriallist = []

    hx_response = json.loads(response.text)
    hxserial = hx_response['serialNumber']
    hxlist = hxserial.split(",")

    for x in hxlist:
        hxseriallist.append([])
        hxseriallist[c].append(x)
        c = c + 1

    return hxseriallist

def hx_cvm_ip(hxip, hxtoken,nuuid):
    # https://10.1.15.13/coreapi/v1/hypervisor/controllervms


    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = 'https://' + hxip + '/coreapi/v1/hypervisor/controllervms'

    hxstcvm = requests.get(url, headers=headers, verify=False)
    counter = 0
    L = []

    for hxitem in hxstcvm.json():
        #hxser = (hxitem['serialNumber'])
        #hxcvmip = (hxitem['nodes']['A']['host']['stctlvm']['mgmtNetworkIp'])  # ['host']['ip']['addr']
        hxcvmip = hxitem['mgmtIp']['ip']
        L.append([])
        #L[counter].append(hxser)
        L[counter].append(hxcvmip)
        counter = counter + 1

    return L
