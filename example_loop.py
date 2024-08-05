import numpy as np
from genie_python import genie as g
from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to


class DoRun(ScriptDefinition):

    @cast_parameters_to(start_temp=float, stop_temp=float, step_temp=float)
    def run(self, start_temp=1.0, stop_temp=1.0, step_temp=0.5):
        # Execute the loop once
        if start_temp == stop_temp:
            step_temp = 1.0
        # Done to account for pythons range non inclusivity
        small_amount = 0.000001
        if start_temp <= stop_temp:
            stop_temp += small_amount
        else:
            stop_temp -= small_amount
        # Regular range can't use floats
        for temp in np.arange(start_temp, stop_temp, step_temp):
            g.cset("temperature", temp)
            g.begin(quiet=True)
            g.waitfor_time(seconds=30)
            g.end(quiet=True)
    
    @cast_parameters_to(start_temp=float, stop_temp=float, step_temp=float)
    def parameters_valid(self, start_temp=1.0, stop_temp=1.0, step_temp=0.5):
        errors = ""
        if start_temp == 0 or stop_temp == 0:
            errors += "Cannot go to zero kelvin\n"
        if start_temp < stop_temp and step_temp < 0.0:
            errors += "Stepping backwards when stop temp is higher than start temp\n"
        elif start_temp > stop_temp and step_temp > 0.0:
            errors += "Stepping forward when stop temp is lower than start temp\n"

    @cast_parameters_to(start_temp=float, stop_temp=float, step_temp=float)
    def estimate_time(self, start_temp=1.0, stop_temp=1.0, step_temp=0.5):
        if stop_temp >= start_temp:
            steps = round((stop_temp - start_temp) / step_temp)
            estimated_time = 30 + steps * 30
            return estimated_time
        else:
            return 0

    def get_help(self):
        return "An example config to show a looping mechanism"
