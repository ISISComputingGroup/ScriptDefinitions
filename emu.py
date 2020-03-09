from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to
from genie_python import genie as g
import numpy as np


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
    raise ValueError("Magnet device must be one of {} or N/A".format(magnet_devices))


class DoRun(ScriptDefinition):

    def get_help(self):
        return """
Magnet device must be one of {} or if the field is KEEP then it can be N/A.\n
If the field is zero magnet device must be ZF.\n
        """.format(list(magnet_devices.keys()))

    @cast_parameters_to(temperature=float_or_keep, field=float_or_keep, mevents=float, magnet_device=magnet_device_type)
    def run(self, temperature=1.0, field=1.0, mevents=10, magnet_device="N/A"):
        import inst
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
        self.begin_waitfor_mevents_end(mevents)

    def begin_waitfor_mevents_end(self, mevents):
        """
        Begin a run, wait for mevents millions of events and end run.

        Parameters:
          mevents (float): The millions of events to wait for in the run.
        """
        g.begin(quiet=True)
        g.waitfor_mevents(mevents)
        g.end(quiet=True)

    @cast_parameters_to(temperature=float_or_keep, field=float_or_keep, mevents=float, magnet_device=magnet_device_type)
    def parameters_valid(self, temperature=1.0, field=1.0, mevents=10, magnet_device="N/A"):
        reason = ""
        # We need a suitable device to set the field with
        if field is not None and magnet_device not in magnet_devices.values():
            reason += "Field set but magnet devices {} not in possible devices {}\n".format(
                magnet_device, list(magnet_devices.keys()))
        if np.isclose(field, 0) and magnet_device != magnet_devices["ZF"]:
            reason += "When setting a zero field must use ZF\n"
        if not np.isclose(field, 0) and magnet_device == magnet_devices["ZF"]:
            reason += "Cannot have a non-zero field when selecting ZF\n"
        # If there are no reasons with the action isn't valid then return None (saying that it is)
        if reason != "":
            return reason
        else:
            return None
