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


class PluribusConfig(object):

    """Defines configuration-specific methods such as: commit, rollback, diff etc."""

    def __init__(self, device):
        self._device = device

    def commit(self):  # pylint: disable=no-self-use
        """Will commit the changes on the device"""
        return True

    def diff(self):  # pylint: disable=no-self-use
        """Will compute the differences"""
        return ''
