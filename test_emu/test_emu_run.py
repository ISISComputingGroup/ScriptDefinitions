import unittest

from emu import DoRun
from mock import MagicMock, patch

inst = MagicMock()


class TestEmuRun(unittest.TestCase):
    def setUp(self):
        self.script_definition = DoRun()
        self.script_definition.begin_waitfor_mevents_end = MagicMock()
        inst.reset_mock()

    @patch.dict("sys.modules", inst=inst)
    def test_GIVEN_no_temp_or_field_WHEN_run_THEN_nothing_set_AND_run_happens(self):
        self.script_definition.run(
            temperature="keep", field="keep", mevents="10", magnet_device="N/A"
        )
        inst.settemp.assert_not_called()
        inst.setmag.assert_not_called()
        self.script_definition.begin_waitfor_mevents_end.assert_called_once()

    @patch.dict("sys.modules", inst=inst)
    @patch("genie_python.genie.cget", return_value={"value": "A Magnet"})
    def test_GIVEN_temp_BUT_no_field_WHEN_run_THEN_temp_set_BUT_not_field_AND_run_happens(
        self, cget_mock
    ):
        self.script_definition.run(
            temperature="1.0", field="keep", mevents="10", magnet_device="N/A"
        )
        inst.settemp.assert_called_once()
        inst.setmag.assert_not_called()
        cget_mock.assert_not_called()
        self.script_definition.begin_waitfor_mevents_end.assert_called_once()

    @patch.dict("sys.modules", inst=inst)
    @patch("genie_python.genie.cget", return_value={"value": "A Magnet"})
    def test_GIVEN_field_BUT_no_temp_WHEN_run_THEN_field_set_BUT_not_temp_AND_run_happens(
        self, cget_mock
    ):
        self.script_definition.run(
            temperature="keep", field="1.0", mevents="10", magnet_device="LF"
        )
        cget_mock.assert_called_once()
        inst.settemp.assert_not_called()
        inst.setmag.assert_called_once()
        inst.lf0.assert_called_once()
        self.script_definition.begin_waitfor_mevents_end.assert_called_once()

    @patch.dict("sys.modules", inst=inst)
    @patch("genie_python.genie.cget", return_value={"value": "A Magnet"})
    def test_GIVEN_field_AND_temp_WHEN_run_THEN_field_set_AND_temp_set_AND_run_happens(
        self, cget_mock
    ):
        self.script_definition.run(
            temperature="10.0", field="1.0", mevents="10", magnet_device="TF"
        )
        cget_mock.assert_called_once()
        inst.settemp.assert_called_once()
        inst.setmag.assert_called_once()
        inst.tf0.assert_called_once()
        self.script_definition.begin_waitfor_mevents_end.assert_called_once()
