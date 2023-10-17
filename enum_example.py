from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to

from enum import Enum


class DoRun(ScriptDefinition):
    

    enum_params = ["process_status"]
    class process_status_enum(Enum):
        ok = 1
        not_okay = 2
        definitely_not_okay = 3


    def run(self, process_status="not_working"):
        print("Running do_run with process_status: " + process_status)

    @cast_parameters_to(process_status=str)
    def parameters_valid(self, process_status="ok"):
        # check that the enum value of process_status is ok
        if self.process_status_enum[process_status] != self.process_status_enum.ok:
            return "process_status must be ok"

    def estimate_time(self, process_status="ok"):
        if process_status == "ok":
            return 10
        else:
            return 0

    def get_help(self):
        return """
This is the example ENUM dropdown script.\n
        """
