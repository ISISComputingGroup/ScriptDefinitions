from genie_python.genie_script_generator import ActionDefinition, cast_parameters_to
from genie_python import genie as g

def mytype(string_input: str) -> float:
    if string_input == "default":
        return 0.0
    else:
        return float(string_input)


class DoRun(ActionDefinition):

    @cast_parameters_to(temperature=float, field=float, uamps=mytype)
    def run(self, temperature: float=0.0, field: float=0.0, uamps: float=0.0):
        g.cset("temperature", temperature)
        g.cset("field", field)
        g.begin()
        g.waitfor_uamps(uamps)
        g.end()

    @cast_parameters_to(temperature=float, field=float, uamps=mytype)
    def parameters_valid(self, temperature: float=0.0, field: float=0.0, uamps: float=0.0):
        with open("C:\\Instrument\\Dev\\PythonLog.txt", "a+") as f:
            f.write("Checking validity example2 \r\n")
        errors: str = ""
        if not 0.1 <= temperature <= 300:
            errors += "Temperature outside range\n"
        if not -5 <= field < 5:
            errors += "Field outside range"
        if not -20 <= uamps <= 32:
            errors += "uamps outside of range"
        with open("C:\\Instrument\\Dev\\PythonLog.txt", "a+") as f:
            f.write(errors+"\r\n")
        if errors != "":
            return errors
        return None    

