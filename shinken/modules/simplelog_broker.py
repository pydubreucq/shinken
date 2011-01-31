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
#to brok information of the service perfdata into the file
#var/service-perfdata
#So it just manage the service_check_return
#Maybe one day host data will be usefull too
#It will need just a new file, and a new manager :)


import time
import shutil
import os
import sys
import datetime


from shinken.basemodule import Module
from shinken.util import get_day


#This text is print at the import
print "I am simple log Broker"


properties = {
    'type' : 'simple_log',
    'external' : True,
    'phases' : ['running'],
    }


#called by the plugin manager to get a broker
def get_instance(plugin):
    print "Get a Simple log broker for plugin %s" % plugin.get_name()

    #Catch errors
    path = plugin.path

    archive_path = plugin.archive_path
    #Clean the archive_path trailing / if need
    if archive_path[-1] == os.sep:
        archive_path = archive_path[:-1]

    instance = Simple_log_broker(plugin, path, archive_path)
    return instance



#Class for the Merlindb Broker
#Get broks and puts them in merlin database
class Simple_log_broker(Module):
    def __init__(self, modconf, path, archive_path):
        Module.__init__(self, modconf)
        self.path = path
        self.archive_path = archive_path


    #Check the path file age. If it's last day, we
    #archive it.
    #Return True if the file has moved
    def check_and_do_archive(self, first_pass = False):
        now = int(time.time())
        #first check if the file last mod (or creation) was
        #not our day
        try :
            t_last_mod = int(float(str(os.path.getmtime(self.path))))
        except OSError: #there should be no path from now, so no move :)
            return False
        #print "Ctime %d" % os.path.getctime(self.path)
        t_last_mod_day = get_day(t_last_mod)
        today = get_day(now)
        #print "Dates: t_last_mod : %d, t_last_mod_day: %d, today : %d" % (t_last_mod, t_last_mod_day, today)
        if t_last_mod_day != today:
            print "We are archiving the old log file"

            #For the first pass, it's not already open
            if not first_pass:
                self.file.close()

            #Now we move it
            #Get a new name like MM

            #f_name is like nagios.log
            f_name = os.path.basename(self.path)
            #remove the ext -> (nagios,.log)
            (f_base_name, ext) = os.path.splitext(f_name)
            #make the good looking day for archive name
            #like -05-09-2010-00
            d = datetime.datetime.fromtimestamp(today)
            s_day = d.strftime("-%m-%d-%Y-00")
            archive_name = f_base_name+s_day+ext
            file_archive_path = os.sep.join([self.archive_path, archive_name])
            print "Moving the old log file from %s to %s" % (self.path, file_archive_path)

            shutil.move(self.path, file_archive_path)

            #and we overwrite it
            print "I open the log file %s" % self.path
            self.file = open(self.path,'a')

            return True
        return False


    #A service check have just arrived, we UPDATE data info with this
    def manage_log_brok(self, b):
        data = b.data
        self.file.write(data['log'].encode('UTF-8'))
        self.file.flush()


    def init(self):
        moved = self.check_and_do_archive(first_pass=True)
        if not moved:
            print "I open the log file %s" % self.path
            self.file = open(self.path,'a')

    def do_loopturn(self):
        self.check_and_do_archive()
        b = self.to_q.get() # can block here :)
        self.manage_brok(b)
