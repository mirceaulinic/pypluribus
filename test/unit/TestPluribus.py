# -*- coding: utf-8 -*-

"""
TestPluribus.py: this is a tester for the pyPluribus library. Will try to open & close connection to the device,
test basic getters such as CLI and execute_show and will test an end-to-end scenario of a configuration change history.
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
import pyPluribus.exceptions
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

    TESTING_FULL_CONFIG_SCENARIO = False  # used to test end-to-end config scenario
    VALID_CONFIG = '''trunk-create name core05.scl01 port 4,8 speed 40g no-autoneg \
    jumbo enable lacp-mode active port-mac-address 06:a0:00:19:a0:4d send-port 4'''
    VALID_CONFIG_FILE_PATH = 'valid.cfg'
    UNWANTED_CONFIG = '''igmp-snooping-modify enable'''  # typed enable instead of disable...
    INVALID_CONFIG = '''port-storm-control-modify port 39 speed Xg'''
    # instead of "port-storm-control-modify port 39 speed 10g"


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

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)  # run this test only in suite
    def test_non_changed_config(self):
        """Configuration should not be changed at this point."""
        self.assertFalse(self.device.config.changed())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_load_valid_candidate(self):
        """Will try to load a valid candidate config."""
        valid_config = ''' '''
        self.assertTrue(self.device.load_candidate(
            config=_MyPluribusDeviceGlobals.VALID_CONFIG))

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_config_changed(self):
        """Tests if the configuration on the deviced is changed now."""
        self.assertTrue(self.device.config.changed())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_commit(self):
        """Will test if the commit succeeds."""
        self.assertTrue(self.device.config.commit())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_committed(self):
        """Are you committed?"""
        self.assertTrue(self.device.config.committed())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_config_changed_after_commit(self):
        """After commit should say that the config was not changed!"""
        self.assertFalse(self.device.config.changed())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_load_valid_candidate_from_file(self):
        """Will try to load a valid candidate configuration from a file."""
        valid_config_file_path = 'pluribus_valid.cfg'
        self.assertTrue(self.device.load_candidate(
            filename=_MyPluribusDeviceGlobals.VALID_CONFIG_FILE_PATH))

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_config_changed_again(self):
        """Now the configuration should be changed again."""
        self.assertTrue(self.device.config.changed())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_commit_again(self):
        """Will try to commit the newest changes."""
        self.assertTrue(self.device.config.commit())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_change_config_by_mistake(self):
        """Will simulate a human error and will set a wrong command."""
        self.assertTrue(self.device.config.load_candidate(
            config=_MyPluribusDeviceGlobals.UNWANTED_CONFIG))

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_discard_unwanted_config(self):
        """Will cancel the unwanted config"""
        self.assertTrue(self.device.config.discard())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_config_changed_after_discard(self):
        """The configuration should be not changed now."""
        self.assertFalse(self.device.config.changed())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_load_invalid_config(self):
        """
        Will try to load invalid commands.
        Should raise pyPluribus.exceptions.ConfigLoadError and discard the config.
        """
        self.assertRaises(pyPluribus.exceptions.ConfigLoadError,
                         self.device.config.load_candidate,
                         _MyPluribusDeviceGlobals.INVALID_CONFIG)

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_config_cahged_after_trying_to_load_invalid_conifg(self):
        """When trying to load an invalid config, should discard and rollback to last commit."""
        self.assertFalse(self.device.config.changed())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_commit_after_trying_to_load_invalid_config(self):
        """Commit command should return false because there's nothing changed."""
        self.assertFalse(self.device.config.commit())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_check_again_if_committed(self):
        """Should not at all be committed."""
        self.assertFalse(self.device.config.committed())

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_rollback_two_steps(self):
        """
        Should rollback nicely and have on the device the config we initially had.
        There were loaded two valid configurations: from a variable and from a file.
        The unwanted config and invalid config should be already discarded.
        """
        self.assertTrue(self.device.config.rollback(2))

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_rollback_big_number_of_steps(self):
        """Should raise error."""
        self.assertRaises(pyPluribus.exceptions.RollbackError, self.device.confi.rollback, 100)

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_rollback_negative_number(self):
        """Should raise error."""
        self.assertRaises(pyPluribus.exceptions.RollbackError, self.device.confi.rollback, -5)

    @unittest.skipUnless(_MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO, True)
    def test_rollback_again(self):
        """
        After the successfully rollback to the initial config and two failed rollbacks, will try to rollback
        once more. But because we are already in the initial state and no more history available, should
        throw an error.
        """
        self.assertRaises(pyPluribus.exceptions.RollbackError, self.device.confi.rollback, 1)

if __name__ == '__main__':

    test_runner = unittest.TextTestRunner()

    basic_commands = unittest.TestSuite()
    basic_commands.addTest(TestPluribusDevice("test_connection_open"))
    basic_commands.addTest(TestPluribusDevice("test_cli"))
    basic_commands.addTest(TestPluribusDevice("test_raise_cli"))
    basic_commands.addTest(TestPluribusDevice("test_execute_show"))
    basic_commands.addTest(TestPluribusDevice("test_raise_execute_show"))
    basic_commands.addTest(TestPluribusDevice("test_show"))
    test_runner.run(basic_commands)

    _MyPluribusDeviceGlobals.TESTING_FULL_CONFIG_SCENARIO = True
    full_config_scenario = unittest.TestSuite()
    full_config_scenario.addTest(TestPluribusDevice("test_non_changed_config"))
    full_config_scenario.addTest(TestPluribusDevice("test_load_valid_candidate"))
    full_config_scenario.addTest(TestPluribusDevice("test_config_changed"))
    full_config_scenario.addTest(TestPluribusDevice("test_commit"))
    full_config_scenario.addTest(TestPluribusDevice("test_commit"))
    full_config_scenario.addTest(TestPluribusDevice("test_config_changed_after_commit"))
    full_config_scenario.addTest(TestPluribusDevice("test_load_valid_candidate_from_file"))
    full_config_scenario.addTest(TestPluribusDevice("test_config_changed_again"))
    full_config_scenario.addTest(TestPluribusDevice("test_commit_again"))
    full_config_scenario.addTest(TestPluribusDevice("test_change_config_by_mistake"))
    full_config_scenario.addTest(TestPluribusDevice("test_discard_unwanted_config"))
    full_config_scenario.addTest(TestPluribusDevice("test_config_changed_after_discard"))
    full_config_scenario.addTest(TestPluribusDevice("test_load_invalid_config"))
    full_config_scenario.addTest(TestPluribusDevice("test_config_cahged_after_trying_to_load_invalid_conifg"))
    full_config_scenario.addTest(TestPluribusDevice("test_commit_after_trying_to_load_invalid_config"))
    full_config_scenario.addTest(TestPluribusDevice("test_check_again_if_committed"))
    full_config_scenario.addTest(TestPluribusDevice("test_rollback_two_steps"))
    full_config_scenario.addTest(TestPluribusDevice("test_rollback_big_number_of_steps"))
    full_config_scenario.addTest(TestPluribusDevice("test_rollback_negative_number"))
    full_config_scenario.addTest(TestPluribusDevice("test_rollback_again"))
    test_runner.run(full_config_scenario)
