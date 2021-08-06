from genie_python.genie_script_generator import ScriptDefinition, GlobalParamValidationError
from collections import OrderedDict

def param2_validator(param2) :
    param2 = float(param2)
    if param2 < 1 or param2 > 3:
        raise GlobalParamValidationError("Param 2 must be between 1 and 3")
    return param2


class DoRun(ScriptDefinition):
    global_params_definition = OrderedDict({"example param:": ("1", int), "example param 2:": ("1.23", param2_validator),
                                            "example param 3:": ("hello", str), "example param 4:": ("0", int)})

    def run(self, to_print="hello"):
        print(self.global_params["example param 3:"])

    def parameters_valid(self, to_print="hello"):
        if self.global_params["example param:"] != 1:
            return f"Global param 1 should be equal to 1, but is {self.global_params['example param:']}"
        if self.global_params["example param 2:"] != 1.23:
            return f"Global param 2 should be equal to 1.23, but is {self.global_params['example param 2:']}"
        if self.global_params["example param 3:"] != 'hello':
            return f'Global param 3 should be equal to "hello", but is "{self.global_params["example param 3:"]}"'
        if self.global_params["example param 4:"] > 100:
            return f'Global param 4 should not be higher than 100, but is "{self.global_params["example param 4:"]}"'

    def estimate_time(self, to_print="hello"):
        return int(self.global_params["example param 4:"])

    def get_help(self):
        return "This is my help for test_dynamic_scripting"
