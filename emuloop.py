from genie_python.genie_script_generator import ActionDefinition, cast_parameters_to
from genie_python import genie as g
from importlib import import_module
import numpy as np

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
    if magnet_device.upper() in magnet_devices.keys():
        return magnet_devices[magnet_device]
    elif magnet_device.upper() == "N/A":
        return magnet_device
    raise ValueError

# Cast the custom python expression to a string or None if empty
def cast_custom_expression(expression):
    if expression == "":
        return "None"
    else:
        return expression

class DoRun(ActionDefinition):

    active_zf = "Active ZF"
    possible_magnet_devices = [active_zf, "Danfysik", "T20 Coils"]


    # Loop through a set of temperatures or fields using a start, stop and step mechanism
    @cast_parameters_to(
         start_temperature=float_or_keep, stop_temperature=float_or_keep, step_temperature=float,
         start_field=float_or_keep, stop_field=float_or_keep, step_field=float, 
         custom=cast_custom_expression, 
         mevents=int, 
         magnet_device=magnet_device_type)
    def run(self, 
         start_temperature=1.0, stop_temperature=1.0, step_temperature=10, 
         start_field=1.0, stop_field=1.0, step_field=1.0,
         custom="None", 
         mevents=10, 
         magnet_device="N/A"):
        # We can only scan through temp and field if all of start, stop and step are defined correctly
        is_temp_scan_defined = start_temperature is not None and stop_temperature is not None
        if is_temp_scan_defined:
            if start_temperature == stop_temperature:
                step_temperature = 1 # Execute the step from x to x once 
            elif start_temperature > stop_temperature:
                step_temperature = -step_temperature # We need to be stepping backwards
                stop_temperature -= 0.00001 # Python range is not inclusive
            else:
                stop_temperature += 0.00001 # Python range is not inclusive
        is_field_scan_defined = start_field is not None and stop_field is not None
        if is_field_scan_defined:
            if start_field == stop_field:
                step_field = 1 # Execute the step from x to x once 
            elif start_field > stop_field:
                step_field = -step_field # We need to be stepping backwards
                stop_field -= 0.00001 # Python range is not inclusive
            else:
                stop_field += 0.00001 # Python range is not inclusive
        # Use the instrument scripts to set the magnet correctly
        inst = import_module("inst")
        magnet_to_function_map = {"Active ZF": inst.f0, "Danfysik": inst.lf0, "T20 Coils": inst.tf0}
        if g.cget("a_selected_magnet")["value"] != magnet_device:
                magnet_to_function_map[magnet_device]()
        # Do scans
        if is_temp_scan_defined and is_field_scan_defined:
            # Evaluate the user command before scanning
            eval(custom)
            # When we are scanning both temperature and field do all combinations
            for temp in np.arange(start_temperature, stop_temperature, step_temperature):
                for field in np.arange(start_field, stop_field, step_field):
                    inst.setmag(field, wait=True)
                    inst.settemp(temp, wait=True)
                    # Do a run for this mag and temp
                    g.begin(quiet=True)
                    g.waitfor_mevents(mevents)
                    g.end(quiet=True)
        elif is_temp_scan_defined:
            # Evaluate the user command before scanning
            eval(custom)
            # Scan through temps
            for temp in np.arange(start_temperature, stop_temperature, step_temperature):
                inst.settemp(temp, wait=True)
                # Do a run for this temp
                g.begin(quiet=True)
                g.waitfor_mevents(mevents)
                g.end(quiet=True)
        elif is_field_scan_defined:
            # Evaluate the user command before scanning
            eval(custom)
            # Scan through fields
            for field in np.arange(start_field, stop_field, step_field):
                inst.setmag(field, wait=True)
                # Do a run for this temp
                g.begin(quiet=True)
                g.waitfor_mevents(mevents)
                g.end(quiet=True)
        else:
            g.begin(quiet=True)
            g.waitfor_mevents(mevents)
            g.end(quiet=True)


    # Check to see if the provided parameters are valid
    @cast_parameters_to(
         start_temperature=float_or_keep, stop_temperature=float_or_keep, step_temperature=float,
         start_field=float_or_keep, stop_field=float_or_keep, step_field=float, 
         custom=cast_custom_expression, 
         mevents=int, 
         magnet_device=magnet_device_type)
    def parameters_valid(self,
         start_temperature=1.0, stop_temperature=1.0, step_temperature=1.0,
         start_field=1.0, stop_field=1.0, step_field=1.0,
         custom="None", 
         mevents=10, 
         magnet_device="N/A"):
        # The reason as to why the parameters are not valid
        reason = ""
        is_temp_scan_defined = start_temperature is not None and stop_temperature is not None
        is_field_scan_defined = start_field is not None and stop_field is not None
        if is_temp_scan_defined:
            # Cannot go below zero kelvin
            if start_temperature < 0.0 and stop_temperature < 0.0:
                reason += "Temperature too low\n"
            # We need to step thorugh at some rate
            if start_temperature != stop_temperature and step_temperature == 0.0:
                reason += "Cannot step through temperatures when step is zero\n"
            if start_temperature == stop_temperature and step_temperature != 0.0:
                reason += "You will be setting the temperature to {} {} times\n".format(start_temperature, step_temperature)
        if is_field_scan_defined:
             # If we are defining a field scan we need to set the magnet
            if magnet_device not in magnet_devices.values():
                reason += "Field set but magnet devices {} not in possible devices {}\n".format(magnet_device, list(magnet_devices.keys()))
            if start_field != stop_field and step_field == 0.0:
                reason += "Cannot step through fields when step is zero\n"
            if start_field == stop_field and step_field != 0.0:
                reason += "You will be setting the field to {} {} times\n".format(start_field, step_field)
            # Only the zero field can set a field of zero
            if (np.isclose(start_field, 0.0) or np.isclose(stop_field, 0.0)) and magnet_device != self.active_zf:
                reason += "Trying to set a zero field without using the active zero field ({}, {})\n".format(magnet_device, self.active_zf)
        # If there is no reason return None i.e. the parameters are valid
        if reason != "":
            return reason
        else:
            return None
