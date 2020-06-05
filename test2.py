from genie_python.genie_script_generator import ScriptDefinition


class DoRun(ScriptDefinition):
    def run(self, field1="1", field3="3"):
        pass

    def parameters_valid(self, field1="1", field3="3"):
        reason = ""
        if field1 != "1":
            reason += "field 1 must be 1\n"
        if field3 != "3":
            reason += "field 3 must be 3\n"
        if reason != "":
            return reason
        else:
            return None
            
    def estimate_time(self, field1="1", field3="2"):
        return float(field1) * float(field3)    

    def get_help(self):
        return "This is my help for test2"