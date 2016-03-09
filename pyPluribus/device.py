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
            index = self._connection.expect(['\(yes\/no\)\?',  # pylint: disable=anomalous-backslash-in-string
                                            'Password:', pexpect.EOF], timeout=self._timeout)
            if index == 0:
                self._connection.sendline('yes')
                index = self._connection.expect(['\(yes\/no\)\?',  # pylint: disable=anomalous-backslash-in-string
                                                'Password:', pexpect.EOF], timeout=self._timeout)
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
        :raise pyPluribus.exceptions.CommandExecutionError: when not able to retrieve the output
        :return: Raw output of the command

        CLI Example:

        .. code-block:: python

            device.cli('switch-poweroff')
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
        except pexpect.EOF as eof:
            raise pyPluribus.exceptions.CommandExecutionError("Unable to execute command: \
                {err}".format(err=eof.message))

        return output

    def execute_show(self, show_command, delim=';'):
        """
        Executes show-type commands on the CLI and returns parsable output usinng ';' as delimitor.

        :param show_command: Show command to be executed
        :param delim: Custom delimiter. Default value: ';'
        :raise pyPluribus.exceptions.TimeoutError: when execution of the command exceeds the timeout
        :raise pyPluribus.exceptions.CommandExecutionError: when not able to retrieve the output
        :return: Parsable output

        CLI Example:

        .. code-block:: python

            device.execute_show('switch-info-show')
            device.execute_show('node-show', '$$')
        """

        if not show_command.endswith('-show'):
            raise pyPluribus.exceptions.CommandExecutionError('All show commands must end with "-show"!')

        if not delim or delim is None:
            delim = ';'

        format_command = '{command} parsable-delim {delim}'.format(
            command=show_command,
            delim=delim
        )

        return self.cli(format_command)

    def show(self, command, delim=';'):
        """
        Executes show-type commands on the CLI and returns parsable output usinng ';' as delimitor.

        :param command: Command to be executed
        :param delim: Custom delimiter. Default value: ';'
        :raise pyPluribus.exceptions.TimeoutError: when execution of the command exceeds the timeout
        :raise pyPluribus.exceptions.CommandExecutionError: when not able to retrieve the output
        :return: Parsable output of the requred stanza

        CLI Example:

        .. code-clock:: python

            device.show('switch-info')
            device.show('switch info')
        """

        if not command.endswith('-show'):
            command += '-show'
        command = command.replace(' ', '-')

        return self.execute_show(command, delim)
