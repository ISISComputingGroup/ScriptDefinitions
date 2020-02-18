from genie_python.genie_script_generator import ActionDefinition, cast_parameters_to
from genie_python import genie as g
import numpy as np
from enum import Enum


class SetDefinition(Enum):
    """
    Describes how we are setting a temperature or field.
    POINT means set once.
    SCAN means set a number of values by scanning through a set of values.
    UNDEFINED means not to set the temperature or field.
    """
    UNDEFINED = 1
    POINT = 2
    SCAN = 3


def float_or_keep(temp_or_field):
    """
    Convert the input to a float or None if the input is keep (to allow not changing of a temperature or field).

    Parameters:
      temp_or_field (str): The temperature or field to cast

    Returns:
      float: The casted input. Will be None if temp_or_field  is 'keep'.

    Raises:
      ValueError: When temp_or_field is not either a valid float or the string 'keep'.
    """
    if temp_or_field.lower() == "keep":
        return None
    else:
        return float(temp_or_field)


# The magnet devices shortened and longer forms
magnet_devices = {"ZF": "Active ZF", "LF": "Danfysik", "TF": "T20 Coils"}


def magnet_device_type(magnet_device):
    """
    Take the shortened magnet selection input e.g. ZF, LF or TF and cast it to the
     required string i.e. Active ZF, Danfysik, T20 Coils.
    Allows N/A to be selected for when we aren't setting a magnet point or scan.

    Parameters:
      magnet_device (str): The  selected magnet to cast

    Returns:
      str: The magnet string to select

    Raises:
      ValueError: If the input is not ZF, LF, TF or N/A. Allows the conversion error to be
       caught and displayed to the user.
    """
    magnet_device = magnet_device.upper()
    if magnet_device in magnet_devices.keys():
        return magnet_devices[magnet_device]
    elif magnet_device == "N/A":
        return magnet_device
    raise ValueError("Magnet device must be one of {} or N/A".format(list(magnet_devices.keys())))


def cast_custom_expression(expression):
    """
    Ensure a custom python expression is not empty (this will cause an error) by filling it with None (does nothing).

    Parameters:
      expression (str): The expression to cast

    Returns:
      str: The python expression to run (the same as the expression param unless that is the empty string
    """
    if expression.lstrip() == "":
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
        # Execute a custom command
        eval(custom)
        # If we are only setting once set it
        if temp_set_definition == SetDefinition.POINT:
            inst.settemp(start_field, wait=True)
        if field_set_definition == SetDefinition.POINT:
            inst.setmag(start_field, wait=True)
        # Run scans for both the temperature and the field
        if temp_set_definition == SetDefinition.SCAN and field_set_definition == SetDefinition.SCAN:
            # When we are scanning both temperature and field do all combinations
            self.run_temp_and_field_scans(start_temperature, stop_temperature, step_temperature,
                                          start_field, stop_field, step_field, mevents, inst)
        elif temp_set_definition == SetDefinition.SCAN:  # Run scans for the temperature
            self.run_scans(start_temperature, stop_temperature, step_temperature, mevents, inst.settemp)
        elif field_set_definition == SetDefinition.SCAN:  # Run scans for the field
            self.run_scans(start_field, stop_field, step_field, mevents, inst.setmag)
        else:
            # If we are not doing any scans do a run with temp and field as they are
            self.check_mevents_and_begin_waitfor_mevents_end(mevents)

    def check_mevents_and_begin_waitfor_mevents_end(self, mevents):
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
            self.run_scans(start_field, stop_field, step_field, mevents, inst.setmag)

    def run_scans(self, start, stop, step, mevents, set_parameter_func):
        for var in inclusive_float_range_with_step_flip(start, stop, step):
            set_parameter_func(var, wait=True)
            self.check_mevents_and_begin_waitfor_mevents_end(mevents)

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
        reason += self.check_keep_in_neither_or_both(start_temperature, stop_temperature, "temperature")
        reason += self.check_keep_in_neither_or_both(start_field, stop_field, "field")
        reason += self.check_step_set_correctly(start_temperature, stop_temperature, step_temperature, "temperature")
        reason += self.check_step_set_correctly(start_field, stop_field, step_field, "field")
        reason += self.check_magnet_selected_correctly(start_field, stop_field, magnet_device)
        # If there is no reason return None i.e. the parameters are valid
        if reason != "":
            return reason
        else:
            return None

    def check_keep_in_neither_or_both(self, start, stop, variable_name):
        if (start is None and stop is not None) or (stop is None and start is not None):
            return "If start {0} or stop {0} is keep, the other must also be keep\n".format(variable_name)
        else:
            return ""

    def check_step_set_correctly(self, start, stop, step, variable_name):
        reason = ""
        set_definition = self.check_set_definition(start, stop)
        if set_definition == SetDefinition.SCAN:
            # We need to step through at some rate
            if step == 0.0:
                reason += "Cannot step through {}s when step is zero\n".format(variable_name)
            elif step < 0.0:
                reason += "Step {} must be positive\n".format(variable_name)
        return reason

    def check_magnet_selected_correctly(self, start_field, stop_field, magnet_device):
        reason = ""
        field_set_definition = self.check_set_definition(start_field, stop_field)
        if field_set_definition != SetDefinition.UNDEFINED:
            # If we are setting a field we need to set the magnet device to use
            if magnet_device not in magnet_devices.values():
                reason += "Field set but magnet devices {} not in possible devices {}\n".format(
                    magnet_device, list(magnet_devices.keys()))
            # Only the zero field can set a field of zero
            if (np.isclose(start_field, 0.0) or np.isclose(stop_field, 0.0)) and magnet_device != self.active_zf:
                reason += "Trying to set a zero field without using the active zero field ({}, {})\n".format(
                    magnet_device, self.active_zf)
            if (not np.isclose(start_field, 0.0) or not np.isclose(stop_field,
                                                                   0.0)) and magnet_device == self.active_zf:
                reason += "Cannot set a non-zero field with the active zero field\n"
        return reason
