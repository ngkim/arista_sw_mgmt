# -*- coding: utf-8 -*-
import sys, ConfigParser
path="/root/workspace/arista_sw_mgmt/lib"
if path not in sys.path:
    sys.path.append(path)

#------------------------------------------------------------------------------
# README
#------------------------------------------------------------------------------
# main 함수 안의 r_start와 r_end값에 설정할 test_id의 값을 지정한다.
# 주의할 점은 r_end -1 값 까지만 적용된다는 것이다.
# 즉 1부터 100까지 하려면 r_start=1, r_end=101 을 입력해야 한다. 
#------------------------------------------------------------------------------

import sys
from utils import Console
from arista_rpc import SwitchConfig, Interface, Vlan
import utm_failover

def add_vlan(cfg, t_id, uplink):
    
    vid = "%d" % (2000 + (t_id * 10) + 10 )

    print "vlan_range= %s" % vid
    uplink.add_trunk_vlan(vid)
    
    if t_id < 50:
        red_ip_c=251
    else:
        red_ip_c=252
        
    ip_ ="211.196.%d.%d/30" % (red_ip_c, (t_id * 4) + 1)
    gw_ ="211.196.%d.%d" % (red_ip_c, (t_id * 4) + 2)
    net ="211.100.%d.0/24" % (t_id)
    
    print "vid= %s" % vid
    print "ip_= %s" % ip_
    print "gw_= %s" % gw_
    print "net= %s" % net
    
    vlan = Vlan(vid)
    vlan.create()
    vlan.set_ip_address(ip_)
    vlan.add_ip_route(net, gw_)    
    
def main():
    cfg = SwitchConfig().get_config()

    uplink = Interface("eth35")
    
    r_start=51
    r_end=101
    for x in range(r_start, r_end):
        add_vlan(cfg, x, uplink)
        
    #Console().log(" ----------------------------------------------------")
    
if __name__ == "__main__":
    main()

