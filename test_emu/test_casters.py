from emu_utils.casters import magnet_device_type, magnet_devices, float_or_keep, cast_custom_expression
import unittest
import numpy as np


class TestMagnetCaster(unittest.TestCase):

    def test_magnet_devices_are_as_expected(self):
        self.assertEqual(magnet_devices, {"ZF": "Active ZF", "LF": "Danfysik", "TF": "T20 Coils"})

    def test_GIVEN_invalid_magnet_WHEN_cast_THEN_raise_value_error(self):
        # GIVEN invalid magnet
        invalid_magnet = "MAGNET"
        self.assertNotIn(invalid_magnet, magnet_devices.keys(), "This magnet should be invalid")
        try:
            # WHEN cast
            magnet_device_type(invalid_magnet)
            self.fail("Should have thrown a value error")
        except ValueError:
            # THEN raise value error
            pass

    def test_GIVEN_valid_magnets_upper_and_lower_WHEN_cast_THEN_returns_correct_value(self):
        # GIVEN valid magnets
        for valid_magnet_input, valid_magnet in magnet_devices.items():
            # WHEN cast THEN returns correct value
            self.assertEqual(valid_magnet, magnet_device_type(valid_magnet_input.upper()),
                             "Should return same as dict")
            self.assertEqual(valid_magnet, magnet_device_type(valid_magnet_input.lower()),
                             "Should return same as dict")
    
    def test_GIVEN_na_magnet_mix_of_case_WHEN_cast_THEN_NA_returned(self):
        # GIVEN N/A Magnet mix of case
        magnet = "N/a"
        # WHEN cast THEN N/A returned
        self.assertEqual(magnet_device_type(magnet), "N/A", "Should have uppercased and returned N/A")


class TestFloatOrKeepCall(unittest.TestCase):

    def test_GIVEN_keep_different_cases_WHEN_cast_THEN_return_none(self):
        keep = "KeEp"
        self.assertIsNone(float_or_keep(keep))
        self.assertIsNone(float_or_keep(keep.lower()))
        self.assertIsNone(float_or_keep(keep.upper()))

    def test_GIVEN_string_convertable_to_float_WHEN_cast_THEN_return_casted_value(self):
        for float_val in np.arange(4.0, 5.0, 0.2):
            self.assertEqual(float_or_keep(str(float_val)), float_val)

    def test_GIVEN_string_unconvertable_to_float_WHEN_cast_THEN_value_error(self):
        # GIVEN string unconvertable to float
        unconvertable = "test"
        try:
            # WHEN cast
            float_or_keep(unconvertable)
            self.fail("Should have thrown a value error")
        except ValueError:
            # THEN value error
            pass


class TestCustomExpressionCaster(unittest.TestCase):

    def test_GIVEN_empty_expression_WHEN_cast_THEN_none_is_returned(self):
        self.assertEqual(cast_custom_expression(""), "None", "We insert None, because eval(\"\") gives an error")

    def test_GIVEN_non_empty_expression_WHEN_cast_THEN_it_is_returned(self):
        self.assertEqual(cast_custom_expression("test"), "test")
