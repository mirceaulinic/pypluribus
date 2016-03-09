__author__ = "Mircea Ulinic <mircea@cloudflare.com>"

# stdlib
import unittest

# local modules
from pyPluribus import PluribusDevice


class _MyPluribusDeviceGlobals(object):

    #----- Connection details ----------------------------------------------------------------------------------------->
    _HOSTNAME_ = 'device.location'
    _USERNAME_ = 'username'
    _PASSWORD_ = 'password'
    #<---- Connection details ------------------------------------------------------------------------------------------


class TestPluribusDevice(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.device = PluribusDevice(_MyPluribusDeviceGlobals._HOSTNAME_,
                                    _MyPluribusDeviceGlobals._USERNAME_,
                                    _MyPluribusDeviceGlobals._PASSWORD_)
        cls.device.open()

    @classmethod
    def tearDownClass(cls):
        cls.device.close()

    def test_connection_open(self):
        self.assertTrue(self.device.up)

    def test_cli(self):
        # will try execute something simple on the CLI and get the output
        help_output = self.device.cli('help')
        result = isinstance(help_output, str) # make sure string is returned
        if result:
            result = result and (len(help_output.splitlines()) > 100) # expecting many lines
        self.assertTrue(result)

    def test_execute_show(self):
        bootenv = self.device.execute_show('bootenv-show') # let's execute a simple show command
        result = isinstance(bootenv, str)
        if result:
            lines_output = bootenv.splitlines()[4:] # exclude first four lines
            # first line is the command sent on the console: 'bootenv-show parsable-delim ;'
            # second line is empty
            # third line contains the loader indicator: 'bootenv-show [-]'
            # fourth line is empty again
            result = result and (len(lines_output) >= 1) # make sure the array is not empty now
            for line in lines_output:
                line_elems = line.split(';')
                result = result and (len(line_elems) == 6) # must have exactly 6 elements
        self.assertTrue(result)
