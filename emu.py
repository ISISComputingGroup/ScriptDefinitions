from genie_python.genie_script_generator import ActionDefinition, cast_parameters_to
from genie_python import genie as g
import inst

def cast_temp_or_field(temp_or_field):
    if temp_or_field.lower() == "keep" or temp_or_field == "":
        return None
    else:
        return float(temp_or_field)

def cast_magnet_device(magnet_device):
    magnet_cast = {"ZF": "Active ZF", "LF": "Danfysik", "TF": "T20 Coils"}
    return magnet_cast[magnet_device]

class DoRun(ActionDefinition):

    possible_magnet_devices = ["ZF", "TF", "LF"]

    magnet_to_function_map = {"Active ZF": inst.f0, "Danfysik": inst.lf0, "T20 Coils": inst.tf0}

    @cast_parameters_to(temperature=cast_temp_or_field, field=cast_temp_or_field, mevents=int, magnet_device=cast_magnet_device)
    def run(self, temperature=1.0, field=1.0, mevents=10, magnet_device="N/A"):
        if temperature is not None:
            inst.set_temp(temperature, wait=True)
        if field is not None:
            if g.cget("a_selected_magnet")["value"] != magnet_device:
                self.magnet_to_function_map[magnet_device]()
            inst.set_mag(field, wait=True)
        g.begin(quiet=True)
        g.waitfor_mevents(mevents)
        g.end(quiet=True)

    @cast_parameters_to(temperature=cast_temp_or_field, field=cast_temp_or_field, mevents=int, magnet_device=cast_magnet_device)
    def parameters_valid(self, temperature=1.0, field=1.0, mevents=10, magnet_device="N/A"):
        reason = ""
        if temperature is not None:
            if temperature < 0.0:
                reason += "Temperature too low"
        if magnet_device not in self.possible_magnet_devices:
            reason += "Magnet devices {} not in possible devices {}".format(magnet_device, self.possible_magnet_devices)
        if reason != "":
            return reason
        else:
            return None
