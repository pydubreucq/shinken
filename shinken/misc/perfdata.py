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

import re
from shinken.util import to_best_int_float

metric_patern = re.compile('^([^=]+)=([\d\.\-]+)([\w\/%]*);?([\d\.\-:~@]+)?;?([\d\.\-:~@]+)?;?([\d\.\-]+)?;?([\d\.\-]+)?;?\s*')

# If we can return an int or a float, or None
# if we can't
def guess_int_or_float(val):
    try:
        return to_best_int_float(val)
    except Exception, exp:
        return None


# Class for one metric of a perf_data
class Metric:
    def __init__(self, s):
        self.name = self.value = self.uom = self.warning = self.critical = self.min = self.max = None
        s = s.strip()
        print "Analysis string", s
        r = metric_patern.match(s)
        if r:
            # Get the name but remove all ' in it
            self.name = r.group(1).replace("'", "")
            self.value = guess_int_or_float(r.group(2))
            self.uom = r.group(3)
            self.warning = guess_int_or_float(r.group(4))
            self.critical = guess_int_or_float(r.group(5))
            self.min = guess_int_or_float(r.group(6))
            self.max = guess_int_or_float(r.group(7))
 #       print 'Name', self.name
 #       print "Value", self.value
 #       print "Res", r
            print r.groups()
            if self.uom == '%':
                self.min = 0
                self.max = 100
        


class PerfDatas:
    def __init__(self, s):
        elts = s.split(' ')
        elts = [e for e in elts if e != '']
        self.metrics = {}
        for e in elts:
            m = Metric(e)
            if m.name is not None:
                self.metrics[m.name] = m


    def __iter__(self):
        return self.metrics.itervalues()


    def __len__(self):
        return len(self.metrics)


    def __getitem__(self, key):
        return self.metrics[key]


    def __contains__(self, key):
        return key in self.metrics

    
