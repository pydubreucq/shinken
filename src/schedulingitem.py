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


#from command import CommandCall
#from copy import deepcopy
from item import Item
#from util import to_int, to_char, to_split, to_bool
import random
import time

from check import Check
from notification import Notification
from timeperiod import Timeperiod
from macroresolver import MacroResolver
from eventhandler import EventHandler



class SchedulingItem(Item):
    #Add a flapping change, but no more than 20 states
    #Then update the self.is_flapping bool by calling update_flapping
    def add_flapping_change(self, b):
        self.flapping_states.append(b)
        #Just 20 changes
        if len(self.flapping_changes) > 20:
            self.flapping_changes.pop(0)
        #Now we add a value, we update the is_flapping prop
        self.update_flapping()


    #We update the is_flapping prop with value in self.flapping_states
    #Old values have less weight than new ones
    def update_flapping(self):
        #We compute the flapping change in %
        r = 0.0
        i = 0
        for b in self.flapping_changes:
           i += 1
           if b:
               r += i*(1.2-0.8)/20 + 0.8
        r = r / 20

        #Now we get the low_flap_threshold and high_flap_threshold values
        #They can be from self, or class
        (low_flap_threshold, high_flap_threshold) = (self.low_flap_threshold, self.high_flap_threshold)
        if low_flap_threshold == -1:
            cls = self.__class__
            low_flap_threshold = cls.low_flap_threshold
        if high_flap_threshold  == -1:
            cls = self.__class__
            high_flap_threshold = cls.high_flap_threshold

        #Now we check is flapping change
        if self.is_flapping and r < low_flap_threshold:
            self.is_flapping = False
        if not self.is_flapping and r >= high_flap_threshold:
            self.is_flapping = True
        self.percent_state_change = r


    #Add an attempt but cannot be more than max_check_attempts
    def add_attempt(self):
        self.attempt += 1
        self.attempt = min(self.attempt, self.max_check_attempts)


    #Return True if attempt is at max
    def is_max_attempts(self):
        return self.attempt >= self.max_check_attempts


    #Call by scheduler to see if last state is older than
    #freshness_threshold if check_freshness, then raise a check
    #even if active check is disabled
    def do_check_freshness(self):
        now = time.time()
        #Before, check if class (host or service) have check_freshness OK
        #Then check if item whant fressness, then check fressness
        cls = self.__class__
        if not self.in_checking:
            if cls.check_freshness:
                if self.check_freshness and self.freshness_threshold != 0:
                    if self.last_state_update < now - self.freshness_threshold:
                        print "Warning : ", self.get_name(), " is not so fresh! I raise a new check", self.check_freshness, self.freshness_threshold, self.last_state_update
                        return self.launch_check(now)
        return None


    #When all dep are resolved, this function say if
    #action can be raise or not by viewing dep status
    #network_dep have to be all raise to be no action
    #logic_dep : just one is enouth
    def is_no_action_dependant(self):
        #Use to know if notif is raise or not
        #no_action = False
        parent_is_down = []
        #So if one logic is Raise, is dep
        #is one network is no ok, is not dep
        #at teh end, raise no dep
        for (dep, status, type, tp) in self.act_depend_of:
            #For logic_dep, only one state raise put no action
            if type == 'logic_dep':
                for s in status:
                    if dep.is_state(s):
                        return True
            #more complicated: if none of the states are match, the host is down
            else:
                p_is_down = False
                dep_match = [dep.is_state(s) for s in status] 
                if True in dep_match:#the parent match a case, so he is down
                    p_is_down = True
                parent_is_down.append(p_is_down)
        #if a parent is not down, no dep can explain the pb
        if False in parent_is_down:
            return False
        else:# every parents are dead, so... It's not my fault :)
            return True


    #Use to know if I raise dependency for soneone else (with status)
    #If I do not raise dep, maybe my dep raise me. If so, I raise dep.
    #So it's a recursive function
    def do_i_raise_dependency(self, status):
        #Do I raise dep?
        for s in status:
            if self.is_state(s):
                return True
        #Ok, I do not raise dep, but my dep maybe raise me
        now = time.time()
        for (dep, status, type, tp) in self.chk_depend_of:
            if dep.do_i_raise_dependency(status):
                if tp is None and tp.is_time_valid(now):
                    return True
        #No, I relly do not raise...
        return False


    #Use to know if my dep force me not to be checked
    #So check the chk_depend_of if they raise me
    def is_no_check_dependant(self):
        now = time.time()
        for (dep, status, type, tp) in self.chk_depend_of:
            if tp is None and tp.is_time_valid(now):
                if dep.do_i_raise_dependency(status):
                        return True
        return False


    #call by a bad consume check where item see that he have dep
    #and maybe he is not in real fault.
    def raise_dependancies_check(self, ref_check):
        now = time.time()
        cls = self.__class__
        checks = []
        for (dep, status, type, tp) in self.act_depend_of:
            #If the dep timeperiod is not valid, do notraise the dep,
            #None=everytime
            if tp is None or tp.is_time_valid(now):
                #if the update is 'fresh', do not raise dep,
                #cached_check_horizon = cached_service_check_horizon for service
                if dep.last_state_update < now - cls.cached_check_horizon:
                    c = dep.launch_check(now, ref_check)
                    checks.append(c)
                else:
                    print "**************** The state is FRESH", dep.host_name, time.asctime(time.localtime(dep.last_state_update))
        return checks


    #Main scheduling function
    #If a check is in progress, or active cehck are disabled, do
    #not schedule a check.
    #The check interval change with HARD state or not:
    #SOFT: retry_interval
    #HARD: check_interval
    #The first scheduling is a little random, so all checks
    #are not launch in the same time...
    def schedule(self, force=False, force_time=None):
        #print "Scheduling:", self.get_name()
        #if last_chk == 0 put in a random way so all checks 
        #are not in the same time
        
        now = time.time()
        #next_chk il already set, do not change
        #if self.next_chk >= now or self.in_checking and not force:
        if self.in_checking and not force:
            return None

        cls = self.__class__
        #if no active check and no force, no check
        #print "Service check?", cls.execute_checks
        if (not self.active_checks_enabled or not cls.execute_checks) and not force:
            return None

        #If I do not have an check_timeperiod and no force time, i do nothing
        if (not hasattr(self, 'check_period') or self.check_period == None and force_time==None):
            return None

        #Interval change is in a HARD state or not
        if self.state_type == 'HARD':
            interval = self.check_interval * 60
        else: #TODO : if no retry_interval?
            interval = self.retry_interval * 60

        #The next_chk is pass so we need a new one
        #so we got a check_interval
        if self.next_chk == 0:
            r = interval * (random.random() - 0.5)
            time_add = interval/2 + r
        else:
            time_add = interval

        if force_time is None:
            self.next_chk = self.check_period.get_next_valid_time_from_t(now + time_add)
        else:
            self.next_chk = force_time

        #If next time is None, do not go
        if self.next_chk == None:
            #TODO : FUCK
            print "Sorry, I do not launch the check for", self.get_name(), "because next_check is None"
            
        #Get the command to launch
        return self.launch_check(self.next_chk)


    def remove_in_progress_check(self, c):
        #The check is consume, uptade the in_checking propertie
        if c in self.checks_in_progress:
            self.checks_in_progress.remove(c)
        else:
            print "Not removing check", c, "for ", self.get_name()
        self.update_in_checking()


    #Is in checking if and ony if there are still checks no consumed
    def update_in_checking(self):
        self.in_checking = (len(self.checks_in_progress) != 0)


    #Del just a notification that is retured
    def remove_in_progress_notification(self, n):
        if n.id in self.notifications_in_progress:
            n.status = 'zombie'
            del self.notifications_in_progress[n.id]


    #We do not need ours currents pending notifications,
    #so we zombify them and clean our list
    def remove_in_progress_notifications(self):
        for n in self.notifications_in_progress.values():
            self.remove_in_progress_notification(n)
    

    #Get a event handler if item got an event handler 
    #command. It must be enabled locally and globally
    def get_event_handlers(self):
        cls = self.__class__
        if self.event_handler == None or not self.event_handler_enabled or self.is_in_downtime or not cls.enable_event_handlers:
            return []

        print self.event_handler.__dict__
        events = []
        m = MacroResolver()
        data = self.get_data_for_event_handler()
        cmd = m.resolve_command(self.event_handler, data)
        e = EventHandler(cmd, timeout=cls.event_handler_timeout)
        print "Event handler call created"
        print e.__dict__
        events.append(e)
        return events


    #consume a check return and send action in return
    #main function of reaction of checks like raise notifications
    #Special case:
    #is_flapping : immediate notif when problem
    #is_in_downtime : no notification
    #is_volatile : notif immediatly (service only)
    def consume_result(self, c):
        now = time.time()
        OK_UP = self.__class__.ok_up #OK for service, UP for host
        
        #We check for stalking if necessery
        #so if check is here
        self.manage_stalking(c)

        #Latency can be <0 is we get a check from the retention file
        #so if <0, set 0
        try:
            self.latency = max(0, c.check_time - c.t_to_go)
        except TypeError:
            #DBG
            print "ERROR FUCK:", c.check_time, c.t_to_go, c.ref.get_name()
        self.execution_time = c.execution_time
        self.last_chk = c.check_time
        self.output = c.output
        self.long_output = c.long_output
        self.perf_data = c.perf_data

        #Before set state, module thems
        for rm in self.resultmodulations:
            if rm != None:
                (c.exit_status, self.output, self.long_output) = rm.module_return(c.exit_status, self.output, self.long_output)
        
        #If we got a bad result on a normal check, and we have dep,
        #we raise dep checks
        #put the actual check in waitdep and we return all new checks
        if c.exit_status != 0 and c.status == 'waitconsume' and len(self.act_depend_of) != 0:
            #print self.get_name(), "I depend of someone, and I need a result"
            c.status = 'waitdep'
            #Make sure the check know about his dep
            #C is my check, and he wants dependancies
            checks = self.raise_dependancies_check(c)
            to_del = []
            for check in checks:
                #C is a int? Ok, in fact it's a check that is
                #already in progress
                if isinstance(check, int):
                    c.depend_on.append(check)
                    to_del.append(check)
                else:
                    #print c.id, self.get_name()," I depend on check", check.id
                    c.depend_on.append(check.id)
            for i in to_del:
                checks.remove(i)
            return checks

        self.set_state_from_exit_status(c.exit_status)
        self.add_attempt()

        #The check is consume, uptade the in_checking propertie
        self.remove_in_progress_check(c)

        #C is a check and someone wait for it
        if c.status == 'waitconsume' and c.depend_on_me != []:
            #print c.id, self.get_name(), "OK, someone wait for me", len(c.depend_on_me)
            c.status = 'havetoresolvedep'

        #if finish, check need to be set to a zombie state to be removed
        #it can be change if necessery before return, like for dependancies
        if c.status == 'waitconsume' and c.depend_on_me == []:
            #print "SRV OK, nobody depend on me!!"
            c.status = 'zombie'
        
        #Use to know if notif is raise or not
        no_action = False
        #C was waitdep, but now all dep are resolved, so check for deps
        if c.status == 'waitdep':
            if c.depend_on_me != []:
                #print self.get_name(), "OK, someone wait for me", len(c.depend_on_me)
                c.status = 'havetoresolvedep'
            else:
                #print self.get_name(), "Great, noboby wait for me!"
                c.status = 'zombie'
            #Check deps
            no_action = self.is_no_action_dependant()
            #print "No action:", no_action

        #If no_action is False, maybe we are in downtime,
        #so no_action become true
        if no_action == False:
            for dt in self.downtimes:
                if dt.is_in_downtime():
                    no_action = True

        #If ok in ok : it can be hard of soft recovery
        if c.exit_status == 0 and (self.last_state == OK_UP or self.last_state == 'PENDING'):
            #action in return can be notification or other checks (dependancies)
            if (self.state_type == 'SOFT' or self.state_type == 'SOFT-RECOVERY') and self.last_state != 'PENDING':
                if self.is_max_attempts() and (self.state_type == 'SOFT' or self.state_type == 'SOFT-RECOVERY'):
                    self.state_type = 'HARD'
                else:
                    self.state_type = 'SOFT-RECOVERY'
            else:
                self.attempt = 1
                self.state_type = 'HARD'
            return []
        
        #If OK on a no OK : if SOFT-> SOFT recovery, if hard, still hard
        elif c.exit_status == 0 and (self.last_state != OK_UP and self.last_state != 'PENDING'):
            if self.state_type == 'SOFT':
                self.state_type = 'SOFT-RECOVERY'
            elif self.state_type == 'HARD':
                #Ok, we can get event_handlers here
                res = self.get_event_handlers()
                #Ok, so current notifications are not need, we 'zombie' thems
                self.remove_in_progress_notifications()
                if not no_action:
                    res.extend(self.create_notifications('RECOVERY'))
                return res
            return []
        
        #Volatile part
        #Only for service
        elif c.exit_status != 0 and hasattr(self, 'is_volatile') and self.is_volatile:
            self.state_type = 'HARD'
            #Ok, event handlers here too
            res = self.get_event_handlers()
            if not no_action:
                res.extend(self.create_notifications('PROBLEM'))
            return res
        
        #If no OK in a OK -> going to SOFT
        elif c.exit_status != 0 and (self.last_state == OK_UP or self.last_state == 'PENDING'):
            if self.is_max_attempts():
                # if max_attempts == 1
                self.state_type = 'HARD'
                self.attempt = 1
            else:
                self.state_type = 'SOFT'
                self.attempt = 1
            #Oh? This is the typical go for a event handler :)
            res = self.get_event_handlers()
            return res
        
        #If no OK in a no OK : if hard, still hard, if soft,
        #check at self.max_check_attempts
        #when we go in hard, we send notification
        elif c.exit_status != 0 and self.last_state != OK_UP:
            if self.is_max_attempts() and self.state_type == 'SOFT':
                #Ok here is when we just go to the hard state
                #So event handlers here too
                res = self.get_event_handlers()
                self.state_type = 'HARD'
                #raise notification only if self.notifications_enabled is True
                if self.notifications_enabled:
                    if not no_action:
                        res.extend(self.create_notifications('PROBLEM'))
                return res
        return []


    #Just update the notification command by resolving Macros
    def update_notification_command(self, n):
        m = MacroResolver()
        data = self.get_data_for_notifications(n.contact, n)
        n.command = m.resolve_command(n.command_call, data)


    #Create notifications
    def create_notifications(self, type):
        #if notif is disabled, not need to go thurser

        cls = self.__class__
        if not self.notifications_enabled or self.is_in_downtime or not cls.enable_notifications:
            return []

        #A recovery is usefull only if previous notif were send
        if type == 'RECOVERY' and self.current_notification_number == 0:
            return []

        #Recovery make the counter of notif become 0
        if type == 'RECOVERY':
            self.current_notification_number = 0
        else:
            self.current_notification_number += 1

        print "Raise notification of type", type, "for", self.get_name()
        
        notifications = []
        now = time.time()
        t = self.notification_period.get_next_valid_time_from_t(now)
        #m = MacroResolver()
        
        for contact in self.contacts:
            #Get the propertie name for notif commands, like
            #service_notification_commands for service
            notif_commands_prop = cls.my_type+'_notification_commands'
            notif_commands = getattr(contact, notif_commands_prop)
            for cmd in notif_commands:
                n = Notification(type, 'scheduled', 'VOID', cmd, self, contact, t, timeout=cls.notification_timeout)
                #The notif must be fill with current data, 
                #so we create the commmand now
                self.update_notification_command(n)
                #data = self.get_data_for_notifications(contact, n)
                #n.command = m.resolve_command(cmd, data)
                #Maybe the contact do not want this notif? Arg!
                if self.is_notification_launchable(n, contact):
                    notifications.append(n)
                #Add in ours queues
                self.notifications_in_progress[n.id] = n
        return notifications


    #We just send a notification, we need new ones in notification_interval
    def get_new_notification_from(self, n):
        now = time.time()
        cls = self.__class__
        #a recovery notif is send ony one time
        if n.type == 'RECOVERY':
            return None
        #TODO : resolv command...
        notif_nb = n.notif_nb
        new_n = Notification(n.type, 'scheduled','', n.command_call, n.ref, n.contact, now + self.notification_interval * 60, notif_nb + 1, timeout=cls.notification_timeout)
        self.notifications_in_progress[new_n.id] = new_n
        return new_n


    #return a check to check the host/service
    def launch_check(self, t, ref_check = None):
        c = None
        cls = self.__class__
        
        #if I'm already in checking, Why launch a new check?
        #If ref_check_id is not None , this is a dependancy_ check
        #If none, it might be a forced check, so OK, I do a new
        if self.in_checking and ref_check != None:
            #print "FUCK, I do not want to launch a new check, I alreay have one"
            c_in_progress = self.checks_in_progress[0] #0 is OK because in_checking is True
            if c_in_progress.t_to_go > time.time(): #Very far?
                c_in_progress.t_to_go = time.time() #No, I want a check right NOW
            c_in_progress.depend_on_me.append(ref_check)
            return c_in_progress.id

        if not self.is_no_check_dependant():
            #Get the command to launch
            m = MacroResolver()
            data = self.get_data_for_checks()
            command_line = m.resolve_command(self.check_command, data)
            
            #Make the Check object and put the service in checking
            #print "Asking for a check with command:", command_line
            c = Check('scheduled', command_line, self, t, ref_check, timeout=cls.check_timeout)
            #We keep a trace of all checks in progress
            #to know if we are in checking_or not
            self.checks_in_progress.append(c)
            #print self.get_name()+" we ask me for a check" + str(c.id)
        self.update_in_checking()
        #We need to return the check for scheduling adding
        return c
