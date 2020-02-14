from genie_python.genie_script_generator import ActionDefinition

class DoRun(ActionDefinition):
    def run(self, field1="1", field2="2"):
        pass

    def parameters_valid(self, field1="1", field2="2"):
        if field1 != "1" and field2 != "2":
            return "field 1 must be 1 and field 2 must be 2"
        else:
            return None

    def get_help(self):
        return None
