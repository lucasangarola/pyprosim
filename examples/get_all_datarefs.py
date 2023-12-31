from pathlib import Path

# This file path
this_path = Path(__file__).resolve().parent

# NOTE: This is only required to allow the system to find the pyprosim module without
# the need of installing it.
# You can avoid this if your main application is located at the same level that the pyprosim module.
import sys
sys.path.append(f"{this_path}/../pyprosim")

# Import the module
from pyprosim import PyProsim

# SDK DLL file path. NOTE: Exclude the extension name.
dll_path = this_path.joinpath("../","prosimsdk", "ProSimSDK")

def on_connect():
    print("Prosim is connected!")

def on_disconnect():
    print("Prosim is DISCONNECTED!")

# Create class passing the dll_path
prosim = PyProsim(prosimsdk_path=dll_path, on_connect_callback=on_connect, on_disconnect_callback=on_disconnect)

# Connect to Prosim. 
# You can also try 127.0.0.1 if you are running locally. If that does not
# work, please use the machine ip address.
prosim.connect("192.168.1.103")

# Print some simulator info
print(prosim.get_info())

# Get list of all datarefs
datarefs = prosim.get_all_avail_datarefs()

# Print dataref list in a readable form
for dr in datarefs:
    print(
        f'[{dr["name"]}]\n'
        f'|-> Descr: {dr["description"]}\n'
        f'|-> Read: {dr["can_read"]}; Write: {dr["can_read"]}\n'
        f'|-> Type: {dr["data_type"]}\n'
        f'|-> Unit: {dr["date_unit"]}\n'
    )


