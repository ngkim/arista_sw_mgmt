#from arista_rpc import SwitchConnection, Vlan, SwitchConfig, Interface
import sys

def is_in_sys_path(path):
    if path in sys.path:
        return True
    else:
        return False    
    
def add_sys_path(path):
    print "Add %s to sys.path" % path
    if is_in_sys_path(path):
        sys.path.append(path)
        if is_in_sys_path(path):
            print "OK!!!"
        else:
            print "Fail!!!"
    else:
        print "%s is already in sys.path" % path
        
if __name__ == "__main__":
    #show_version()
    add_sys_path("/root/admin/switch/arista/python-rpc")