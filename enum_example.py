from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to

class DoRun(ScriptDefinition):

    # Create a property to store valid enum names
    process_status_values = ["ok", "not_okay", "definitely_not_okay"]

    enum_params = ["process_status"]

    def run(self, process_status="start"):
        print("Running do_run with process_status: " + process_status)

    @cast_parameters_to(process_status=str)
    def parameters_valid(self, process_status="ok"):
        # if process_status_enum not in self.process_status_enum_values:
        #     return "process_status must be one of: " + str(self.process_status_enum_values)
        # return None
        if process_status == "ok":
            return None
        else: 
            return "process_status must be one of: " + str(self.process_status_values)

    def estimate_time(self, process_status="ok"):
        if process_status == "ok":
            return 10
        elif process_status == "not_okay":
            return 0

    def get_help(self):
        return """
This is the example ENUM script.\n
        """
