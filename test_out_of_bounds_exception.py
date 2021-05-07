from genie_python.genie_script_generator import ScriptDefinition


class DoRun(ScriptDefinition):

    def get_help(self):
        return "Magnet device must not be N/A\n"

    def estimate_time(self, temperature=1.0, field=1.0, mevents=10, magnet_device="N/A"):
        return 0

    def run(self, temperature=1.0, field=1.0, mevents=10, magnet_device="N/A"):
        pass

    def parameters_valid(self, temperature=1.0, field=1.0, mevents=10, magnet_device="N/A"):
        if magnet_device == "N/A":
            return "Magnet must not be N/A"
        else:
            return None
