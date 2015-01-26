# -*- coding: utf-8 -*-
import sys, ConfigParser
path="/root/admin/switch/arista/python-rpc"
if path not in sys.path:
    sys.path.append(path)

from arista_rpc import SwitchConfig    
from utils import Console, StringUtil, TimeUtil, NetUtil, InteractionUtil
import utm_failover

"""
Baremetal UTM Main이 다운되었을 때 Baremetal UTM Backup으로 절체 또는 그 반대의 기능을 수행
원래는 Trunk port에서 UTM용 GREEN이나 ORANGE VLAN을 제거해주는 형태로 동작해야 하나, 여기에서는 스위치의 포트를 shutdown시키는 형태로만 동작
"""

def usage(argv):
    print "Usage: %s [active or standby]" % argv[0]
    print "   - to use active  : %s active" % argv[0]
    print "   - to use standby : %s standby" % argv[0]
    sys.exit()    

def main():
    if len(sys.argv) < 2: 
        usage(sys.argv)
    
    t_util = TimeUtil()
    cfg = SwitchConfig().get_config()
        
    customer = cfg.get("failover", "customer")
    max_count = cfg.getint("failover", "max_count")
    time_sleep = cfg.getfloat("failover", "time_sleep")
    
    fo_active = cfg.get("failover", "active")
    fo_standby = cfg.get("failover", "standby")
    
    target = sys.argv[1]    
    
    if target == "active":
        curr = fo_standby
        targ = fo_active
        
        fo = utm_failover.UTMFailOver(cfg, curr, targ)
        
        fo.show_config(curr, "현재 설정 내용")
        fo.show_config(targ, "Failback 설정 내용")
        if InteractionUtil().ask_user("Failback 설정 내용을 적용하시겠습니까?"):
            t_util.start() 
            fo.failover(curr, targ)
            
            # 현재 구현된 l3_check는 
            # red/orange/green과 동일한 망에 연결된 노드에서만 수행 가능
            # 일단은 False로 설정 
            l3_check = fo.loop_l2_connectivity(False, max_count, time_sleep)
            fo.loop_l3_connectivity(l3_check, max_count, time_sleep)         
        else: 
            return False
    elif target == "standby":
        curr = fo_active
        targ = fo_standby
        
        fo = utm_failover.UTMFailOver(cfg, curr, targ)
        
        fo.show_config(curr, "현재 설정 내용")
        fo.show_config(targ, "Failover 설정 내용")
        
        if InteractionUtil().ask_user("Failover 설정 내용을 적용하시겠습니까?"): 
            t_util.start()
            fo.failover(curr, targ)
            
            l3_check = fo.loop_l2_connectivity(False, max_count, time_sleep)
            fo.loop_l3_connectivity(l3_check, max_count, time_sleep)            
        else: 
            return False        
    else:
        usage(argv)
    
    #Console().info(" *** [INFO] max_count= %s time_sleep= %s count= %s" % (max_count, time_sleep, count))
    t_util.stop()
    Console().info(" *** [INFO] Time= %s seconds!!!" % t_util.get_duration())
    
if __name__ == "__main__":
    main()

