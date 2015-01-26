# -*- coding: utf-8 -*-
from datetime import datetime
from subprocess import Popen, PIPE
import re

class TimeUtil:
    
    def start(self):
        self.start = datetime.now()
    
    def stop(self):     
        self.stop = datetime.now()

    def get_duration(self):
        delta = self.stop - self.start
        return delta.total_seconds()

class InteractionUtil:
    
    def ask_user(self, msg):
        get_input=False
        result = False
        
        try:
            while not get_input:
                user_input = raw_input("%s (y/n) " % msg)
                if user_input.strip() in ["y", "yes"]:
                    result=True
                    get_input=True                
                elif user_input.strip() in ["n", "no"]:
                    result=False
                    get_input=True
                else:
                    get_input=False
            Console().log(" ----------------------------------------------------")
        except KeyboardInterrupt:
            print ""
            result = False
                
        return result
    
class NetUtil:
    
    def get_mac_from_arp(self, ip_address):
        Popen(["ping", "-c 1", ip_address], stdout = PIPE)
        pid = Popen(["arp", "-n", ip_address], stdout = PIPE)
        s = pid.communicate()[0]
    
        result=re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s)
    
        mac = ""
        if result:
            mac = result.groups()[0]        
        #Console().info(" *** [INFO] get_mac: ip_address= %s mac= %s" % (ip_address, mac.upper()))
        return mac

class StringUtil:
    
    # 문자열을 int 배열로 만들어줌
    # 예) "1-4,7,9" ==> [1,2,3,4,7,9] 
    def list_str_to_int(self, list_str):
        lstr = list_str.split(",")
        
        lint = []
        for str in lstr:
            lstr1 = str.split("-")
            
            if len(lstr1) == 2:
                min = int(lstr1[0])
                max = int(lstr1[1]) + 1 # range함수에서 max 값을 포함할 수 있도록 1을 더함 
            
                for i in range(min, max):
                    lint.append(i)
            else:
                lint.append(int(str))
        
        return lint
        
 
class Console:
    
    def __init__(self):
        self.INFO = '\033[94m'
        self.DBG = '\033[93m'        
        self.WARN = '\033[92m'
        self.ERR = '\033[91m'
        
        self.ENDC = '\033[0m'
            
    def log(self, msg, type = "" ):
        if type == "info":
            print self.INFO + "%s" % msg + self.ENDC
        elif type == "debug":
            print self.DBG + "%s" % msg + self.ENDC
        elif type == "warn":
            print self.WARN + "%s" % msg + self.ENDC
        elif type == "error":
            print self.ERR + "%s" % msg + self.ENDC
        else:
            print "%s" % msg
    
    def info(self, msg):
        self.log(msg, "info") 
            
    def debug(self, msg):
        self.log(msg, "debug")
        
    def error(self, msg):
        self.log(msg, "error")        