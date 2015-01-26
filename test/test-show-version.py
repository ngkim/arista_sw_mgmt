import sys
path="/root/admin/switch/arista/python-rpc"
if path not in sys.path:
    sys.path.append(path)

from arista_rpc import SwitchConnection, Vlan, SwitchConfig, Interface

def show_version():
    proxy = SwitchConnection().get_proxy()

    response = proxy.runCmds( 1, ["show version"] )
    print "The switch's system MAC addess is", response[0]["systemMacAddress"]

if __name__ == "__main__":
    show_version()
    