#!/usr/bin/python

import pexpect
import sys

class SwitchConnection:

    def __init__(self, mgmtIp, mgmtUser, mgmtPass):
        self.mgmtIp = mgmtIp
        self.mgmtUser = mgmtUser
        self.mgmtPass = mgmtPass

    def connect(self):
        self.conn = pexpect.spawn ('ssh %s@%s' % (self.mgmtUser, self.mgmtIp))
#        self.conn.logfile = sys.stdout

        self.conn.expect ('word:')
        self.conn.sendline (self.mgmtPass)
        
        self.conn.expect ('SWITCH>')
        self.conn.sendline ('en')

        self.conn.expect('SWITCH#')

        return self

    def conf_t(self):
    #    self.spawn.expect('SWITCH#')
        try: 
          print "Entering configuration terminal..."
          self.conn.sendline('conf t')

          #print "Expect switch config..."
          #self.spawn.expect ('SWITCH(config)')

        except pexpect.EOF: 
          print "EOF exception"

    def expect(self, line_to_expect):
        self.conn.expect(line_to_expect)

    def get_before(self):
        return self.conn.before

    def sendline(self, cmd):
        try: 
          self.conn.sendline(cmd)

        except pexpect.EOF: 
          print "EOF exception"

    def close(self):
#        self.conn.expect('SWITCH#')
        self.conn.sendline('exit')

class Routing:

    def __init__(self, conn):
        self.conn = conn
        
    def enable_routing(self):
        self.conn.conf_t()
        self.conn.sendline ('ip routing')
        self.conn.sendline ('exit')

    def disable_routing(self):
        self.conn.conf_t()
        self.conn.sendline ('no ip routing')
        self.conn.sendline ('exit')

    def add_route(self, network, gateway):
        self.conn.conf_t()
        self.conn.sendline ('ip route %s %s' % (network, gateway))
        self.conn.sendline ('exit')

    def remove_route(self, network, gateway):
        self.conn.conf_t()
        self.conn.sendline ('no ip route %s %s' % (network, gateway))
        self.conn.sendline ('exit')

class MgmtInterface:

    def __init__(self, conn):
        self.conn = conn

    def set_ip_address(self, ip_address):
        self.ip_address = ip_address

        self.conn.conf_t()
        self.conn.sendline ('interface ma1')
        self.conn.sendline ('ip address %s' % self.ip_address)
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

    def clear_ip_address(self):
        self.conn.conf_t()
        self.conn.sendline ('interface ma1')
        self.conn.sendline ('no ip address')
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

class Interface:

    def __init__(self, interface_id, conn):
        self.interface_id = interface_id
        self.conn = conn

    def set_name(self, name):
        self.name = name

        self.conn.conf_t()
        self.conn.sendline ('interface eth%s' % self.interface_id)
        self.conn.sendline ('name %s' % self.name)
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

    def set_speed(self):
        self.conn.conf_t()
        self.conn.sendline ('interface eth%s' % self.interface_id)
        self.conn.sendline ('speed sfp-1000baset auto 100full')
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

    def clear_speed(self):
        self.conn.conf_t()
        self.conn.sendline ('interface eth%s' % self.interface_id)
        self.conn.sendline ('no speed sfp-1000baset auto 100full')
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

    def access_vlan(self, vlan):
        self.conn.conf_t()
        self.conn.sendline ('interface eth%s' % self.interface_id)
        self.conn.sendline ('switchport mode access')
        self.conn.sendline ('switchport access vlan %s' % vlan.get_vlan_id())
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')
     
    def _access_vlan(self, vlan_name, vlan_id):
        vlan = VLAN(vlan_name, vlan_id, self.conn)
        self.access_vlan(vlan)

    def clear_vlan(self):
        self.conn.conf_t()
        self.conn.sendline ('interface eth%s' % self.interface_id)
        self.conn.sendline ('no switchport mode access')
        self.conn.sendline ('no switchport access vlan')
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

    def set_trunk(self, vlan_ranges):
        self.vlan_ranges = vlan_ranges

        self.conn.conf_t()
        self.conn.sendline ('interface eth%s' % self.interface_id)
        self.conn.sendline ('switchport mode trunk')
        self.conn.sendline ('switchport trunk allowed vlan none')
        self.conn.sendline ('switchport trunk allowed vlan add %s' % self.vlan_ranges)
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

    def clear_trunk(self):
        self.conn.conf_t()
        self.conn.sendline ('interface eth%s' % self.interface_id)
        self.conn.sendline ('no switchport mode trunk')
        self.conn.sendline ('no switchport trunk allowed vlan')
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

    def show_running_config(self):
        self.conn.sendline ('show run interfaces eth%s' % self.interface_id)
        self.conn.expect ('SWITCH#')
        print self.conn.get_before()

    def shutdown(self):
        self.conn.conf_t()
        self.conn.sendline ('interface eth%s' % self.interface_id)
        self.conn.sendline ('shutdown')
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

    def no_shutdown(self):
        self.conn.conf_t()
        self.conn.sendline ('interface eth%s' % self.interface_id)
        self.conn.sendline ('no shutdown')
        self.conn.sendline ('exit')
        self.conn.sendline ('exit')

class VLAN:

    def __init__(self, vlan_name, vlan_id, conn):
        self.name = vlan_name
        self.vlan_id = vlan_id
        self.conn = conn
    
    def create(self):
        try: 
          print "Create VLAN %s NAME= %s" % (self.vlan_id, self.name)
          self.conn.sendline ('vlan %s' % self.vlan_id)
          self.conn.sendline ('name %s' % self.name)
  
          #self.conn.expect ('SWITCH(config-vlan-%s)#' % vlanId)
          self.conn.sendline ('exit')
  
          #self.conn.expect ('SWITCH(config)#')
          self.conn.sendline ('exit')
        except pexpect.TIMEOUT: 
          print "Timeout exception"
        except pexpect.EOF: 
          print "EOF exception"

    def create_if_not_exist(self):
        if vlan_mgmt.exists():
            print "VLAN %s exists" % vlanId
        else:
            print "VLAN %s does not exist. Create VLAN." % vlanId
            switch.conf_t()
            self.create()

    def delete(self):
        self.conn.expect ('SWITCH(config)#')
        self.conn.sendline ('no vlan %s' % vlanId)

        self.conn.expect ('SWITCH(config)#')
        self.conn.sendline ('exit')

    def exists(self):
        self.conn.expect ('SWITCH#')
        self.conn.sendline ('sh vlan %s' % vlanId)
    
        index=self.conn.expect (['Name', 'not found in current VLAN database'])
        if index == 0:
            return True
        elif index == 1:
            return False
            print "VLAN %s does not exist" % vlanId
 
    def get_vlan_id(self):
        return self.vlan_id


