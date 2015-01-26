# -*- coding: utf-8 -*-
import sys
import ConfigParser
from arista_rpc import SwitchConnection, Vlan, SwitchConfig, Interface

"""
* switch.cfg의 설정 내용 중 아래 항목을 이용하여 이를 스위치에 반영한다. 

[test]
green=21
orange=20

[test-client]
nic=eth1
port=Ethernet25
port_mode=access
port_vlan=test:green

[test-server]
nic=eth1
port=Ethernet26
port_mode=access
port_vlan=test:orange

예) python config_zero_offcie.py test-client 
- 고객망(green망)에 존재하는 서버인 test-client를 위해 Ethernet25에 VLAN 21을 설정

예) python config_zero_offcie.py test-server
- 서버망(orange망)에 존재하는 서버인 test-server를 위해 Ethernet26에 VLAN 20을 설정

* 설정 내용 확인
  - 스위치 인터페이스가 주어진 VLAN에 할당되어 있는지를 확인하여 정상 설정되었음을 점검

"""

"""
* CfgOfficeNet 클래스
  - ToR 스위치에 연결된 ZeroOffice 고객망의 서버와 서버망의 서버에 대한 ToR 스위치 설정 정보 보관
"""
class CfgOfficeNet:
    
    def __init__(self):
        self.cfg = SwitchConfig().get_config()
    
    def read_config(self):
        # 스위치와 연결된 서버 NIC
        self.nic=cfg.get(server_name, "nic")
        
        # 서버가 연결된 스위치 포트, access/trunk 모드 및 VLAN 아이디
        self.port=cfg.get(server_name, "port")
        self.port_mode=cfg.get(server_name, "port_mode")
        self.port_vlan_cfg=cfg.get(server_name, "port_vlan")
        
        # 스위치 포트에 설정할 vlan값을 설정으로부터 읽어옴
        key = port_vlan_cfg.split(":")
        self.port_vlan = cfg.get(key[0], key[1])    

def usage(argv):
    print "Usage: %s [server_name]" % argv[0]
    print "   ex) %s test-client" % argv[0]
    sys.exit()    
    
"""
* 설정 내용 확인
  - 스위치 인터페이스가 주어진 VLAN에 할당되어 있는지를 확인하여 정상 설정되었음을 점검
"""
def check_config(eth, port_vlan):
    return eth.has_set_access(port_vlan)
    
def main(argv):
    proxy = SwitchConnection().get_proxy()
    cfg = SwitchConfig().get_config()
    
    if len(sys.argv) < 2: 
        usage()
    
    server_name = sys.argv[1]    
    try:    
        cfg = CfgOfficeNet()
        
        print "server= %s" % server_name
        print "   nic= %s" % cfg.nic
        print "  port= %s mode= %s vlan= %s" % (cfg.port, cfg.port_mode, cfg.port_vlan)
        
        # Interface에 대해 VLAN 설정
        eth = Interface(cfg.port)
        if cfg.port_mode == "access": 
            eth.set_access_vlan(cfg.port_vlan)
            
         # 설정 내용 확인
        if check_config(eth, cfg.port_vlan):
            print " port %s has successfully configured for vlan %s" % (cfg.port, cfg.port_vlan)
        else:
            print " port %s has failed to configure vlan %s" % (cfg.port, cfg.port_vlan)
              
    except ConfigParser.NoSectionError as err:
        print "[ERROR] %s" % str(err)
         
if __name__ == "__main__":
    main(sys.argv[1:])
    
