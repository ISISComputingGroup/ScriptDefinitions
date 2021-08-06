from genie_python.genie_script_generator import ScriptDefinition
from collections import OrderedDict


class DoRun(ScriptDefinition):
    global_params_definition = OrderedDict({"example param:": ("1", int), "example param 2:": ("1.23", float),
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
