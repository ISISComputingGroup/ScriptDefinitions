from typing import Generator, Optional

import numpy as np
from genie_python import genie as g
from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to


def inclusive_float_range_with_step_flip(start: float, stop: float, step: float)-> Generator:
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
    # Get the modulo so we know to stop early like arrange if the steps don't fit evenly.
    modulo = abs(stop - start) % abs(step)
    if stop > start:
        vstop = stop - modulo
    else:
        vstop = stop + modulo
    for i in np.linspace(start, vstop, int(abs(vstop - start) / abs(step)) + 1):
        if ((i >= start) and (i <= stop)) or (
            (i >= stop) and (i <= start)
        ):  # Check inserted here to ensure scan remains within defined range
            yield i


class DoRun(ScriptDefinition):
    @cast_parameters_to(start_temp=float, stop_temp=float, step_temp=float)
    def run(self, start_temp: float = 1.0, stop_temp: float = 1.0, step_temp: float = 0.5) -> None:
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
        for temp in inclusive_float_range_with_step_flip(start_temp, stop_temp, step_temp):
            g.cset("temperature", temp)
            g.begin(quiet=True)
            g.waitfor_time(seconds=30)
            g.end(quiet=True)

    @cast_parameters_to(start_temp=float, stop_temp=float, step_temp=float)
    def parameters_valid(
        self, start_temp: float = 1.0, stop_temp: float = 1.0, step_temp: float = 0.5
    ) -> Optional[str]:
        errors = ""
        if start_temp == 0 or stop_temp == 0:
            errors += "Cannot go to zero kelvin\n"
        if start_temp < stop_temp and step_temp < 0.0:
            errors += "Stepping backwards when stop temp is higher than start temp\n"
        elif start_temp > stop_temp and step_temp > 0.0:
            errors += "Stepping forward when stop temp is lower than start temp\n"
        if errors != "":
            return errors
        return None

    @cast_parameters_to(start_temp=float, stop_temp=float, step_temp=float)
    def estimate_time(
        self, start_temp: float = 1.0, stop_temp: float = 1.0, step_temp: float = 0.5
    ) -> int:
        if stop_temp >= start_temp:
            steps = round((stop_temp - start_temp) / step_temp)
            estimated_time = 30 + steps * 30
            return estimated_time
        else:
            return 0

    def get_help(self) -> str:
        return "An example config to show a looping mechanism"
