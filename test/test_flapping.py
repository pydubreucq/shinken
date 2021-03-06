#!/usr/bin/env python2.6
#Copyright (C) 2009-2010 :
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
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

#
# This file is used to test reading and processing of config files
#

#It's ugly I know....
from shinken_test import *


class TestFlapping(ShinkenTest):
    #Uncomment this is you want to use a specific configuration
    #for your test
    def setUp(self):
        self.setup_with_file('etc/nagios_flapping.cfg')

    
    #Change ME :)
    def test_flapping(self):
        #
        # Config is not correct because of a wrong relative path
        # in the main config file
        #
        print "Get the hosts and services"
        now = time.time()
        host = self.sched.hosts.find_by_name("test_host_0")
        router = self.sched.hosts.find_by_name("test_router_0")
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_0", "test_ok_0")
        self.scheduler_loop(2, [[host, 0, 'UP | value1=1 value2=2'], [router, 0, 'UP | rtt=10'], [svc, 0, 'OK']])
        self.assert_(host.state == 'UP')
        self.assert_(host.state_type == 'HARD')
        self.assert_(svc.flap_detection_enabled)

        # Now 1 test with a bad state
        self.scheduler_loop(1, [[svc, 2, 'Crit']])
        print "******* Current flap change lsit", svc.flapping_changes
        self.scheduler_loop(1, [[svc, 2, 'Crit']])
        print "****** Current flap change lsit", svc.flapping_changes
        #Ok, now go in flap!
        for i in xrange(1, 10):
            "**************************************************"
            print "I:", i
            self.scheduler_loop(1, [[svc, 0, 'Ok']])
            print "******* Current flap change lsit", svc.flapping_changes
            self.scheduler_loop(1, [[svc, 2, 'Crit']])
            print "****** Current flap change lsit", svc.flapping_changes
            print "In flapping?", svc.is_flapping

        # Should get in flapping now
        self.assert_(svc.is_flapping)
        #and get a log about it
        self.assert_(self.any_log_match('SERVICE FLAPPING ALERT.*;STARTED'))

        # Now we put it as back :)
        # 10 is not enouth to get back as normal
        for i in xrange(1, 11):
            self.scheduler_loop(1, [[svc, 0, 'Ok']])
            print "In flapping?", svc.is_flapping
        self.assert_(svc.is_flapping)

        # 10 others can be good (near 4.1 %)
        for i in xrange(1, 11):
            self.scheduler_loop(1, [[svc, 0, 'Ok']])
            print "In flapping?", svc.is_flapping
        self.assert_(not svc.is_flapping)
        self.assert_(self.any_log_match('SERVICE FLAPPING ALERT.*;STOPPED'))

if __name__ == '__main__':
    unittest.main()

