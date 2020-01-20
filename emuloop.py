from genie_python.genie_script_generator import ActionDefinition, cast_parameters_to
from genie_python import genie as g
import inst

def cast_temp_or_field(temp_or_field):
    if temp_or_field.lower() == "keep" or temp_or_field == "":
        return None
    else:
        return float(temp_or_field)

def cast_magnet_device(magnet_device):
    magnet_cast = {"ZF": "Active ZF", "LF": "Danfysik", "TF": "T20 Coils", "N/A": "N/A"}
    return magnet_cast[magnet_device]

class DoRun(ActionDefinition):

    possible_magnet_devices = ["Active ZF", "Danfysik", "T20 Coils"]

    magnet_to_function_map = {"Active ZF": inst.f0, "Danfysik": inst.lf0, "T20 Coils": inst.tf0}

    @cast_parameters_to(start_temperature=cast_temp_or_field, stop_temperature=cast_temp_or_field, step_temperature=cast_temp_or_field,
         start_field=cast_temp_or_field, stop_field=cast_temp_or_field, step_field=1.0, mevents=int, magnet_device=cast_magnet_device)
    def run(self, start_temperature=1.0, stop_temperature=1.0, step_temperature=10, start_field=1.0, stop_field=1.0, step_field=1.0, mevents=10, magnet_device="N/A"):
        is_temp_scan_defined = start_temperature is not None and stop_temperature is not None and step_temperature is not None
        is_field_scan_defined = start_field is not None and stop_field is not None and step_field is not None
        if g.cget("a_selected_magnet")["value"] != magnet_device:
                self.magnet_to_function_map[magnet_device]()
        if is_temp_scan_defined and is_field_scan_defined:
            for temp in range(start_temperature, stop_temperature+0.0001, step_temperature): # TODO: Use np.arange
                for field in range(start_field, stop_field+0.0001, step_field): # TODO: Use np.arange
                    inst.set_mag(field, wait=True)
                    inst.set_temp(temp, wait=True)
                    g.begin(quiet=True)
                    g.waitfor_mevents(mevents)
                    g.end(quiet=True)
        elif is_temp_scan_defined:
            for temp in range(start_temperature, stop_temperature+0.0001, step_temperature): # TODO: Use np.arange
                inst.set_temp(temp, wait=True)
                g.begin(quiet=True)
                g.waitfor_mevents(mevents)
                g.end(quiet=True)
        elif is_field_scan_defined:
            for field in range(start_field, stop_field+0.0001, step_field): # TODO: Use np.arange
                inst.set_mag(field, wait=True)
                g.begin(quiet=True)
                g.waitfor_mevents(mevents)
                g.end(quiet=True)

    @cast_parameters_to(start_temperature=cast_temp_or_field, stop_temperature=cast_temp_or_field, step_temperature=cast_temp_or_field,
         start_field=cast_temp_or_field, stop_field=cast_temp_or_field, step_field=1.0, mevents=int, magnet_device=cast_magnet_device)
    def parameters_valid(self, start_temperature=1.0, stop_temperature=1.0, step_temperature=1.0, start_field=1.0, stop_field=1.0, step_field=1.0, mevents=10, magnet_device="N/A"):
        reason = ""
        is_temp_scan_defined = start_temperature is not None and stop_temperature is not None and step_temperature is not None
        is_field_scan_defined = start_field is not None and stop_field is not None and step_field is not None
        if is_field_scan_defined is False and is_temp_scan_defined is False:
            reason += "Neither temp nor field scans have been defined"
        if is_temp_scan_defined:
            if start_temperature < 0.0 and stop_temperature < 0.0 and step_temperature == 0.0:
                reason += "Temperature too low\n"
        if magnet_device not in self.possible_magnet_devices:
            reason += "Magnet devices {} not in possible devices {}\n".format(magnet_device, self.possible_magnet_devices)
        if is_field_scan_defined and magnet_device in self.possible_magnet_devices and magnet_device == "N/A":
            reason += "No magnet device set but field is being set\n"
        if reason != "":
            return reason
        else:
            return None