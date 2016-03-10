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
Defines pyPluribus specific exceptions.
"""


class TimeoutError(Exception):
    """Raised in case of exceeded runtime for a command."""
    pass


class CommandExecutionError(Exception):
    """Raised in case the output cannot be retrieved."""
    pass


class ConnectionError(Exception):
    """Raised when the connection with the pluribus device cannot be open."""
    pass


class ConfigLoadError(Exception):
    """Raised when not able to upload configuration on the device"""
    pass


class ConfigurationDiscardError(Exception):
    """Raised when not possible to discard a candidate configuration"""
    pass


class MergeConfigError(Exception):
    """Raised when not able to merge the config"""
    pass


class ReplaceConfigError(Exception):
    """Raised when not able to replace the config"""
    pass


class RollbackError(Exception):
    """Raised in case of rollback failure."""
    pass
