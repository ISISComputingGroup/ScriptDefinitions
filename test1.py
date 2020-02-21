from genie_python.genie_script_generator import ScriptDefinition


class DoRun(ScriptDefinition):
    def run(self, field1="1", field2="2"):
        pass

    def parameters_valid(self, field1="1", field2="2"):
        reason = ""
        if field1 != "1":
            reason += "field 1 must be 1\n"
        if field2 != "2":
            reason += "field 2 must be 2\n"
        if reason != "":
            return reason
        else:
            return None

    def get_help(self):
        return "This is my help for test1"
