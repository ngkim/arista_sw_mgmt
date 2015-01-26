from arista_rpc import SwitchConnection, Vlan, SwitchConfig, Interface

def show_version():
    proxy = SwitchConnection().get_proxy()

    response = proxy.runCmds( 1, ["show version"] )
    print "The switch's system MAC addess is", response[0]["systemMacAddress"]

def show_interfaces():
    proxy = SwitchConnection().get_proxy()

    response = proxy.runCmds( 1, ["show interfaces"] )
    for key in response[0]["interfaces"].keys():
        interface_name=response[0]["interfaces"][key]["name"]
        interface_status=response[0]["interfaces"][key]["lineProtocolStatus"]
        print "Interface %s is %s." % (interface_name, interface_status)
 
def get_interface_config():
    port = Interface("Ethernet1")
    vlan_mode = port.get_vlan_mode()
    print "vlan_mode= %s" % port.get_vlan_mode()
    if vlan_mode == "access": 
        print "vlan= %s" % port.get_vlan()
    elif vlan_mode == "trunk":
        print "vlan= %s" % port.get_vlan()
        
def show_ports(vlanList):
    for vlan in vlanList:
        vlan.show_ports()    

def test_access_vlan(mode):
    proxy = SwitchConnection().get_proxy()  
    cfg = SwitchConfig().get_config()
    
    # Management VLAN, API VLAN, External VLAN
    mgmtVlanId = cfg.get("access_vlan", "mgmt_vlan")
    mgmtVlan = Vlan(mgmtVlanId)
    
    eth3 = Interface("Ethernet3")
    if mode == True: 
        eth3.set_access_vlan(mgmtVlan.get_id())
    else:
        eth3.unset_access_vlan()   

def test_trunk_vlan(mode):
    proxy = SwitchConnection().get_proxy()  
    cfg = SwitchConfig().get_config()
    
    privateMin = cfg.get("private", "min")
    privateMax = cfg.get("private", "max")
    trunk_range = "%s-%s" % (privateMin, privateMax)
    
    eth3 = Interface("Ethernet3")
    if mode == True: 
        eth3.set_trunk(trunk_range)
    else:
        eth3.unset_trunk()

def move_trunk_interface():
    proxy = SwitchConnection().get_proxy()  
    cfg = SwitchConfig().get_config()
    
    # clear trunk configuration of ethernet10
    eth10 = Interface("Ethernet10")
    eth10.unset_trunk()
    
    # clear trunk configuration of ethernet17
    eth17 = Interface("Ethernet17")
    eth17.unset_trunk()
    
    # set trunk for ethernet10
    trunkMin = cfg.get("hybrid", "min")
    trunkMax = cfg.get("hybrid", "max")
    trunk_range = "%s-%s" % (trunkMin, trunkMax)
    
    eth10.set_trunk(trunk_range)
    
    if eth10.has_set_trunk(trunkMin, trunkMax):
        print "%s has set successfully!!!" % eth10.interface_id
    if eth17.has_unset_trunk(trunkMin, trunkMax):
        print "%s has unset successfully!!!" % eth17.interface_id
        
# 현재 Vlan 3이 설정된 인터페이스인 Ethernet14,15,16에서 Vlan 3을 unset하고, 
# Ethernet13에 Vlan 3을 access vlan으로 set해준다
def test_move_access_interface():
    proxy = SwitchConnection().get_proxy()  
    cfg = SwitchConfig().get_config()
    
    extVlanId = cfg.get("access_vlan", "ext_vlan")
    extVlan = Vlan(extVlanId)
    
    eth = Interface("Ethernet22")
    
    list_to_unset = [eth]
    for eth in list_to_unset:
        print "Unset %s" % eth.interface_id
        eth.unset_access_vlan()
        eth.unset_speed()
    
        if eth.has_set_access(extVlanId):
            print "%s has failed to unset!!!" % eth.interface_id
        else:
            print "%s has unset successfully!!!" % eth.interface_id
        
    eth = Interface("Ethernet23")
    print "Set vlan %s for %s" % (extVlanId, eth.interface_id)

    eth.set_access_vlan(extVlanId)
    eth.set_speed()
    
    if eth.has_set_access(extVlanId):
        print "%s has set successfully!!!" % eth.interface_id
    else:
        print "%s has failed to set!!!" % eth.interface_id

def test_server_config(name):
    proxy = SwitchConnection().get_proxy()  
    cfg = SwitchConfig().get_config()  
    
    nic=cfg.get(name, "nic")
    port=cfg.get(name, "port")
    port_mode=cfg.get(name, "port_mode")
    port_vlan_cfg=cfg.get(name, "port_vlan")
    key = port_vlan_cfg.split(":")
    port_vlan = cfg.get(key[0], key[1])
    
    print "server= %s" % name
    print "   nic= %s" % nic
    print "  port= %s mode= %s vlan= %s" % (port, port_mode, port_vlan)
    
def test_set_speed():
    proxy = SwitchConnection().get_proxy()  
    cfg = SwitchConfig().get_config()  
    
    eth = Interface("Ethernet23")
    eth.unset_speed()

def main():
    proxy = SwitchConnection().get_proxy()  
    cfg = SwitchConfig().get_config()  
    
    # Management VLAN, API VLAN, External VLAN
    mgmtVlanId = cfg.get("access_vlan", "mgmt_vlan")
    mgmtVlan = Vlan(mgmtVlanId)
    
    eth = Interface("Ethernet13")
    eth.unset_access_vlan()
    
def show_vlan():
    proxy = SwitchConnection().get_proxy()

    response = proxy.runCmds( 1, ["show vlan"] )
    vlans=response[0]
    for key in sorted(vlans["vlans"]):
        vlan = vlans["vlans"][key]
        vlan_name = vlan["name"]
        print "**** vlan name= %s" % (vlan_name)
        interface = vlan["interfaces"]
        for itf in sorted(interface):
            print " interface= %s" % (itf)
 
if __name__ == "__main__":
    #show_version()
    #get_interface_config()
    #get_vlan_ports()
    #get_vlan_configured_ports()
    #test_access_vlan(False)
    #test_trunk_vlan(False)
    #test_server_config("forbiz-server")
    #main()
    #move_trunk_interface()
    test_move_access_interface()
    #test_set_speed()