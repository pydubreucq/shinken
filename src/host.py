from command import CommandCall
from graph import digraph
from item import Item, Items
from util import to_int, to_char, to_split, to_bool
import time, random
from macroresolver import MacroResolver
from check import Check
from notification import Notification

class Host(Item):
    id = 1 #0 is reserved for host (primary node for parents)
    properties={'host_name': {'required': True},
                'alias': {'required':  True},
                'display_name': {'required': False, 'default':'none'},
                'address': {'required': True},
                'parents': {'required': False, 'default': '' , 'pythonize': to_split},
                'hostgroups': {'required': False, 'default' : ''},
                'check_command': {'required': False, 'default':''},
                'initial_state': {'required': False, 'default':'u', 'pythonize': to_char},
                'max_check_attempts': {'required': True , 'pythonize': to_int},
                'check_interval': {'required': False, 'default':'0', 'pythonize': to_int},
                'retry_interval': {'required': False, 'default':'0', 'pythonize': to_int},
                'active_checks_enabled': {'required': False, 'default':'1', 'pythonize': to_bool},
                'passive_checks_enabled': {'required': False, 'default':'1', 'pythonize': to_bool},
                'check_period': {'required': True},
                'obsess_over_host': {'required': False, 'default':'0' , 'pythonize': to_bool},
                'check_freshness': {'required': False, 'default':'0', 'pythonize': to_bool},
                'freshness_threshold': {'required': False, 'default':'0', 'pythonize': to_int},
                'event_handler': {'required': False, 'default':''},
                'event_handler_enabled': {'required': False, 'default':'0', 'pythonize': to_bool},
                'low_flap_threshold': {'required':False, 'default':'25', 'pythonize': to_int},
                'high_flap_threshold': {'required': False, 'default':'50', 'pythonize': to_int},
                'flap_detection_enabled': {'required': False, 'default':'1', 'pythonize': to_bool},
                'flap_detection_options': {'required': False, 'default':'o,d,u', 'pythonize': to_split},
                'process_perf_data': {'required': False, 'default':'1', 'pythonize': to_bool},
                'retain_status_information': {'required': False, 'default':'1', 'pythonize': to_bool},
                'retain_nonstatus_information': {'required': False, 'default':'1', 'pythonize': to_bool},
                'contacts': {'required': True},
                'contact_groups': {'required': True},
                'notification_interval': {'required': True, 'pythonize': to_int},
                'first_notification_delay': {'required': False, 'default':'0', 'pythonize': to_int},
                'notification_period': {'required': True},
                'notification_options': {'required': False, 'default':'d,u,r,f', 'pythonize': to_split},
                'notifications_enabled': {'required': False, 'default':'1', 'pythonize': to_bool},
                'stalking_options': {'required': False, 'default':'o,d,u', 'pythonize': to_split},
                'notes': {'required': False, 'default':''},
                'notes_url': {'required': False, 'default':''},
                'action_url': {'required': False, 'default':''},
                'icon_image': {'required': False, 'default':''},
                'icon_image_alt': {'required': False, 'default':''},
                'vrml_image': {'required': False, 'default':''},
                'statusmap_image': {'required': False, 'default':''},
                '2d_coords': {'required': False, 'default':''},
                '3d_coords': {'required': False, 'default':''},
                'failure_prediction_enabled': {'required' : False, 'default' : '0', 'pythonize': to_bool}
                }

    running_properties = {
        'last_chk' : 0,
        'next_chk' : 0,
        'in_checking' : False,
        'latency' : 0,
        'attempt' : 0,
        'state' : 'PENDING',
        'state_type' : 'SOFT',
        'output' : '',
        'long_output' : ''
        }


    macros = {'HOSTNAME' : 'host_name',
              'HOSTDISPLAYNAME' : 'display_name',
              'HOSTALIAS' :  'alias',
              'HOSTADDRESS' : 'address',
              'HOSTSTATE' : 'state',
              'HOSTSTATEID' : 'get_stateid',
              'LASTHOSTSTATE' : 'last_state',
              'LASTHOSTSTATEID' : 'get_last_stateid',
              'HOSTSTATETYPE' : 'state_type',
              'HOSTATTEMPT' : 'attempt',
              'MAXHOSTATTEMPTS' : 'max_check_attempts',
              'HOSTEVENTID' : None,
              'LASTHOSTEVENTID' : None,
              'HOSTPROBLEMID' : None,
              'LASTHOSTPROBLEMID' : None,
              'HOSTLATENCY' : 'latency',
              'HOSTEXECUTIONTIME' : 'exec_time',
              'HOSTDURATION' : 'get_duration',
              'HOSTDURATIONSEC' : 'get_duration_sec',
              'HOSTDOWNTIME' : 'get_downtime',
              'HOSTPERCENTCHANGE' : 'get_percent_change',
              'HOSTGROUPNAME' : 'get_groupname',
              'HOSTGROUPNAMES' : 'get_groupnames',
              'LASTHOSTCHECK' : 'last_chk',
              'LASTHOSTSTATECHANGE' : 'last_state_change',
              'LASTHOSTUP' : 'last_host_up',
              'LASTHOSTDOWN' : 'last_host_down',
              'LASTHOSTUNREACHABLE' : 'last_host_unreachable',
              'HOSTOUTPUT' : 'output',
              'LONGHOSTOUTPUT' : 'long_output',
              'HOSTPERFDATA' : 'perf_data',
              'HOSTCHECKCOMMAND' : 'get_check_command',
              'HOSTACKAUTHOR' : 'ack_author',
              'HOSTACKAUTHORNAME' : 'get_ack_author_name',
              'HOSTACKAUTHORALIAS' : 'get_ack_author_alias',
              'HOSTACKCOMMENT' : 'ack_comment',
              'HOSTACTIONURL' : 'action_url',
              'HOSTNOTESURL' : 'notes_url',
              'HOSTNOTES' : 'notes',
              'TOTALHOSTSERVICES' : 'get_total_services',
              'TOTALHOSTSERVICESOK' : 'get_total_services_ok',
              'TOTALHOSTSERVICESWARNING' : 'get_total_services_warning',
              'TOTALHOSTSERVICESUNKNOWN' : 'get_total_services_unknown',
              'TOTALHOSTSERVICESCRITICAL' : 'get_total_services_critical'
        }



    def clean(self):
        pass


    #Check is required prop are set:
    #template are always correct
    #contacts OR contactgroups is need
    def is_correct(self):
        if self.is_tpl:
            return True
        for prop in Host.properties:
            if not self.has(prop) and Host.properties[prop]['required']:
                if prop == 'contacts' or prop == 'contacgroups':
                    pass
                else:
                    print "I do not have", prop
                    return False
        if self.has('contacts') or self.has('contacgroups'):
            return True
        else:
            print "I do not have contacts nor contacgroups"
            return False


    #TODO make a real value
    def get_total_services(self):
        return '99999'



    def set_state_from_exit_status(self, status):
        self.last_state = self.state
        if status == 0:
            self.state = 'UP'
        elif status == 1 or status == 2 or status == 3:
            self.state = 'DOWN'
        else:
            self.state = 'UNDETERMINED'


    #consume a check return and send action in return
    #main function of reaction of checks like raise notifications
    def consume_result(self, c):
        self.in_checking = False
        now = time.time()
        
        latency = now - c.t_to_go
        self.latency = latency
        self.output = c.output
        self.long_output = c.long_output
        #print "Latency:", self.latency
        #print "Check return", c.exit_status
        #print "Before:", self.state,"/" ,self.state_type, "test", self.attempt ,"/", self.max_check_attempts

        self.set_state_from_exit_status(c.exit_status)
        #self.last_state = self.state

        #If ok in ok : it can be hard of soft recovery
        if c.exit_status == 0 and (self.last_state == 'OK' or self.last_state == 'PENDING'):
            #if finish, check need to be set to a zombie state to be removed
            c.status = 'zombie'
            #action in return can be notification or other checks (dependancies)
            if (self.state_type == 'SOFT' or self.state_type == 'SOFT-RECOVERY') and self.last_state != 'PENDING':
                self.attempt += 1
                self.attempt = min(self.attempt, self.max_check_attempts)
                if self.attempt >= self.max_check_attempts and (self.state_type == 'SOFT' or self.state_type == 'SOFT-RECOVERY'):
                    self.state_type = 'HARD'
                    print "Raise notification"
                else:
                    self.state_type = 'SOFT-RECOVERY'
            else:
                self.attempt = 1
                self.state_type = 'HARD'
            print "Quitting 1 withstate:", self.state,"/" ,self.state_type, "test", self.attempt ,"/", self.max_check_attempts
            return []
        #If OK on a no OK : if SOFT-> SOFT recovery, if hard, still hard
        elif c.exit_status == 0 and (self.last_state != 'OK' and self.last_state != 'PENDING'):
            c.status = 'zombie'
            self.attempt += 1
            self.attempt = min(self.attempt, self.max_check_attempts)
            if self.state_type == 'SOFT':
                self.state_type = 'SOFT-RECOVERY'
            print "Quitting 1 bis withstate:", self.state,"/" ,self.state_type, "test", self.attempt ,"/", self.max_check_attempts
            return []
        #If no OK in a OK -> going to SOFT
        elif c.exit_status != 0 and self.last_state == 'OK':
            c.status = 'zombie'
            self.state_type = 'SOFT'
            self.attempt = 1
            print "Quitting 2 with state:", self.state,"/" ,self.state_type, "test", self.attempt ,"/", self.max_check_attempts
            return []
        #If no OK in a no OK : if hard, still hard, if soft, check at self.max_check_attempts
        #when we go in hard, we send notification
        elif c.exit_status != 0 and self.last_state != 'OK':
            c.status = 'zombie'
            self.attempt += 1
            self.attempt = min(self.attempt, self.max_check_attempts)
            if self.attempt >= self.max_check_attempts and self.state_type == 'SOFT':
                self.state_type = 'HARD'
                print "Raise notification"
                print "Quitting 3 withstate:", self.state,"/" ,self.state_type, "test", self.attempt ,"/", self.max_check_attempts
                #raise notification only if self.notifications_enabled is True
                if self.notifications_enabled:
                    return self.create_notifications()
                else:
                    return []
            print "Quitting 3 withstate:", self.state,"/" ,self.state_type, "test", self.attempt ,"/", self.max_check_attempts
            return []
        c.status = 'zombie'
        self.attempt += 1
        self.attempt = min(self.attempt, self.max_check_attempts)
        print "Quitting 4 withstate:", self.state,"/" ,self.state_type, "test", self.attempt ,"/", self.max_check_attempts
        return []


    def schedule(self):
        #if last_chk == 0 put in a random way so all checks are not in the same time
        
        now = time.time()
        #next_chk il already set, do not change
        if self.next_chk >= now or self.in_checking:
            return None
        
        #Interval change is in a HARD state or not
        if self.state == 'HARD':
            interval = self.check_interval
        else:
            interval = self.retry_interval
        
        #The next_chk is pass so we need a new one
        #so we got a check_interval
        if self.next_chk == 0:
            r = interval * (random.random() - 0.5)
            self.next_chk = self.check_period.get_next_valid_time_from_t(now + interval*10/2 + r*10)
        else:
            self.next_chk = self.check_period.get_next_valid_time_from_t(now + interval*10)
        
        print "Next check", time.asctime(time.localtime(self.next_chk))
        
        #Get the command to launch
        return self.launch_check(self.next_chk)    



    #Create notifications but without commands. It will be update juste before being send
    def create_notifications(self):
        notifications = []
        now = time.time()
        t = self.notification_period.get_next_valid_time_from_t(now)
        print "::::::::::::::::::We are creating a notification for", time.asctime(time.localtime(t))
        print self
        for contact in self.contacts:
            for cmd in contact.host_notification_commands:
                #create without real command, it will be update just before being send
                notifications.append(Notification('scheduled', 'VOID', {'host' : self.id, 'contact' : contact.id, 'command': cmd}, 'host', t))
        return notifications


    #We are just going to launch the notif to the poller
    #so we must actualise the command (Macros)
    def update_notification(self, n,  contact):
        m = MacroResolver()
        command = n.ref['command']
        n._command = m.resolve_command(command, self, None, contact)


    #see if the notification is launchable (time is OK and contact is OK too)
    def is_notification_launchable(self, n, contact):
        now = time.time()
        return now > n.t_to_go and self.state != 'UP' and  contact.want_host_notification(now, self.state)
            

    #We just send a notification, we need new ones in notification_interval
    def get_new_notification_from(self, n):
        now = time.time()
        return Notification('scheduled','', {'host' : n.ref['host'], 'contact' : n.ref['contact'], 'command': n.ref['command']}, 'host', now + self.notification_interval * 60)


    #Check if the notificaton is still necessery
    def still_need(self, n):
        now = time.time()
        #if state != UP, the host still got a pb, so notification still necessery
        if self.state != 'UP':
            return True
        #state is UP but notif is in poller, so do not remove, will be done after
        if n.status == 'inpoller':
            return True
        #we do not see why to save this notification, so...
        return False


    #return a check to check the host
    def launch_check(self, t):
        #Get the command to launch
        m = MacroResolver()
        command_line = m.resolve_command(self.check_command, self, None, None)
        
        #Make the Check object and put the service in checking
        print "Asking for a check with command:", command_line
        c = Check('scheduled',command_line, self.id, 'host', self.next_chk)
        self.in_checking = True
        #We need to return the check for scheduling adding
        return c







class Hosts(Items):
    name_property = "host_name" #use for the search by name
    inner_class = Host #use for know what is in items


    def linkify(self, timeperiods=None, commands=None, contacts=None):
        self.linkify_h_by_tp(timeperiods)
        self.linkify_h_by_h()
        self.linkify_h_by_cmd(commands)
        self.linkify_h_by_c(contacts)

    #Simplify notif_period and check period by timeperiod id
    def linkify_h_by_tp(self, timeperiods):
        for h in self.items.values():
            try:
                #notif period
                ntp_name = h.notification_period
                ntp = timeperiods.find_by_name(ntp_name)
                h.notification_period = ntp
                #check period
                ctp_name = h.check_period
                ctp = timeperiods.find_by_name(ctp_name)
                h.check_period = ctp
            except AttributeError as e:
                print e
    

    #Simplify parents names by host id
    def linkify_h_by_h(self):
        for h in self.items.values():
            parents = h.parents
            #The new member list, in id
            new_parents = []
            for parent in parents:
                new_parents.append(self.find_by_name(parent))
            
            #We find the id, we remplace the names
            h.parents = new_parents

    
    #Simplify hosts commands by commands id
    def linkify_h_by_cmd(self, commands):
        for h in self.items.values():
            h.check_command = CommandCall(commands, h.check_command)


    def linkify_h_by_c(self, contacts):
        for id in self.items:
            h = self.items[id]
            contacts_tab = h.contacts.split(',')
            new_contacts = []
            for c_name in contacts_tab:
                c_name = c_name.strip()
                c = contacts.find_by_name(c_name)
                new_contacts.append(c)
                
            h.contacts = new_contacts


    #We look for hostgroups property in hosts and
    def explode(self, hostgroups, contactgroups):
        #Hostgroups property need to be fullfill for got the informations
        self.apply_partial_inheritance('hostgroups')
        self.apply_partial_inheritance('contact_groups')
        
        #Explode host in the hostgroups
        for h in self.items.values():
            if not h.is_tpl():
                hname = h.host_name
                if h.has('hostgroups'):
                    hgs = h.hostgroups.split(',')
                    for hg in hgs:
                        hostgroups.add_member(hname, hg.strip())
        
        #We add contacts of contact groups into the contacts prop
        for id in self.items:
            h = self.items[id]
            if h.has('contact_groups'):
                cgnames = h.contact_groups.split(',')
                for cgname in cgnames:
                    cgname = cgname.strip()
                    cnames = contactgroups.get_members_by_name(cgname)
                    #We add hosts in the service host_name
                    if cnames != []:
                        if h.has('contacts'):
                            h.contacts += ','+cnames
                        else:
                            h.contacts = cnames

        
    #Create depenancies
    def apply_dependancies(self):
        #Create parent graph
        self.parents = digraph()
        #0 is pynag node
        self.parents.add_node(0)
        for h in self.items.values():
            id = h.id
            #h = self.hosts[id]
            if id not in self.parents:
                self.parents.add_node(id)
            #Make pynag the parent of all nodes

            if len(h.parents) >= 1:
                for parent in h.parents:
                    if parent not in self.parents:
                        self.parents.add_node(parent)
                    self.parents.add_edge(parent, id)
            else:#host without parent are pynag childs
                self.parents.add_edge(0, id)
        print "Loop: ", self.parents.find_cycle()
        #print "Fin loop check"
        
        #Debug
        #dot = self.parents.write(fmt='dot')
        #f = open('graph.dot', 'w')
        #f.write(dot)
        #f.close()
        #import os
        # Draw as a png (note: this requires the graphiz 'dot' program to be installed)
        #os.system('dot graph.dot -Tpng > hosts.png')
