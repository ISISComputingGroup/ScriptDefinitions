import unittest

from emulooptime import inclusive_float_range_with_step_flip


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

    def test_GIVEN_float_range_AND_difference_not_divisible_by_step_WHEN_get_range_matches_arrange(
        self,
    ):
        start, stop, step = 1, 2, 0.3
        # WHEN get range
        returned_range = []
        for i in inclusive_float_range_with_step_flip(start, stop, step):
            returned_range.append(i)
        # THEN inclusive AND expected values
        self.assertEqual([1, 1.3, 1.6, 1.9], returned_range)

    def test_GIVEN_inverted_float_range_AND_difference_not_divisible_by_step_WHEN_get_range_matches_arrange(
        self,
    ):
        start, stop, step = 2, 1, 0.3
        # WHEN get range
        returned_range = []
        for i in inclusive_float_range_with_step_flip(start, stop, step):
            returned_range.append(i)
        # THEN inclusive AND expected values
        self.assertEqual([2, 1.7, 1.4, 1.1], returned_range)

    def test_GIVEN_inverted_float_range_AND_difference_not_divisible_by_step_AND_negative_step_WHEN_get_range_matches_arrange(
        self,
    ):
        start, stop, step = 2, 1, -0.3
        # WHEN get range
        returned_range = []
        for i in inclusive_float_range_with_step_flip(start, stop, step):
            returned_range.append(i)
        # THEN inclusive AND expected values
        self.assertEqual([2, 1.7, 1.4, 1.1], returned_range)
