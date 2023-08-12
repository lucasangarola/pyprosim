from pathlib import Path
import time
from enum import Enum

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

class StateMachine(Enum):
    RUN = 0
    ONLINE = 1
    OFFLINE = 2

def on_connect():
    print("Prosim is connected!")
    global sm_state
    sm_state = StateMachine.ONLINE

def on_disconnect():
    print("Prosim is DISCONNECTED!")
    global sm_state
    sm_state = StateMachine.OFFLINE

def on_change(dataref):
    # Do something here!
    # Also if you use this same method as callback for other datarefs
    # You would need to do some sort of switch case depending on
    # what you would like to achieve.
    print(f"{dataref.name} = {dataref.value}")


# Create class passing the dll_path
prosim = PyProsim(prosimsdk_path=dll_path, on_connect_callback=on_connect, on_disconnect_callback=on_disconnect)

print("Example Running... Wating to connect to ProSim")
sm_state = StateMachine.OFFLINE
while True:
    # Attempt to connect
    if sm_state == StateMachine.OFFLINE:
        # Connect to Prosim. 
        # You can also try 127.0.0.1 if you are running locally. If that does not
        # work, please use the machine ip address.
        prosim.connect("192.168.1.103", synchronous=False)
    elif sm_state == StateMachine.ONLINE:
        # Print some simulator info
        print(prosim.get_info())
        # Register dataref to interact with
        prosim.add_dataref("aircraft.engines.1.thrust", 100, on_change_callback=on_change)
        sm_state = StateMachine.RUN
    elif sm_state == StateMachine.RUN:
        pass
    time.sleep(0.25)

