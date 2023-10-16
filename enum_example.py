from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to

class DoRun(ScriptDefinition):

    # Create a property to store valid enum names
    process_status_enum_values = ["ok", "not_okay"]

    def run(self, process_status_enum="start"):
        print("Running do_run with process_status: " + process_status_enum)

    @cast_parameters_to(process_status_enum=str)
    def parameters_valid(self, process_status_enum="ok"):
        if process_status_enum not in self.process_status_enum_values:
            return "process_status must be one of: " + str(self.process_status_enum_values)
        return None

    def estimate_time(self, process_status_enum="ok"):
        if process_status_enum == "ok":
            return 10
        elif process_status_enum == "not_okay":
            return 0

    def get_help(self):
        return None
