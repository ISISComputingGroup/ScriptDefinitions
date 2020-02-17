# Allow the user to right keep in temp or field to use the current value
def float_or_keep(temp_or_field):
    if temp_or_field.lower() == "keep":
        return None
    else:
        return float(temp_or_field)


magnet_devices = {"ZF": "Active ZF", "LF": "Danfysik", "TF": "T20 Coils"}


# Convert to magnet device type if possible, if not they have input an incorrect magnet_device
# Raise a ValueError and this will be caught and displayed to the user that the conversion is incorrect 
def magnet_device_type(magnet_device):
    magnet_device = magnet_device.upper()
    if magnet_device in magnet_devices.keys():
        return magnet_devices[magnet_device]
    elif magnet_device == "N/A":
        return magnet_device
    raise ValueError("Magnet device must be one of {} or N/A".format(magnet_devices))


# Cast the custom python expression to a string or None if empty
def cast_custom_expression(expression):
    if expression == "":
        return "None"
    else:
        return expression
