# ---------------------- VMware vCenter ----------------------
import requests
import json
from pyVim import connect
from pyVmomi import vim, vmodl
import ssl



# Authenticate to vCenter
def get_vc_session(vcip, username, password):
    s = requests.Session()
    s.verify = False
    s.post('https://' + vcip + '/rest/com/vmware/cis/session', auth=(username, password))
    return s


# Get all VM's running on the vcenter.
def get_vms(vcip,s):
    vms = s.get('https://' + vcip + '/rest/vcenter/vm')
    return vms

def get_cluster_id(vcip,s):
    #TODO Return multiple clusters ?

    vms = s.get('https://' + vcip + '/rest/vcenter/cluster')
    vm_response = json.loads(vms.text)
    json_data = vm_response["value"]
    #print (json_data)
    L=[]
    for x in json_data:
        L.append(x["cluster"])

    #print ("List: ",L)

    #cluster_id = json_data[0]["cluster"]

    return L

def getURL():
    cmd = ['/bin/stcli', '--raw', 'cluster', 'info']
    out = Popen(cmd, stderr=STDOUT, stdout=PIPE)
    data = out.communicate()[0]
    clusterInfo = json.loads(data)
    return clusterInfo['config']['vCenterURL'], clusterInfo['config']['vCenterClusterId']

def prompt(message, inputType):

    while True:
        t = input(message)
        if t != '':
            if inputType == 'ip':
                regex = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|' \
                        '25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|'\
                        '2[0-4][0-9]|25[0-5])$'
                result = re.match(regex, t)
                if result:
                    break
                else:
                    print('Not a valid IP')
            else:
                break
        else:
            print('Field cannot be empty')
    return t

def eam_enabled(vcip,vcsession,hxserial):
    ###########################################################################
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()

    si = None
    stCtlVMName = 'STCTLVM-'

    # try:
    #     vc_url, cluster_id = getURL()
    # except:
    #     vc_url = '10.1.15.12'  # prompt("Enter vCenter URL:  ", 'text')
    #     # TODO Find CLuster ID
    #     cluster_id = 'domain-c336'  # prompt("Enter vCenter Cluster DomainID (mob):  ", 'text')
    #     # cluster_id = 'group-d1'  # prompt("Enter vCenter Cluster DomainID (mob):  ", 'text')
    #     print("Connecting to VC {}".format(vc_url))

    while True:

        vc_url = vcip #print("vCenter URL: {}".format(vc_url))
        vc_user = 'administrator@vsphere.local'  # prompt("Enter vCenter username (user@domain): ", 'text')
        vc_pwd = 'Hyp3rFlex123!'  # getpass.getpass('vCenter Password: ')

        try:
            si = connect.SmartConnect(host=vc_url, user=vc_user, pwd=vc_pwd)
        except vmodl.MethodFault as e:
            print("Could not connect to vCenter - {}".format(e.msg))
        if si is not None:
            break
        else:
            os._exit(1)


    #vcsession = vc.get_vc_session(vc_url, vc_user, vc_pwd)

    cluster_id = get_cluster_id(vc_url, vcsession)
    print(cluster_id)

    # print (si.content.rootFolder)

    container = si.content.viewManager.CreateContainerView(si.content.rootFolder, [vim.ClusterComputeResource], True)
    for c in container.view:
        # print (c._moId)
        # if c._moId == cluster_id:
        if c._moId in cluster_id:
            for host in c.host:
                # print (host)
                stCtlVMs = [v for v in host.vm if stCtlVMName in v.name.upper()]
                if len(stCtlVMs) > 1:
                    raise Exception("More than one stCtlVMs found: %s" % stCtlVMs)

                eamStatus = 'Yes' if stCtlVMs[0].summary.config.managedBy else 'No'
                print("{} - EAM Enabled: {}".format(stCtlVMs[0].name, eamStatus))
    if eamStatus == "No":
        return False
    else:
        return True


# Shutdown Guest OS VM <- IS NOT WORKING If EAM is enabled. How to check ???

def shutdownvm(vcip, vmid,s):
    s.post('https://' + vcip + '/rest/vcenter/vm/' + vmid + '/guest/power?action=shutdown')


# Power On the VM
def poweron_vm(vcip, vmid,s):
    s.post('https://' + vcip + '/rest/vcenter/vm/' + vmid + '/power/start')


# Power Off a VM. (NOT USED)
def poweroff_vm(vmid, vcip,s):
    s.post('https://' + vcip + '/rest/vcenter/vm/' + vmid + '/power/stop')


# Get CPU of VM
def get_cpu_vm(vcip, vmid,s):
    cpuvm = s.get('https://' + vcip + '/rest/vcenter/vm/' + vmid + '/hardware/cpu')
    return cpuvm


# Get Status of VM
def get_power_vm(vcip, vmid,s):
    vmpower = s.get('https://' + vcip + '/rest/vcenter/vm/' + vmid + '/power')
    return vmpower


# Get IP of VM
def get_vm_ip(vcip, vmid,s):
    vmipget = s.get('https://' + vcip + '/rest/vcenter/vm/' + vmid + '/guest/identity')
    vm_response = json.loads(vmipget.text)
    json_data = vm_response["value"]
    vmip = json_data.get("ip_address")

    return vmip


# Add or subtract number of CPU
def update_cpu_vm(vcip, vmid, cpu_value,s):
    payload = {
        "spec": {
            "hot_remove_enabled": False,
            "count": cpu_value,
            "hot_add_enabled": False,
            "cores_per_socket": 1

        }
    }

    header = {
        "Content-type": "application/json"
    }
    s.patch('https://' + vcip + '/rest/vcenter/vm/' + vmid + '/hardware/cpu', data=json.dumps(payload), headers=header)
