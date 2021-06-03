from genie_python.genie_script_generator import ScriptDefinition


class DoRun(ScriptDefinition):
    def run(self, to_print="hello"):
        print(to_print)

    def parameters_valid(self, to_print="hello"):
        pass
            
    def estimate_time(self, to_print="hello"):
        return 1.0

    def get_help(self):
        return "This is my help for test_dynamic_scripting"
