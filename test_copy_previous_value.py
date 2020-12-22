from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to, CopyPreviousRow


class DoRun(ScriptDefinition):
    def run(self, field1=CopyPreviousRow("1"), field2="2"):
        pass

    def parameters_valid(self, field1=CopyPreviousRow("1"), field2="2"):
        reason = ""
        if field1 != "1":
            reason += "field 1 must be 1\n"
        if field2 != "3":
            reason += "field 3 must be 3\n"
        if reason != "":
            return reason
        else:
            return None
            
    def estimate_time(self, field1=CopyPreviousRow("1"), field2="2"):
        return float(field1) * float(field2)    

    def get_help(self):
        return "This is my help for test2"
