from genie_python.genie_script_generator import ScriptDefinition


class DoRun(ScriptDefinition):
    def run(self, to_print="1"):
        sleep(1)
        print(to_print)

    def parameters_valid(self, to_print="1"):
        if to_print == "invalid":
            return "cannot equal invalid"

    def estimate_time(self, to_print="1"):
        return 1.0

    def get_help(self):
        return "This script is for printing anything other than the string 'invalid'"
