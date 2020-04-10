# ---------------------- VMware vCenter ----------------------
import requests

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


# Shutdown Guest OS VM <- IS NOT WORKING If EAM is enabled. How to check ???

def shutdownvm(vcip, vmid,s):
    s.post('https://' + vcip + '/rest/vcenter/vm/' + vmid + '/guest/power?action=shutdown')
    # Todo failure or not ?


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
