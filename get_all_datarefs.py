from pyprosim import PyProsim
from pathlib import Path

# This file path
this_path = Path(__file__).resolve().parent
# SDK DLL file path. NOTE: Do no include the extension name.
dll_path = this_path.joinpath("prosimsdk", "ProSimSDK")

prosim = PyProsim(prosimsdk_path=dll_path)

prosim.connect("192.168.1.103")

l = prosim.get_all_avail_datarefs()
print(l)

print(prosim.get_info())
