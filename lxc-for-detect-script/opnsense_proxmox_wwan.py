# import libraries
import json
import requests
from proxmoxer import ProxmoxAPI
import time
from pprint import pp

# Disable SSL verification warnings
import urllib3
urllib3.disable_warnings()

# OPNsense API
# https://opnsense.local/api/<module>/<controller>/<command>/[<param1>/[<param2>/...]]
# define endpoint and credentials
opn_addr="10.10.0.1"
opn_api_key="zAHgzq8pdV1pMt1xiqao0H4ZX99yeoxmlngra4Imn90OS4bhaWdjXHJqlsfQXu459HvRIbsDPJSQGpqW"
opn_api_secret="cTJxvOV9ZxQywcObanbDJoJ1ysMHHdOcKq/nbgy7ov0w80wLZTF3G05XArVuFfZVy2l7cdGca7PxPP1d"
opn_api_url = "https://%s/api/routes/gateway/status" % opn_addr

def OPN_checkGWs():
    """Uses OPNsense API to get the status of all gateways"""
    r = requests.get(opn_api_url,
                    auth=(opn_api_key, opn_api_secret),
                    verify=False)
    gateways = {}
    if r.status_code == 200:
        response = json.loads(r.text)
        if response['status'] == 'ok':
            for gw in response['items']:
                gateways[gw['name']] = {key: gw[key] for key in ['address','status','status_translated']}
    return gateways

#ProxmoxVE API
pve_addr="0.0.0.0"
pve_user="root@pam"
pve_pass="password"
pve_node="pvenode"

def PVE_checkVM(vmid):
    """Uses PVE API to get the status of a QEMU VM by VMID"""
    try:
        pve = ProxmoxAPI(pve_addr, user=pve_user, password=pve_pass, verify_ssl=False)
        results = pve.nodes(pve_node).qemu(str(vmid)).status().current().get()
        del pve
        if int(results['vmid']) == int(vmid):
            return results['status']
    except:
        pass
    return 'stopped'

def PVE_switchVM(vmid, newstate):
    """Uses PVE API to start or shutdown a QEMU VM by VMID"""
    convstate = {'start':'running','shutdown':'stopped'}
    oldstate = PVE_checkVM(vmid) 
    if oldstate == convstate[newstate]:
        return
    try:
        pve = ProxmoxAPI(pve_addr, user=pve_user, password=pve_pass, verify_ssl=False)
        if newstate == 'start':
            pve.nodes(pve_node).qemu(str(vmid)).status().start().post()
            print("start VMID", vmid)
        elif newstate == 'shutdown':
            pve.nodes(pve_node).qemu(str(vmid)).status().shutdown().post()
            print("shutdown VMID", vmid)
        del pve
    except:
        pass

def monitor_check(vmid, gw):
    gw_status = OPN_checkGWs()[gw]
    vm_status = PVE_checkVM(vmid)
    if gw_status['status_translated'].lower().startswith('offline'): # or gw_status['status'].lower().startswith('down'):
        PVE_switchVM(vmid, 'start')
    elif gw_status['status_translated'].lower().startswith('online'): # or (gw_status['status'].lower() == 'none'):
        PVE_switchVM(vmid, 'shutdown')

#monitor interval (seconds)
mon_interval = 30
#gateway to monitor
mon_gw = "WAN_DHCP"
#vmID to start/stop
mon_vmid = 102

from simple_cli_args import cli_args

@cli_args
def startmonitor(gateway=mon_gw, vmid=mon_vmid, interval=mon_interval):
    print('=' * 80)
    print("OPNsense Gateway Control ProxmoxVE VM")
    print("Monitor Interval: ", interval)
    print("OPNsense Gateway: ", gateway)
    print("  ProxmoxVE VMID: ", vmid)
    print('=' * 80)
    print("Gateway Status:", OPN_checkGWs()[gateway])
    print("VMID", vmid, "staus:", PVE_checkVM(vmid))
    print('=' * 80)
    print('starting monitoring....')
    while True:
        try:
            monitor_check(vmid, gateway)
            if interval == 0:
                raise Exception('interval of 0')
            time.sleep(interval)
        except:
            break

if __name__ == "__main__":
    startmonitor()
