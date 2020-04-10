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

# What model is the HyperFlex node ?
# 1 = All Flash
# 2 = All NVMe
# 0 = The rest.

def hx_in_list(hxmodel):
    hxallflash = ['HXAF220C-M5SX', 'HXAF240C-M5SX']
    hxallnvme =['HXAF220C-M5SN']
    if hxmodel in hxallflash:
        return 1
    else:
        if hxmodel in hxallnvme:
            return 2
    return 0

# HX Exit if not testing
def hxexit(testing):
    if testing == True:
        print ("Testing is enabled. Continue the script.")
    else:
        os._exit(1)

# Generate HyperFlex API Token.
def get_hxtoken(hxip, hxuser, hxpasswd):
    payload = {'username': hxuser, 'password': hxpasswd, 'client_id': 'HxGuiClient', 'client_secret': 'Sunnyvale',
               'redirect_uri': 'http://localhost:8080/aaa/redirect/'}

    headers = {
        "Content-type": "application/json",
        "Accept": "application/json"}

    url = 'https://' + hxip + '/aaa/v1/auth?grant_type=password'

    hxauth = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    if hxauth.status_code == 201:
        return (hxauth)
    else:
        print ("There was an error getting the Token. Please try again in 15 minutes")
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
def hxstatus(hxip, hxtoken, clusteruuid):
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


# Get the Controller VM IP and serial number via HyperFlex API.
def hx_cvm_ser(hxip, hxtoken):
    # https://10.1.15.13/coreapi/v1/hypervisor/controllervms

    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + hxtoken}

    url = 'https://' + hxip + '/rest/appliances'

    hxstat = requests.get(url, headers=headers, verify=False)
    counter = 0
    L = []

    for hxitem in hxstat.json():
        hxser = (hxitem['serialNumber'])
        hxcvmip = (hxitem['nodes']['A']['host']['stctlvm']['mgmtNetworkIp'])  # ['host']['ip']['addr']
        L.append([])
        L[counter].append(hxser)
        L[counter].append(hxcvmip)
        counter = counter + 1

    return L

