# -*- coding: utf-8 -*-
import sys
import ConfigParser
from arista_rpc import SwitchConnection, Vlan, SwitchConfig, Interface

"""
* 스위치의 인터페이스의 access vlan 설정을 제거한다.  
"""

def usage(argv):
    print "Usage: %s [interface_name]" % argv[0]
    print "   ex) %s Ethernet1" % argv[0]
    sys.exit()    
    
"""
* 설정 내용 확인
  - 스위치 인터페이스의 vlan id가 -1이면 정상 설정된 것임
"""
def check_config(vlan_id):
    return vlan_id == 1
    
def main():
    cfg = SwitchConfig().get_config()
    
    if len(sys.argv) < 2: 
        usage(sys.argv)
    
    interface_name = sys.argv[1]    
    try:
        print "interface= %s" % interface_name
        
        # Interface에 대해 access mode 해제
        eth = Interface(interface_name)
        eth.unset_access_vlan()
        eth.unset_speed()
            
         # 설정 내용 확인
        if check_config(eth.get_vlan()):
            print "Unsetting access vlan configuration has been successfully applied for %s" % (interface_name)
        else:
            print "Unsetting access vlan configuration has failed for %s (%s)" % (interface_name, eth.get_vlan())
              
    except ConfigParser.NoSectionError as err:
        print "[ERROR] %s" % str(err)
         
if __name__ == "__main__":
    main()
    
