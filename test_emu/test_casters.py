import unittest

import numpy as np
from emuloop import cast_custom_expression as cast_custom_expression_emuloop
from emuloop import float_or_keep as float_or_keep_emuloop
from emuloop import magnet_device_type as magnet_device_type_emuloop
from emuloop import magnet_devices as magnet_devices_emuloop
from emulooptime import float_or_keep as float_or_keep_emu
from emulooptime import magnet_device_type as magnet_device_type_emu
from emulooptime import magnet_devices as magnet_devices_emu
from hamcrest import assert_that, calling, raises


class TestMagnetCaster(unittest.TestCase):
    def test_magnet_devices_are_as_expected(self):
        self.assertEqual(
            magnet_devices_emu, {"ZF": "Active ZF", "LF": "Danfysik", "TF": "T20 Coils"}
        )
        self.assertEqual(
            magnet_devices_emuloop, {"ZF": "Active ZF", "LF": "Danfysik", "TF": "T20 Coils"}
        )

    def test_GIVEN_invalid_magnet_WHEN_cast_THEN_raise_value_error(self):
        # GIVEN invalid magnet
        invalid_magnet = "MAGNET"
        self.assertNotIn(invalid_magnet, magnet_devices_emu.keys(), "This magnet should be invalid")
        self.assertNotIn(
            invalid_magnet, magnet_devices_emuloop.keys(), "This magnet should be invalid"
        )
        # WHEN cast THEN raise value error
        assert_that(calling(magnet_device_type_emu).with_args(invalid_magnet), raises(ValueError))
        assert_that(
            calling(magnet_device_type_emuloop).with_args(invalid_magnet), raises(ValueError)
        )

    def test_GIVEN_valid_magnets_upper_and_lower_WHEN_cast_THEN_returns_correct_value(self):
        # GIVEN valid magnets
        for valid_magnet_input, valid_magnet in magnet_devices_emu.items():
            # WHEN cast THEN returns correct value
            self.assertEqual(
                valid_magnet,
                magnet_device_type_emu(valid_magnet_input.upper()),
                "Should return same as dict",
            )
            self.assertEqual(
                valid_magnet,
                magnet_device_type_emu(valid_magnet_input.lower()),
                "Should return same as dict",
            )
            self.assertEqual(
                valid_magnet,
                magnet_device_type_emuloop(valid_magnet_input.upper()),
                "Should return same as dict",
            )
            self.assertEqual(
                valid_magnet,
                magnet_device_type_emuloop(valid_magnet_input.lower()),
                "Should return same as dict",
            )

    def test_GIVEN_na_magnet_mix_of_case_WHEN_cast_THEN_NA_returned(self):
        # GIVEN N/A Magnet mix of case
        magnet = "N/a"
        # WHEN cast THEN N/A returned
        self.assertEqual(
            magnet_device_type_emu(magnet), "N/A", "Should have uppercased and returned N/A"
        )
        self.assertEqual(
            magnet_device_type_emuloop(magnet), "N/A", "Should have uppercased and returned N/A"
        )


class TestFloatOrKeepCall(unittest.TestCase):
    def test_GIVEN_keep_different_cases_WHEN_cast_THEN_return_none(self):
        keep = "KeEp"
        self.assertIsNone(float_or_keep_emu(keep))
        self.assertIsNone(float_or_keep_emu(keep.lower()))
        self.assertIsNone(float_or_keep_emu(keep.upper()))
        self.assertIsNone(float_or_keep_emuloop(keep))
        self.assertIsNone(float_or_keep_emuloop(keep.lower()))
        self.assertIsNone(float_or_keep_emuloop(keep.upper()))

    def test_GIVEN_string_convertable_to_float_WHEN_cast_THEN_return_casted_value(self):
        for float_val in np.linspace(4.0, 5.0, int(abs(4.0 - 5.0) / 0.2) + 1):
            self.assertEqual(float_or_keep_emu(str(float_val)), float_val)
            self.assertEqual(float_or_keep_emuloop(str(float_val)), float_val)

    def test_GIVEN_string_unconvertable_to_float_WHEN_cast_THEN_value_error(self):
        # GIVEN string unconvertable to float
        unconvertable = "test"
        # WHEN cast THEN value error
        assert_that(calling(float_or_keep_emu).with_args(unconvertable), raises(ValueError))
        assert_that(calling(float_or_keep_emuloop).with_args(unconvertable), raises(ValueError))


class TestCustomExpressionCaster(unittest.TestCase):
    def test_GIVEN_empty_expression_WHEN_cast_THEN_none_is_returned(self):
        self.assertEqual(
            cast_custom_expression_emuloop(""),
            "None",
            'We insert None, because eval("") gives an error',
        )

    def test_GIVEN_non_empty_expression_WHEN_cast_THEN_it_is_returned(self):
        self.assertEqual(cast_custom_expression_emuloop("test"), "test")
