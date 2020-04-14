# THIS SCRIPT IS NOT OPERATIONAL YET.
## Stay tuned.
####But you can try it in your lab environment.

This script will automatically enable or disable HyperFlex boost mode on the cluster.

### Requirements
Python 3.8 is needed to run this script.

HyperFlex Boost Mode can be enabled when:
- HXDP 4.02a or higher is running
- HX All-Flash with a CPU with aminimum of 12 cores
- HX All-NVMe with a CPU with aminimum of 16 cores

This script is tested with HXDP 4.0.2a, ESXi 6.7U3 and vCenter 6.7

Use this script only in your lab environment.

If EAM is enabled, this script will SSH into the HX Storage Controller
to shutdown the stCVM.
If EAM is not enabled, you can use the --vceam no parameter.

##### Installation
```
pip install -r requirements.txt
```
##### Usage of the HXboost script:
```
python HXBoost.py -h
usage: HXBoost.py [-h] [--hxip HXIP] [--hxpasswd HXPASSWD] [--hxuser HXUSER]
                  [--vcuser VCUSER] [--vcpasswd VCPASSWD] [--vcip VCIP]
                  [--ucsmuser UCSMUSER] [--ucsmpasswd UCSMPASSWD]
                  [--ucsmip UCSMIP] --hxboost {on,off} [--force FORCE]
                  [--hxtoken HXTOKEN] [--vceam {yes,no}] [--test {true,false}]

*****************   DISCLAIMER   ********************
Please read the readme.txt regarding limitations of this script.
Use this script at your own risk.
To be test this script without change use the argument: --test true 

optional arguments:
  -h, --help            show this help message and exit
  --hxip HXIP           HyperFlex IP Address
  --hxpasswd HXPASSWD   HyperFlex Cluster Password
  --hxuser HXUSER       HyperFlex UserName
  --vcuser VCUSER       vCenter UserName
  --vcpasswd VCPASSWD   vCenter Password
  --vcip VCIP           vCenter IP Address
  --ucsmuser UCSMUSER   UCS-M Username
  --ucsmpasswd UCSMPASSWD
                        UCS-M Password
  --ucsmip UCSMIP       UCS-M IP Address
  --hxboost {on,off}    HyperFlex Boostmode on / off
  --force FORCE         Force power off : on / off
  --hxtoken HXTOKEN     HyperFlex API Token
  --vceam {yes,no}      Is EAM Running
  --test {true,false}   Test the script without doing it. When set to "true"
                        the script will run and not change the vCPUs.
```
Run Example:
This example don't have enough CPU resources. The script will halt.
You see the HX Token and you can use the token as arguments. There is a max of 5 auth within 15 minutes
against the HX Auth API.
```
>python HXBoost.py --hxboost off
*****************   DISCLAIMER   ********************
This script will enable or disable HyperFlex boost mode on a cluster with:
* HXDP 4.0.2a and higher
* All Flash cluster with 12 or more physical cores per CPU
* All NVMe cluster with 16 or more physical cores per CPU.

If you don't have a cluster with the required hardware and software, the script cannot run.

Use this script on your own responsibility. To test the script use the argument: --test true

HyperFlex IP Address: 10.1.1.1
HyperFlex UserName: admin
Please enter the HyperFlex Password:
vCenter IP Address: 10.1.1.2
vCenter UserName: administrator@vsphere.local
Please enter the vCenter Password:
UCS Manager IP: 1.1.1.3
UCS Manager UserName: admin
Please enter the UCS Manager Password:
HX Token:  eyJdbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2Vycy9hZG1pbiIsImV4cCI6MTU4ODQ2MTIwNywidXNlciI6ImFkbWluIiwidG9rZW4iOiIxOSIs
InNjb3BlIjoiUkVBRCxNT0RJRlkiLCJpc3N1ZWRBdCI6MTU4NjkwNjAwNzc2NCwidG9rZW5MaWZlVGltZSI6MTU1NTIwMDAwMCwiaWRsZVRpbWVvdXQiOjE4
MDAwMDAsIndhcm5JZGxlVGltZW91dCI6MTAwMDAsImh5cGVydmlzb3IiOiJoeXBlcnYifQ.4w0U7CHKesnQBVxNuWNPHFj1OmAhDOGNO1kqpiFavAI
HyperFlex Data Platform version is greater than 4.0(2a)
HyperFlex Cluster is Healthy.
This is a HyperFlex All-Flash system
CPU don't have enough cores. Minimum of 12 cores per CPU required.

```
