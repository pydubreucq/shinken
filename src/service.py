from command import CommandCall
from copy import deepcopy
from item import Item, Items
from util import to_int, to_char, to_split, to_bool
import random
import time
from check import Check
from notification import Notification
#from timeperiod import Timeperiod
from macroresolver import MacroResolver

latency = 0.0
nb_res = 0

class Service(Item):
    id = 0
    properties={'host_name' : {'required':True},
            'hostgroup_name' : {'required':True},
            'service_description' : {'required':True},
            'display_name' : {'required':False , 'default':None},
            'servicegroups' : {'required':False, 'default':''},
            'is_volatile' : {'required':False, 'default':'0', 'pythonize': to_bool},
            'check_command' : {'required':True},
            'initial_state' : {'required':False, 'default':'o', 'pythonize': to_char},
            'max_check_attempts' : {'required':True, 'pythonize': to_int},
            'check_interval' : {'required':True, 'pythonize': to_int},
            'retry_interval' : {'required':True, 'pythonize': to_int},
            'active_checks_enabled' : {'required':False, 'default':'1', 'pythonize': to_bool},
            'passive_checks_enabled' : {'required':False, 'default':'1', 'pythonize': to_bool},
            'check_period' : {'required':True},
            'obsess_over_service' : {'required':False, 'default':'0', 'pythonize': to_bool},
            'check_freshness' : {'required':False, 'default':'0', 'pythonize': to_bool},
            'freshness_threshold' : {'required':False, 'default':'0', 'pythonize': to_int},
            'event_handler' : {'required':False, 'default':''},
            'event_handler_enabled' : {'required':False, 'default':'0', 'pythonize': to_bool},
            'low_flap_threshold' : {'required':False, 'default':'25', 'pythonize': to_int},
            'high_flap_threshold' : {'required':False, 'default':'50', 'pythonize': to_int},
            'flap_detection_enabled' : {'required':False, 'default':'1', 'pythonize': to_bool},
            'flap_detection_options' : {'required':False, 'default':'o,w,c,u', 'pythonize': to_split},
            'process_perf_data' : {'required':False, 'default':'1', 'pythonize': to_bool},
            'retain_status_information' : {'required':False, 'default':'1', 'pythonize': to_bool},
            'retain_nonstatus_information' : {'required':False, 'default':'1', 'pythonize': to_bool},
            'notification_interval' : {'required':True, 'pythonize': to_int},
            'first_notification_delay' : {'required':False, 'default':'0', 'pythonize': to_int},
            'notification_period' : {'required':True},
            'notification_options' : {'required':False, 'default':'w,u,c,r,f,s', 'pythonize': to_split},
            'notifications_enabled' : {'required':False, 'default':'1', 'pythonize': to_bool},
            'contacts' : {'required':True},
            'contact_groups' : {'required':True},
            'stalking_options' : {'required':False, 'default':'o,w,u,c', 'pythonize': to_split},
            'notes' : {'required':False, 'default':''},
            'notes_url' : {'required':False, 'default':''},
            'action_url' : {'required':False, 'default':''},
            'icon_image' : {'required':False, 'default':''},
            'icon_image_alt' : {'required':False, 'default':''},
            'failure_prediction_enabled' : {'required':False, 'default':'0', 'pythonize': to_bool},
            'parallelize_check' : {'required':False, 'default':'1', 'pythonize': to_bool}
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

    macros = {
        'SERVICEDESC' : 'service_description',
        'SERVICEDISPLAYNAME' : 'display_name',
        'SERVICESTATE' : 'state',
        'SERVICESTATEID' : 'get_state_id',
        'LASTSERVICESTATE' : 'last_state',
        'LASTSERVICESTATEID' : 'get_last_state_id',
        'SERVICESTATETYPE' : 'state_type',
        'SERVICEATTEMPT' : 'attempt',
        'MAXSERVICEATTEMPTS' : 'max_check_attempts',
        'SERVICEISVOLATILE' : 'is_volatile',
        'SERVICEEVENTID' : None,
        'LASTSERVICEEVENTID' : None,
        'SERVICEPROBLEMID' : None,
        'LASTSERVICEPROBLEMID' : None,
        'SERVICELATENCY' : 'latency',
        'SERVICEEXECUTIONTIME' : 'exec_time',
        'SERVICEDURATION' : 'get_duration',
        'SERVICEDURATIONSEC' : 'get_duration_sec',
        'SERVICEDOWNTIME' : 'get_downtime',
        'SERVICEPERCENTCHANGE' : 'get_percent_change',
        'SERVICEGROUPNAME' : 'get_groupname',
        'SERVICEGROUPNAMES' : 'get_groupnames',
        'LASTSERVICECHECK' : 'last_chk',
        'LASTSERVICESTATECHANGE' : 'last_state_change',
        'LASTSERVICEOK' : 'last_service_ok',
        'LASTSERVICEWARNING' : 'last_service_warning',
        'LASTSERVICEUNKNOWN' : 'last_service_unknown',
        'LASTSERVICECRITICAL' : 'last_service_critical',
        'SERVICEOUTPUT' : 'output',
        'LONGSERVICEOUTPUT' : 'long_output',
        'SERVICEPERFDATA' : 'perf_data',
        'SERVICECHECKCOMMAND' : 'get_check_command',
        'SERVICEACKAUTHOR' : 'ack_author',
        'SERVICEACKAUTHORNAME' : 'get_ack_author_name',
        'SERVICEACKAUTHORALIAS' : 'get_ack_author_alias',
        'SERVICEACKCOMMENT' : 'ack_comment',
        'SERVICEACTIONURL' : 'action_url',
        'SERVICENOTESURL' : 'notes_url',
        'SERVICENOTES' : 'notes'
        }


    def clean(self):
        pass


    #return a copy of a service, but give im a new id
    def copy(self):
        s = deepcopy(self)
        s.id = Service.id
        Service.id = Service.id + 1
        return s


    #Set state with status return by the check
    def set_state_from_exit_status(self, status):
        self.last_state = self.state
        if status == 0:
            self.state = 'OK'
        elif status == 1:
            self.state = 'WARNING'
        elif status == 2:
            self.state = 'CRITICAL'
        elif status == 3:
            self.state = 'UNKNOWN'
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
        
        for contact in self.contacts:
            for cmd in contact.service_notification_commands:
                #create without real command, it will be update just before being send
                notifications.append(Notification('scheduled', 'VOID', {'service' : self.id, 'contact' : contact.id, 'command': cmd}, 'service', t))
        return notifications


    #We are just going to launch the notif to the poller
    #so we must actualise the command (Macros)
    def update_notification(self, n,  contact):
        m = MacroResolver()
        command = n.ref['command']
        n._command = m.resolve_command(command, self.host_name, self, contact)


    #see if the notification is launchable (time is OK and contact is OK too)
    def is_notification_launchable(self, n, contact):
        now = time.time()
        return now > n.t_to_go and self.state != 'OK' and  contact.want_service_notification(now, self.state)
            

    #We just send a notification, we need new ones in notification_interval
    def get_new_notification_from(self, n):
        now = time.time()
        return Notification('scheduled','', {'service' : n.ref['service'], 'contact' : n.ref['contact'], 'command': n.ref['command']}, 'service', now + self.notification_interval * 60)


    #Check if the notificaton is still necessery
    def still_need(self, n):
        now = time.time()
        #if state != OK, te service still got a pb, so notification still necessery
        if self.state != 'OK':
            return True
        #state is OK but notif is in poller, so do not remove, will be done after
        if n.status == 'inpoller':
            return True
        #we do not see why to save this notification, so...
        return False


    #return a check to check the service
    def launch_check(self, t):
        #Get the command to launch
        m = MacroResolver()
        command_line = m.resolve_command(self.check_command, self.host_name, self, None)

        #Make the Check object and put the service in checking
        print "Asking for a check with command:", command_line
        c = Check('scheduled',command_line, self.id, 'service', self.next_chk)
        self.in_checking = True
        #We need to return the check for scheduling adding
        return c
    

class Services(Items):
    def find_srv_id_by_name_and_hostname(self, host_name, name):
        for id in self.items:
            if self.items[id].has('service_description') and self.items[id].has('host_name'):
                if self.items[id].service_description == name and self.items[id].host_name == host_name:
                    return id
        return None


    def find_srv_by_name_and_hostname(self, host_name, name):
        id = self.find_srv_id_by_name_and_hostname(host_name, name)
        if id is not None:
            return self.items[id]
        else:
            return None


    def linkify(self, hosts, commands, timeperiods, contacts):
        self.linkify_s_by_hst(hosts)
        self.linkify_s_by_cmd(commands)
        self.linkify_s_by_tp(timeperiods)
        self.linkify_s_by_c(contacts)

    #We just search for each host the id of the host
    #and replace the name by the id
    def linkify_s_by_hst(self, hosts):
        for id in self.items:
            try:
                hst_name = self.items[id].host_name
                
                #The new member list, in id
                hst = hosts.find_by_name(hst_name)
                self.items[id].host_name = hst
            except AttributeError as exp:
                print exp


    def linkify_s_by_cmd(self, commands):
        for id in self.items:
            self.items[id].check_command = CommandCall(commands, self.items[id].check_command)


    def linkify_s_by_tp(self, timeperiods):
        for id in self.items:
            try:
                #notif period
                ntp_name = self.items[id].notification_period
                ntp = timeperiods.find_by_name(ntp_name)
                self.items[id].notification_period = ntp
            except:
                pass
            try:
                #Check period
                ctp_name = self.items[id].check_period
                ctp = timeperiods.find_by_name(ctp_name)
                self.items[id].check_period = ctp
            except:
                pass #problem will be check at is_correct fucntion


    def linkify_s_by_c(self, contacts):
        for id in self.items:
            s = self.items[id]
            contacts_tab = s.contacts.split(',')
            new_contacts = []
            for c_name in contacts_tab:
                c_name = c_name.strip()
                c = contacts.find_by_name(c_name)
                new_contacts.append(c)
                
            s.contacts = new_contacts

    
    def delete_services_by_id(self, ids):
        for id in ids:
            del self.items[id]


    def apply_implicit_inheritance(self, hosts):
        for prop in ['contact_groups', 'notification_interval' , 'notification_period']:
            for id in self.items:
                s = self.items[id]
                if not s.is_tpl():
                    if not s.has(prop) and s.has('host_name'):
                        h = hosts.find_by_name(s.host_name)
                        if h is not None and h.has(prop):
                            setattr(s, prop, getattr(h, prop))


    def apply_inheritance(self, hosts):
        #We check for all Host properties if the host has it
        #if not, it check all host templates for a value
        for prop in Service.properties:
            self.apply_partial_inheritance(prop)

        #Then implicit inheritance
        self.apply_implicit_inheritance(hosts)
        for id in self.items:
            s = self.items[id]
            s.get_customs_properties_by_inheritance(self)


    #We create new service if necessery (host groups and co)
    def explode(self, hostgroups, contactgroups, servicegroups):
        #Hostgroups property need to be fullfill for got the informations
        self.apply_partial_inheritance('contact_groups')
        self.apply_partial_inheritance('hostgroup_name')
        self.apply_partial_inheritance('host_name')

        #The "old" services will be removed. All services with 
        #more than one host or a host group will be in it
        srv_to_remove = []
        
        #We adding all hosts of the hostgroups into the host_name property
        #because we add the hostgroup one AFTER the host, they are before and 
        #hostgroup one will NOT be created
        for id in self.items:
            s = self.items[id]
            if s.has('hostgroup_name'):
                hgnames = s.hostgroup_name.split(',')
                for hgname in hgnames:
                    hgname = hgname.strip()
                    hnames = hostgroups.get_members_by_name(hgname)
                    #We add hosts in the service host_name
                    if s.has('host_name'):
                        s.host_name += ','+hnames
                    else:
                        s.host_name = hnames

        #We adding all hosts of the hostgroups into the host_name property
        #because we add the hostgroup one AFTER the host, they are before and 
        #hostgroup one will NOT be created
        for id in self.items:
            s = self.items[id]
            if s.has('contact_groups'):
                cgnames = s.contact_groups.split(',')
                for cgname in cgnames:
                    cgname = cgname.strip()
                    cnames = contactgroups.get_members_by_name(cgname)
                    #We add hosts in the service host_name
                    if cnames != []:
                        if s.has('contacts'):
                            s.contacts += ','+cnames
                        else:
                            s.contacts = cnames
        
        #Then for every host create a copy of the service with just the host
        service_to_check = self.items.keys() #because we are adding services, we can't just loop in it
        for id in service_to_check:
            s = self.items[id]
            if not s.is_tpl(): #Exploding template is useless
                hnames = s.host_name.split(',')
                if len(hnames) >= 2:
                    for hname in hnames:
                        hname = hname.strip()
                        new_s = s.copy()
                        new_s.host_name = hname
                        self.items[new_s.id] = new_s
                    srv_to_remove.append(id)
        
        self.delete_services_by_id(srv_to_remove)

        #Servicegroups property need to be fullfill for got the informations
        self.apply_partial_inheritance('servicegroups')
        for id in self.items:
            s = self.items[id]
            if not s.is_tpl():
                sname = s.service_description
                shname = s.host_name
                if s.has('servicegroups'):
                    sgs = s.servicegroups.split(',')
                    for sg in sgs:
                        servicegroups.add_member(shname+','+sname, sg)
        
