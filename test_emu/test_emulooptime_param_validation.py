import unittest

from emulooptime import DoRun, magnet_devices
from mock import MagicMock


class TestParameterValidation(unittest.TestCase):
    def setUp(self):
        self.script_definition = DoRun()
        self.check_mevents_mock = MagicMock()
        self.script_definition.check_mevents_and_begin_waitfor_mevents_end = self.check_mevents_mock

    def test_GIVEN_we_are_setting_field_BUT_not_selecting_a_valid_magnet_WHEN_validate_THEN_return_reason(
        self,
    ):
        self.assertEqual(
            self.script_definition.parameters_valid(
                start_temperature="1.0",
                stop_temperature="1.0",
                step_temperature="1.0",
                start_field="17.0",
                stop_field="17.0",
                step_field="1",
                custom="None",
                mevents="10",
                magnet_device="N/A",
            ),
            "Field set but magnet devices N/A not in possible devices {}\n".format(
                list(magnet_devices.keys())
            ),
        )

    def test_GIVEN_we_are_setting_zero_field_BUT_not_using_active_zf_device_WHEN_validate_THEN_return_reason(
        self,
    ):
        self.assertEqual(
            self.script_definition.parameters_valid(
                start_temperature="1.0",
                stop_temperature="1.0",
                step_temperature="1.0",
                start_field="0.0",
                stop_field="0.0",
                step_field="0.0",
                custom="None",
                mevents="10",
                magnet_device="TF",
            ),
            "Trying to set a zero field without using the active zero field (T20 Coils, Active ZF)\n",
        )

    def test_GIVEN_we_are_not_setting_zero_field_BUT_are_using_active_zf_device_WHEN_validate_THEN_return_reason(
        self,
    ):
        self.assertEqual(
            self.script_definition.parameters_valid(
                start_temperature="1.0",
                stop_temperature="1.0",
                step_temperature="1.0",
                start_field="0.0",
                stop_field="200.0",
                step_field="20.0",
                custom="None",
                mevents="10",
                magnet_device="TF",
            ),
            "Trying to set a zero field without using the active zero field (T20 Coils, Active ZF)\n",
        )

    def test_GIVEN_we_have_valid_params_WHEN_validate_THEN_return_none(self):
        self.assertIsNone(
            self.script_definition.parameters_valid(
                start_temperature="1.0",
                stop_temperature="1.0",
                step_temperature="1.0",
                start_field="17.0",
                stop_field="17.0",
                step_field="1",
                custom="None",
                mevents="10",
                magnet_device="TF",
            )
        )
