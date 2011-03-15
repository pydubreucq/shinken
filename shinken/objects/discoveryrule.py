#!/usr/bin/env python
#Copyright (C) 2009-2010 :
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
#    Hartmut Goebel, h.goebel@goebel-consult.de
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

from shinken.objects.item import Item, Items

from shinken.property import IntegerProp, StringProp, ListProp

class Discoveryrule(Item):
    id = 1 #0 is always special in database, so we do not take risk here
    my_type = 'discoveryrule'

    properties = {
        'discoveryrule_name':    StringProp (),
        'check_command':         StringProp (),
        'service_description':   StringProp (),
        'use':                   StringProp(),
    }

    running_properties = {}

    macros = {}


    #For debugging purpose only (nice name)
    def get_name(self):
        return self.discoveryrule_name


class Discoveryrules(Items):
    name_property = "discoveryrule_name"
    inner_class = Discoveryrule

