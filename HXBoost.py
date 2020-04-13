#TODO SSH Shutdown is for ROOT only !

"""
HyperFlex Boost mode Script

This script will enable or disable HyperFlex Boost Mode on you HyperFlex Cluster.
Shutdown of the Controller VM via the vCenter API is NOT possible when
ESXi agent manager (EAM) is controlling the storage controllers
.
The script ssh into the controller to shutdown the controller. You will have to provide
the root password for the Controller VM when it wants to SSH to it.

This solution is tested on HyperFlex 4.0.2a and vCenter 6.7 with vSphere 6.7
Earlier HXDP of 4.0.2a are not supported.

You can change this script to have it working anyway you want.
THIS SCRIPT IS NOT IDIOT PROOF

--FORCE ON will Power Off the HX CVM not gracefully! Use with Caution.
--test True will test the script, ignore the warnings and it WON'T update the stCVM.

Author: Joost van der Made
Email: awesome@iamjoost.com

IAmJoost.com

Copyright (c) 2018 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at:

             https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

##################
# Packages #######
##################
import hxdef

import argparse
import sys
import getpass
import urllib3
import os
import textwrap
import vcenterdef as vc
import json
import time
import subprocess

hxsupportedversion = 4.02
urllib3.disable_warnings()  # Disable warnings when you're not working with certificates.


##################
# Functions ######
##################

# -------------------- SSH -----------------------
# SSH into HX Controller and shutdown the system.
def shutdown_controller(cip):
    my_timeout = 100  # Seconds
    p = subprocess.Popen(['ssh', 'root@' + cip, ' shutdown', '-P', 'now'])
    try:
        p.wait(my_timeout)
        ssh_status = True
    except subprocess.TimeoutExpired:
        p.kill()
        print('Timeout ! Please provide the password on time.')
        ssh_status = False

    return ssh_status


# Getting the parameters
def check_arg(args=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''
         *****************   DISCLAIMER   ********************
         Please read the readme.txt regarding limitations of this script.
         Use this script at your own risk.
         To be test this script without change use the argument: --test true 
         '''))
    parser.add_argument('--hxip',
                        help='HyperFlex IP Address'
                        )
    parser.add_argument('--hxpasswd',
                        help='HyperFlex Cluster Password'
                        )
    parser.add_argument('--hxuser',
                        help='HyperFlex UserName')
    parser.add_argument('--vcuser',
                        help='vCenter UserName')
    parser.add_argument('--vcpasswd',
                        help='vCenter Password'
                        )
    parser.add_argument('--vcip',
                        help='vCenter IP Address'
                        )
    parser.add_argument('--ucsmuser',
                        help='UCS-M Username')

    parser.add_argument('--ucsmpasswd',
                        help='UCS-M Password'
                        )
    parser.add_argument('--ucsmip',
                        help='UCS-M IP Address'
                        )
    parser.add_argument('--hxboost',
                        choices=['on','off'],
                        help='HyperFlex Boostmode on / off',
                        required='True'
                        )
    parser.add_argument('--force',
                        help='Force power off : on / off',
                        default='off')
    parser.add_argument('--hxtoken',
                        help='HyperFlex API Token'
                        )
    # parser.add_argument('--vceam',
    #                     choices=['yes','no'],
    #                     default='yes',
    #                     help='Is EAM Running'
    #                     )
    parser.add_argument('--test',
                        choices=['true','false'],
                        default='false',
                        help='Test the script without doing it. When set to "true" the script will run and not change the vCPUs.'
                        )
    return parser.parse_args(args)


###########################################
################## MAIN ###################
###########################################
L_hx = []

args = check_arg(sys.argv[1:])

print("*****************   DISCLAIMER   ********************")
print("This script will enable or disable HyperFlex boost mode on a cluster with:")
print("* HXDP 4.0.2a and higher")
print("* All Flash cluster with 12 or more physical cores per CPU")
print("* All NVMe cluster with 16 or more physical cores per CPU.")
print()
print("If you don't have a cluster with the required hardware and software, the script cannot run.")
print()
print("Use this script on your own responsibility. To test the script use the argument: --test true")
print()

hxip = args.hxip
hxuser = args.hxuser
hxpasswd = args.hxpasswd
vcuser = args.vcuser
vcip = args.vcip
vcpasswd = args.vcpasswd
hxtoken = args.hxtoken
ucsmip = args.ucsmip
ucsmuser = args.ucsmuser
ucsmpasswd = args.ucsmpasswd

if args.hxip == None:
    hxip = input("HyperFlex IP Address: ")

if args.hxuser == None:
    hxuser = input("HyperFlex UserName: ")

if args.hxpasswd == None:
    hxpasswd = getpass.getpass("Please enter the HyperFlex Password: ")

if args.vcip == None:
    vcip= input("vCenter IP Address: ")

if args.vcuser == None:
    vcuser = input("vCenter UserName: ")

if args.vcpasswd == None:
    vcpasswd = getpass.getpass("Please enter the vCenter Password: ")

if args.ucsmip == None:
    ucsmip = input("UCS Manager IP: ")

if args.ucsmuser == None:
    ucsmuser = input("UCS Manager UserName: ")

if args.ucsmpasswd == None:
    ucsmpasswd = getpass.getpass("Please enter the UCS Manager Password: ")

if args.hxboost == 'on':
    enable_boost_mode = True
else:
    enable_boost_mode = False

# if args.vceam == 'no':
#     vceam = False
# else:
#     vceam = True

if args.test == 'true':
    testing = True
    print ("This script will run in Testing mode. VMs will not be powered off. HX Boost will not be enabled.")
else:
    testing = False

if args.hxtoken == None:
    # Get the Token.
    hxbearer = hxdef.get_hxtoken(hxip, hxuser, hxpasswd).json()
    hxtoken = hxbearer['access_token']
    print ('HX Token: ',hxtoken)

# Get HX CLuster UUID
clusteruuid = hxdef.get_hxuuid(hxip, hxtoken)

# Get the HX Version
hxversion = hxdef.get_hxversion(hxip, hxtoken, clusteruuid)

hxversion2 = hxversion[:3]
hxversion2 = hxversion2 + hxversion[4]

if float(hxversion2) >= hxsupportedversion:
    print("HyperFlex Data Platform version is greater than 4.0(2a)")
else:
    print("Please upgrade HXDP to version 4.0(2a) first")
    hxdef.hxexit(testing)

# Is HyperFLex cluster Healty ?
hxready = hxdef.get_hxstatus(hxip, hxtoken, clusteruuid)

if hxready is False:
    print('HyperFlex Cluster is NOT HEALTHY!')
    print('Aborting this program.')
    os._exit(1)
else:
    print("HyperFlex Cluster is Healthy.")

    # Get list with serial numbers
    L_hx = hxdef.get_hx_ser(hxip, hxtoken)

    # Get UCS-M Info
    from ucsmsdk.ucshandle import UcsHandle

    handle = UcsHandle(ucsmip, ucsmuser, ucsmpasswd)
    handle.login()

    rack_servers = handle.query_classid("computeRackUnit")

    x = 0
    for node in L_hx:
        for compute in rack_servers:
            if compute.serial == node[1]:
                L_hx[x].extend([int(compute.num_of_cores_enabled) / int(compute.num_of_cpus)])
                hxmodel = hxdef.hx_in_list(compute.model)
                # hxmodel[0] = 1 for All Flash, 2 for All NVMe
                # hxmodel[1] = Number of cores needed.
                if hxmodel[0] == 1:
                    print ("This is a HyperFlex All-Flash system")
                if hxmodel[0] == 2:
                    print ("This is a HyperFlex All-NVMe system")

                if hxmodel[0] >= 1:
                    CoresPerCPU = int(compute.num_of_cores_enabled) / int(compute.num_of_cpus)

                    if CoresPerCPU < hxmodel[1]:
                        print("CPU don't have enough cores. Minimum of",hxmodel[1],"cores per CPU required.")
                        hxdef.hxexit(testing)
                else:
                    print("This is not an HX All-Flash or HX All-NVMe cluster")
                    hxdef.hxexit(testing)

                x = x + 1

    handle.logout()
    print("This is a HyperFlex All-Flash or All-NVMe Cluster.")

print('Please Have Patience and dont abort this script.')
vcsession = vc.get_vc_session(vcip, vcuser, vcpasswd)

# Get all the VMs
vms = vc.get_vms(vcip, vcsession)

# Put the VM in JSON format
vm_response = json.loads(vms.text)
json_data = vm_response["value"]
counter = 0

for vm in json_data:
    text = vm.get("name")[0:8]
    # print (text)
    if text == "stCtlVM-":
        # Find name in L_hx table.
        # print (vm.get('name')[8:19])
        for x in L_hx:
            if x[1] == vm.get('name')[8:19]:
                x.append(vm.get("name"))
                x.append(vm.get("vm"))
                x.append(False)


# Structure of L_hx
# [['huuid','SerialNumber Node','HX Model','Node Status','HX CVM IP','VM name','VM ID','Upgraded True/False'],...[]]

vceam = True

for node in L_hx:
    vmid = node[7]
    if node[8] == False:
        #TODO Loop for all servers

        hxserial=node[1]
        if vceam is True:
            if not vc.eam_enabled(vcip,vcuser,vcpasswd,vcsession,hxserial):
                vceam = False

        textcpu = vc.get_cpu_vm(vcip, node[7], vcsession)
        cpu_response = json.loads(textcpu.text)
        cpu_json_data = cpu_response["value"]
        cpucount = (cpu_json_data['count'])
        # Is system All Flash or All NVMe ?
        if (cpucount == hxmodel[1]) and (enable_boost_mode is True):
            print("HyperFlex Boost is already Enabled.")
            os._exit(1)

        if (cpucount == (hxmodel[1]-4)) and (enable_boost_mode is False):
            print ("HyperFlex Boost is not configured. You cannot disable it.")
            os._exit(1)

        vm_status_power = ""
        if testing:
            print("Fake power off of the Storage Controller.")

        else:
            if args.force == 'on':
                vc.poweroff_vm(node[7], vcip, vcsession)
            else:
                if vceam is False:
                    vc.shutdownvm(vcip, vmid,vcsession)
                else:
                    print('ESXi Agent Manager is running for HyperFLex:')
                    print()
                    print("You can remove ESXi Agent Manager for HyperFlex by removing the HX Cluster in vCenter")
                    print("And reregister the HyperFlex cluster to vCenter again.")
                    print()
                    print('You will need to provide the HyperFlex Controller VM passwords when the script is running')
                    print('This process will take about 5 min per HyperFlex Node')
                    print()
                    if testing == True:
                        print("Script is going on. Normally you will see a question here.")
                    else:
                        answer = input('Enter yes if you want to continue : ')
                        if answer != 'yes':
                            os._exit(1)
                    ssh_executed = False
                    while ssh_executed == False:
                        input('You will have 100 seconds to provide the root password. Hit Enter to Login to HX CVM: ')
                        ssh_executed = shutdown_controller(node[4])

        print('Waiting for shutdown of : ' + node[6])
        while (vm_status_power != "POWERED_OFF") and testing == False:
            print('.', end='')
            # Get VM Info Again.
            vmstatus = vc.get_power_vm(vcip, node[7], vcsession)
            vm_status = json.loads(vmstatus.text)
            vm_status_power = vm_status["value"]["state"]

            if not testing:
                time.sleep(10)

        print('VM is Powered Off')

        # Change CPU
        if testing:
            print("Fake changing vCPUs of Storage Controller.")
        else:
            if enable_boost_mode:
                vc.update_cpu_vm(vcip, node[7], cpucount + 4, vcsession)
            else:
                vc.update_cpu_vm(vcip, node[7], cpucount - 4, vcsession)

            node[8] = True

            # Power On VM
            vc.poweron_vm(vcip, node[7], vcsession)

        # Wait until Powered On
        vm_status_power = "Hello"
        print('Waiting for Powered On of ' + node[6])
        print('Please Have Patience and dont abort this script.')
        while vm_status_power != "POWERED_ON":
            # Read VM again
            vmstatus = vc.get_power_vm(vcip, node[7], vcsession)
            vm_status = json.loads(vmstatus.text)
            vm_status_power = vm_status["value"]["state"]

            if not testing:
                time.sleep(10)
        print('VM ' + node[6] + ' is Powered On')

        # If HX Healthy ?
        print('Waiting for HyperFlex Cluster to become Healthy')

        if not testing:
            time.sleep(30)
        hxready = hxdef.get_hxstatus(hxip, hxtoken, clusteruuid)
        while not hxready:
            print('.', end='')
            if not testing:
                time.sleep(10)
            hxready = hxdef.get_hxstatus(hxip, hxtoken, clusteruuid)
        # input("Verify if the HX Cluster is really Healthy !!! Press Enter to continue...")

        print('HyperFlex is Healthy again.')
        print('We are repeating these steps until all HX CVM are reconfigured.')

print()
if enable_boost_mode is True:
    print("Configure HyperFlex Boost Mode is now finished.")
else:
    print('Disable HyperFlex Boost Mode is now finished.')
