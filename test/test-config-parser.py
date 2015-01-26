# -*- coding: utf-8 -*-
import sys, ConfigParser
path="/root/admin/switch/arista/python-rpc"
if path not in sys.path:
    sys.path.append(path)

from arista_rpc import SwitchConnection, Vlan, SwitchConfig, Interface
import utils

def test_get_int(cfg):
    config = ConfigParser.ConfigParser()
    config.read(cfg)
    
    interfaces = config.get("hybrid", "interfaces")
    print "interfaces= %s" % interfaces
    
    lint = utils.list_str_to_int(interfaces)
    
    print "list interfaces= %s" % lint
    
            
if __name__ == "__main__":
    test_get_int("switch.cfg")
    