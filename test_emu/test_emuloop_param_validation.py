from emuloop import DoRun, magnet_devices
import unittest


class TestParameterValidation(unittest.TestCase):

    def setUp(self):
        self.script_definition = DoRun()
        self.start_stop_must_both_be_keep_error_message = \
            "If start {0} or stop {0} is keep, the other must also be keep\n"
        self.field_set_but_magnet_device_not_selected_error_message = \
            "Field set but magnet devices N/A not in possible devices {}\n".format(list(magnet_devices.keys()))
        self.magnet_device_set_error_message = \
            "Magnet device must be one of {} or N/A\n".format(list(magnet_devices.keys()))
        self.non_zero_field_with_active_zf_error_message = "Cannot set a non-zero field with the active zero field\n"
        self.zero_field_with_non_active_zf_error_message = \
            "Trying to set a zero field without using the active zero field ({}, Active ZF)\n"
        self.step_is_zero_error_message = \
            "Cannot step through temperatures when step is zero\n" + "Cannot step through fields when step is zero\n"
        self.step_is_not_positive_error_message = \
            "Step temperature must be positive\n" + "Step field must be positive\n"

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
            self.start_stop_must_both_be_keep_error_message.format("temperature")
        )

    def test_GIVEN_temp_stop_is_keep_and_start_not_keep_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="1.0", stop_temperature="keep",
                                                    step_temperature="1", start_field="keep", stop_field="keep",
                                                    step_field="1", custom="None", mevents="10", magnet_device="TF"),
            self.start_stop_must_both_be_keep_error_message.format("temperature")
        )

    def test_GIVEN_field_start_is_keep_and_stop_not_keep_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_field="keep", stop_field="1.0",
                                                    step_temperature="1", start_temperature="keep",
                                                    stop_temperature="keep", step_field="1", custom="None",
                                                    mevents="10", magnet_device="TF"),
            self.start_stop_must_both_be_keep_error_message.format("field")
        )

    def test_GIVEN_field_stop_is_keep_and_start_not_keep_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_field="1.0", stop_field="keep",
                                                    step_temperature="1", start_temperature="keep",
                                                    stop_temperature="keep", step_field="1", custom="None",
                                                    mevents="10", magnet_device="TF"),
            self.start_stop_must_both_be_keep_error_message.format("field")
        )

    def test_GIVEN_scans_are_defined_AND_steps_are_zero_WHEN_validate_THEN_does_note_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="0", start_field="2", stop_field="30.0",
                                                    step_field="0", custom="None", mevents="10", magnet_device="TF"),
            self.step_is_zero_error_message
        )

    def test_GIVEN_scans_are_defined_AND_steps_are_less_than_zero_WHEN_validate_THEN_does_note_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="-0.0001", start_field="2", stop_field="30.0",
                                                    step_field="-2", custom="None", mevents="10", magnet_device="TF"),
            self.step_is_not_positive_error_message
        )

    def test_GIVEN_try_to_set_zero_field_with_danfysik_and_t20_coils_WHEN_validate_THEN_does_not_validate(self):
        for invalid_magnet, invalid_magnet_name in {"LF": "Danfysik", "TF": "T20 Coils"}.items():
            self.assertEqual(
                self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                        step_temperature="1", start_field="0", stop_field="0",
                                                        step_field="2", custom="None", mevents="10",
                                                        magnet_device=invalid_magnet),
                self.zero_field_with_non_active_zf_error_message.format(invalid_magnet_name)
            )

    def test_GIVEN_try_to_scan_non_zero_field_with_active_zf_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="20.2",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="ZF"),
            self.non_zero_field_with_active_zf_error_message
        )

    def test_GIVEN_try_to_set_non_zero_field_with_active_zf_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="1",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="ZF"),
            self.non_zero_field_with_active_zf_error_message
        )

    def test_GIVEN_try_to_set_field_using_invalid_magnet_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="1",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="INVALID"),
            self.magnet_device_set_error_message
        )

    def test_GIVEN_try_to_set_field_using_na_magnet_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="1",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="N/A"),
            self.field_set_but_magnet_device_not_selected_error_message
        )

    def test_GIVEN_try_to_scan_field_using_na_magnet_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="10.0",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="N/A"),
            self.field_set_but_magnet_device_not_selected_error_message
        )