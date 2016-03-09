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

# local modules
import pyPluribus.exceptions


class PluribusConfig(object):

    """Defines configuration-specific methods such as: commit, rollback, diff etc."""

    def __init__(self, device):
        self._device = device
        self._last_working_config = ''
        self._loaded = False
        self._config_history = list()

        self._download_initial_config()

    def _download_initial_config(self):
        """Loads the initial config."""
        _initial_config = self._download_running_config()
        self._last_working_config = _initial_config
        self._config_history[0] = _initial_config
        self._config_history[1] = _initial_config
        self._loaded = True

    def _download_running_config(self):
        """Downloads the config from the switch."""
        return self._device.show('running config')

    def _upload_config_content(self, configuration, rollbacked=False):
        """Will try to upload configuration on the device."""
        try:
            for configuration_line in configuration.splitlines():
                self._device.cli(configuration_line)
        except (pyPluribus.exceptions.CommandExecutionError,
                pyPluribus.exceptions.TimeoutError) as plbrserr:
            if not rollbacked:
                # rollack errors will just trow
                # to avoid loops
                self.discard()
            raise pyPluribus.exceptions.ConfigLoadError("Unable to upload config on the device: {err}.\
                Configuration discarded.".format(err=plbrserr.message))
        return True

    def load_candidate_config(self, filename=None, config=None):
        """
        Will load a candidate configuration on the device.
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
        """Clears uncommited changes"""
        return self.rollback(1)

    def commit(self):  # pylint: disable=no-self-use
        """Will commit the changes on the device"""
        self._last_working_config = self._download_running_config()
        return True  # this will be always true
        # since the changes are automatically applied
        # Pluribus is WYSIWYG-type device...

    def compare(self):  # pylint: disable=no-self-use
        """Will compute the differences"""
        return ''

    def rollback(self, number=1):
        """Rollbacks the configuration to a previous committed state."""
        available_configs = len(self._config_history)
        config_location = available_configs - number - 1
        config = self._config_history[config_location]
        self._upload_config_content(config, rollbacked=True)
        return True
