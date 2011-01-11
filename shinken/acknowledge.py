#!/usr/bin/env python
# Copyright (C) 2009-2010 :
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Shinken. If not, see <http://www.gnu.org/licenses/>.
#
"""
Allows you to acknowledge the current problem for the specified service.
By acknowledging the current problem, future notifications (for the same
servicestate) are disabled.
"""
class Acknowledge:
    id = 0

    #Just to list the properties we will send as pickle
    #so to others daemons, so all but NOT REF
    properties = {
        'id' : None,
        'sticky' : None,
        'notify' : None,
        'author' : None,
        'comment' : None,
        }


    # If the "sticky" option is set to one (1), the acknowledgement
    # will remain until the service returns to an OK state. Otherwise
    # the acknowledgement will automatically be removed when the
    # service changes state. In this case Web interfaces set a value
    # of (2).
    #
    # If the "notify" option is set to one (1), a notification will be
    # sent out to contacts indicating that the current service problem
    # has been acknowledged.
    #
    # If the "persistent" option is set to one (1), the comment
    # associated with the acknowledgement will survive across restarts
    # of the Shinken process. If not, the comment will be deleted the
    # next time Nagios restarts. "persistent" not only means "survive
    # restarts", but also
    #
    def __init__(self, ref, sticky, notify, persistent, author, comment):
        self.id = self.__class__.id
        self.__class__.id += 1
        self.ref = ref # pointer to srv or host we are apply
        self.sticky = sticky
        self.notify = notify
        self.author = author
        self.comment = comment


    #Call by picle for dataify the ackn
    #because we DO NOT WANT REF in this pickleisation!
    def __getstate__(self):
#        print "Asking a getstate for a comment on", self.ref.get_dbg_name()
        cls = self.__class__
        #id is not in *_properties
        res = [self.id]
        for prop in cls.properties:
            res.append(getattr(self, prop))
        #We reverse because we want to recreate
        #By check at properties in the same order
        res.reverse()
        return res


    #Inversed funtion of getstate
    def __setstate__(self, state):
        cls = self.__class__
        self.id = state.pop()
        for prop in cls.properties:
            val = state.pop()
            setattr(self, prop, val)
