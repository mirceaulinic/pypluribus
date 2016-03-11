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
This module contains configuration-specific class PluribusConfig and necessary helpers.
"""

from __future__ import absolute_import

import difflib

# local modules
import pyPluribus.exceptions


class PluribusConfig(object):

    """
    Defines configuration-specific methods such as:
        * load_candidate
        * commit
        * rollback
        * discard
        * compare
    Since Pluribus devices are WYSIWYG-type devices, there is only a "running-config" file
    which also is "startup-config" equivalent. Thus, all changes are definitive.
    In order to overcome this disadvantage, we have to emulate all methodologies and
    store the history of configuration changes.
    """

    def __init__(self, device):
        self._device = device
        self._last_working_config = ''
        self._config_changed = False
        self._committed = False
        self._config_history = list()

        self._download_initial_config()

    def _download_initial_config(self):
        """Loads the initial config."""
        _initial_config = self._download_running_config()  # this is a bit slow!
        self._last_working_config = _initial_config
        self._config_history.append(_initial_config)
        self._config_history.append(_initial_config)

    def _download_running_config(self):
        """Downloads the running config from the switch."""
        return self._device.show('running config')

    def _upload_config_content(self, configuration, rollbacked=False):
        """Will try to upload a specific configuration on the device."""
        try:
            for configuration_line in configuration.splitlines():
                self._device.cli(configuration_line)
            self._config_changed = True  # configuration was changed
            self._committed = False  # and not committed yet
        except (pyPluribus.exceptions.CommandExecutionError,
                pyPluribus.exceptions.TimeoutError) as clierr:
            if not rollbacked:
                # rollack errors will just trow
                # to avoid loops
                self.discard()
            raise pyPluribus.exceptions.ConfigLoadError("Unable to upload config on the device: {err}.\
                Configuration will be discarded.".format(err=clierr.message))
        return True

    def changed(self):  # pylint: disable=no-self-use
        """Returns if the configuration changes loaded had actually any effect on running config on the device"""
        return self._config_changed and self.compare()

    def committed(self):  # pylint: disable=no-self-use
        """Returns if the configuration was committed"""
        return self._committed

    def load_candidate(self, filename=None, config=None):
        """
        Loads a candidate configuration on the device.
        In case the load fails at any point, will automatically rollback to last working configuration.

        :param filename: Specifies the name of the file with the configuration content.
        :param config: New configuration to be uploaded on the device.
        :raise pyPluribus.exceptions.ConfigLoadError: When the configuration could not be uploaded to the device.
        """

        configuration = ''

        if filename is None:
            configuration = config
        else:
            with open(filename) as config_file:
                configuration = config_file.read()

        return self._upload_config_content(configuration)

    def discard(self):  # pylint: disable=no-self-use
        """
        Clears uncommited changes.

        :raise pyPluribus.exceptions.ConfigurationDiscardError: If the configuration applied cannot be discarded.
        """
        try:
            self.rollback(0)
        except pyPluribus.exceptions.RollbackError as rbackerr:
            raise pyPluribus.exceptions.ConfigurationDiscardError("Cannot discard configuration: {err}.\
                ".format(err=rbackerr))

    def commit(self):  # pylint: disable=no-self-use
        """Will commit the changes on the device"""
        if self._config_changed:
            self._last_working_config = self._download_running_config()
            self._config_history.append(self._last_working_config)
            self._committed = True  # comfiguration was committed
            self._config_changed = False  # no changes since last commit :)
            return True  # this will be always true
            # since the changes are automatically applied
        self._committed = False  # make sure the _committed attribute is not True by any chance
        return False  # nothing to commit

    def compare(self):  # pylint: disable=no-self-use
        """
        Computes the difference between the candidate config and the running config.
        """
        # becuase we emulate the configuration history
        # the difference is between the last committed config and the running-config
        running_config = self._download_running_config()
        running_config_lines = running_config.splitlines()
        last_committed_config = self._last_working_config
        last_committed_config_lines = last_committed_config.splitlines()
        difference = difflib.unified_diff(running_config_lines, last_committed_config_lines, n=0)
        return '\n'.join(difference)

    def rollback(self, number=0):
        """
        Will rollback the configuration to a previous state.
        Can be called also when

        :param number: How many steps back in the configuration history must look back.
        :raise pyPluribus.exceptions.RollbackError: In case the configuration cannot be rolled back.
        """
        if number < 0:
            raise pyPluribus.exceptions.RollbackError("Please provide a positive number to rollback to!")
        available_configs = len(self._config_history)
        max_rollbacks = available_configs - 2
        if max_rollbacks < 0:
            raise pyPluribus.exceptions.RollbackError("Cannot rollback: \
                not enough configration history available!")
        if max_rollbacks > 0 and number > max_rollbacks:
            raise pyPluribus.exceptions.RollbackError("Cannot rollback more than {cfgs} configurations!\
                ".format(cfgs=max_rollbacks))
        config_location = 1  # will load the initial config worst case (user never commited, but wants to discard)
        if max_rollbacks > 0:  # in case of previous commit(s) will be able to load a specific configuration
            config_location = available_configs - number - 1  # stored in location len() - rollabck_nb - 1
            # covers also the case of discard uncommitted changes (rollback 0)
        desired_config = self._config_history[config_location]
        try:
            self._upload_config_content(desired_config, rollbacked=True)
        except pyPluribus.exceptions.ConfigLoadError as loaderr:
            raise pyPluribus.exceptions.RollbackError("Cannot rollback: {err}".format(err=loaderr))
        del self._config_history[(config_location+1):]  # delete all newer configurations than the config rolled back
        self._last_working_config = desired_config
        self._committed = True
        self._config_changed = False
        return True
