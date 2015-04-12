# -*- coding: utf-8 -*-
import sys, ConfigParser
path="/root/workspace/arista_sw_mgmt/lib"
if path not in sys.path:
    sys.path.append(path)
    
import sys
from utils import Console
from arista_rpc import SwitchConfig 
import utm_failover

def add_vlan(cfg, t_id, uplink):
    
    vlan_start = (t_id * 10) + 10
    vlan_end   = (t_id * 10) + 13
    vlan_range = "%d-%d" % (vlan_start, vlan_end)
    
    print "vlan_range= %s" % vlan_range
    uplink.add_trunk_vlan(vlan_range)
    
    vid = "%d" % (2000 + (t_id * 10) + 10 )
    
    ip_ ="211.196.251.%d/30" % ((t_id * 4) + 1)
    gw_ ="211.196.251.%d/30" % ((t_id * 4) + 2)
    net ="211.100.%d.0/24" % (t_id)
    
    print "vid= %s" % vid
    print "ip_= %s" % ip_
    print "gw_= %s" % gw_
    print "net= %s" % net
    
    vlan = Vlan(vid)
    vlan.set_ip_address(ip_)
    vlan.add_ip_route(net, gw_)    
    
def main():
    cfg = SwitchConfig().get_config()

    uplink = Interface("eth35")
    
    for x in range(100):
        add_vlan(cfg, x, uplink)
        
    #Console().log(" ----------------------------------------------------")
    
if __name__ == "__main__":
    main()
