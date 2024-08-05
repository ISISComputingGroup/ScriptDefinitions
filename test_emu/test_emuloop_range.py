import unittest

from emuloop import inclusive_float_range_with_step_flip


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
