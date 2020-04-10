"""
This script will enable or disable HyperFlex Boost Mode on you HyperFlex Cluster.
Shutdown of the Controller VM via the vCenter API is NOT possible !
ESXi agent manager is controlling it.
The script ssh into the controller to shutdown the controller. Herefor you will have to provide
the root password for the Controller VM.

This solution is tested on HyperFlex 4.0.2a and vCenter 6.7 with vSphere 6.7

You can change this script to have it working anyway you want.
THIS SCRIPT IS NOT IDIOT PROOF

--FORCE ON will Power Off the HX CVM !

SSH has a timeout of 120 Sec. When you don't fill in the password on time, you will hit this timeout and the script won't work correctly.

Author : Joost van der Made 2020
IAmJoost.com

"""
import hxdef
import vcenterdef as vc
import argparse
import sys
import getpass
import urllib3
import os

# -------------------- SSH -----------------------

# SSH into HX Controller and shutdown the system.
def shutdown_controller(cip):
    # os.system('ssh root@'+cip+' shutdown -P now')
    my_timeout = 100  # Seconds
    # os.system('ssh root@'+cip+' shutdown -P now')
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
    parser = argparse.ArgumentParser(description='Enable/Disable HyperFlex Boost Mode')
    parser.add_argument('--hxip',
                        help='HyperFlex ip'
                        )
    parser.add_argument('--hxpasswd',
                        help='HyperFlex Cluster Password'
                        )
    parser.add_argument('--hxuser',
                        help='hx user name')
    parser.add_argument('--vcuser',
                        help='hx user name',
                        default='administrator@vsphere.local')
    parser.add_argument('--vcpasswd',
                        help='vCenter Password'
                        )
    parser.add_argument('--vcip',
                        help='vCenter ip'
                        )
    parser.add_argument('--ucsmuser',
                        help='UCS-M user name',
                        default='admin')
    parser.add_argument('--ucsmpasswd',
                        help='UCS-M Password'
                        )
    parser.add_argument('--ucsmip',
                        help='UCS-M ip'
                        )
    parser.add_argument('--hxboost',
                        help='Hyper Flex Boostmode on / off',
                        default='on')
    parser.add_argument('--force',
                        help='Force power off : on / off',
                        default='off')
    parser.add_argument('--hxtoken',
                        help='HX API Token'
                        )
    parser.add_argument('--test',
                        help='Test the script without doing it. true = testing'
                        )
    return parser.parse_args(args)

################## MAIN ###################
urllib3.disable_warnings() #Disable warnings when you're not working with certificates.

#TODO Cisco License ? See MichZimm

#TODO Start with GetAccessToken

# TODO Get HX Serial Numbers

###########################

args = check_arg(sys.argv[1:])

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

if args.test == 'true':
    testing = True
else:
    testing = False

if args.hxtoken == None:
    # Get the Token.
    hxbearer = hxdef.get_hxtoken(hxip, hxuser, hxpasswd).json()
    hxtoken = hxbearer['access_token']

#Get HX CLuster UUID
clusteruuid = hxdef.get_hxuuid(hxip, hxtoken)

# Is HyperFLex cluster Healty ?
hxready = hxdef.hxstatus(hxip, hxtoken, clusteruuid)
print ("HyperFlex Cluster is Healthy.")
if hxready == True:


    #Get list with serial numbers
    L_hx = hxdef.hx_cvm_ser(hxip, hxtoken)

    # TODO Get UCS-M Info
    from ucsmsdk.ucshandle import UcsHandle

    handle = UcsHandle("10.1.15.9", "admin", "Hyp3rFlex123!")
    handle.login()

    rack_servers = handle.query_classid("computeRackUnit")

#    L_hx[0].extend(['Hello'])
    x = 0
    for node in L_hx:
        #
        for compute in rack_servers:
            if compute.serial == node[0]:
                print ("Serials Match: ",compute.serial)

                L_hx[x].extend([compute.model])
                L_hx[x].extend([int(compute.num_of_cores_enabled)/int(compute.num_of_cpus)])

                if hxdef.hx_in_list(compute.model) == 1 or hxdef.hx_in_list(compute.model) == 2:
                    pass
                else:
                    print ("This is not an HX All-Flash or HX All-NVMe cluster")
                    hxdef.hxexit(testing)

                if int(compute.num_of_cores_enabled)/int(compute.num_of_cpus) >= 12:
                    print ("Over 12 Cores. ",compute.num_of_cores_enabled)
                else:
                    print("CPU don't have enough cores.")
                    hxdef.hxexit(testing)
                x = x + 1


    handle.logout()
    os._exit(1)

    print('HyperFlex is Healthy.')
    print('You will still need to provide the HyperFlex Controller VM passwords when the script is running')
    print('')
    print('There is no check which HyperFLex cluster you are using.')
    print('Only HX All-Flash and HX All-NVMe are supported')
    print('HyperFlex is NOT supported')
    print()
    print('For HyperFlex Boost Mode your CPU needs to have more cores than the new values')
    print('HX All-Flash -> 12 cores per CPU.')
    print('HX All-NVMe -> 16 cores per CPU')
    print('')
    print('This process will take about 5 min per HyperFlex Node')
    print(' ')
    answer = input('Enter yes if you want to continue : ')
    if answer != 'yes':
        exit()

else:
    print('HyperFlex Cluster is NOT HEALTHY!')
    print('Aborting this program.')
    exit()


vcsession = vc.get_vc_session(vcip, vcuser, vcpasswd)

# Get all the VMs
vms = get_vms(vcip)

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
            if x[0] == vm.get('name')[8:19]:
                x.append(vm.get("name"))
                x.append(vm.get("vm"))
                x.append(False)

            # Structure of L_hx
# [['SerialNumber Node','HX CVM IP','VM name','VM ID','Upgraded True/False'],...[]]
# print (L_hx)


for node in L_hx:
    # print (node)
    # print (node[4])

    if node[4] == False:
        # Is powered of ?
        #             vm_status_power = vm.get("power_state")
        vm_status_power = ""
        if args.force == 'on':
            poweroff_vm(node[3], vcip)
        else:
            ssh_executed = False
            while ssh_executed == False:
                input('You will have 100 seconds to provide the root password. Hit Enter to Login to HX CVM: ')
                ssh_executed = shutdown_controller(node[1])

        print('Waiting for shutdown of : ' + node[2])
        print('Please Have Patience and dont abort this script.')
        while vm_status_power != "POWERED_OFF":
            print('.')
            # Get VM Info Again.
            # vmstatus = get_power_vm (vcip, vm.get('vm'))

            vmstatus = get_power_vm(vcip, node[3])
            vm_status = json.loads(vmstatus.text)
            vm_status_power = vm_status["value"]["state"]

            time.sleep(10)

        print('VM is Powered Off')

        # Get number of cpu

        # textcpu = get_cpu_vm(vcip, vm.get('vm'))
        textcpu = get_cpu_vm(vcip, node[3])

        cpu_response = json.loads(textcpu.text)
        cpu_json_data = cpu_response["value"]
        cpucount = (cpu_json_data['count'])

        # Change CPU

        if enable_boost_mode:
            update_cpu_vm(vcip, node[3], cpucount + 4)
        else:
            update_cpu_vm(vcip, node[3], cpucount - 4)

        node[4] = True

        # Power On VM
        poweron_vm(vcip, node[3])

        # Wait until Powered On
        vm_status_power = "Hello"
        print('Waiting for Powered On of ' + node[2])
        print('Please Have Patience and dont abort this script.')
        while vm_status_power != "POWERED_ON":
            # Read VM again
            vmstatus = get_power_vm(vcip, node[3])
            vm_status = json.loads(vmstatus.text)
            vm_status_power = vm_status["value"]["state"]

            time.sleep(10)
        print('VM ' + node[2] + ' is Powered On')

        # If HX Healthy ?
        print('Waiting for HyperFlex Cluster to become Healthy')
        time.sleep(60)
        # "healthState": "UNKNOWN"
        hxready = hxstatus(hxip, hxbearer['access_token'], clusteruuid)
        while not hxready:
            print('.')
            time.sleep(10)
            hxready = hxstatus(hxip, hxbearer['access_token'], clusteruuid)
        # input("Verify if the HX Cluster is really Healthy !!! Press Enter to continue...")

        print('HyperFlex is Healthy again.')
        print('We are repeating these steps until all HX CVM are reconfigured.')

print(' ')
if enable_boost_mode == True:
    print("Configure HyperFlex Boost Mode is now finished.")
else:
    print('Disable HyperFlex Boost Mode is now finished.')