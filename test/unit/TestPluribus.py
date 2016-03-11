# -*- coding: utf-8 -*-

"""
TestPluribus.py: this is a tester for the pyPluribus library. Will try to open & close connection to the device,
test basic getters such as CLI and execute_show and will test an end-to-end scenario of a configuration change history.
"""

# stdlib
from __future__ import absolute_import
import unittest

# local modules
import pyPluribus.exceptions
from pyPluribus import PluribusDevice

__author__ = "Mircea Ulinic"
__copyright__ = 'Copyright 2016, CloudFlare, Inc.'
__license__ = "Apache"
__maintainer__ = "Mircea Ulinic"
__contact__ = "mircea@cloudflare.com"
__status__ = "Prototype"


class _MyPluribusDeviceGlobals(object):  # pylint: disable=too-few-public-methods

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

    VALID_CONFIG = '''trunk-create name core05.scl01 port 4,8 speed 40g no-autoneg \
    jumbo enable lacp-mode active port-mac-address 06:a0:00:19:a0:4d send-port 4'''
    VALID_CONFIG_FILE_PATH = 'valid.cfg'
    UNWANTED_CONFIG = '''igmp-snooping-modify enable'''  # typed enable instead of disable...
    INVALID_CONFIG = '''port-storm-control-modify port 39 speed Xg'''
    # instead of "port-storm-control-modify port 39 speed 10g"


class TestPluribusDevice(unittest.TestCase):  # pylint: disable=too-many-public-methods

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

    # ----- Connection management ------------------------------------------------------------------------------------->

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

    # <---- Connection management ------------------------------------------------------------------------------------->

    # ----- Basic interaction ----------------------------------------------------------------------------------------->

    def test_cli(self):
        """Will test if the CLI is available, trying to execute a simple command."""
        help_output = self.device.cli('help')
        self.assertIsInstance(help_output, unicode)
        self.assertGreater(len(help_output.splitlines()), 100)

    def test_raise_cli(self):
        """Will test cli() to raise Exception in case of inexisting command."""
        wrong_command = 'fakecommand'
        self.assertRaises(pyPluribus.exceptions.CommandExecutionError, self.device.cli, wrong_command)

    def test_execute_show(self):
        """Will try to execute a simple show command on the CLI."""
        bootenv = self.device.execute_show('bootenv-show')  # let's execute a simple show command
        self.assertIsInstance(bootenv, unicode)
        lines_output = bootenv.splitlines()
        self.assertGreater(len(lines_output), 0)  # make sure the array is not empty now
        for line in lines_output:
            line_elems = line.split(';')
            self.assertEquals(len(line_elems), 6)  # must have exactly 6 elements

    def test_raise_execute_show(self):
        """Will make execute_show() raise exception."""
        wrong_command = 'switch-config-reset'  # if it does not raise, will erase the config on the switch...
        self.assertRaises(pyPluribus.exceptions.CommandExecutionError, self.device.execute_show, wrong_command)

    def test_show(self):
        """Will test the show() method if returns content when issuing non-specific-formatted commands."""
        mac_addr_table = self.device.show('l2 table')  # for sure this will always return some content
        self.assertGreater(len(mac_addr_table.splitlines()), 0)

    # <---- Basic interaction ------------------------------------------------------------------------------------------

    # ----- Configuration management ---------------------------------------------------------------------------------->

    def test_load_valid_candidate(self):
        """Will try to load a valid candidate config."""
        self.assertFalse(self.device.config.changed())  # config should not be changed at this point
        self.assertTrue(self.device.config.load_candidate(
            config=_MyPluribusDeviceGlobals.VALID_CONFIG))
        self.assertTrue(self.device.config.changed())  # now it should
        self.assertTrue(self.device.config.commit())  # will try to commit changes
        self.assertTrue(self.device.config.committed())  # committed?
        self.assertFalse(self.device.config.changed())  # config should not be changed

    def test_load_valid_candidate_from_file(self):  # pylint: disable=invalid-name
        """Will try to load a valid candidate configuration from a file."""
        self.assertFalse(self.device.config.changed())  # config should not be changed at this point
        self.assertTrue(self.device.config.load_candidate(
            filename=_MyPluribusDeviceGlobals.VALID_CONFIG_FILE_PATH))
        self.assertTrue(self.device.config.changed())  # now it should
        self.assertTrue(self.device.config.commit())  # will try to commit changes
        self.assertTrue(self.device.config.committed())  # committed?
        self.assertFalse(self.device.config.changed())  # config should not be changed

    def test_change_config_by_mistake(self):
        """Will simulate a human error and will set a wrong command."""
        self.assertFalse(self.device.config.changed())  # config should not be changed at this point
        self.assertTrue(self.device.config.load_candidate(
            config=_MyPluribusDeviceGlobals.UNWANTED_CONFIG))
        self.assertTrue(self.device.config.changed())  # now it should be changed
        self.assertTrue(self.device.config.discard())  # let's discard the unwanted config
        self.assertFalse(self.device.config.changed())  # config discarded thus not changes

    def test_load_invalid_config(self):
        """
        Will try to load invalid commands.
        Should raise pyPluribus.exceptions.ConfigLoadError and discard the config.
        """
        self.assertFalse(self.device.config.changed())
        self.assertRaises(pyPluribus.exceptions.ConfigLoadError,
                          self.device.config.load_candidate,
                          _MyPluribusDeviceGlobals.INVALID_CONFIG)
        # should raise error and discard the wron config
        self.assertFalse(self.device.config.changed())  # configuration should not be changed
        self.assertFalse(self.device.config.commit())  # will not commit since the configuration was discarded
        self.assertFalse(self.device.config.committed())  # definitely not committed

    def test_rollback_two_steps(self):
        """
        Should rollback nicely and have on the device the config we initially had.
        There were loaded two valid configurations: from a variable and from a file.
        The unwanted config and invalid config should be already discarded.
        """
        self.assertTrue(self.device.config.rollback(2))

    def test_rollback_big_number_of_steps(self):  # pylint: disable=invalid-name
        """Should raise error."""
        self.assertRaises(pyPluribus.exceptions.RollbackError, self.device.config.rollback, 100)

    def test_rollback_negative_number(self):
        """Should raise error."""
        self.assertRaises(pyPluribus.exceptions.RollbackError, self.device.config.rollback, -5)

    def test_rollback_verify(self):
        """
        After the successfully rollback to the initial config and two failed rollbacks, will try to rollback
        once more. But because we are already in the initial state and no more history available, should
        throw an error.
        """
        self.assertRaises(pyPluribus.exceptions.RollbackError, self.device.config.rollback, 1)

if __name__ == '__main__':

    TEST_RUNNER = unittest.TextTestRunner()

    BASIC_COMMANDS = unittest.TestSuite()
    BASIC_COMMANDS.addTest(TestPluribusDevice("test_connection_open"))
    BASIC_COMMANDS.addTest(TestPluribusDevice("test_cli"))
    BASIC_COMMANDS.addTest(TestPluribusDevice("test_raise_cli"))
    BASIC_COMMANDS.addTest(TestPluribusDevice("test_execute_show"))
    BASIC_COMMANDS.addTest(TestPluribusDevice("test_raise_execute_show"))
    BASIC_COMMANDS.addTest(TestPluribusDevice("test_show"))
    TEST_RUNNER.run(BASIC_COMMANDS)

    FULL_CONFIG_SCENARIO = unittest.TestSuite()
    FULL_CONFIG_SCENARIO.addTest(TestPluribusDevice("test_load_valid_candidate"))
    FULL_CONFIG_SCENARIO.addTest(TestPluribusDevice("test_load_valid_candidate_from_file"))
    FULL_CONFIG_SCENARIO.addTest(TestPluribusDevice("test_change_config_by_mistake"))
    FULL_CONFIG_SCENARIO.addTest(TestPluribusDevice("test_load_invalid_config"))
    FULL_CONFIG_SCENARIO.addTest(TestPluribusDevice("test_rollback_two_steps"))
    FULL_CONFIG_SCENARIO.addTest(TestPluribusDevice("test_rollback_big_number_of_steps"))
    FULL_CONFIG_SCENARIO.addTest(TestPluribusDevice("test_rollback_negative_number"))
    FULL_CONFIG_SCENARIO.addTest(TestPluribusDevice("test_rollback_verify"))
    TEST_RUNNER.run(FULL_CONFIG_SCENARIO)
