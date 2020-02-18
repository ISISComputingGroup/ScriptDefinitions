from mock import patch, MagicMock
# adapted from: https://stackoverflow.com/questions/8658043/how-to-mock-an-import
import sys
inst_mock = MagicMock()
sys.modules['inst'] = inst_mock
from emuloop import inclusive_float_range_with_step_flip, DoRun, SetDefinition
import unittest


class TestRange(unittest.TestCase):

    def test_GIVEN_float_range_WHEN_get_range_THEN_inclusive_AND_expected_values(self):
        # GIVEN float range
        start, stop, step = 0.5, 2, 0.5
        # WHEN get range
        returned_range = []
        for i in inclusive_float_range_with_step_flip(start, stop, step):
            returned_range.append(i)
        # THEN inclusive AND expected values
        self.assertEqual([0.5, 1, 1.5, 2], returned_range)

    def test_GIVEN_inverted_float_range_WHEN_get_range_THEN_inclusive_AND_expected_values(self):
        # GIVEN float range
        start, stop, step = 2, 0.5, 0.5
        # WHEN get range
        returned_range = []
        for i in inclusive_float_range_with_step_flip(start, stop, step):
            returned_range.append(i)
        # THEN inclusive AND expected values
        self.assertEqual([2, 1.5, 1, 0.5], returned_range)


class TestRun(unittest.TestCase):

    def setUp(self):
        self.script_definition = DoRun()
        self.script_definition.check_mevents_and_begin_waitfor_mevents_end = MagicMock()
        inst_mock.reset_mock()

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_both_temp_field_scans_WHEN_run_THEN_scans_run_once_for_each_set(self, _):
        self.script_definition.run(start_temperature="1.0", stop_temperature="10.0", step_temperature="1",
                                   start_field="2.0", stop_field="20.0", step_field="2.0",
                                   custom="None", mevents="10", magnet_device="LF")
        inst_mock.lf0.assert_called_once()
        self.assertEqual(inst_mock.settemp.call_count, 10)
        self.assertEqual(inst_mock.setmag.call_count, 10 * 10)
        self.assertEqual(self.script_definition.check_mevents_and_begin_waitfor_mevents_end.call_count, 10 * 10)

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_temp_scan_field_point_WHEN_run_THEN_setmag_called_once_AND_scan_runs(self, _):
        self.script_definition.run(start_temperature="1.0", stop_temperature="10.0", step_temperature="1",
                                   start_field="2.0", stop_field="2.0", step_field="2.0",
                                   custom="None", mevents="10", magnet_device="LF")
        inst_mock.lf0.assert_called_once()
        self.assertEqual(inst_mock.settemp.call_count, 10)
        inst_mock.setmag.assert_called_once()
        self.assertEqual(self.script_definition.check_mevents_and_begin_waitfor_mevents_end.call_count, 10)

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_field_scan_temp_point_WHEN_run_THEN_settemp_called_once_AND_scan_runs(self, _):
        self.script_definition.run(start_temperature="1.0", stop_temperature="1.0", step_temperature="1",
                                   start_field="2.0", stop_field="20.0", step_field="2.0",
                                   custom="None", mevents="10", magnet_device="TF")
        inst_mock.tf0.assert_called_once()
        inst_mock.settemp.assert_called_once()
        self.assertEqual(inst_mock.setmag.call_count, 10)
        self.assertEqual(self.script_definition.check_mevents_and_begin_waitfor_mevents_end.call_count, 10)

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_both_field_and_temp_points_WHEN_run_THEN_temp_mag_run_called_once(self, _):
        self.script_definition.run(start_temperature="1.0", stop_temperature="1.0", step_temperature="1",
                                   start_field="2.0", stop_field="2.0", step_field="2.0",
                                   custom="None", mevents="10", magnet_device="TF")
        inst_mock.tf0.assert_called_once()
        inst_mock.settemp.assert_called_once()
        inst_mock.setmag.assert_called_once()
        self.script_definition.check_mevents_and_begin_waitfor_mevents_end.assert_called_once()

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_one_of_start_stop_field_is_keep_AND_temp_scan_WHEN_run_THEN_setmag_not_called_AND_temp_scans_run(
            self, _):
        self.script_definition.run(start_temperature="1.0", stop_temperature="10.0", step_temperature="1",
                                   start_field="keep", stop_field="10.0", step_field="2.0",
                                   custom="None", mevents="10", magnet_device="TF")
        inst_mock.tf0.assert_not_called()
        self.assertEqual(inst_mock.settemp.call_count, 10)
        inst_mock.setmag.assert_not_called()
        self.assertEqual(self.script_definition.check_mevents_and_begin_waitfor_mevents_end.call_count, 10)

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_one_of_start_stop_field_is_keep_AND_temp_point_WHEN_run_THEN_setmag_not_called_AND_temp_set(self, _):
        self.script_definition.run(start_temperature="1.0", stop_temperature="1.0", step_temperature="1",
                                   start_field="keep", stop_field="keep", step_field="2.0",
                                   custom="None", mevents="10", magnet_device="TF")
        inst_mock.tf0.assert_not_called()
        inst_mock.settemp.assert_called_once()
        inst_mock.setmag.assert_not_called()
        self.script_definition.check_mevents_and_begin_waitfor_mevents_end.assert_called_once()

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_one_of_start_stop_temp_is_keep_AND_field_scan_WHEN_run_THEN_settemp_not_called_AND_field_scans_run(
            self, _):
        self.script_definition.run(start_temperature="1.0", stop_temperature="keep", step_temperature="1",
                                   start_field="2", stop_field="20.0", step_field="2.0",
                                   custom="None", mevents="10", magnet_device="TF")
        inst_mock.tf0.assert_called_once()
        self.assertEqual(inst_mock.setmag.call_count, 10)
        inst_mock.settemp.assert_not_called()
        self.assertEqual(self.script_definition.check_mevents_and_begin_waitfor_mevents_end.call_count, 10)

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_one_of_start_stop_temp_is_keep_AND_field_point_WHEN_run_THEN_settemp_not_called_AND_mag_set(self, _):
        self.script_definition.run(start_temperature="keep", stop_temperature="1.0", step_temperature="1",
                                   start_field="2", stop_field="2.0", step_field="2.0",
                                   custom="None", mevents="10", magnet_device="TF")
        inst_mock.tf0.assert_called_once()
        inst_mock.setmag.assert_called_once()
        inst_mock.settemp.assert_not_called()
        self.script_definition.check_mevents_and_begin_waitfor_mevents_end.assert_called_once()

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_keep_temp_and_field_WHEN_run_THEN_settemp_and_setmag_not_called_AND_begin_waitfor_called_once(
            self, _):
        self.script_definition.run(start_temperature="keep", stop_temperature="1.0", step_temperature="1",
                                   start_field="2", stop_field="keep", step_field="2.0",
                                   custom="None", mevents="10", magnet_device="TF")
        inst_mock.tf0.assert_not_called()
        inst_mock.setmag.assert_not_called()
        inst_mock.settemp.assert_not_called()
        self.script_definition.check_mevents_and_begin_waitfor_mevents_end.assert_called_once()


class TestEmuRunHelpers(unittest.TestCase):

    def setUp(self):
        self.script_definition = DoRun()
        inst_mock.reset_mock()

    @patch('genie_python.genie.begin')
    @patch('genie_python.genie.end')
    @patch('genie_python.genie.waitfor_mevents')
    def test_GIVEN_no_mevents_to_wait_for_WHEN_run_THEN_no_run_started(self, begin_mock, _, __):
        self.script_definition.check_mevents_and_begin_waitfor_mevents_end(0)
        begin_mock.assert_not_called()
        self.script_definition.check_mevents_and_begin_waitfor_mevents_end(-3)
        begin_mock.assert_not_called()

    @patch('genie_python.genie.begin')
    @patch('genie_python.genie.end')
    @patch('genie_python.genie.waitfor_mevents')
    def test_GIVEN_more_than_one_mevents_to_wait_for_WHEN_run_THEN_run_started(self, begin_mock, _, __):
        self.script_definition.check_mevents_and_begin_waitfor_mevents_end(3)
        begin_mock.assert_called_once()

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_danfysik_new_selection_WHEN_select_magnet_THEN_danfysik_selected(self, _):
        self.script_definition.set_magnet_device("Danfysik", inst_mock)
        inst_mock.lf0.assert_called_once()

    @patch('genie_python.genie.cget', return_value={"value": "Danfysik"})
    def test_GIVEN_danfysik_old_selection_WHEN_select_magnet_THEN_danfysik_stays_selected(self, _):
        self.script_definition.set_magnet_device("Danfysik", inst_mock)
        inst_mock.lf0.assert_not_called()

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_t20_coils_new_selection_WHEN_select_magnet_THEN_t20_coils_selected(self, _):
        self.script_definition.set_magnet_device("T20 Coils", inst_mock)
        inst_mock.tf0.assert_called_once()

    @patch('genie_python.genie.cget', return_value={"value": "T20 Coils"})
    def test_GIVEN_t20_coils_old_selection_WHEN_select_magnet_THEN_t20_coils_stays_selected(self, _):
        self.script_definition.set_magnet_device("T20 Coils", inst_mock)
        inst_mock.tf0.assert_not_called()

    @patch('genie_python.genie.cget', return_value={"value": "A Magnet"})
    def test_GIVEN_active_zf_new_selection_WHEN_select_magnet_THEN_active_zf_selected(self, _):
        self.script_definition.set_magnet_device("Active ZF", inst_mock)
        inst_mock.f0.assert_called_once()

    @patch('genie_python.genie.cget', return_value={"value": "Active ZF"})
    def test_GIVEN_active_zf_old_selection_WHEN_select_magnet_THEN_active_zf_stays_selected(self, _):
        self.script_definition.set_magnet_device("Active ZF", inst_mock)
        inst_mock.f0.assert_not_called()

    def test_GIVEN_start_stop_equal_WHEN_check_set_definition_THEN_definition_is_point(self):
        self.assertEqual(self.script_definition.check_set_definition(3.0, 3.0), SetDefinition.POINT)

    def test_GIVEN_start_stop_None_WHEN_check_set_definition_THEN_definition_is_undefined(self):
        self.assertEqual(self.script_definition.check_set_definition(None, None), SetDefinition.UNDEFINED)

    def test_GIVEN_start_None_WHEN_check_set_definition_THEN_definition_is_undefined(self):
        self.assertEqual(self.script_definition.check_set_definition(None, 3.0), SetDefinition.UNDEFINED)

    def test_GIVEN_stop_None_WHEN_check_set_definition_THEN_definition_is_undefined(self):
        self.assertEqual(self.script_definition.check_set_definition(3.0, None), SetDefinition.UNDEFINED)

    def test_GIVEN_start_stop_not_equal_WHEN_check_set_definition_THEN_definition_is_undefined(self):
        self.assertEqual(self.script_definition.check_set_definition(3.0, 3.1), SetDefinition.SCAN)


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
            "If start temperature or stop_temperature is keep, the other must also be keep\n",
        )

    def test_GIVEN_temp_stop_is_keep_and_start_not_keep_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="1.0", stop_temperature="keep",
                                                    step_temperature="1", start_field="keep", stop_field="keep",
                                                    step_field="1", custom="None", mevents="10", magnet_device="TF"),
            "If start temperature or stop_temperature is keep, the other must also be keep\n",
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
            "Magnet device must be one of ['LF', 'TF', 'ZF'] or N/A\n"
        )

    def test_GIVEN_try_to_set_field_using_na_magnet_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="1",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="N/A"),
            "Field set but magnet devices N/A not in possible devices ['LF', 'TF', 'ZF']\n"
        )

    def test_GIVEN_try_to_scan_field_using_na_magnet_WHEN_validate_THEN_does_not_validate(self):
        self.assertEqual(
            self.script_definition.parameters_valid(start_temperature="10.5", stop_temperature="1.0",
                                                    step_temperature="1", start_field="1", stop_field="10.0",
                                                    step_field="2", custom="None", mevents="10",
                                                    magnet_device="N/A"),
            "Field set but magnet devices N/A not in possible devices ['LF', 'TF', 'ZF']\n"
        )

