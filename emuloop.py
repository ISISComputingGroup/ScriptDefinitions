from genie_python.genie_script_generator import ActionDefinition, cast_parameters_to
from genie_python import genie as g
from importlib import import_module
import numpy as np

# Allow the user to right keep in temp or field to use the current value
def cast_temp_or_field(temp_or_field):
    if temp_or_field.lower() == "keep":
        return None
    else:
        return float(temp_or_field)

# Cast the shortened magnet device name to the correct name
def cast_magnet_device(magnet_device):
    magnet_cast = {"ZF": "Active ZF", "LF": "Danfysik", "TF": "T20 Coils", "N/A": "N/A"}
    return magnet_cast[magnet_device]

# Cast the custom python expression to a string or None if empty
def cast_custom_expression(expression):
    if expression == "":
        return "None"
    else:
        return expression

class DoRun(ActionDefinition):

    possible_magnet_devices = ["Active ZF", "Danfysik", "T20 Coils"]


    # Loop through a set of temperatures or fields using a start, stop and step mechanism
    @cast_parameters_to(
         start_temperature=cast_temp_or_field, stop_temperature=cast_temp_or_field, step_temperature=float,
         start_field=cast_temp_or_field, stop_field=cast_temp_or_field, step_field=float, 
         custom=cast_custom_expression, 
         mevents=int, 
         magnet_device=cast_magnet_device)
    def run(self, 
         start_temperature=1.0, stop_temperature=1.0, step_temperature=10, 
         start_field=1.0, stop_field=1.0, step_field=1.0,
         custom="None", 
         mevents=10, 
         magnet_device="N/A"):
        # We can only scan through temp and field if all of start, stop and step are defined correctly
        is_temp_scan_defined = start_temperature is not None and stop_temperature is not None and step_temperature != 0.0
        is_field_scan_defined = start_field is not None and stop_field is not None and step_field != 0.0
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
            for temp in np.linspace(start_temperature, stop_temperature+0.0001, step_temperature):
                for field in np.linspace(start_field, stop_field+0.0001, step_field):
                    inst.set_mag(field, wait=True)
                    inst.set_temp(temp, wait=True)
                    # Do a run for this mag and temp
                    g.begin(quiet=True)
                    g.waitfor_mevents(mevents)
                    g.end(quiet=True)
        elif is_temp_scan_defined:
            # Evaluate the user command before scanning
            eval(custom)
            # Scan through temps
            for temp in np.linspace(start_temperature, stop_temperature+0.0001, step_temperature):
                inst.set_temp(temp, wait=True)
                # Do a run for this temp
                g.begin(quiet=True)
                g.waitfor_mevents(mevents)
                g.end(quiet=True)
        elif is_field_scan_defined:
            # Evaluate the user command before scanning
            eval(custom)
            # Scan through fields
            for field in np.linspace(start_field, stop_field+0.0001, step_field):
                inst.set_mag(field, wait=True)
                # Do a run for this temp
                g.begin(quiet=True)
                g.waitfor_mevents(mevents)
                g.end(quiet=True)


    # Check to see if the provided parameters are valid
    @cast_parameters_to(
         start_temperature=cast_temp_or_field, stop_temperature=cast_temp_or_field, step_temperature=float,
         start_field=cast_temp_or_field, stop_field=cast_temp_or_field, step_field=float, 
         custom=cast_custom_expression, 
         mevents=int, 
         magnet_device=cast_magnet_device)
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
        # Must define one of the scans otherwise we are doing nothing
        if not is_field_scan_defined and not is_temp_scan_defined:
            reason += "Neither temp nor field scans have been defined\n"
        if is_temp_scan_defined:
            # Cannot go below zero kelvin
            if start_temperature < 0.0 and stop_temperature < 0.0:
                reason += "Temperature too low\n"
            # We need to step thorugh at some rate
            if step_temperature == 0.0:
                reason += "Cannot step through temperatures when step is zero\n"
        # Limit the amount of devices they can input
        if magnet_device not in self.possible_magnet_devices:
            reason += "Magnet devices {} not in possible devices {}\n".format(magnet_device, self.possible_magnet_devices)
        # If we are defining a field scan we need to set the magnet
        if is_field_scan_defined and magnet_device in self.possible_magnet_devices and magnet_device == "N/A":
            reason += "No magnet device set but field is being set\n"
        # If there is no reason return None i.e. the parameters are valid
        if reason != "":
            return reason
        else:
            return None