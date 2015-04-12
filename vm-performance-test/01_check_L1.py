# -*- coding: utf-8 -*-
import sys, ConfigParser
path="/root/workspace/arista_sw_mgmt/lib"
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
    cfg = SwitchConfig().get_config()
    
    Vlan vlan = Vlan(10)
    Interface uplink = Interface("eth35")
    
        
    customer = cfg.get("failover", "customer")
    
    fo_active = cfg.get("failover", "active")
    fo_standby = cfg.get("failover", "standby")
    
    fo = utm_failover.UTMFailOver(cfg, fo_active, fo_standby)
        
    fo.show_config(fo_active, "Active 설정 내용")
    fo.show_config(fo_standby, "Standby 설정 내용")
    
    is_active=False
    if fo.is_applied(fo_active):
        is_active=True
        mode_name = "Active"
        Console().info(" *** 현재 %s 모드가 적용된 상태입니다." % mode_name)
    
    is_standby=False
    if fo.is_applied(fo_standby):
        is_standby=True
        mode_name = "Standby"
        Console().info(" *** 현재 %s 모드가 적용된 상태입니다." % mode_name)
    
    if is_active and is_standby:
        Console().info(" *** 현재 Active와 Standby가 모두 적용된 상태입니다.")
    
    if is_active == False and is_standby == False:
        Console().error(" *** 현재 Active와 Standby가 모두 적용되지 않은 상태입니다.")
    
    Console().log(" ----------------------------------------------------")
    
if __name__ == "__main__":
    main()

