import unittest
from mock import MagicMock

from emu import DoRun, magnet_devices


class TestParameterValidation(unittest.TestCase):

    def setUp(self):
        self.script_definition = DoRun()
        self.script_definition.begin_waitfor_mevents_end = MagicMock()

    def test_GIVEN_we_are_setting_field_BUT_not_selecting_a_valid_magnet_WHEN_validate_THEN_return_reason(self):
        self.assertEqual(
            self.script_definition.parameters_valid(temperature="1.0", field="17.0", mevents="10", magnet_device="N/A"),
            "Field set but magnet devices N/A not in possible devices {}\n".format(list(magnet_devices.keys()))
        )

    def test_GIVEN_we_are_setting_zero_field_BUT_not_using_active_zf_device_WHEN_validate_THEN_return_reason(self):
        self.assertEqual(
            self.script_definition.parameters_valid(temperature="1.0", field="0.0", mevents="10", magnet_device="TF"),
            "When setting a zero field must use ZF\n"
        )

    def test_GIVEN_we_are_not_setting_zero_field_BUT_are_using_active_zf_device_WHEN_validate_THEN_return_reason(self):
        self.assertEqual(
            self.script_definition.parameters_valid(temperature="1.0", field="200.0", mevents="10", magnet_device="ZF"),
            "Cannot have a non-zero field when selecting ZF\n"
        )

    def test_GIVEN_we_have_valid_params_WHEN_validate_THEN_return_none(self):
        self.assertIsNone(
            self.script_definition.parameters_valid(temperature="1.0", field="200.0", mevents="10", magnet_device="TF")
        )
