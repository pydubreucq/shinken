#!/usr/bin/env python
# Copyright (C) 2009-2010 :
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
#    Hartmut Goebel, h.goebel@goebel-consult.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.


from shinken.action import Action
from shinken.property import UnusedProp, BoolProp, IntegerProp, FloatProp, CharProp, StringProp, ListProp
from shinken.autoslots import AutoSlots

class Check(Action):
    # AutoSlots create the __slots__ with properties and
    # running_properties names
    __metaclass__ = AutoSlots


    my_type = 'check'

    properties = {
        'is_a':         StringProp(default='check'),
        'type':         StringProp(default=''),
        '_in_timeout':  BoolProp(default=False),
        'status' :      StringProp(default=''),
        'exit_status' : IntegerProp(default=3),
        'state':        IntegerProp(default=0),
        'output':       StringProp(default=''),
        'long_output':  StringProp(default=''),
        'ref':          IntegerProp(default=-1),
        't_to_go':      IntegerProp(default=0),
        'depend_on':    StringProp(default=[]),
        'dep_check':    StringProp(default=[]),
        'check_time':   IntegerProp(default=0),
        'execution_time': IntegerProp(default=0),
        'perf_data':    StringProp(default=''),
        'poller_tag':   StringProp(default='None'),
        'reactionner_tag':   StringProp(default='None'),
        'env':          StringProp(default={}),
        'internal':     BoolProp(default=False),
        'module_type':  StringProp(default='fork'),
        'worker':       StringProp(default='none'),
    }

    #id = 0 #Is common to Actions
    def __init__(self, status, command, ref, t_to_go, dep_check=None, id=None, timeout=10,\
                     poller_tag='None', reactionner_tag='None', env={}, module_type='fork'):

        self.is_a = 'check'
        self.type = ''
        if id is None: #id != None is for copy call only
            self.id = Action.id
            Action.id += 1
        self._in_timeout = False
        self.timeout = timeout
        self.status = status
        self.exit_status = 3
        self.command = command
        self.output = ''
        self.long_output = ''
        self.ref = ref
        #self.ref_type = ref_type
        self.t_to_go = t_to_go
        self.depend_on = []
        if dep_check is None:
            self.depend_on_me = []
        else:
            self.depend_on_me = [dep_check]
        self.check_time = 0
        self.execution_time = 0
        self.perf_data = ''
        self.poller_tag = poller_tag
        self.reactionner_tag = reactionner_tag
        self.module_type = module_type
        self.env = env
        # we keep the reference of the poller that will take us
        self.worker = 'none'
        # If it's a business rule, manage it as a special check
        if ref and ref.got_business_rule or command.startswith('_internal'):
            self.internal = True
        else:
            self.internal = False


    #return a copy of the check but just what is important for execution
    #So we remove the ref and all
    def copy_shell(self):
        #We create a dummy check with nothing in it, just defaults values
        return self.copy_shell__( Check('', '', '', '', '', id=self.id) )


    def get_return_from(self, c):
        self.exit_status  = c.exit_status
        self.output = c.output
        self.long_output = c.long_output
        self.check_time = c.check_time
        self.execution_time = c.execution_time
        self.perf_data = c.perf_data


    def is_launchable(self, t):
        return t > self.t_to_go


    def __str__(self):
        return "Check %d status:%s command:%s ref:%s" % (self.id, self.status, self.command, self.ref)


    def get_id(self):
        return self.id
