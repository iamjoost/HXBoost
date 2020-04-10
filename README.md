# THIS SCRIPT IS NOT OPERATIONAL YET.
## Stay tuned.

This script will automatically enable or disable HyperFlex boost mode on the cluster.

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
                  [--ucsmip UCSMIP] [--hxboost HXBOOST] [--force FORCE]
                  [--hxtoken HXTOKEN] [--test TEST]

Enable/Disable HyperFlex Boost Mode

optional arguments:
  -h, --help            show this help message and exit
  --hxip HXIP           HyperFlex ip
  --hxpasswd HXPASSWD   HyperFlex Cluster Password
  --hxuser HXUSER       hx user name
  --vcuser VCUSER       hx user name
  --vcpasswd VCPASSWD   vCenter Password
  --vcip VCIP           vCenter ip
  --ucsmuser UCSMUSER   UCS-M user name
  --ucsmpasswd UCSMPASSWD
                        UCS-M Password
  --ucsmip UCSMIP       UCS-M ip
  --hxboost HXBOOST     Hyper Flex Boostmode on / off
  --force FORCE         Force power off : on / off
  --hxtoken HXTOKEN     HX API Token
  --test TEST           Test the script without doing it. true = testing

```