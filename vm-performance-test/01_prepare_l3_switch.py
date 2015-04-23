# -*- coding: utf-8 -*-
import sys, ConfigParser
path="/root/workspace/arista_sw_mgmt/lib"
if path not in sys.path:
    sys.path.append(path)

from utils import Console
from arista_rpc import SwitchConfig, Interface, Vlan
import utm_failover

#------------------------------------------------------------------------------
# README
#------------------------------------------------------------------------------
# main 함수 안의 r_start와 r_end값에 설정할 test_id의 값을 지정한다.
# 소스 코드 내에서 python range 함수의 특성 반영을 위해 range에는 r_end + 1을 입력 
#------------------------------------------------------------------------------
# red 인터페이스의 가장 끝자리 아이피는 
# red 인터페이스의 serial ip는 t_id가 50이 넘으면 252.x를 사용
#------------------------------------------------------------------------------

def get_vlan_vid(t_id):
    return "%d" % (2000 + (t_id * 10) + 10 )
    
def get_red_ip_c(t_id):
    if t_id < 50:
        red_ip_c=251       
    else:
        red_ip_c=252
    return red_ip_c
    
def get_red_ip_d(t_id):
    return ((t_id % 50) * 4) + 1

def get_red_ip_d_gw(t_id):
    return ((t_id % 50) * 4) + 2

def get_red_ip(t_id):
    red_ip_c=get_red_ip_c(t_id)    
    red_ip_d=get_red_ip_d(t_id)
    
    return "211.196.%d.%d/30" % (red_ip_c, red_ip_d)

def get_red_ip_gw(t_id):
    red_ip_c=get_red_ip_c(t_id)
    red_ip_d_gw=get_red_ip_gw(t_id)
    
    return "211.196.%d.%d" % (red_ip_c, red_ip_d_gw)

def get_red_ip_net(t_id):
    return "211.100.%d.0/24" % (t_id)

def add_vlan(cfg, t_id, uplink):
    vid = get_vlan_vid(t_id)
    uplink.add_trunk_vlan(vid)
        
    ip_ = get_red_ip(t_id)
    gw_ = get_red_ip_gw(t_id)
    net = get_red_ip_net(t_id)

    print "vid= %s" % vid
    print "ip_= %s" % ip_
    print "gw_= %s" % gw_
    print "net= %s" % net
    
    vlan = Vlan(vid)
    vlan.create()
    vlan.set_ip_address(ip_)
    vlan.add_ip_route(net, gw_)

def delete_vlan(cfg, t_id, uplink):
    vid = get_vlan_vid(t_id)
    
    ip_ = get_red_ip(t_id)
    gw_ = get_red_ip_gw(t_id)
    net = get_red_ip_net(t_id)

    print "vid= %s" % vid
    print "ip_= %s" % ip_
    print "gw_= %s" % gw_
    print "net= %s" % net
    
    vlan = Vlan(vid)
    vlan.delete_ip_route(net, gw_)
    vlan.clear_ip_address(ip_)
    vlan.delete()
    
    uplink.remove_trunk_vlan(vid)
    
def usage():
    print "Usage: %s [MODE] [START] [END]" % sys.argv[0]
    print " ex 1) %s add 0 49" % sys.argv[0]
    print " ex 2) %s del 0 49" % sys.argv[0]
    sys.exit(0)
        
def main():
    if len(sys.argv) < 4: 
        usage()
    
    mode=sys.argv[1]
    r_start=int(sys.argv[2])
    r_end=int(sys.argv[3])
            
    cfg = SwitchConfig().get_config()

    uplink = Interface("eth35")
    if mode == "add":
        print " Add: %d ==> %d " % (r_start, r_end)
        for x in range(r_start, r_end + 1 ):
            add_vlan(cfg, x, uplink)
            print " ----------------------------------------------------"
    elif mode == "del":
        print " Delete: %d ==> %d " % (r_start, r_end)
        for x in range(r_start, r_end + 1):
            delete_vlan(cfg, x, uplink)
            print " ----------------------------------------------------"
    else:
        usage()
    
if __name__ == "__main__":
    main()

