# -*- coding: utf-8 -*-

"""
TestPluribus.py: this is a tester for the pyPluribus library. Will try to open & close connection to the device,
test basic getters such as CLI and execute_show.
"""

from __future__ import absolute_import

__author__ = "Mircea Ulinic"
__copyright__ = 'Copyright 2016, CloudFlare, Inc.'
__license__ = "Apache"
__maintainer__ = "Mircea Ulinic"
__contact__ = "mircea@cloudflare.com"
__status__ = "Prototype"

# stdlib
import unittest

# local modules
from pyPluribus import PluribusDevice


class _MyPluribusDeviceGlobals(object):

    """
    This clsas contains only static data, basically only constants to be used in the tester classes.
    """

    def __init__(self):
        pass

    def __repr__(self):
        return 'class {class_name} having the following globals defined: {global_list}'.format(
            class_name=self.__class__.__name__,
            global_list=','.join(dir(self))
        )

    # ----- Connection details ---------------------------------------------------------------------------------------->
    HOSTNAME = 'device.location'
    USERNAME = 'username'
    PASSWORD = 'password'
    # <---- Connection details -----------------------------------------------------------------------------------------


class TestPluribusDevice(unittest.TestCase):

    """
    This will test the basic methods of the PluribusDevice: open&close connection, CLI getter etc.
    """

    def __repr__(self):
        return 'class {class_name}: {class_doc}'.format(
            class_name=self.__class__.__name__,
            class_doc=self.__doc__
        )

    def __str__(self):
        return self.__repr__()

    @classmethod
    def setUpClass(cls):
        """Opens the connection with the device."""
        cls.device = PluribusDevice(_MyPluribusDeviceGlobals.HOSTNAME,
                                    _MyPluribusDeviceGlobals.USERNAME,
                                    _MyPluribusDeviceGlobals.PASSWORD)
        cls.device.open()

    @classmethod
    def tearDownClass(cls):
        """Closes the connection with the device."""
        cls.device.close()

    def test_connection_open(self):
        """Will test if the connection is really open."""
        self.assertTrue(self.device.connected)

    def test_cli(self):
        """Will test if the CLI is available, trying to execute a simple command."""
        help_output = self.device.cli('help')
        result = isinstance(help_output, str)  # make sure string is returned
        if result:
            result = result and (len(help_output.splitlines()) > 100)  # expecting many lines
        self.assertTrue(result)

    def test_execute_show(self):
        """Will try to execute a simple show command on the CLI"""
        bootenv = self.device.execute_show('bootenv-show')  # let's execute a simple show command
        result = isinstance(bootenv, str)
        if result:
            lines_output = bootenv.splitlines()[4:]  # exclude first four lines
            # first line is the command sent on the console: 'bootenv-show parsable-delim ;'
            # second line is empty
            # third line contains the loader indicator: 'bootenv-show [-]'
            # fourth line is empty again
            result = result and (len(lines_output) >= 1)  # make sure the array is not empty now
            for line in lines_output:
                line_elems = line.split(';')
                result = result and (len(line_elems) == 6)  # must have exactly 6 elements
        self.assertTrue(result)
