# THIS SCRIPT IS NOT OPERATIONAL YET.
## Stay tuned.
####But you can try it in your lab environment.

This script will automatically enable or disable HyperFlex boost mode on the cluster.

### Requirements
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