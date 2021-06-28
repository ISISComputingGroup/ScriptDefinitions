from genie_python.genie_script_generator import ScriptDefinition
from collections import OrderedDict


class DoRun(ScriptDefinition):
    global_params_definition = OrderedDict({"example param:": ("0", int), "example param 2:": ("2", float),
                                            "example param 3:": ("any string", str)})

    def run(self, to_print="hello"):
        print(self.global_params["example param 3:"])

    def parameters_valid(self, to_print="hello"):
        pass
            
    def estimate_time(self, to_print="hello"):
        return int(self.global_params["example param 2:"])

    def get_help(self):
        return "This is my help for test_dynamic_scripting"
