from genie_python.genie_script_generator import ActionDefinition, cast_parameters_to
from genie_python import genie as g
from importlib import import_module
import numpy as np
from enum import Enum


class SetDefinition(Enum):
    UNDEFINED = 1
    POINT = 2
    SCAN = 3


# Allow the user to right keep in temp or field to use the current value
def float_or_keep(temp_or_field):
    if temp_or_field.lower() == "keep":
        return None
    else:
        return float(temp_or_field)


magnet_devices = {"ZF": "Active ZF", "LF": "Danfysik", "TF": "T20 Coils"}


# Convert to magnet device type if possible, if not they have input an incorrect magnet_device
# Raise a ValueError and this will be caught and displayed to the user that the conversion is incorrect
def magnet_device_type(magnet_device):
    magnet_device = magnet_device.upper()
    if magnet_device in magnet_devices.keys():
        return magnet_devices[magnet_device]
    elif magnet_device == "N/A":
        return magnet_device
    raise ValueError("Magnet device must be one of {} or N/A".format(magnet_devices))


# Cast the custom python expression to a string or None if empty
def cast_custom_expression(expression):
    if expression == "":
        return "None"
    else:
        return expression


def inclusive_float_range_with_step_flip(start, stop, step):
    """
    If we are counting downwards from start to stop automatically flips step to be negative.
    Inclusive of stop. Only tested for float values.

    Parameters:
      start (float): the value to start the range from
      stop (float): the value to stop the range at
      step (float): the steps to take from start to stop

    Returns:
      The range from start to stop including all steps in between.

    Examples:
      >>> inclusive_float_range_with_step_flip(0.5, 2, 0.5) == [0.5, 1, 1.5, 2]
      >>> inclusive_float_range_with_step_flip(2, 0.5, 0.5) == [2, 1.5, 1, 0.5]
    """
    if start > stop and step > 0:
        step = -step
    stop = stop + step
    for i in np.arange(start, stop, step):
        yield i


class DoRun(ActionDefinition):

    active_zf = "Active ZF"
    possible_magnet_devices = [active_zf, "Danfysik", "T20 Coils"]

    def get_help(self):
        return """
Magnet device must be one of {} or if the field is KEEP then it can be N/A.\n
If the field is zero magnet device must be ZF.\n
        """.format(list(magnet_devices.keys()))

    # Loop through a set of temperatures or fields using a start, stop and step mechanism
    @cast_parameters_to(
         start_temperature=float_or_keep, stop_temperature=float_or_keep, step_temperature=float,
         start_field=float_or_keep, stop_field=float_or_keep, step_field=float, 
         custom=cast_custom_expression, mevents=int, magnet_device=magnet_device_type)
    def run(self,
            start_temperature=1.0, stop_temperature=1.0, step_temperature=10,
            start_field=1.0, stop_field=1.0, step_field=1.0,
            custom="None", mevents=10, magnet_device="N/A"):
        # Scan if start and stop are different, set once if they are equal or do not set if they are None
        temp_set_definition = self.check_set_definition(start_temperature, stop_temperature)
        field_set_definition = self.check_set_definition(start_field, stop_field)
        # Use the instrument scripts to set the magnet device correctly
        import inst
        if field_set_definition != SetDefinition.UNDEFINED:
            self.set_magnet_device(magnet_device, inst)
        # Run scans for both the temperature and the field
        if temp_set_definition == SetDefinition.SCAN and field_set_definition == SetDefinition.SCAN:
            # Evaluate the user command before scanning
            eval(custom)
            # When we are scanning both temperature and field do all combinations
            self.run_temp_and_field_scans(start_temperature, stop_temperature, step_temperature,
                                          start_field, stop_field, step_field, mevents, inst)
        elif temp_set_definition == SetDefinition.SCAN:  # Run scans for the temperature
            # Evaluate the user command before scanning
            eval(custom)
            # Set the field to use for all the scans
            if field_set_definition == SetDefinition.POINT:
                inst.setmag(start_field, wait=True)
            self.run_scans(start_temperature, stop_temperature, step_temperature, mevents, inst.settemp)
        elif field_set_definition == SetDefinition.SCAN:  # Run scans for the field
            # Evaluate the user command before scanning
            eval(custom)
            # Set the temperature to use for all the scans
            if temp_set_definition == SetDefinition.POINT:
                inst.settemp(start_temperature, wait=True)
            self.run_scans(start_field, stop_field, step_field, mevents, inst.setmag)
        elif field_set_definition == SetDefinition.POINT and temp_set_definition == SetDefinition.POINT:
            # Set the temperature and the field once each and do a run (if mevents > 0)
            eval(custom)
            inst.settemp(start_temperature, wait=True)
            inst.setmag(start_field, wait=True)
            self.begin_waitfor_mevents_end(mevents)
        elif field_set_definition == SetDefinition.POINT:
            eval(custom)
            inst.setmag(start_field, wait=True)
            self.begin_waitfor_mevents_end(mevents)
        elif temp_set_definition == SetDefinition.POINT:
            eval(custom)
            inst.settemp(start_field, wait=True)
            self.begin_waitfor_mevents_end(mevents)
        else:
            # Do a run without setting (if mevents > 0)
            self.begin_waitfor_mevents_end(mevents)

    def begin_waitfor_mevents_end(self, mevents):
        if mevents > 0:
            g.begin(quiet=True)
            g.waitfor_mevents(mevents)
            g.end(quiet=True)

    def set_magnet_device(self, magnet_device, inst):
        magnet_to_function_map = {"Active ZF": inst.f0, "Danfysik": inst.lf0, "T20 Coils": inst.tf0}
        if g.cget("a_selected_magnet")["value"] != magnet_device:
            magnet_to_function_map[magnet_device]()

    def check_set_definition(self, start_temp_or_field, stop_temp_or_field):
        if start_temp_or_field is None or stop_temp_or_field is None:
            return SetDefinition.UNDEFINED
        elif start_temp_or_field == stop_temp_or_field:
            return SetDefinition.POINT
        else:
            return SetDefinition.SCAN

    def run_temp_and_field_scans(self, start_temperature, stop_temperature, step_temperature,
                                 start_field, stop_field, step_field, mevents, inst):
        for temp in inclusive_float_range_with_step_flip(start_temperature, stop_temperature, step_temperature):
            inst.settemp(temp, wait=True)
            for field in inclusive_float_range_with_step_flip(start_field, stop_field, step_field):
                inst.setmag(field, wait=True)
                # Do a run for this mag and temp
                self.begin_waitfor_mevents_end(mevents)

    def run_scans(self, start_temperature, stop_temperature, step_temperature, mevents, set_parameter_func):
        for temp in inclusive_float_range_with_step_flip(start_temperature, stop_temperature, step_temperature):
            set_parameter_func(temp, wait=True)
            self.begin_waitfor_mevents_end(mevents)

    # Check to see if the provided parameters are valid
    @cast_parameters_to(
         start_temperature=float_or_keep, stop_temperature=float_or_keep, step_temperature=float,
         start_field=float_or_keep, stop_field=float_or_keep, step_field=float, 
         custom=cast_custom_expression, mevents=int, magnet_device=magnet_device_type)
    def parameters_valid(self,
                         start_temperature=1.0, stop_temperature=1.0, step_temperature=1.0,
                         start_field=1.0, stop_field=1.0, step_field=1.0,
                         custom="None",  mevents=10, magnet_device="N/A"):
        # The reason as to why the parameters are not valid
        reason = ""
        if (start_temperature is None and stop_temperature is not None) or (stop_temperature is None and start_temperature is not None):
            reason += "If start temperature or stop_temperature is keep, the other must also be keep"
        is_temp_scan_defined = start_temperature is not None and stop_temperature is not None
        if is_temp_scan_defined:
            # We need to step thorugh at some rate
            if start_temperature != stop_temperature and step_temperature <= 0.0:
                reason += "Cannot step through temperatures when step is zero\n"
        if (start_field is None and stop_field is not None) or (stop_field is None and start_field is not None):
            reason += "If start field or stop field is keep, the other must also be keep"
        is_field_scan_defined = start_field is not None and stop_field is not None
        if is_field_scan_defined:
            # If we are defining a field scan we need to set the magnet
            if magnet_device not in magnet_devices.values():
                reason += "Field set but magnet devices {} not in possible devices {}\n".format(magnet_device, list(magnet_devices.keys()))
            if start_field != stop_field and step_field <= 0.0:
                reason += "Cannot step through fields when step is zero\n"
            # Only the zero field can set a field of zero
            if (np.isclose(start_field, 0.0) or np.isclose(stop_field, 0.0)) and magnet_device != self.active_zf:
                reason += "Trying to set a zero field without using the active zero field ({}, {})\n".format(magnet_device, self.active_zf)
            if not (np.isclose(start_field, 0.0) or not np.isclose(stop_field, 0.0)) and magnet_device == self.active_zf:
                reason += "When setting a zero field must use ZF"
        # If there is no reason return None i.e. the parameters are valid
        if reason != "":
            return reason
        else:
            return None
