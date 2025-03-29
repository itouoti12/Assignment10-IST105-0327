import requests
from requests.auth import HTTPBasicAuth
from dnac_config import DNAC
import urllib3
import sys

# Disable SSL warnings for sandbox
urllib3.disable_warnings()

class DNAC_Manager:

    def __init__(self):
        self.dna_token = None
    
    def make_dna_host(self):
        return f"https://{DNAC['host']}:{DNAC['port']}/"

    def get_auth_token(self, display_token=False):
        try:
            response = requests.post(
                url=f"{self.make_dna_host()}/dna/system/api/v1/auth/token",
                auth=HTTPBasicAuth(DNAC['username'],DNAC['password']),
                verify=False
            )
            response.raise_for_status()
            self.dna_token = response.json()['Token']

            if display_token:
                print("Here is your Auth Token:")
                print("-"*50)
                print(self.dna_token)
                print("-"*50)

            return True

        except Exception as e:
            print("Get Auth token failed:")
            print(str(e))
            return False

    def get_network_devices(self):

        if not self.dna_token:
            print("You havn't gotten Auth Token yet.")
            print("Get Auth Token in advance.")
            return None

        try:
            headers = {"X-Auth-Token": self.dna_token}
            response = requests.get(
                url=f"{self.make_dna_host()}/dna/intent/api/v1/network-device",
                headers=headers,
                verify=False
            )
            response.raise_for_status()
            return response.json()["response"]

        except Exception as e:
            print(f"Get devices list is failed:{str(e)}")
            return None
    
    def display_devices(self, devices):
        if not devices:
            print("Devices are not found.")
            return
        
        print("\nNetwork Devices")
        print("="*80)
        print(f"{'Hostname':20}{'IP Address':15}{'Platform':20}{'Status':10}")
        print("-"*80)
        
        for device in devices:
            print(
                f"{device.get('hostname', 'N/A'):20}"
                f"{device.get('managementIpAddress', 'N/A'):15}"
                f"{device.get('platformId', 'N/A'):20}"
                f"{device.get('reachabilityStatus', 'N/A'):10}"
            )
    
    def get_device_interfaces(self, device_ip):
        if not self.dna_token:
            print("You havn't gotten Auth Token yet.")
            print("Get Auth Token in advance.")
            return None
        
        try:
            devices = self.get_network_devices()
            device = next(
                (d for d in devices if d.get('managementIpAddress') == device_ip), 
                None
            )
            if not device:
                print(f"Device {device_ip} is not found.")
                return None
            
            headers = {"X-Auth-Token": self.dna_token}
            params = {"deviceId":device['id']}
            response = requests.get(
                url=f"{self.make_dna_host()}/api/v1/interface",
                headers=headers,
                params=params,
                verify=False
            )
            response.raise_for_status()
            return response.json().get("response",[])

        except Exception as e:
            print(f"Get device interfaces is failed: {str(e)}")
            return None


    def display_interfaces(self, interfaces):
        if not interfaces:
            print("No interfaces found!")
            return
            
        print("\n🔌 Device Interfaces")
        print("="*80)
        print(f"{'Interface':20}{'Status':10}{'VLAN':10}{'Speed':10}")
        print("-"*80)
        
        for intf in interfaces:
            print(
                f"{intf.get('portName', 'N/A'):20}"
                f"{intf.get('status', 'N/A'):10}"
                f"{intf.get('vlanId', 'N/A'):10}"
                f"{intf.get('speed', 'N/A'):10}"
            )

def main():

    print("\n" + "*"*50)
    print("Automation Network Config Tool")
    print("*"*50)

    dnac = DNAC_Manager()


    options = [
        {"no":"1","desc":"Authenticate & Show Token"},
        {"no":"2","desc":"Show Network Devices"},
        {"no":"3","desc":"Show Device Interfaces"},
        {"no":"4","desc":"Finish"},
        ]

    while True:
        print("\n Main Menu:")
        for option in options:
            print(f"  {option["no"]}. {option["desc"]}")
        print("\n")

        selected = input(f"What do you want to do?({options[0]['no']}-{options[len(options)-1]['no']}): ").strip()

        if selected == options[0]["no"]:
            if dnac.get_auth_token(display_token=True):
                print("Authentication success.")

        elif selected == options[1]["no"]:
            devices = dnac.get_network_devices()
            dnac.display_devices(devices)

        elif selected == options[2]["no"]:
            device_ip = input("Enter device IP address: ").strip()
            interfaces = dnac.get_device_interfaces(device_ip)
            dnac.display_interfaces(interfaces)

        elif selected == options[3]["no"]:
            print("Finish this Tool")
            sys.exit()

        else:
            print("Invalid option you choose. Try again.")

if __name__ == "__main__":
    main()

        






    










