# -*- coding: utf-8 -*-
from arista_rpc import SwitchConnection, Vlan, SwitchConfig, Interface
from utils import Console, StringUtil

"""
 switch.cfg 파일의 내용과 arista 스위치의 설정 내용을 비교해서 차이점을 보여준다.
"""

def check_access_vlan(cfg, vlan_name):
    
    Console().log("=== Access VLAN %s " % vlan_name, "info")
    str_cfg_intf = cfg.get(vlan_name, "interfaces")
    conf_port_list = StringUtil().list_str_to_int(str_cfg_intf)
    Console().log("    conf_port_list= %s" % conf_port_list)
    
    vlanId = cfg.get("access_vlan", vlan_name)
    vlan = Vlan(vlanId)
    phys_port_list = vlan.get_port_list()
    Console().log("    phys_port_list= %s" % phys_port_list)
    
    result = True
    if not conf_port_list == phys_port_list:
        Console().debug(" 물리 스위치의 VLAN 구성이 설정된 내용과 다릅니다.")
        Console().info("    - VLAN 설정 내용: %s" % conf_port_list)
        Console().info("    - 물리 스위치 VLAN 구성: %s" % phys_port_list)
        
        for port in conf_port_list:
            intf = Interface("Ethernet%s" % port) 
            if not is_intf_in_vlan(intf, vlan):
                result = False
    else: 
        result = True   
            
    return result

def check_trunk_vlan(cfg, vlan_name):
    
    Console().log("=== Trunk VLAN %s " % vlan_name, "info")
    
    str_cfg_intf = cfg.get(vlan_name, "interfaces")
    conf_port_list = StringUtil().list_str_to_int(str_cfg_intf)
    Console().log("    conf_port_list= %s" % conf_port_list)
    
    minVlanId = cfg.get(vlan_name, "min")
    maxVlanId = cfg.get(vlan_name, "max")
    
    minVlan = Vlan(minVlanId)
    maxVlan = Vlan(maxVlanId)
    
    phys_port_list_1 = minVlan.get_port_list("trunk")
    phys_port_list_2 = maxVlan.get_port_list("trunk")
    
    Console().log("    vlan= %s phys_port_list= %s" % (minVlanId, phys_port_list_1))
    Console().log("    vlan= %s phys_port_list_2= %s" % (maxVlanId, phys_port_list_2))
    
    result = True
    if conf_port_list == phys_port_list_1 and conf_port_list == phys_port_list_2:
        result = True
    else:
        Console().debug(" 물리 스위치의 VLAN 구성이 설정된 내용과 다릅니다.")
        Console().info("    - VLAN 설정 내용: %s" % conf_port_list)
        Console().info("    - 물리 스위치 VLAN 구성(vlan %s): %s" % (minVlanId, phys_port_list_1))
        Console().info("    - 물리 스위치 VLAN 구성(vlan %s): %s" % (maxVlanId, phys_port_list_2))
        
        for port in conf_port_list:
            intf = Interface("Ethernet%s" % port) 
            if not is_intf_in_vlan(intf, minVlan, "trunk"):
                result = False
            if not is_intf_in_vlan(intf, maxVlan, "trunk"):
                result = False
        result = False
    return result    

"""
고객 네트워크의 port가 고객 네트워크의 port_vlan에 존재하는지 체크
"""
def check_customer_network(cfg, nw_name):
    
    Console().log("=== Customer Network %s " % nw_name, "info")
    
    cfgPort = cfg.get(nw_name, "port")
    intf = Interface(cfgPort)
    intf_idx = intf.get_index()
    Console().log("    port= %s" % cfgPort)
    
    cfgVlan = cfg.get(nw_name, "port_vlan").split(":")
    vlanId = cfg.get(cfgVlan[0], cfgVlan[1])
    vlan = Vlan(vlanId)
    
    phys_port_list = vlan.get_port_list()
    Console().log("    phys_port_list= %s" % phys_port_list)
    
    return is_intf_in_vlan(intf, vlan)
    
# 주어진 interface가 vlan에 속한 인터페이스인지를 확인해줌
def is_intf_in_vlan(intf, vlan, mode="access"):
    
    intf_idx = intf.get_index()
    intf_name = intf.get_id()
    
    vlan_id = vlan.get_id()
    phys_port_list = vlan.get_port_list(mode)
    if intf_idx in phys_port_list:
        return True
    else:
        phys_port_list = vlan.get_configured_port_list(mode)    
        #Console().debug("    phys_configured_port_list= %s" % phys_port_list)
        if intf_idx in phys_port_list:
            Console().debug("%s is configured for vlan %s, but not active" % (intf_name, vlan_id))
            return True
        else:
            Console().debug("%s is not configured for vlan %s" % (intf_name, vlan_id))
            
            check = False
            while not check:
                user_input = raw_input("Will you configure %s for vlan %s as %s mode? (y/n)" % (intf_name, vlan_id, mode))
                if user_input.strip() in ["y", "yes"]:
                    
                    check = True
                elif user_input.strip() in ["n", "no"]:
                    
                    check = True
                else:
                    print "(y/n)?"
                    check = False
                 
            return False

def main():
    cfg = SwitchConfig().get_config()
    
    list_access_vlan = (cfg.get("list", "access")).split(",")
    for vlan_name in list_access_vlan:
        if not check_access_vlan(cfg, vlan_name.strip()):
            Console().error("       * No sync!!!")
            
    list_trunk_vlan = (cfg.get("list", "trunk")).split(",")
    for vlan_name in list_trunk_vlan:
        if not check_trunk_vlan(cfg, vlan_name.strip()):
            Console().error("       * No sync!!!")
            
    list_customer_network = (cfg.get("list", "customer")).split(",")
    for nw_name in list_customer_network:
        if not check_customer_network(cfg, nw_name.strip()):
            Console().error("       * No sync!!!")
    
if __name__ == "__main__":
    main()