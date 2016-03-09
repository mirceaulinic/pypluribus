# -*- coding: utf-8 -*-
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

"""
Contains one single class: PluribusDevice necessary to open connection with Pluribus devices
and define basic interaction methods. Configuration-specific methods must be defined in
PluribusConfig class, in config.py file.
"""

from __future__ import absolute_import

# third party libs
import pexpect

# local modules
import pyPluribus.exceptions
from pyPluribus.config import PluribusConfig


class PluribusDevice(object):  # pylint: disable=too-many-instance-attributes

    """Connection establishment and basic interaction with a Pluribus device."""

    def __init__(self, hostname, username, password, port=22, timeout=60):

        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._timeout = timeout

        self._cli_banner = 'CLI ({user}@{host}) > '.format(
            user=self._username,
            host=self._hostname
        )

        self._connection = None

        self.connected = False
        self.config = None

    # ---- Connection management -------------------------------------------------------------------------------------->

    def open(self):
        """Opens a SSH connection with a Pluribus machine."""
        self._connection = pexpect.spawn(
            'ssh -o ConnectTimeout={timeout} -p {port} {user}@{host}'.format(
                timeout=self._timeout,
                port=self._port,
                user=self._username,
                host=self._hostname
            )
        )

        try:
            index = self._connection.expect(['\(yes\/no\)\?', 'Password:', pexpect.EOF], timeout=self._timeout)  # pylint: disable=anomalous-backslash-in-string
            if index == 0:
                self._connection.sendline('yes')
                index = self._connection.expect(['\(yes\/no\)\?', 'Password:', pexpect.EOF], timeout=self._timeout)  # pylint: disable=anomalous-backslash-in-string
            if index == 1:
                self._connection.sendline(self._password)
            elif index == 2:
                pass
            self._connection.expect_exact(self._cli_banner, timeout=self._timeout)
            self._connection.sendline('pager off')  # to disable paging and get all output at once
            self._connection.expect_exact(self._cli_banner, timeout=self._timeout)
            self.connected = True
            self.config = PluribusConfig(self)
        except pexpect.TIMEOUT:
            raise pyPluribus.exceptions.ConnectionError("Connection to the device took too long!")
        except pexpect.EOF:
            raise pyPluribus.exceptions.ConnectionError("Cannot connect to the device! Able to access the device?!")

    def close(self):
        """Closes the SSH connection if the connection is UP."""
        if not self.connected:
            return None
        self._connection.close()
        self.connected = False

    # <--- Connection management ---------------------------------------------------------------------------------------

    def cli(self, command):
        """
        Executes a command and return raw output from the CLI.

        :param command: Command to be executed on the CLI.
        :raise pyPluribus.exceptions.TimeoutError: when execution of the command exceeds the timeout
        :raise pyPluribus.exceptions.EOFError: when not able to retrieve the output
        :return: Raw output of the command
        """
        if not self.connected:
            raise pyPluribus.exceptions.ConnectionError("Not connected to the deivce.")

        output = ''

        try:
            self._connection.sendline(command)
            self._connection.expect_exact(self._cli_banner, timeout=self._timeout)
            output = self._connection.before
        except pexpect.TIMEOUT:
            raise pyPluribus.exceptions.TimeoutError("Execution of command took too long!")
        except pexpect.EOF:
            raise pyPluribus.exceptions.EOFError("Reached EOF while executing comamnd.")

        return output

    def execute_show(self, command):
        """
        Executes show-type commands on the CLI and returns parsable output usinng ';' as delimitor.

        :param command: Show command to be executed
        :raise pyPluribus.exceptions.TimeoutError: when execution of the command exceeds the timeout
        :raise pyPluribus.exceptions.EOFError: when not able to retrieve the output
        :return: Parsable output
        """
        format_command = '{command} parsable-delim ;'.format(
            command=command
        )

        return self.cli(format_command)
