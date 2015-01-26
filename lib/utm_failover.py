# -*- coding: utf-8 -*-
from arista_rpc import SwitchConnection, Vlan, SwitchConfig, Interface
from utils import Console, NetUtil
import time

class UTMFailOver:
    
    def __init__(self, cfg, curr, targ):
        self.cfg = cfg
        self.LOG = Console()
        
        # 상태 : active, standby
        # curr : 현재상태
        # targ : 다음상태
        self.curr = curr
        self.targ = targ
        
    def loop_l3_connectivity(self, run_l3_check=False, max_count = 10, time_sleep=3):
        # L3 연결성 체크    
        count = 0
        if run_l3_check:
            while (count < max_count):
                if self.check_l3():
                    break
                self.LOG.log(" ====================================================")
                if count != max_count-1: time.sleep(time_sleep)
                count = count + 1
                    
    # utm의 interface가 올라왔는지 ping과 arp로 확인한다.
    # target의 ip 주소로 ping을 하고,
    # 그 결과 arp를 확인하여 mac주소가 설정값과 동일한지 확인  
    def is_l3_connected(self, ip_addr, mac_in_cfg):
        mac_in_real = NetUtil().get_mac_from_arp(ip_addr)
        
        self.LOG.log("     - CONF ip= %-15s mac= %s" % (ip_addr, mac_in_cfg))
        self.LOG.log("     - REAL ip= %-15s mac= %s" % (ip_addr, mac_in_real))
        
        if mac_in_cfg.upper() == mac_in_real.upper():
            return True
        else:
            return False

    def check_l3(self):
        customer = self.cfg.get("failover", "customer")
        ip_red = self.cfg.get(customer, "ip_red")
        ip_green = self.cfg.get(customer, "ip_green")
        
        mac_red_in_cfg = self.cfg.get(self.target, "port_red_mac")
        mac_green_in_cfg = self.cfg.get(self.target, "port_green_mac")
        
        self.LOG.info(" *** [INFO] Checking L3 connectivity...")
        
        red_l3_failover = is_l3_connected(ip_red, mac_red_in_cfg)
        green_l3_failover = is_l3_connected(ip_green, mac_green_in_cfg)
        
        if red_l3_failover and green_l3_failover:
            self.LOG.info(" ***                             성공!!!")
            return True
        else:
            self.LOG.error(" ***                             진행중!!!")
            return False

    #  L2 연결성 체크, 성공시 L3 연결 체크 문의
    def loop_l2_connectivity(self, ask_l3_check=False, max_count = 10, time_sleep=3 ):
        run_l3_check=False
            
        count = 0
        while (count < max_count):
            if self.check_l2():
                if ask_l3_check: 
                    run_l3_check=InteractionUtil().ask_user("L3 연결을 체크하시겠습니까?")                
                break
            self.LOG.log(" ====================================================")
            if count != max_count-1: time.sleep(time_sleep)
            count = count + 1
        return run_l3_check  
    
    # 스위치 인터페이스 중 active가 disable되고
    # standby가 active되었는지를 확인
    def is_l2_connected(self, intf_curr, intf_targ):
        l2_connected = False
        if intf_curr.is_disabled() and intf_targ.is_enabled():
            l2_connected = True
        else:
            l2_connected = False
        
        return l2_connected
    
    # switch의 interface가 올라왔는지 확인한다.
    # current interface는 down되고, target interface는 up 
    def check_l2(self):
        port_red_curr = self.cfg.get(self.curr, "port_red")
        port_red_targ = self.cfg.get(self.targ, "port_red")
        
        port_green_curr = self.cfg.get(self.curr, "port_green")
        port_green_targ = self.cfg.get(self.targ, "port_green")
        
        intf_red_curr = Interface(port_red_curr)
        intf_red_targ = Interface(port_red_targ)
        intf_green_curr = Interface(port_green_curr)
        intf_green_targ = Interface(port_green_targ)
        
        red_failover = self.is_l2_connected(intf_red_curr, intf_red_targ)
        green_failover = self.is_l2_connected(intf_green_curr, intf_green_targ)
        
        self.LOG.info(" *** [INFO] Checking L2 connectivity...")
    
        self.LOG.log("     - %-5s interface failover result= %s" % ("RED", red_failover))
        self.LOG.log("     - %-5s interface failover result= %s" % ("GREEN", green_failover))
        
        if red_failover and green_failover:
            self.LOG.log(" ----------------------------------------------------")
            self.LOG.info(" ***                                          성공!!!")
            self.LOG.log(" ----------------------------------------------------")
            return True
        else:
            self.LOG.log(" ----------------------------------------------------")
            self.LOG.error(" ***                                        진행중!!!")
            self.LOG.log(" ----------------------------------------------------")        
            return False

    def failover(self, curr, targ):
        curr_port_green = self.cfg.get(curr, "port_green")
        curr_port_red = self.cfg.get(curr, "port_red")
        targ_port_green = self.cfg.get(targ, "port_green")
        targ_port_red = self.cfg.get(targ, "port_red")
        
        intf_curr_green = Interface(curr_port_green)
        intf_curr_red = Interface(curr_port_red)
        
        intf_targ_green = Interface(targ_port_green)
        intf_targ_red = Interface(targ_port_red)
        
        self.LOG.info(" *** [INFO] Running failover for GREEN interface")
        self.LOG.log("     - Shutdown interface= %s" % intf_curr_green.interface_id)
        intf_curr_green.shutdown(True)
        
        self.LOG.log("     - Enable interface= %s" % intf_targ_green.interface_id)
        intf_targ_green.shutdown(False)
        
        self.LOG.info(" *** [INFO] Running failover for RED interface")
        self.LOG.log("     - Shutdown interface= %s" % intf_curr_red.interface_id)
        intf_curr_red.shutdown(True)
        
        self.LOG.log("     - Enable interface= %s" % intf_targ_red.interface_id)
        intf_targ_red.shutdown(False)  
        
        self.LOG.log(" ----------------------------------------------------")


    def is_applied(self, cfg_name):
        customer = self.cfg.get("failover", "customer")
        
        cfg_red_ip = self.cfg.get(customer, "red_ip")
        cfg_green_ip = self.cfg.get(customer, "green_ip")
        
        cfg_red_port = self.cfg.get(cfg_name, "port_red")
        cfg_green_port = self.cfg.get(cfg_name, "port_green")
        cfg_orange_port = self.cfg.get(cfg_name, "port_orange")
        
        intf_red = Interface(cfg_red_port)
        intf_green = Interface(cfg_green_port)
        intf_orange = Interface(cfg_orange_port)
        
        if intf_red.is_enabled() and intf_green.is_enabled() and intf_orange.is_enabled():
            return True
        else:
            return False
                
    def show_config(self, cfg_name, title):
        self.LOG.log(" ----------------------------------------------------")
        self.LOG.info(" *** %s (%s)" % ( title, cfg_name) )
        self.LOG.log(" ----------------------------------------------------")
    
        customer = self.cfg.get("failover", "customer")
        
        cfg_red_ip = self.cfg.get(customer, "red_ip")
        cfg_green_ip = self.cfg.get(customer, "green_ip")
        
        cfg_red_port = self.cfg.get(cfg_name, "port_red")
        cfg_green_port = self.cfg.get(cfg_name, "port_green")
        cfg_orange_port = self.cfg.get(cfg_name, "port_orange")
        
        intf_red = Interface(cfg_red_port)
        intf_green = Interface(cfg_green_port)
        intf_orange = Interface(cfg_orange_port)
        
        self.LOG.info(" - %s" % "RED")
        self.LOG.log("     . switch port= %s (%s)" % (cfg_red_port, intf_red.get_status()))
        self.LOG.log("     . ip address = %s" % cfg_red_ip)
        
        self.LOG.info(" - %s" % "GREEN")
        self.LOG.log("     . switch port= %s (%s)" % (cfg_green_port, intf_red.get_status()))
        self.LOG.log("     . ip address = %s" % cfg_green_ip)
        
        self.LOG.info(" - %s" % "ORANGE")
        self.LOG.log("     . switch port= %s (%s)" % (cfg_orange_port, intf_red.get_status()))
        
        self.LOG.log(" ----------------------------------------------------")