from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to
from genie_python import genie as g
import numpy as np
from enum import Enum
from collections import OrderedDict


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
magnet_not_applicable = "N/A"


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
    elif magnet_device == magnet_not_applicable:
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
#    stop = stop + step **** This original code can cause the scan to extend beyond the given range
    vstop = stop + step     # note 'arange' doesn't include last point
# number of decimal places determined by required user entry
    dec_places = max([len(str(start).split(".")[1]), len(str(stop).split(".")[1]), len(str(step).split(".")[1])])
    for i in np.arange(start, vstop, step):
        p = round(i,dec_places)
        if ((p >= start) and (p <= stop)) or ((p >= stop) and (p <= start)):    # Check inserted here to ensure scan remains within defined range
            yield p
#    for i in np.arange(start, vstop, step):
#        print(i)
#        if ((i >= start) and (i <= stop)) or ((i >= stop) and (i <= start)):    # Check inserted here to ensure scan remains within defined range
#            yield i

def log_range(start, stop, n):
    """
    Do n fields between start and stop, logarithmically spaced.

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

# number of decimal places determined by required user entry
    dec_places = max([len(str(start).split(".")[1]), len(str(stop).split(".")[1])])
    for i in range(0, n):
        this_field = start + (stop-start) ** (i/(n*1.))
        p = round(this_field, dec_places)
        if ((p >= start) and (p <= stop)):    # Check inserted here to ensure scan remains within defined range
            yield p
#    for i in np.arange(start, vstop, step):
#        print(i)
#        if ((i >= start) and (i <= stop)) or ((i >= stop) and (i <= start)):    # Check inserted here to ensure scan remains within defined range
#            yield i


class DoRun(ScriptDefinition):

    active_zf = "Active ZF"
    possible_magnet_devices = [active_zf, "Danfysik", "T20 Coils"]
    
    global_params_definition = OrderedDict({"Rate (Mev/hr)": ("110", int)})
    

    def get_help(self):
        return """
This script logarithmically steps the field between start_field and stop_field.
Magnet device must be one of {} or if the field is KEEP then it can be N/A.\n
If the field is zero, active ZF will be engaged automatically.

        """.format(list(magnet_devices.keys()))

    @cast_parameters_to(
         start_temperature=float_or_keep, stop_temperature=float_or_keep, step_temperature=float,
         start_field=float_or_keep, stop_field=float_or_keep, n_fields=int, 
         custom=cast_custom_expression, mevents=float, magnet_device=magnet_device_type)	
    def estimate_time(self,
            start_temperature="keep", stop_temperature="keep", step_temperature=0,
            start_field="keep", stop_field="keep", n_fields=1,
            custom="None", mevents=10, magnet_device="N/A"):
        # Scan if start and stop are different, set once if they are equal or do not set if they are None
        temp_set_definition = self.check_set_definition(start_temperature, stop_temperature)
        field_set_definition = self.check_set_definition(start_field, stop_field)
        if (temp_set_definition == SetDefinition.SCAN):
            temp_pts = 0
            for i in inclusive_float_range_with_step_flip(start_temperature, stop_temperature, step_temperature):
                temp_pts += 1
        else:
            temp_pts = 1
        if (field_set_definition == SetDefinition.SCAN):
            field_pts = n_fields
        else:
            field_pts = 1
        return (float(mevents) * float(temp_pts) * float(field_pts)) / (float(self.global_params["Rate (Mev/hr)"]) / 3600.0)


    # Loop through a set of temperatures or fields using a start, stop and step mechanism0
    @cast_parameters_to(
         start_temperature=float_or_keep, stop_temperature=float_or_keep, step_temperature=float,
         start_field=float_or_keep, stop_field=float_or_keep, n_fields=int, 
         custom=cast_custom_expression, mevents=float, magnet_device=magnet_device_type)
    def run(self,
            start_temperature="keep", stop_temperature="keep", step_temperature=0,
            start_field="keep", stop_field="keep", n_fields=1,
            custom="None", mevents=10, magnet_device="N/A"):
        # Scan if start and stop are different, set once if they are equal or do not set if they are None
        temp_set_definition = self.check_set_definition(start_temperature, stop_temperature)
        field_set_definition = self.check_set_definition(start_field, stop_field)
        # Use the instrument scripts to set the magnet device correctly
        import inst
        if field_set_definition != SetDefinition.UNDEFINED:
            if start_field < 1e-3:
                magnet_device = self.active_zf
            self.set_magnet_device(magnet_device, inst)
        # Execute a custom command - changed from 'eval' to 'exec' by spc 2/1/24
        exec(custom)
        # If we are not scanning the temp/field but still setting once, set them
        if temp_set_definition == SetDefinition.POINT:
            inst.settemp(start_temperature, wait=True)
        if field_set_definition == SetDefinition.POINT:
            if start_field < 1e-3:
                magnet_device = self.active_zf
                inst.f0()
            else:
                inst.setmag(start_field, wait=True)
        # If we are running scans do them
        if temp_set_definition == SetDefinition.SCAN and field_set_definition == SetDefinition.SCAN:
            # When we are running scans for both temperature and field do all combinations
            self.run_temp_and_field_scans(start_temperature, stop_temperature, step_temperature,
                                          start_field, stop_field, n_fields, mevents, inst, magnet_device)
        elif temp_set_definition == SetDefinition.SCAN:  # Run scans for the temperature
            self.run_scans(start_temperature, stop_temperature, step_temperature, mevents, inst.settemp)
        elif field_set_definition == SetDefinition.SCAN:  # Run scans for the field
            self.run_field_scan(start_field, stop_field, n_fields, mevents, inst.setmag, magnet_device)
        else:
            # If we are not doing any scans do a run with temp and field as they are
            self.check_mevents_and_begin_waitfor_mevents_end(mevents)

    def check_mevents_and_begin_waitfor_mevents_end(self, mevents):
        """
        If mevents are more than zero do a run and wait for the mevents in that run.

        Parameters:
          mevents (float): The millions of events to wait for.
        """
        if mevents > 0:
            g.begin(quiet=True)
            g.waitfor_mevents(mevents)
            g.end(quiet=True)

    def set_magnet_device(self, magnet_device, inst):
        """
        Use the instrument scripts to set the magnet device, given a string.

        Parameters:
          magnet_device (str): The string representation of the magnet device to select.
          inst (module): The instrument scripts module to set the magnet device with.
        """
        magnet_to_function_map = {"Active ZF": inst.f0, "Danfysik": inst.lf0, "T20 Coils": inst.tf0}
        if g.cget("a_selected_magnet")["value"] != magnet_device:
            magnet_to_function_map[magnet_device]()

    def check_set_definition(self, start_temp_or_field, stop_temp_or_field):
        """
        Check if we are running a scan, doing one set (a point) or not setting at all.

        Parameters:
          start_temp_or_field (float): The value to start a scan with or set once
          stop_temp_or_field (float): The value to end a scan with

        Returns:
          SetDefinition:
           UNDEFINED is either start or stop is None.
           POINT if start and stop are equal.
           SCAN if they are not equal.
        """
        if start_temp_or_field is None or stop_temp_or_field is None:
            return SetDefinition.UNDEFINED
        elif start_temp_or_field == stop_temp_or_field:
            return SetDefinition.POINT
        else:
            return SetDefinition.SCAN

    def run_temp_and_field_scans(self, start_temperature, stop_temperature, step_temperature,
                                 start_field, stop_field, n_fields, mevents, inst):
        """
        Run scans for both the temperature and field.

        Parameters:
          start_temperature (float): The temperature to start the temperature scan with.
          stop_temperature (float): The temperature to end the temperature scan with (inclusive).
          step_temperature (float): The size of the steps to take to go from start_temperature to stop_temperature.
          start_field (float): The field to start the field scan with.
          stop_field (float): The field to end the field scan with (inclusive).
          n_fields (int): Number of steps to take between start and stop field
          mevents (float): The amount of millions of events to wait for in each run.
          inst (module): The instrument scripts module to set the temperature and field with.
        """
        for temp in inclusive_float_range_with_step_flip(start_temperature, stop_temperature, step_temperature):
            inst.settemp(temp, wait=True)
            self.run_field_scan(start_field, stop_field, n_fields, mevents, inst.setmag)

    def run_temp_scan(self, start, stop, step, mevents, set_parameter_func):
        """
        Run a scan for the given set_parameter_func

        Parameters:
          start (float): The value to start the scan with.
          stop (float): The value to end the scan with.
          step (float): The size of the steps to take from start to stop.
          mevents (float): The amount of millions of events to wait for in each run.
          set_parameter_func (function): A function to call to set the value with each step of the scan.
        """
        for var in inclusive_float_range_with_step_flip(start, stop, step):
            set_parameter_func(var, wait=True)
            self.check_mevents_and_begin_waitfor_mevents_end(mevents)

    def run_field_scan(self, start, stop, n, mevents, set_parameter_func, magnet_device):
        """
        Run a log scan for the fields

        Parameters:
          start (float): The value to start the scan with.
          stop (float): The value to end the scan with.
          n (integer): Number of fields to scan
          mevents (float): The amount of millions of events to wait for in each run.
          set_parameter_func (function): A function to call to set the value with each step of the scan.
        """
        for var in log_range(start, stop, n):
            if var < 1e-3:
                # engage ZF automatically if a field < 1mG requested
                print('ZF enganged')
                self.set_magnet_device(self.active_zf)
            else:
                set_parameter_func(var, wait=True)
            self.check_mevents_and_begin_waitfor_mevents_end(mevents)
            if var < 1e-3:
                # put the field back on if in ZF mode
                self.set_magnet_device(magnet_device)
            


    # Check to see if the provided parameters are valid
    @cast_parameters_to(
         start_temperature=float_or_keep, stop_temperature=float_or_keep, step_temperature=float,
         start_field=float_or_keep, stop_field=float_or_keep, n_fields=int, 
         custom=cast_custom_expression, mevents=float, magnet_device=magnet_device_type)
    def parameters_valid(self,
                         start_temperature=1.0, stop_temperature=1.0, step_temperature=1.0,
                         start_field=1.0, stop_field=1.0, n_fields=1,
                         custom="None",  mevents=10, magnet_device="N/A"):
        # The reason as to why the parameters are not valid
        reason = ""
        reason += self.check_start_and_stop_valid(start_temperature, stop_temperature, "temperature")
        reason += self.check_start_and_stop_valid(start_field, stop_field, "field")
        reason += self.check_step_set_correctly(start_temperature, stop_temperature, step_temperature, "temperature")
        reason += self.check_step_set_correctly(start_field, stop_field, n_fields, "field")
        reason += self.check_magnet_selected_correctly(start_field, stop_field, magnet_device)
        reason += self.check_if_start_or_stop_field_are_keep_then_magnet_is_na(start_field, stop_field, magnet_device)
        # If there is no reason return None i.e. the parameters are valid
        if reason != "":
            return reason
        else:
            return None

    def check_start_and_stop_valid(self, start, stop, variable_name):
        """
        Check that start and stop are either both None or both values.

        Parameters:
          start (float): The start value of a scan.
          stop (float): The end value of a scan.
          variable_name (str): The name of the variable we are checking (e.g. temperature or field).

        Returns:
          str: An empty string if start and stop are valid, or a string containing a reason why they are not.
        """
        if (start is None and stop is not None) or (stop is None and start is not None):
            return "If start {0} or stop {0} is keep, the other must also be keep\n".format(variable_name)
        else:
            return ""
    
    def check_if_start_or_stop_field_are_keep_then_magnet_is_na(self, start_field, stop_field, magnet):
      """
      Check that if the start or stop fields are keep then the magnet is set to N/A

      Parameters:
          start_field (float): The start value of a scan.
          stop_field (float): The end value of a scan.
          magnet (str): The magnet device selected.

        Returns:
          str: A string to raise awareness of invalidity if start or stop are "keep" and the magnet is not N/A, 
           or an empty string to show they are valid. 
      """
      if (start_field is None or stop_field is None) and magnet != magnet_not_applicable:
        return "If start_field or stop_field is keep, then the selected magnet must be N/A".format()
      else:
        return ""

    def check_step_set_correctly(self, start, stop, step, variable_name):
        """
        If we are scanning check that the step is positive and not zero.

        Parameters:
          start (float): The start value of a scan.
          stop (float): The end value of a scan.
          step (float): The size of the steps to take from start to stop.
          variable_name (str): The name of the variable we are checking (e.g. temperature or field).

        Returns:
          str: An empty string if valid, or a string containing a reason why they are not.
        """
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
        """
        If we are setting a field check:
         - The magnet device that has been selected is a valid one i.e. one of our listed magnet devices
         - If the field is zero we are using the active zero field device
         - If the field is not zero we are not using the the active zero field device

        Parameters:
          start_field (float): The start value of a field scan.
          stop_field (float): The start value of a field scan.
          magnet_device (str): The device we are selecting to use to set the field.

        Returns:
          str: An empty string if valid, or a string containing a reason why they are not.
        """
        reason = ""
        field_set_definition = self.check_set_definition(start_field, stop_field)
        if field_set_definition != SetDefinition.UNDEFINED:
            # If we are setting a field we need to set the magnet device to use
            if magnet_device not in magnet_devices.values():
                reason += "Field set but magnet devices {} not in possible devices {}\n".format(
                    magnet_device, list(magnet_devices.keys()))
            if (not np.isclose(start_field, 0.0) or not np.isclose(stop_field,
                                                                   0.0)) and magnet_device == self.active_zf:
                reason += "Cannot set a non-zero field with the active zero field\n"
        return reason
