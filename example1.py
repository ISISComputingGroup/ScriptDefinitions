from collections import OrderedDict

from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to


class DoRun(ScriptDefinition):
    global_params_definition = OrderedDict(
        {
            "example param:": ("0", int),
            "example param 2:": ("2", float),
            "example param 3:": ("any string", str),
        }
    )

    def run(self, the="1", imat="2", fields="2", there="2", are="2", more="2"):
        print(the)
        print(imat)
        print(fields)
        print(there)
        print(are)
        print(more)

    def parameters_valid(self, the="1", imat="2", fields="2", there="2", are="1", more="2"):
        if are != "1":
            return "are is not 1"
        else:
            return None

    def estimate_time(self, the="1", imat="2", fields="2", there="2", are="1", more="2"):
        return float(the) * float(imat) * float(self.global_params["example param 2:"])

    def get_help(self):
        return None

    @cast_parameters_to(the=float, imat=float, fields=float, there=float, are=float, more=float)
    def estimate_custom(self, the="1", imat="2", fields="2", there="2", are="1", more="2"):
        custom1 = the * 2
        custom2 = imat + 5
        return OrderedDict([("custom1", str(custom1)), ("custom2", str(custom2))])
