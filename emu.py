from genie_python.genie_script_generator import ActionDefinition, cast_parameters_to
from genie_python import genie as g
from importlib import import_module

# Allow a user to input keep and we will know not to update the value as we cast to None
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

class DoRun(ActionDefinition):

    def get_help(self):
        return """
Magnet device must be one of {} or if the field is KEEP then it can be N/A.\n
If the field is zero magnet device must be ZF.\n
        """.format(list(magnet_devices.keys()))

    @cast_parameters_to(temperature=float_or_keep, field=float_or_keep, mevents=int, magnet_device=magnet_device_type)
    def run(self, temperature=1.0, field=1.0, mevents=10, magnet_device="N/A"):
        inst = import_module("inst")
        # Don't set temp if the user has specified keep
        if temperature is not None:
            inst.settemp(temperature, wait=True)
        # Don't set field if the user has specified keep
        if field is not None:
            # Select a magnet to set the field with
            if g.cget("a_selected_magnet")["value"] != magnet_device:
                magnet_to_function_map = {"Active ZF": inst.f0, "Danfysik": inst.lf0, "T20 Coils": inst.tf0}
                magnet_to_function_map[magnet_device]()
            inst.setmag(field, wait=True)
        # Do the run for this action
        g.begin(quiet=True)
        g.waitfor_mevents(mevents)
        g.end(quiet=True)

    @cast_parameters_to(temperature=float_or_keep, field=float_or_keep, mevents=int, magnet_device=magnet_device_type)
    def parameters_valid(self, temperature=1.0, field=1.0, mevents=10, magnet_device="N/A"):
        reason = ""
        if temperature is not None:
            if temperature < 0.0:
                reason += "Temperature too low"
        # We need a suitable device to set the field with
        if field is not None and magnet_device not in magnet_devices.values():
            reason += "Field set but magnet devices {} not in possible devices {}".format(magnet_device, list(magnet_devices.keys()))
        if field == 0 and magnet_device != magnet_devices["ZF"]:
            reason += "When setting a zero field must use ZF"
        if field != 0 and magnet_device == magnet_devices["ZF"]:
            reason += "Cannot have a non-zero field when selecting ZF"
        # If there are no reasons with the action isn't valid then return None (saying that it is)
        if reason != "":
            return reason
        else:
            return None
