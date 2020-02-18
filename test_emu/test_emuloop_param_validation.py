from emuloop import DoRun, magnet_devices
import unittest


class TestParameterValidation(unittest.TestCase):

    def setUp(self):
        self.script_definition = DoRun()

    def test_GIVEN_valid_params_WHEN_validate_THEN_none_returned(self):
        self.assertIsNone(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="keep", stop_field="keep",
                                                    step_field="1", custom="None", mevents="10", magnet_device="TF")
        )

    def test_GIVEN_temp_start_is_keep_and_stop_not_keep_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="keep", stop_temperature="1.0",
                                                    step_temperature="1", start_field="keep", stop_field="keep",
                                                    step_field="1", custom="None", mevents="10", magnet_device="TF"),
            "If start temperature or stop temperature is keep, the other must also be keep\n",
        )

    def test_GIVEN_temp_stop_is_keep_and_start_not_keep_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="1.0", stop_temperature="keep",
                                                    step_temperature="1", start_field="keep", stop_field="keep",
                                                    step_field="1", custom="None", mevents="10", magnet_device="TF"),
            "If start temperature or stop temperature is keep, the other must also be keep\n",
        )

    def test_GIVEN_field_start_is_keep_and_stop_not_keep_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_field="keep", stop_field="1.0",
                                                    step_temperature="1", start_temperature="keep",
                                                    stop_temperature="keep", step_field="1", custom="None",
                                                    mevents="10", magnet_device="TF"),
            "If start field or stop field is keep, the other must also be keep\n",
        )

    def test_GIVEN_field_stop_is_keep_and_start_not_keep_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_field="1.0", stop_field="keep",
                                                    step_temperature="1", start_temperature="keep",
                                                    stop_temperature="keep", step_field="1", custom="None",
                                                    mevents="10", magnet_device="TF"),
            "If start field or stop field is keep, the other must also be keep\n",
        )

    def test_GIVEN_scans_are_defined_AND_steps_are_zero_WHEN_validate_THEN_does_note_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="0", start_field="2", stop_field="30.0",
                                                    step_field="0", custom="None", mevents="10", magnet_device="TF"),
            "Cannot step through temperatures when step is zero\n" + "Cannot step through fields when step is zero\n"
        )

    def test_GIVEN_scans_are_defined_AND_steps_are_less_than_zero_WHEN_validate_THEN_does_note_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="-0.0001", start_field="2", stop_field="30.0",
                                                    step_field="-2", custom="None", mevents="10", magnet_device="TF"),
            "Step temperature must be positive\n" + "Step field must be positive\n"
        )

    def test_GIVEN_try_to_set_zero_field_with_danfysik_and_t20_coils_WHEN_validate_THEN_does_not_validate(self):
        for invalid_magnet, invalid_magnet_name in {"LF": "Danfysik", "TF": "T20 Coils"}.items():
            self.assertEqual(
                self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                        step_temperature="1", start_field="0", stop_field="0",
                                                        step_field="2", custom="None", mevents="10",
                                                        magnet_device=invalid_magnet),
                "Trying to set a zero field without using the active zero field ({}, Active ZF)\n".format(
                    invalid_magnet_name)
            )

    def test_GIVEN_try_to_scan_non_zero_field_with_active_zf_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="20.2",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="ZF"),
            "Cannot set a non-zero field with the active zero field\n"
        )

    def test_GIVEN_try_to_set_non_zero_field_with_active_zf_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="1",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="ZF"),
            "Cannot set a non-zero field with the active zero field\n"
        )

    def test_GIVEN_try_to_set_field_using_invalid_magnet_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="1",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="INVALID"),
            "Magnet device must be one of {} or N/A\n".format(list(magnet_devices.keys()))
        )

    def test_GIVEN_try_to_set_field_using_na_magnet_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="1",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="N/A"),
            "Field set but magnet devices N/A not in possible devices {}\n".format(list(magnet_devices.keys()))
        )

    def test_GIVEN_try_to_scan_field_using_na_magnet_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="10.0",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="N/A"),
            "Field set but magnet devices N/A not in possible devices {}\n".format(list(magnet_devices.keys()))
        )