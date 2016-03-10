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
from socket import error as socket_error
from socket import gaierror as socket_gaierror

# third party libs
import paramiko

# local modules
import pyPluribus.exceptions
from pyPluribus.config import PluribusConfig


class PluribusDevice(object):  # pylint: disable=too-many-instance-attributes

    """Connection establishment and basic interaction with a Pluribus device."""

    def __init__(self, hostname, username, password, port=22, timeout=60, keepalive=60):

        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._timeout = timeout
        self._keepalive = keepalive

        self._ssh_banner = 'Connected to Switch {hostname};'.format(
            hostname=self._hostname
        )
        self._connection = None

        self.connected = False
        self.config = None

    # ---- Connection management -------------------------------------------------------------------------------------->

    def open(self):
        """Opens a SSH connection with a Pluribus machine."""
        self._connection = paramiko.SSHClient()
        self._connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._connection.connect(hostname=self._hostname,
                                     username=self._username,
                                     password=self._password,
                                     timeout=self._timeout,
                                     port=self._port)
            self._connection.get_transport().set_keepalive(self._keepalive)
            self.connected = True
            self.config = PluribusConfig(self)
        except paramiko.ssh_exception.AuthenticationException:
            raise pyPluribus.exceptions.ConnectionError("Unable to open connection with {hostname}: \
                invalid credentials!".format(hostname=self._hostname))
        except socket_error as sockerr:
            raise pyPluribus.exceptions.ConnectionError("Cannot open connection: {skterr}. \
                Wrong port?".format(skterr=sockerr.message))
        except socket_gaierror as sockgai:
            raise pyPluribus.exceptions.ConnectionError("Cannot open connection: {gaierr}. \
                Wrong hostname?".format(gaierr=sockgai.message))

    def close(self):
        """Closes the SSH connection if the connection is UP."""
        if not self.connected:
            return None
        if self.config is not None:
            if self.config.changed() and not self.config.committed():
                try:
                    self.config.discard()  # if configuration changed and not committed, will rollback
                except pyPluribus.exceptions.ConfigurationDiscardError as discarderr:  # bad luck.
                    raise pyPluribus.exceptions.ConnectionError("Could not discard the configuration: \
                        {err}".format(err=discarderr))
        self._connection.close()  # close SSH connection
        self.config = None  # reset config object
        self._connection = None  #
        self.connected = False

    # <--- Connection management ---------------------------------------------------------------------------------------

    def cli(self, command):
        """
        Executes a command and returns raw output from the CLI.

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

        cli_output = ''

        ssh_session = self._connection.get_transport().open_session()  # opens a new SSH session
        ssh_session.settimeout(self._timeout)

        ssh_session.exec_command(command)

        ssh_output = ''
        err_output = ''

        ssh_output_makefile = ssh_session.makefile()
        ssh_error_makefile = ssh_session.makefile_stderr()

        for byte_output in ssh_output_makefile:
            ssh_output += byte_output

        for byte_error in ssh_error_makefile:
            err_output += byte_error

        if not ssh_output:
            if err_output:
                raise pyPluribus.exceptions.CommandExecutionError(err_output)

        cli_output = '\n'.join(ssh_output.split(self._ssh_banner)[-1].splitlines()[1:])

        if cli_output == 'Please enter username and password:':  # rare cases when connection is lost :(
            self.open()  # retry to open connection
            return self.cli(command)

        return cli_output

    def execute_show(self, show_command, delim=';'):
        """
        Executes show-type commands on the CLI and returns parsable output usinng ';' as delimitor.

        :param show_command: Show command to be executed
        :param delim: Will use specific delimitor. Default: ';'
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
