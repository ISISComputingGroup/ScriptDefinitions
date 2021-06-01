from genie_python.genie_script_generator import ScriptDefinition
from collections import OrderedDict

class DoRun(ScriptDefinition):

    global_params_definition = OrderedDict({"example param:": ("0", int), "example param 2:": ("2", float),
                                            "example param 3:": ("any string", str)})

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
