#!/usr/bin/env python
#Copyright (C) 2009-2010 :
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
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

import os, time, copy
import shlex
import sys
import subprocess

__all__ = ( 'Action' )

valid_exit_status = (0, 1, 2, 3)

only_copy_prop = ('id', 'status', 'command', 't_to_go', 'timeout', 'env')

shellchars = ( '!', '$', '^', '&', '*', '(', ')', '~', '[', ']',
                   '|', '{', '}', ';', '<', '>', '?', '`')


# This abstract class is use just for having a common id between actions and checks
class __Action:
    id = 0

    # Mix the env into the environnment variables
    # into a new local env dict
    # rmq : we cannot just update os.environ because
    # it will be modified for all other checks too
    def get_local_environnement(self):
        local_env = copy.copy(os.environ)
        for p in self.env:
            local_env[p] = self.env[p]
        return local_env


    def execute(self):
        """ Start this action command ; the command will be executed in a subprocess """
        self.status = 'launched'
        self.check_time = time.time()
        self.wait_time = 0.0001
        self.last_poll = self.check_time
        # Get a local env variables with our additionnal values
        self.local_env = self.get_local_environnement()

        return self.execute__()  ## OS specific part


    def get_outputs(self, out, max_plugins_output_length):
        #print "Get only," , max_plugins_output_length, "bytes"
        # Squize all output after max_plugins_output_length
        out = out[:max_plugins_output_length]
        # Then cuts by lines
        elts = out.split('\n')
        # For perf data
        elts_line1 = elts[0].split('|')
        # First line before | is output, and strip it
        self.output = elts_line1[0].strip()
        # After | is perfdata, and strip it
        if len(elts_line1) > 1:
            self.perf_data = elts_line1[1].strip()
        # The others lines are long_output
        # but others are are not stripped
        if len(elts) > 1:
            self.long_output = '\n'.join(elts[1:])


    def check_finished(self, max_plugins_output_length):
        # We must wait, but checks are variable in time
        # so we do not wait the same for an little check
        # than a long ping. So we do like TCP : slow start with *2
        # but do not wait more than 0.1s.
        self.last_poll = time.time()
        if self.process.poll() is None:
            self.wait_time = min(self.wait_time*2, 0.1)
            #time.sleep(wait_time)
            now = time.time()
            if (now - self.check_time) > self.timeout:
                self.kill__()
                #print "Kill", self.process.pid, self.command, now - self.check_time
                self.status = 'timeout'
                self.execution_time = now - self.check_time
                self.exit_status = 3
                return
            return
        # Get standards outputs
        self.exit_status = self.process.returncode
        (stdoutdata, stderrdata) = self.process.communicate()

        #we should not keep the process now
        del self.process

        # if the exit status is anormal, we add stderr to the output
        if self.exit_status not in valid_exit_status:
            stdoutdata = stdoutdata + stderrdata
        # Now grep what we want in the output
        self.get_outputs(stdoutdata, max_plugins_output_length)

        self.status = 'done'
        self.execution_time = time.time() - self.check_time


    def copy_shell__(self, new_i):
        """ This will assign the attributes present in 'only_copy_prop' from self to new_i """
        for prop in only_copy_prop:
            setattr(new_i, prop, getattr(self, prop))
        return new_i


    def got_shell_characters(self):
        for c in self.command:
            if c in shellchars:
                return True
        return False


###
## OS specific "execute__" & "kill__" are defined by "Action" class definition:

if os.name != 'nt': 
    
    class Action(__Action):
  
        # We allow direct launch only for 2.7 and higher version
        # because if a direct launch crash, under this the file hanldes
        # are not releases, it's not good.
        def execute__(self, force_shell=sys.version_info < (2, 7)):
            # If the command line got shell characters, we should go in a shell
            # mode. So look at theses parameters
            force_shell |= self.got_shell_characters()

            if force_shell:
                cmd = self.command
            else :
                cmd = shlex.split(self.command)
              
            try:
                self.process = subprocess.Popen(cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        close_fds=True, shell=force_shell, env=self.local_env)
            except OSError , exp:
                print "Debug : Error in launching command:", self.command, exp, force_shell
                # Maybe it's just a shell we try to exec. So we must retry
                if not force_shell and exp.errno == 8 and exp.strerror == 'Exec format error':
                    return self.execute__(True)
                self.output = exp.__str__()
                self.exit_status = 2
                self.status = 'done'
                self.execution_time = time.time() - self.check_time
  
                # Maybe we run out of file descriptor. It's not good at all!
                if exp.errno == 24 and exp.strerror == 'Too many open files':
                    return 'toomanyopenfiles'

        def kill__(self):
            os.kill(self.process.pid, 9)
  
else:

    import ctypes
    TerminateProcess = ctypes.windll.kernel32.TerminateProcess

    class Action(__Action):
        def execute__(self):
            try:
                self.process = subprocess.Popen(shlex.split(self.command),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.local_env, shell=True)
            except WindowsError, exp:
                print "We kill the process : ", exp, self.command
                self.status = 'timeout'
                self.execution_time = time.time() - self.check_time
  
        def kill__(self):
            TerminateProcess(int(self.process._handle), -1)      

