# -*- coding: utf-8 -*-
from jsonrpclib import Server, jsonrpc
import traceback
import ConfigParser
import ConfigParser

class SwitchConfig:

    def __init__(self, cfg="switch.cfg"):
        self.cfg=cfg

        self.config = ConfigParser.ConfigParser()
        self.config.read(cfg)

    def get_config(self):
        return self.config

class SwitchConnection:

    def __init__(self, cfg = None):
        if cfg == None: 
            self.cfg = SwitchConfig().get_config()
        else:
            self.cfg = cfg
        self.mgmtIp = self.cfg.get("connection", "ip")
        self.mgmtUser = self.cfg.get("connection", "user")
        self.mgmtPass = self.cfg.get("connection", "pass")
        #print "ip= %s user= %s pass= %s" % (self.mgmtIp, self.mgmtUser, self.mgmtPass)

    def get_proxy(self):
        api_url = "http://%s:%s@%s/command-api" % (self.mgmtUser, self.mgmtPass, self.mgmtIp)
        #print "api_url= %s" % api_url
        return Server(api_url)
    
class DirectFlow:
    
    def __init__(self, cfg = None):
        
        if cfg == None: 
            self.cfg = SwitchConfig().get_config()
        else:
            self.cfg = cfg
            
        self.proxy = SwitchConnection().get_proxy()
        
    
    def enable(self):
        self.is_enabled = True
        response = self.proxy.runCmds( 1, [ "enable", "configure", \
                                           "directflow", "no shutdown", \
                                           "end" ] )
        
    def disable(self):
        self.is_enabled = False    
        response = self.proxy.runCmds( 1, [ "enable", "configure", \
                                           "directflow", "shutdown", \
                                           "end" ] )
        
    def create_flow(self, flow_name, in_port, vlan_in, vlan_out):
        cmd_flow        = "flow %s" % flow_name
        cmd_match_intf  = "match input interface ethernet %s" % in_port
        cmd_match_vlan  = "match vlan %s" % vlan_in 
        cmd_action      = "action set vlan %s" % vlan_out 
        
        response = self.proxy.runCmds( 1, [ "enable", "configure", \
                                           "directflow", cmd_flow, \
                                           cmd_match_intf, cmd_match_vlan, \
                                           cmd_action, "end" ] )
    def delete_flow(self, flow_name):
        cmd_flow        = "no flow %s" % flow_name
        response = self.proxy.runCmds( 1, [ "enable", "configure", \
                                           "directflow", cmd_flow, "end" ] )
    
class Vlan:

    def __init__(self, vlan_id, name = ""):
        self.vlan_id = vlan_id
        self.proxy = SwitchConnection().get_proxy()
        if name == "":
            self.set_name()
        else:
            self.config_name(name)
            self.set_name(name)

    def get_id(self):
        return self.vlan_id

    def get_name(self):
        return self.name

    def create(self, name = ""):
        cmd_vlan = "vlan %s" % self.vlan_id
        
        if name == "":
            response = self.proxy.runCmds( 1, [ "enable", "configure", cmd_vlan, "end" ] )
        else:
            cmd_set_name = "name \"%s\"" % name
            response = self.proxy.runCmds( 1, [ "enable", "configure", cmd_vlan, cmd_set_name, "end" ] )
        
#config name은 항상 set name과 쌍으로 호출됨
#name이 설정되면 이를 장치에 적용하고, 동시에 Vlan 인스턴스에도 반영함
    def config_name(self, name):
        cmd_vlan = "vlan %s" % self.vlan_id
        cmd_set_name = "name \"%s\"" % name
        response = self.proxy.runCmds( 1, [ "enable", "configure", cmd_vlan, cmd_set_name, "end" ] )

    def set_name(self, name = ""):
        if name == "":
            cmd = "show vlan %s" % self.vlan_id
            try:
                response = self.proxy.runCmds( 1, [ cmd ] )
            except jsonrpc.ProtocolError:
                self.create()  

            self.name = response[0]["vlans"][self.vlan_id]["name"]
        else:
            self.name = name
            
    def set_ip_address(self, ip_address):
        cmd_svi = "interface vlan%s" % self.vlan_id
        cmd_ip = "ip addr %s" % ip_address
        try:
            response = self.proxy.runCmds( 1, [ "enable", "configure", cmd_svi, cmd_ip, "end" ] )
        except jsonrpc.ProtocolError:
            traceback.print_exc()

    def add_ip_route(self, net, gw):
        cmd_ip_route = "ip route %s %s" % (net, gw)
        try:
            response = self.proxy.runCmds( 1, [ "enable", "configure", cmd_ip_route, "end" ] )
        except jsonrpc.ProtocolError:
            traceback.print_exc()
    
    def get_ports(self):
        cmd = "show vlan %s" % self.vlan_id
        response = self.proxy.runCmds( 1, [ cmd ] )

        interfaces = response[0]["vlans"][self.vlan_id]["interfaces"]
        
        # key 중 'Cpu'가 있을 경우 이를 제거 후 반환
        if "Cpu" in interfaces:
            del interfaces["Cpu"]
                
        return interfaces
    
    # trunk port list를 구할 때는 mode에 "trunk" 입력
    def get_port_list(self, mode = "access"):
        list_port = []
        for key in self.get_ports():
            intf = Interface(key)
            if intf.get_vlan_mode() == mode:
                list_port.append(intf.get_index())
                
        return sorted(list_port)
    
    # set mode=trunk for trunk ports
    def get_configured_port_list(self, mode = "access"):
        list_port = []
        for key in self.get_configured_ports():
            intf = Interface(key)
            if intf.get_vlan_mode() == mode:
                list_port.append(intf.get_index())
                
        return sorted(list_port)
    
    def get_configured_ports(self):
        cmd = "show vlan %s configured-ports" % self.vlan_id
        #print "cmd= %s" % cmd
        response = self.proxy.runCmds( 1, [ cmd ] )

        interfaces = response[0]["vlans"][self.vlan_id]["interfaces"]
  
        return interfaces 

    # show_ports는 trunk interface까지 모두 보여준다
    def show_ports(self):
        print "* vlan= %-24s id= %-5s" % (self.get_name(), self.get_id())
        for key in sorted(self.get_ports()):
            intf = Interface(key)
            print "    - %-20s %-10s" % (key, intf.get_vlan_mode())
        print ""

    def show_access_ports(self):
        print "* vlan= %-24s id= %-5s" % (self.get_name(), self.get_id())
        for key in sorted(self.get_ports()):
            #print "show_access_ports %s" % key
            intf = Interface(key)
            if intf.get_vlan_mode() == "access":
                print "    - %s" % (key)
        print ""
        
    def show_trunk_ports(self):
        print "* vlan= %-24s id= %-5s" % (self.get_name(), self.get_id())
        for key in sorted(self.get_ports()):
            intf = Interface(key)
            if intf.get_vlan_mode() == "trunk":
                print "    - %s" % (key)            
        print ""

    def show_configured_ports(self):
        print "* vlan= %-24s id= %-5s" % (self.get_name(), self.get_id())
        for key in sorted(self.get_configured_ports()):
            print "    - %s" % (key)
        print ""
    
    def contains(self, interface_id):
        for key in sorted(self.get_configured_ports()):
            if key == interface_id:
                return True
        return False

class Interface:

    def __init__(self, interface_id):
        self.interface_id = interface_id.strip()
        self.proxy = SwitchConnection().get_proxy()
    
    def get_id(self):
        return self.interface_id
    
    def get_index(self):
        return int(self.interface_id.strip("Ethernet"))

    def get_vlan_mode(self):
        cmd = "show interfaces %s status" % self.interface_id
        #print "cmd= %s" % cmd
        response = self.proxy.runCmds( 1, [ cmd ])

        vlanMode = response[0]["interfaceStatuses"][self.interface_id]["vlanInformation"]["interfaceMode"]

        if vlanMode == "bridged":
            vlanMode = "access"
        elif vlanMode == "trunk":
            vlanMode = "trunk"
        else:
            vlanMode = "undefined"

        return vlanMode
    
    #Either 'uninitialized', 'admin', 'unknown', 'notconnect', 'disabled', 'connected' or 'errdisabled'
    def get_status(self):
        cmd = "show interfaces %s status" % self.interface_id
        response = self.proxy.runCmds( 1, [ cmd ])
        
        status = response[0]["interfaceStatuses"][self.interface_id]["linkStatus"]
        
        return status

    def is_disabled(self):
        if self.get_status() in "disabled notconnect":
            return True
        else:
            return False
    
    def is_enabled(self):
        if self.get_status() in "connected":
            return True
        else:
            return False
        
    def get_vlan(self):
        cmd = "show interfaces %s status" % self.interface_id
        response = self.proxy.runCmds( 1, [ cmd ])

        vlanId = response[0]["interfaceStatuses"][self.interface_id]["vlanInformation"]["vlanId"]

        return vlanId
    
    # flag = True 이면 shutdown, flag = False이면 no shutdown
    def shutdown(self, flag):
        cmd_intf = "interface %s" % self.interface_id
        if flag:
            cmd_shutdown = "shutdown"
        else:
            cmd_shutdown = "no shutdown"
            
        reponse = self.proxy.runCmds( 1, [ "enable", "configure", cmd_intf, cmd_shutdown, "end"])
        
    def set_speed(self):
        cmd_intf = "interface %s" % self.interface_id
        cmd_set_speed = "speed sfp-1000baset auto 100full"
        
        reponse = self.proxy.runCmds( 1, [ "enable", "configure", cmd_intf, cmd_set_speed, "end"])
        
    def unset_speed(self):
        cmd_intf = "interface %s" % self.interface_id
        cmd_set_speed = "no speed sfp-1000baset auto 100full"
        
        reponse = self.proxy.runCmds( 1, [ "enable", "configure", cmd_intf, cmd_set_speed, "end"])

    def set_access_vlan(self, vlan_id):
        cmd_intf = "interface %s" % self.interface_id
        cmd_access_mode = "switchport mode access"
        cmd_vlan = "switchport access vlan %s" % vlan_id
        #print "cmd_vlan= %s" % cmd_vlan
        
        reponse = self.proxy.runCmds( 1, [ "enable", "configure", cmd_intf, cmd_access_mode, cmd_vlan, "end"]) 
    
    def unset_access_vlan(self):
        cmd_intf = "interface %s" % self.interface_id
        cmd_access_vlan = "no switchport access vlan"
        
        reponse = self.proxy.runCmds( 1, [ "enable", "configure", cmd_intf, cmd_access_vlan, "end"]) 
            
    def set_trunk(self):
        cmd_intf = "interface %s" % self.interface_id
        cmd_trunk_mode = "switchport mode trunk"
        cmd_trunk_none = "switchport trunk allowed vlan none"
        
        reponse = self.proxy.runCmds( 1, [ "enable", "configure", cmd_intf, cmd_trunk_mode, cmd_trunk_none, "end"])
    
    def add_trunk_vlan(self, vlan_range):
        cmd_intf = "interface %s" % self.interface_id
        cmd_trunk_add = "switchport trunk allowed vlan add %s" % vlan_range
        
        reponse = self.proxy.runCmds( 1, [ "enable", "configure", cmd_intf, cmd_trunk_add, "end"])
        
    def unset_trunk(self):
        cmd_intf = "interface %s" % self.interface_id
        cmd_trunk_mode = "no switchport mode trunk"
        cmd_trunk_none = "no switchport trunk allowed vlan"
        
        reponse = self.proxy.runCmds( 1, [ "enable", "configure", cmd_intf, cmd_trunk_mode, cmd_trunk_none, "end"])
   
    # 이 인터페이스에 주어진 vlan_id값을 가지는 access vlan이 설정되었는지 확인
    def has_set_access(self, vlan_id):
        vlan = Vlan(vlan_id)
        
        if vlan.contains(self.interface_id):
            return True
        else:
            return False
    
    def has_unset_access(self, vlan_id):
        vlan = Vlan(vlan_id)
        
        if vlan.contains(self.interface_id):
            return False
        else:
            return True
    
    # confirm it's set if both vlan_min and vlan_max contains this interface
    def has_set_trunk(self, vlan_min, vlan_max):
        minVlan = Vlan(vlan_min)
        maxVlan = Vlan(vlan_max)
        
        if minVlan.contains(self.interface_id) and maxVlan.contains(self.interface_id):
            return True
        else:
            return False
    
    # confirm it's unset if both vlan_min and vlan_max does not contain this interface
    def has_unset_trunk(self, vlan_min, vlan_max):
        minVlan = Vlan(vlan_min)
        maxVlan = Vlan(vlan_max)
        
        if minVlan.contains(self.interface_id):
            return False
        elif maxVlan.contains(self.interface_id):
            return False
        else:
            return True                         
                         

class ServerNode:
    
        def __init__(self, name):
            self.name = name
        
        def get_name(self):
            return self.name
        
        def set_nic(self, nic):
            self.nic = nic
        
        def get_nic(self):
            return self.nic
                            
        def set_switch_port(self, switch_port):
            self.switch_port = switch_port
            
        def get_switch_port(self):
            return self.switch_port     
