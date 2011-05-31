#!/usr/bin/python
#Copyright (C) 2011 Durieux David, d.durieux@siprossii.com
#
#This file is part of Shinken.
#
#Shinken is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Shinken is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with Shinken.  If not, see <http://www.gnu.org/licenses/>.


#This Class is a plugin for the Shinken Arbiter. It connect to
#a GLPI with webservice (xmlrpc, SOAP is garbage) and take all
#hosts. Simple way from now


import xmlrpclib

from shinken.basemodule import BaseModule

#This text is print at the import
print "Detected module : GLPI importer configuration for Arbiter"


properties = {
    'daemons' : ['arbiter'],
    'type' : 'glpi',
    'external' : False,
    'phases' : ['configuration'],
    }


#called by the plugin manager to get a broker
def get_instance(plugin):
    print "Get a Simple GLPI arbiter for plugin %s" % plugin.get_name()
    uri = plugin.uri
    login_name = plugin.login_name
    login_password = plugin.login_password
    if hasattr(plugin, 'use_property'):
        use_property = plugin.use_property
    else:
        use_property = 'otherserial'
    instance = Glpi_arbiter(plugin, uri, login_name, login_password, use_property)
    return instance



#Just get hostname from a GLPI webservices
class Glpi_arbiter(BaseModule):
    def __init__(self, mod_conf, uri, login_name, login_password, use_property):
        BaseModule.__init__(self, mod_conf)
        self.uri = uri
        self.login_name = login_name
        self.login_password = login_password
        self.use_property = use_property


    #Called by Arbiter to say 'let's prepare yourself guy'
    def init(self):
        print "I open the GLPI connection to %s" % self.uri
        self.con = xmlrpclib.ServerProxy(self.uri)
        print "Connexion opened"
        print "Authentification in progress"
        arg = {'login_name' : self.login_name , 'login_password' : self.login_password}
        res = self.con.glpi.doLogin(arg)
        self.session = res['session']
        print "My session number", self.session


    #Ok, main function that will load hosts from GLPI
    def get_objects(self):
        r = {'commands' : [],
             'hosts' : []}
        arg = {'session' : self.session}

        # Get commands
        all_commands = self.con.monitoring.shinkenCommands(arg)
        print "Get all commands", all_commands
        for command_info in all_commands:
            print "\n\n"
            print "Command info in GLPI", command_info
            h = {'command_name' : command_info['command_name'],
                 'command_line' : command_info['command_line'],
                 }
            #Then take use only if there is a value inside
            if command_info[self.use_property] != '':
                h['use'] = command_info[self.use_property]

            r['commands'].append(h)

        # Get hosts
        all_hosts = self.con.monitoring.shinkenHosts(arg)
        print "Get all hosts", all_hosts
        for host_info in all_hosts:
            print "\n\n"
            print "Host info in GLPI", host_info
            h = {'host_name' : host_info['host_name'],
                 'address' : host_info['address'],
                 'parents' : host_info['parents'],
                 'check_command' : host_info['check_command'],
                 'check_interval' : host_info['check_interval'],
                 'retry_interval' : host_info['retry_interval'],
                 'max_check_attempts' : host_info['max_check_attempts'],
                 'check_period' : host_info['check_period'],
                 'contacts' : host_info['contacts'],
                 }
            #Then take use only if there is a value inside
            if host_info[self.use_property] != '':
                h['use'] = host_info[self.use_property]

            r['hosts'].append(h)
        #print "Returning to Arbiter the hosts:", r
        return r
