#!/usr/bin/python
#Copyright (C) 2009 Gabes Jean, naparuba@gmail.com
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


#This Class is a plugin for the Shinken Broker. It is in charge
#to brok log into the syslog 


import syslog


#This text is print at the import
print "I am simple syslog Broker"


properties = {
    'type' : 'syslog',
    'external' : False,
    'phases' : ['running'],
    }


#called by the plugin manager to get a broker
def get_instance(plugin):
    print "Get a Syslog broker for plugin %s" % plugin.get_name()

    #Catch errors
    #path = plugin.path
    instance = Syslog_broker(plugin.get_name())
    return instance



#Class for the Merlindb Broker
#Get broks and puts them in merlin database
class Syslog_broker:
    def __init__(self, name):
        self.name = name


    #Called by Broker so we can do init stuff
    #TODO : add conf param to get pass with init
    #Conf from arbiter!
    def init(self):
        pass
        #self.q = self.properties['to_queue']
    

    def get_name(self):
        return self.name


    #Get a brok, parse it, and put in in database
    #We call functions like manage_ TYPEOFBROK _brok that return us queries
    def manage_brok(self, b):
        type = b.type
        manager = 'manage_'+type+'_brok'
        if hasattr(self, manager):
            f = getattr(self, manager)
            f(b)


    #A service check have just arrived, we UPDATE data info with this
    def manage_log_brok(self, b):
        data = b.data
        syslog.syslog(data['log'].encode('UTF-8'))


#    def main(self):
#        while True:
#            b = self.q.get() # can block here :)
#            self.manage_brok(b)
                        
