import unittest

from parameterized import parameterized

from emuloop import DoRun, magnet_devices

start_stop_must_both_be_keep_error_message = (
    "If start {0} or stop {0} is keep, the other must also be keep\n"
)

field_set_but_magnet_device_not_selected_error_message = (
    "Field set but magnet devices N/A not in possible devices {}\n".format(
        list(magnet_devices.keys())
    )
)

magnet_device_set_error_message = "Magnet device must be one of {} or N/A\n".format(
    list(magnet_devices.keys())
)

non_zero_field_with_active_zf_error_message = (
    "Cannot set a non-zero field with the active zero field\n"
)

zero_field_with_non_active_zf_error_message = (
    "Trying to set a zero field without using the active zero field ({}, Active ZF)\n"
)

step_is_zero_error_message = (
    "Cannot step through temperatures when step is zero\n"
    + "Cannot step through fields when step is zero\n"
)

step_is_not_positive_error_message = (
    "Step temperature must be positive\n" + "Step field must be positive\n"
)


class TestParameterValidation(unittest.TestCase):
    def setUp(self):
        self.script_definition = DoRun()

    @parameterized.expand(
        [
            (
                {
                    "start_temperature": "keep",
                    "stop_temperature": "keep",
                    "step_temperature": "1",
                    "start_field": "keep",
                    "stop_field": "keep",
                    "step_field": "1",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "TF",
                },
                None,
            ),
            (
                {
                    "start_temperature": "keep",
                    "stop_temperature": "1.0",
                    "step_temperature": "1",
                    "start_field": "keep",
                    "stop_field": "keep",
                    "step_field": "1",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "TF",
                },
                start_stop_must_both_be_keep_error_message.format("temperature"),
            ),
            (
                {
                    "start_temperature": "1.0",
                    "stop_temperature": "keep",
                    "step_temperature": "1",
                    "start_field": "keep",
                    "stop_field": "keep",
                    "step_field": "1",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "TF",
                },
                start_stop_must_both_be_keep_error_message.format("temperature"),
            ),
            (
                {
                    "start_temperature": "keep",
                    "stop_temperature": "keep",
                    "step_temperature": "1",
                    "start_field": "keep",
                    "stop_field": "1.0",
                    "step_field": "1",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "TF",
                },
                start_stop_must_both_be_keep_error_message.format("field"),
            ),
            (
                {
                    "start_temperature": "keep",
                    "stop_temperature": "keep",
                    "step_temperature": "1",
                    "start_field": "1.0",
                    "stop_field": "keep",
                    "step_field": "1",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "TF",
                },
                start_stop_must_both_be_keep_error_message.format("field"),
            ),
            (
                {
                    "start_temperature": "10.5",
                    "stop_temperature": "1.0",
                    "step_temperature": "0",
                    "start_field": "1",
                    "stop_field": "30.0",
                    "step_field": "0",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "TF",
                },
                step_is_zero_error_message,
            ),
            (
                {
                    "start_temperature": "10.5",
                    "stop_temperature": "1.0",
                    "step_temperature": "-0.0001",
                    "start_field": "2",
                    "stop_field": "30.0",
                    "step_field": "-2",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "TF",
                },
                step_is_not_positive_error_message,
            ),
            (
                {
                    "start_temperature": "10.5",
                    "stop_temperature": "1.0",
                    "step_temperature": "1",
                    "start_field": "1",
                    "stop_field": "20.2",
                    "step_field": "2",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "ZF",
                },
                non_zero_field_with_active_zf_error_message,
            ),
            (
                {
                    "start_temperature": "10.5",
                    "stop_temperature": "1.0",
                    "step_temperature": "1",
                    "start_field": "1",
                    "stop_field": "1",
                    "step_field": "2",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "ZF",
                },
                non_zero_field_with_active_zf_error_message,
            ),
            (
                {
                    "start_temperature": "10.5",
                    "stop_temperature": "1.0",
                    "step_temperature": "1",
                    "start_field": "1",
                    "stop_field": "1",
                    "step_field": "2",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "INVALID",
                },
                magnet_device_set_error_message,
            ),
            (
                {
                    "start_temperature": "10.5",
                    "stop_temperature": "1.0",
                    "step_temperature": "1",
                    "start_field": "1",
                    "stop_field": "1",
                    "step_field": "2",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "N/A",
                },
                field_set_but_magnet_device_not_selected_error_message,
            ),
            (
                {
                    "start_temperature": "10.5",
                    "stop_temperature": "1.0",
                    "step_temperature": "1",
                    "start_field": "1",
                    "stop_field": "10.0",
                    "step_field": "2",
                    "custom": "None",
                    "mevents": "10",
                    "magnet_device": "N/A",
                },
                field_set_but_magnet_device_not_selected_error_message,
            ),
        ]
    )
    def test_GIVEN_params_WHEN_validate_THEN_appropriate_return(self, params, expected_return):
        self.assertEqual(self.script_definition.parameters_valid(**params), expected_return)

    @parameterized.expand([("LF", "Danfysik"), ("TF", "T20 Coils")])
    def test_GIVEN_try_to_set_zero_field_with_non_activezf_mag_WHEN_validate_THEN_does_not_validate(
        self, invalid_magnet, invalid_magnet_name
    ):
        self.assertEqual(
            self.script_definition.parameters_valid(
                start_temperature="10.5",
                stop_temperature="1.0",
                step_temperature="1",
                start_field="0",
                stop_field="0",
                step_field="2",
                custom="None",
                mevents="10",
                magnet_device=invalid_magnet,
            ),
            zero_field_with_non_active_zf_error_message.format(invalid_magnet_name),
        )
