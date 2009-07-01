import os, sys, re, time, string

from timeperiod import Timeperiod,Timeperiods
from service import Service,Services
from command import Command,Commands
from host import Host,Hosts
from hostgroup import Hostgroup,Hostgroups
from contact import Contact,Contacts
from contactgroup import Contactgroup,Contactgroups
from servicegroup import Servicegroup,Servicegroups
from item import Item
from macroresolver import MacroResolver

from util import to_int, to_char, to_split, to_bool
#import psyco
#psyco.full()


class Config(Item):
    cache_path = "objects.cache"
    #hosts
    #hostgroups
    #services
    #contacts
    #contactgroups
    #commands
    #timeperiods

    properties={'log_file' : {'required':False, 'default' : '/tmp/log.txt'},
                'object_cache_file' : {'required':False, 'default' : '/tmp/object.dat'},
                'precached_object_file' : {'required':False , 'default' : '/tmp/object.precache'},
                'resource_file' : {'required':False , 'default':'/tmp/ressources.txt'},
                'temp_file' : {'required':False, 'default':'/tmp/temp_file.txt'},
                'status_file' : {'required':False, 'default':'/tmp/status.dat'},
                'status_update_interval' : {'required':False, 'default':'15', 'pythonize': to_int},
                'nagios_user' : {'required':False, 'default':'nap'},
                'nagios_group' : {'required':False, 'default':'nap'},
                'enable_notifications' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'execute_service_checks' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'accept_passive_service_checks' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'execute_host_checks' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'accept_passive_host_checks' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'enable_event_handlers' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'log_rotation_method' : {'required':False, 'default':'d', 'pythonize': to_char},
                'log_archive_path' : {'required':False, 'default':'/tmp/'},
                'check_external_commands' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'command_check_interval' : {'required':False, 'default':'-1'},
                'command_file' : {'required':False, 'default':'/tmp/command.cmd'},
                'external_command_buffer_slots' : {'required':False, 'default':'512', 'pythonize': to_int},
                'check_for_updates' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'bare_update_checks' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'lock_file' : {'required':False, 'default':'/tmp/lock.lock'},
                'retain_state_information' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'state_retention_file' : {'required':False, 'default':'/tmp/retention.dat'},
                'retention_update_interval' : {'required':False, 'default':'60', 'pythonize': to_int},
                'use_retained_program_state' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'use_retained_scheduling_info' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'retained_host_attribute_mask' : {'required':False, 'default':'0'},
                'retained_service_attribute_mask' : {'required':False, 'default':'0'},
                'retained_process_host_attribute_mask' : {'required':False, 'default':'0'},
                'retained_process_service_attribute_mask' : {'required':False, 'default':'0'},
                'retained_contact_host_attribute_mask' : {'required':False, 'default':'0'},
                'retained_contact_service_attribute_mask' : {'required':False, 'default':'0'},
                'use_syslog' : {'required':False, 'default':'0', 'pythonize': to_bool},
                'log_notifications' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'log_service_retries' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'log_host_retries' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'log_event_handlers' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'log_initial_states' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'log_external_commands' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'log_passive_checks' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'global_host_event_handler' : {'required':False, 'default':''},
                'global_service_event_handler' : {'required':False, 'default':''},
                'sleep_time' : {'required':False, 'default':'1', 'pythonize': to_int},
                'service_inter_check_delay_method' : {'required':False, 'default':'s'},
                'max_service_check_spread' : {'required':False, 'default':'30', 'pythonize': to_int},
                'service_interleave_factor' : {'required':False, 'default':'s'},
                'max_concurrent_checks' : {'required':False, 'default':'200', 'pythonize': to_int},
                'check_result_reaper_frequency' : {'required':False, 'default':'5', 'pythonize': to_int},
                'max_check_result_reaper_time' : {'required':False, 'default':'30', 'pythonize': to_int},
                'check_result_path' : {'required':False, 'default':'/tmp/'},
                'max_check_result_file_age' : {'required':False, 'default':'3600', 'pythonize': to_int},
                'host_inter_check_delay_method' : {'required':False, 'default':'s'},
                'max_host_check_spread' : {'required':False, 'default':'30', 'pythonize': to_int},
                'interval_length' : {'required':False, 'default':'60', 'pythonize': to_int},
                'auto_reschedule_checks' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'auto_rescheduling_interval' : {'required':False, 'default':'30', 'pythonize': to_int},
                'auto_rescheduling_window' : {'required':False, 'default':'180', 'pythonize': to_int},
                'use_aggressive_host_checking' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'translate_passive_host_checks' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'passive_host_checks_are_soft' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'enable_predictive_host_dependency_checks' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'enable_predictive_service_dependency_checks' : {'required':False, 'default':'1'},
                'cached_host_check_horizon' : {'required':False, 'default':'15', 'pythonize': to_int},
                'cached_service_check_horizon' : {'required':False, 'default':'15', 'pythonize': to_int},
                'use_large_installation_tweaks' : {'required':False, 'default':'0', 'pythonize': to_bool},
                'free_child_process_memory' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'child_processes_fork_twice' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'enable_environment_macros' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'enable_flap_detection' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'low_service_flap_threshold' : {'required':False, 'default':'25', 'pythonize': to_int},
                'high_service_flap_threshold' : {'required':False, 'default':'50', 'pythonize': to_int},
                'low_host_flap_threshold' : {'required':False, 'default':'25', 'pythonize': to_int},
                'high_host_flap_threshold' : {'required':False, 'default':'50', 'pythonize': to_int},
                'soft_state_dependencies' : {'required':False, 'default':'0', 'pythonize': to_bool},
                'service_check_timeout' : {'required':False, 'default':'10', 'pythonize': to_int},
                'host_check_timeout' : {'required':False, 'default':'10', 'pythonize': to_int},
                'event_handler_timeout' : {'required':False, 'default':'10', 'pythonize': to_int},
                'notification_timeout' : {'required':False, 'default':'5', 'pythonize': to_int},
                'ocsp_timeout' : {'required':False, 'default':'5', 'pythonize': to_int},
                'ochp_timeout' : {'required':False, 'default':'5', 'pythonize': to_int},
                'perfdata_timeout' : {'required':False, 'default':'2', 'pythonize': to_int},
                'obsess_over_services' : {'required':False, 'default':'0', 'pythonize': to_bool},
                'ocsp_command' : {'required':False, 'default':''},
                'obsess_over_hosts' : {'required':False, 'default':'0', 'pythonize': to_bool},
                'ochp_command' : {'required':False, 'default':''},
                'process_performance_data' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'host_perfdata_command' : {'required':False, 'default':''},
                'service_perfdata_command' : {'required':False, 'default':''},
                'host_perfdata_file' : {'required':False, 'default':'/tmp/host.perf'},
                'service_perfdata_file' : {'required':False, 'default':'/tmp/service.perf'},
                'host_perfdata_file_template' : {'required':False, 'default':'/tmp/host.perf'},
                'service_perfdata_file_template' : {'required':False, 'default':'/tmp/host.perf'},
                'host_perfdata_file_mode' : {'required':False, 'default':'a', 'pythonize': to_char},
                'service_perfdata_file_mode' : {'required':False, 'default':'a', 'pythonize': to_char},
                'host_perfdata_file_processing_interval' : {'required':False, 'default':'15', 'pythonize': to_int},
                'service_perfdata_file_processing_interval' : {'required':False, 'default':'15', 'pythonize': to_int},
                'host_perfdata_file_processing_command' : {'required':False, 'default':''},
                'service_perfdata_file_processing_command' : {'required':False, 'default':''},
                'check_for_orphaned_services' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'check_for_orphaned_hosts' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'check_service_freshness' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'service_freshness_check_interval' : {'required':False, 'default':'60', 'pythonize': to_int},
                'check_host_freshness' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'host_freshness_check_interval' : {'required':False, 'default':'60', 'pythonize': to_int},
                'additional_freshness_latency' : {'required':False, 'default':'15', 'pythonize': to_int},
                'enable_embedded_perl' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'use_embedded_perl_implicitly' : {'required':False, 'default':'0', 'pythonize': to_bool},
                'date_format' : {'required':False, 'default':'us'},
                'use_timezone' : {'required':False, 'default':'FR/Paris'},
                'illegal_object_name_chars' : {'required':False, 'default':'/tmp/'},
                'illegal_macro_output_chars' : {'required':False, 'default':''},
                'use_regexp_matching' : {'required':False, 'default':'1', 'pythonize': to_bool},
                'use_true_regexp_matching' : {'required':False, 'default':'0', 'pythonize': to_bool},
                'admin_email' : {'required':False, 'default':'admin@localhost'},
                'admin_pager' : {'required':False, 'default':''},
                'event_broker_options' : {'required':False, 'default':''},
                'broker_module' : {'required':False, 'default':''},
                'debug_file' : {'required':False, 'default':'/tmp/debug.txt'},
                'debug_level' : {'required':False, 'default':'0'},
                'debug_verbosity' : {'required':False, 'default':'1'},
                'max_debug_file_size' : {'required':False, 'default':'10000', 'pythonize': to_int}
    }


    macros = {
        'MAINCONFIGFILE' : '',
        'STATUSDATAFILE' : '',
        'COMMENTDATAFILE' : '',
        'DOWNTIMEDATAFILE' : '',
        'RETENTIONDATAFILE' : '',
        'OBJECTCACHEFILE' : '',
        'TEMPFILE' : '',
        'TEMPPATH' : '',
        'LOGFILE' : '',
        'RESOURCEFILE' : '',
        'COMMANDFILE' : '',
        'HOSTPERFDATAFILE' : '',
        'SERVICEPERFDATAFILE' : '',

        'ADMINEMAIL' : '',
        'ADMINPAGER' : ''
        }

    def __init__(self):
        self.params = {}

    def load_params(self, params):
        for elt in params:
            elts = elt.split('=')
            self.params[elts[0]] = elts[1]

    def _cut_line(self, line):
        punct = '"#$%&\'()*+/<=>?@[\\]^`{|}~'
        tmp = re.split("[" + string.whitespace + "]+" , line)
        r = [elt for elt in tmp if elt != '']
        return r

    def _join_values(self, values):
        return ' '.join(values)

    def read_config(self, file):
        print "Opening config file", file
        #just a first pass to get the cfg_file and all files in a buf
        res = ''
        fd=open(file)
        buf=fd.readlines()
        fd.close()
        #res += buf
        for line in buf:
            res += line
            line = line[:-1]
            if re.search("^cfg_file", line):
                elts = line.split('=')
                try:
                    fd = open(elts[1])
                    res += fd.read()
                    fd.close()
                except IOError as exp:
                    print exp
        #print "Got", res
        self.read_config_buf(res)
        

    def read_config_buf(self, buf):
        #fd=open(file)
        #buf=buf.readlines()
        #fd.close()

        params=[]
        objectscfg={'void': [],
                    'timeperiod' : [],
                    'command' : [],
                    'contactgroup' : [],
                    'hostgroup' : [],
                    'contact' : [],
                    'host' : [],
                    'service' : [],
                    'servicegroup' : []
                    }
        
        tmp=[]
        tmp_type='void'
        in_define = False
        lines = buf.split('\n')
        for line in lines:#buf.readlines():
            #line = line[:-1]

            line=line.split(';')[0]
            if re.search("}",line):
                in_define = False
            if re.search("^#|^$|}", line):
                pass
                        
            #A define must be catch and the type save
            #The old entry must be save before
            elif re.search("^define", line):
                in_define = True
                #print "Add a", tmp_type, ":", tmp
                objectscfg[tmp_type].append(tmp)
                tmp=[]
                #Get new type
                elts = re.split('\s', line)
                tmp_type = elts[1]
                tmp_type = tmp_type.split('{')[0]
            else:
                if in_define:
                    tmp.append(line)
                else:
                    params.append(line)
                    
                #print 'Add line', line
        objects = {}
        
        #print "Debug:", objectscfg
        print "Params",params
        self.load_params(params)
        
        for type in objectscfg:
            objects[type]=[]
            #print 'Doing type:',type
            for items in objectscfg[type]:
                #print 'Items:', items
                tmp={}
                for line in items:
                    elts = self._cut_line(line)
                    if elts !=  []:
                        #print "Got elts:", elts
                        prop = elts[0]
                        value = self._join_values(elts[1:])
                        tmp[prop] = value
                        #print 'Add', prop, 'Val:', value
                if tmp != {}:
                    #print 'Append:', tmp, '\n\n'
                    objects[type].append(tmp)
        
        #print 'Objects:', objects['service']
        #print "Nb of services:", len(objects['service'])
    
        #We create dict of objects
        timeperiods = []
        for timeperiodcfg in objects['timeperiod']:
            t = Timeperiod(timeperiodcfg)
            t.clean()
            timeperiods.append(t)
        self.timeperiods = Timeperiods(timeperiods)
        
        services = []
        #services_tpl = []
        for servicecfg in objects['service']:
            s = Service(servicecfg)
            s.clean()
            #if s.is_tpl():
            services.append(s)
            #else:
            #    services_tpl.append(s)
        self.services = Services(services)
        #self.services_tpl = Services(services_tpl)

        servicegroups = []
        #services_tpl = []
        for servicegroupcfg in objects['servicegroup']:
            sg = Servicegroup(servicegroupcfg)
            sg.clean()
            #if s.is_tpl():
            servicegroups.append(sg)
            #else:
            #    services_tpl.append(s)
        self.servicegroups = Servicegroups(servicegroups)
        #self.services_tpl = Services(services_tpl)

        
        commands = []
        for commandcfg in objects['command']:
            c = Command(commandcfg)
            c.clean()
            commands.append(c)
            print "Creating command", c
        self.commands = Commands(commands)
        
        hosts = []
        #hosts_tpl = []
        for hostcfg in objects['host']:
            h = Host(hostcfg)
            h.clean()
            #if h.is_tpl():
            #    hosts_tpl.append(h)
            #else:
            hosts.append(h)
        self.hosts = Hosts(hosts)
        #self.hosts_tpl = Hosts(hosts_tpl)

        hostgroups = []
        for hostgroupcfg in objects['hostgroup']:
            hg = Hostgroup(hostgroupcfg)
            hg.clean()
            hostgroups.append(hg)
        self.hostgroups = Hostgroups(hostgroups)
        
        contacts = []
        for contactcfg in objects['contact']:
            c = Contact(contactcfg)
            c.clean()
            contacts.append(c)
        self.contacts = Contacts(contacts)
        
        contactgroups = []
        for contactgroupcfg in objects['contactgroup']:
            cg = Contactgroup(contactgroupcfg)
            cg.clean()
            contactgroups.append(cg)
        self.contactgroups = Contactgroups(contactgroups)


    #We use linkify to make the config smaller (not name but direct link when possible)
    def linkify(self):
        #Do the simplify AFTER explode groups
        print "Hostgroups"
        #link hostgroups with hosts
        self.hostgroups.linkify(self.hosts)

        print "Hosts"
        #link hosts with timeperiodsand commands
        self.hosts.linkify(self.timeperiods, self.commands, self.contacts)

        print "Service groups"
        #link servicegroups members with services
        self.servicegroups.linkify(self.services)

        print "Services"
        #link services with hosts, commands, timeperiods and contacts
        self.services.linkify(self.hosts, self.commands, self.timeperiods, self.contacts)

        print "Contactgroups"
        #link contacgroups with contacts
        self.contactgroups.linkify(self.contacts)

        print "Contacts"
        #link contacts with timeperiods and commands
        self.contacts.linkify(self.timeperiods, self.commands)

        print "Timeperiods"
        #link timeperiods with timeperiods (exclude part)
        self.timeperiods.linkify()
        
        
    def dump(self):
        #print 'Parameters:', self
        #print 'Hostgroups:',self.hostgroups,'\n'
        #print 'Services:', self.services
        #print 'Templates:', self.hosts_tpl
        print 'Hosts:',self.hosts,'\n'
        #print 'Contacts:', self.contacts
        #print 'contactgroups',self.contactgroups
        #print 'Servicegroups:', self.servicegroups
        #print 'Timepriods:', self.timeperiods
        #print 'Commands:', self.commands
        #print "Number of services:", len(self.services.items)
        pass

    #Use to fill groups values on hosts and create new services (for host group ones)
    def explode(self):
        #first elements, after groups

        #hosts = time.time()
        #self.contactgroups.explode()
        #contactgroups = time.time()

        print "Contacts"
        self.contacts.explode(self.contactgroups)

        print "Contactgroups"
        self.contactgroups.explode()
        #contacts = time.time()

        print "Hosts"
        self.hosts.explode(self.hostgroups, self.contactgroups)
        print "Hostgroups"
        self.hostgroups.explode()

        print "Services"
        self.services.explode(self.hostgroups, self.contactgroups, self.servicegroups)

        print "Servicegroups"
        self.servicegroups.explode()

        print "Timeperiods"
        self.timeperiods.explode()
        #services = time.time()
        #print "Time: Overall Explode :", services-begin, " (hosts:",hosts-begin," ) (contactgroups:",contactgroups-hosts," ) (contacts:",contacts-contactgroups," ) (services:",services-contacts,")"        


    def apply_dependancies(self):
        self.hosts.apply_dependancies()

    #Use to apply inheritance (template and implicit ones)
    def apply_inheritance(self):
        #inheritance properties by template
        #begin = time.time()
        print "Hosts"
        self.hosts.apply_inheritance()
        #hosts = time.time()
        print "Contacts"
        self.contacts.apply_inheritance()
        #contacts = time.time()
        print "Services"
        self.services.apply_inheritance(self.hosts)
        #services = time.time()
        #print "Time: Overall Inheritance :", services-begin, " (hosts:",hosts-begin," ) (contacts:",contacts-hosts," ) (services:",services-contacts,")"

    def fill_default(self):
        super(Config, self).fill_default()
        self.hosts.fill_default()
        self.contacts.fill_default()
        self.services.fill_default()

    def is_correct(self):
        self.hosts.is_correct()
        self.hostgroups.is_correct()
        self.contacts.is_correct()
        self.contactgroups.is_correct()

    def pythonize(self):
        #call item pythonize for parameters
        super(Config, self).pythonize()
        #begin = time.time()
        self.hosts.pythonize()
        #hosts = time.time()
        self.hostgroups.pythonize()
        #hostgroups = time.time()
        self.contactgroups.pythonize()
        #contactgroups = time.time()
        self.contacts.pythonize()
        #contacts = time.time()
        self.services.pythonize()
        #services = time.time()
        #print "Time: Overall Pythonize :", services-begin, " (hosts:",hosts-begin," ) (hostgroups:",hostgroups-hosts,") (contactgroups:",contactgroups-hostgroups," ) (contacts:",contacts-contactgroups," ) (services:",services-contacts,")"


    def clean_useless(self):
        self.hosts.clean_useless()
        self.contacts.clean_useless()
        self.services.clean_useless()

if __name__ == '__main__':
    c = Config()
    #c.read_cache(c.cache_path)
    
    print "****************** Read ******************"
    
    c.read_config("nagios.cfg")
    #c.idfy()
    #c.dump()
    
    
    print "****************** Explode ******************"
    
    #create or update new hostgroup or service by looking at
    c.explode()
    c.dump()

    print "****************** Inheritance ******************"
    
    #We apply all inheritance
    c.apply_inheritance()
    c.dump()
    
    
    print "****************** Fill default ******************"
    #After inheritance is ok, we can fill defaults
    #values not set by inheritance
    c.fill_default()
    c.dump()
    
    print "****************** Clean templates ******************"
    
    #We can clean the tpl now
    c.clean_useless()
    c.dump()
    
    
    print "****************** Pythonize ******************"
    #We pythonize every data
    c.pythonize()
    c.dump()
    
    
    print "****************** Linkify ******************"
    #Now we can make relations between elements
    #relations = id
    c.linkify()
    c.dump()
    
    
    print "*************** applying dependancies ************"
    c.apply_dependancies()
    
    
    print "****************** Correct ?******************"
    #We check if the config is OK
    c.is_correct()
    dump = getattr(c, 'dump')
    print dump
    dump()
    #c.dump()
    
    m = MacroResolver()
    m.init(c)
    h = c.hosts.items[6]
    print h
    s = c.services.items[3]
    print s
    com = s.check_command
    print com
    con = c.contacts.items[2]
    #for i in xrange(1 ,1000):
    m.resolve_command(com, h, s, con)
    print "finish!!"
    

