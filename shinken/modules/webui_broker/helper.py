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

import time
import copy
try:
    import json
except ImportError:
    # For old Python version, load
    # simple json (it can be hard json?! It's 2 functions guy!)
    try:
        import simplejson as json
    except ImportError:
        print "Error : you need the json or simplejson module"
        raise



# Sort hosts and services by impact, states and co
def hst_srv_sort(s1, s2):
    if s1.business_impact > s2.business_impact:
        return -1
    if s2.business_impact > s1.business_impact:
        return 1

    # Ok, we compute a importance value so
    # For host, the order is UP, UNREACH, DOWN
    # For service : OK, UNKNOWN, WARNING, CRIT
    # And DOWN is before CRITICAL (potential more impact)
    tab = {'host' : { 0 : 0, 1: 4, 2 : 1},
           'service' : {0 : 0, 1 : 2, 2 : 3, 3 : 1}
           }
    state1 = tab[s1.__class__.my_type].get(s1.state_id ,0)
    state2 = tab[s2.__class__.my_type].get(s2.state_id ,0)
    # ok, here, same business_impact
    # Compare warn and crit state
    if state1 > state2:
        return -1
    if state2 > state1:
        return 1
    
    # Ok, so by name...
    return s1.get_full_name() > s2.get_full_name()



class Helper(object):
    def __init__(self):
        pass

    def gogo(self):
        return 'HELLO'


    def act_inactive(self, b):
        if b:
            return 'Active'
        else:
            return 'Inactive'

    def yes_no(self, b):
        if b:
            return 'Yes'
        else:
            return 'No'

    def print_float(self, f):
        return '%.2f' % f

    def ena_disa(self, b):
        if b:
            return 'Enabled'
        else:
            return 'Disabled'

    # For a unix time return something like
    # Tue Aug 16 13:56:08 2011
    def print_date(self, t):
        if t == 0 or t == None:
            return 'N/A'
        return time.asctime(time.localtime(t))


    # For a time, print something like
    # 10m 37s  (just duration = True)
    # N/A if got bogus number (like 1970 or None)
    # 1h 30m 22s ago (if t < now)
    # Now (if t == now)
    # in 1h 30m 22s
    # Or in 1h 30m (no sec, if we ask only_x_elements=2, 0 means all)
    def print_duration(self, t, just_duration=False, x_elts=0):
        if t == 0 or t == None:
            return 'N/A'
        print "T", t
        # Get the difference between now and the time of the user
        seconds = int(time.time()) - int(t)
        
        # If it's now, say it :)
        if seconds == 0:
            return 'Now'

        in_future = False

        # Remember if it's in the future or not
        if seconds < 0:
            in_future = True
        
        # Now manage all case like in the past
        seconds = abs(seconds)
        print "In future?", in_future

        print "sec", seconds
        seconds = long(round(seconds))
        print "Sec2", seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        months, weeks = divmod(weeks, 4)
        years, months = divmod(months, 12)
 
        minutes = long(minutes)
        hours = long(hours)
        days = long(days)
        weeks = long(weeks)
        months = long(months)
        years = long(years)
 
        duration = []
        if years > 0:
            duration.append('%dy' % years)
        else:
            if months > 0:
                duration.append('%dM' % months)
            if weeks > 0:
                duration.append('%dw' % weeks)
            if days > 0:
                duration.append('%dd' % days)
            if hours > 0:
                duration.append('%dh' % hours)
            if minutes > 0:
                duration.append('%dm' % minutes)
            if seconds > 0:
                duration.append('%ds' % seconds)

        print "Duration", duration
        # Now filter the number of printed elements if ask
        if x_elts >= 1:
            duration = duration[:x_elts]

        # Maybe the user just want the duration
        if just_duration:
            return ' '.join(duration)

        # Now manage the future or not print
        if in_future:
            return 'in '+' '.join(duration)
        else: # past :)
            return ' '.join(duration) + ' ago'


    # Need to create a X level higer and lower to teh element
    def create_json_dep_graph(self, elt, levels=3):
        t0 = time.time()
        # First we need ALL elements
        all_elts = self.get_all_linked_elts(elt, levels=levels)
        print "We got all our elements"
        dicts = []
        for i in all_elts:
            print "Elt", i.get_dbg_name()
            d = self.get_dep_graph_struct(i)
            dicts.append(d)
        j = json.dumps(dicts)
        print "Create json", j
        print "create_json_dep_graph::Json creation time", time.time() - t0
        return j

    # Return something like:
    #{
    #                  "id": "localhost",
    #                  "name": "localhost",
    #                  "data": {"$color":"red", "$dim": 5*2, "some other key": "some other value"},
    #                  "adjacencies": [{
    #                          "nodeTo": "main router",
    #                          "data": {
    #                              "$type":"arrow",
    #                              "$color":"gray",
    #                              "weight": 3,
    #                              "$direction": ["localhost", "main router"],
    #                          }
    #                      }
    #                      ]
    #              }
    # But as a python dict
    def get_dep_graph_struct(self, elt, levels=3):
        t = elt.__class__.my_type
        d = {'id' : elt.get_dbg_name(), 'name' : elt.get_dbg_name(),
             'data' : {'$dim': max(elt.business_impact*elt.business_impact / 2, 5)},
             'adjacencies' : []
             }
        # Service got a 'star' type :)
        if t == 'service':
            d['data']["$type"] = "star"
            d['data']["$color"] = {0 : 'green', 1 : 'orange', 2 : 'red', 3 : 'gray'}.get(elt.state_id, 'red')
        else: #host
            d['data']["$color"] = {0 : 'green', 1 : 'red', 2 : '#CC6600', 3 : 'gray'}.get(elt.state_id, 'red')

        # Now put in adj our parents
        for p in elt.parent_dependencies:
            pd = {'nodeTo' : p.get_dbg_name(),
                  'data' : {"$type":"line", "$direction": [elt.get_dbg_name(), p.get_dbg_name()]}}
            # Naive way of looking at impact
            if elt.state_id != 0 and p.state_id != 0:
                pd['data']["$color"] = 'Tomato'
            # If OK, show host->service as a green link
            elif elt.__class__.my_type != p.__class__.my_type:
                 pd['data']["$color"] = 'PaleGreen'
            d['adjacencies'].append(pd)

        # The sons case is now useful, it will be done by our sons
        # that will link us
        return d
        

    # Return all linked elements of this elt, and 2 level
    # higer and lower :)
    def get_all_linked_elts(self, elt, levels=3):
        if levels == 0 :
            return set()

        my = set()
        for i in elt.child_dependencies:
            my.add(i)
            child_elts = self.get_all_linked_elts(i, levels=levels - 1)
            for c in child_elts:
                my.add(c)
        for i in elt.parent_dependencies:
            my.add(i)
            par_elts = self.get_all_linked_elts(i, levels=levels - 1)
            for c in par_elts:
                my.add(c)
            
        print "get_all_linked_elts::Give elements", my
        return my


    # Return a button with text, image, id and class (if need)
    def get_button(self, text, img=None, id=None, cls=None):
        s = '<div class="buttons">\n'
        if cls and not id:
            s += '<button class="%s">\n' % cls
        elif id and not cls:
            s += '<button id="%s">\n' % id
        elif id and cls:
            s += '<button class="%s" id="%s">\n' % (cls, id)
        else:
            s += '<button>\n'
        if img:
            s += '<img src="%s" alt=""/>\n' % img
        s += "%s" % text
        s+= ''' </button>
            </div>\n'''
        return s


    # For and host, return the services sorted by business
    # impact, then state, then desc
    def get_host_services_sorted(self, host):
        t = copy.copy(host.services)
        t.sort(hst_srv_sort)
        return t


    def get_input_bool(self, b, id=None):
        id_s = ''
        if id:
            id_s = 'id="%s"' % id
        if b:
            return """<input type="checkbox" checked="checked" %s/>\n""" % id_s
        else:
            return """<input type="checkbox" %s />\n""" % id_s


    def print_business_rules(self, tree, level=0):
        print "Should print tree", tree
        node = tree['node']
        name = node.get_full_name()
        fathers = tree['fathers']
        s = ''
        # Do not print the node if it's the root one, we already know its state!
        if level != 0:
            s += "%s is %s since %s\n" % (self.get_link(node), node.state, self.print_duration(node.last_state_change, just_duration=True))

        # If we got no parents, no need to print the expand icon
        if len(fathers) > 0:
            # We look ifthe below tree is goodor not
            tree_is_good = (node.state_id == 0)
            
            # If the tree is good, we will use an expand image
            # and hide the tree
            if tree_is_good:
                display = 'none'
                img = 'expand.png'
            else: # we will already show the tree, and use a reduce image
                display = 'block'
                img = 'reduce.png'

            # If we are the root, we already got this
            if level != 0:
                s += """<a id="togglelink-%s" href="javascript:toggleBusinessElt('%s')"><img id="business-parents-img-%s" src="/static/images/%s"> </a> \n""" % (name, name, name, img)
                
            s += """<ul id="business-parents-%s" style="display: %s; ">""" % (name, display)
        
            for n in fathers:
                sub_node = n['node']
                sub_s = self.print_business_rules(n, level=level+1)
                s += '<li class="%s">%s</li>' % (self.get_small_icon_state(sub_node), sub_s)
            s += "</ul>"
        print "Returing s:", s
        return s


    # Get the small state for host/service icons
    def get_small_icon_state(self, obj):
        if obj.state == 'PENDING':
            return 'unknown'
        if obj.state == 'OK':
            return 'ok'
        if obj.state == 'up':
            return 'up'
        # Outch, not a good state...
        if obj.problem_has_been_acknowledged:
            return 'ack'
        return obj.state.lower()

    # For an object, give it's business impact as text 
    # and stars if need
    def get_business_impact_text(self, obj):
        txts = {0 : 'None', 1 : 'Low', 2: 'Normal',
                3 : 'High', 4 : 'Very important', 5 : 'Top for business'}
        nb_stars = max(0, obj.business_impact - 2)
        stars = '<img src="/static/images/star.png">\n' * nb_stars
        
        res = "%s %s" % (txts.get(obj.business_impact, 'Unknown'), stars)
        return res
            

    # We will outpout as a ul/li list the impacts of this 
    def got_impacts_list_as_li(self, obj):
        impacts = obj.impacts
        r = '<ul>\n'
        for i in impacts:
            r += '<li>%s</li>\n' % i.get_full_name()
        r += '</ul>\n'
        return r

    # Return the impacts as a business sorted list
    def get_impacts_sorted(self, obj):
        t = copy.copy(obj.impacts)
        t.sort(hst_srv_sort)
        return t


    def get_link(self, obj, short=False):
        if obj.__class__.my_type == 'service':
            if short:
                name = obj.get_name()
            else:
                name = obj.get_full_name()
            return '<a href="/service/%s"> %s </a>' % (obj.get_full_name(), name)
        # if not service, host
        return '<a href="/host/%s"> %s </a>' % (obj.get_full_name(), obj.get_full_name())
    
    #Give only the /service/blabla or /hsot blabla string, like for buttons inclusion
    def get_link_dest(self, obj):
        return "/%s/%s" % (obj.__class__.my_type, obj.get_full_name())

    # For an host, give it's own link, for a servie, give the link of its host
    def get_host_link(self, obj):
        if obj.__class__.my_type == 'service':
            return self.get_link(obj.host)
        return self.get_link(obj)
    

helper = Helper()
