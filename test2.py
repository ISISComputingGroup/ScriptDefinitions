from genie_python.genie_script_generator import ActionDefinition

class DoRun(ActionDefinition):
    def run(self, field1="1", field3="3"):
        pass

    def parameters_valid(self, field1="1", field3="3"):
        if field1 != "1" and field3 != "3":
            return "field 1 must be 1 and field3 must be 3"
        else:
            return None

    def get_help(self):
        return None
