# -*- coding: utf-8 -*-
import sys, ConfigParser
path="/home/ngkim/workspace/arista_sw_mgmt/lib"
if path not in sys.path:
    sys.path.append(path)
    
import sys
from utils import Console
from arista_rpc import SwitchConfig 
import utm_failover

"""
failover한 interface의 status를 체크
"""

def main():
    #cfg = SwitchConfig().get_config()

    #uplink = Interface("eth35")
    
    t_id=0
    
    vid = "%d" % ((t_id * 10) + 10)
    ip_ ="211.196.251.%d/30" % ((t_id * 4) + 1)
    gw_ ="211.196.251.%d/30" % ((t_id * 4) + 2)
    net ="211.100.%d.0/24" % (t_id)
    
    print "vid= %s" % vid
    print "ip_= %s" % ip_
    print "gw_= %s" % gw_
    print "net= %s" % net
        
    #vlan = Vlan(10)
    #vlan.set_ip_address("")
    #vlan.add_ip_route(net, gw)
        
    #Console().log(" ----------------------------------------------------")
    
if __name__ == "__main__":
    main()

