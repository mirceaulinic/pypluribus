# Copyright 2016 CloudFlare, Inc. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import pexpect

from exceptions import TimeoutError, EOFError, ConnectionError


class PluribusDevice(object):

    def __init__(self, hostname, username, password, port = 22, timeout = 60):

        self.hostname = hostname
        self.username = username
        self.password = password
        self.port     = port
        self.timeout  = timeout

        self.cli_banner = 'CLI ({user}@{host}) > '.format(
            user = self.username,
            host = self.hostname
        )

        self.device = None
        self.up = False

    def open(self):

        self.device = pexpect.spawn(
            'ssh -o ConnectTimeout={timeout} -p {port} {user}@{host}'.format(
                timeout = self.timeout,
                port    = self.port,
                user    = self.username,
                host    = self.hostname
            )
        )

        try:
            index = self.device.expect(['\(yes\/no\)\?', 'Password:', pexpect.EOF], timeout = self.timeout)
            if index == 0:
                self.device.sendline('yes')
                index = self.device.expect(['\(yes\/no\)\?', 'Password:', pexpect.EOF], timeout = self.timeout)
            if index == 1:
                self.device.sendline(self.password)
            elif index == 2:
                pass
            self.device.expect_exact(self.cli_banner, timeout = self.timeout)
            self.device.sendline('pager off') # to disable paging and get all output at once
            self.device.expect_exact(self.cli_banner, timeout = self.timeout)
            self.up = True
        except pexpect.TIMEOUT:
            raise TimeoutError("Connection to the device took too long!")
        except pexpect.EOR:
            raise EOFError("Reached EOF!")


    def close(self):

        if not self.up:
            return

        self.device.close()

    def cli(self, command):

        if not self.up:
            raise ConnectionError("Not connected to the deivce")

        output = ''

        try:
            self.device.sendline(command)
            self.device.expect_exact(self.cli_banner, timeout = self.timeout)
            output = self.device.before
        except pexpect.TIMEOUT:
            raise TimeoutError("")
        except pexpect.EOF:
            raise EOFError("")

        return output


    def execute_show(self, command):

        format_command = '{command} parsable-delim ;'.format(
            command = command
        )

        return self.cli(format_command)
