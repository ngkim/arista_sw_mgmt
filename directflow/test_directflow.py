#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time

sys.path.append('/root/admin/switch/arista/python-rpc')
from arista_rpc import SwitchConnection, DirectFlow

def delete_direct_flow(directflow):
    port_cli    = 8
    vlan_cli    = 10
    port_stb    = 48
    vlan_stb    = 12
    
    # client port로부터 입력되는 vlan_cli (10) 을 vlan_stb (12)로 변환하는 flow
    flow_name   = "CLI_%s_to_STB_%s" % (vlan_cli, vlan_stb)
    directflow.delete_flow(flow_name)
    
    # standby port로부터 입력되는 vlan_stb (12)를 vlan_cli (10)로 변환하는 flow
    flow_name   = "STB_%s_to_CLI_%s" % (vlan_stb, vlan_cli)
    directflow.delete_flow(flow_name)
    

def add_direct_flow(directflow):
    port_cli    = 8
    vlan_cli    = 10
    port_stb    = 48
    vlan_stb    = 12
    
    # client port로부터 입력되는 vlan_cli (10) 을 vlan_stb (12)로 변환하는 flow
    flow_name   = "CLI_%s_to_STB_%s" % (vlan_cli, vlan_stb)
    print("- Add directflow flow= %s" % flow_name)
    directflow.create_flow(flow_name, port_cli, vlan_cli, vlan_stb)
    
    # standby port로부터 입력되는 vlan_stb (12)를 vlan_cli (10)로 변환하는 flow
    flow_name   = "STB_%s_to_CLI_%s" % (vlan_stb, vlan_cli)
    print("- Add directflow flow= %s" % flow_name)
    directflow.create_flow(flow_name, port_stb, vlan_stb, vlan_cli)

if __name__ == "__main__":
    directflow = DirectFlow()
    
    print("- [DIRECTFLOW] Enable directflow")
    directflow.enable()
    
    print("- [DIRECTFLOW] Add direct flows")
    add_direct_flow(directflow)
    
    
    print("Wait for 10 seconds...")
    time.sleep(10)
    
    print("Delete direct flows")
    delete_direct_flow(directflow)
    
    directflow.disable()
    
    