from pathlib import Path
import time
from enum import Enum
from pyprosim import PyProsim

# This file path
this_path = Path(__file__).resolve().parent

# SDK DLL file path. NOTE: Exclude the extension name.
dll_path = this_path.joinpath("../", "prosimsdk", "ProSimSDK")


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


# Create class passing the dll_path
prosim = PyProsim(
    prosimsdk_path=dll_path,
    on_connect_callback=on_connect,
    on_disconnect_callback=on_disconnect,
)

print("Example Running... Wating to connect to ProSim")
sm_state = StateMachine.OFFLINE
while True:
    # Attempt to connect
    if sm_state == StateMachine.OFFLINE:
        # Connect to Prosim.
        # You can also try 127.0.0.1 if you are running locally. If that does not
        # work, please use the machine ip address.
        prosim.connect("localhost", synchronous=False)
    elif sm_state == StateMachine.ONLINE:
        # Print some simulator info
        print(prosim.get_info())
        # Register dataref to interact with.
        # Notice that interval is set to zero, this is because we want only to write the value
        # but we dont have interest on Prosim sending us updates of the value.
        # If both read/write is required then interval should be set with an integer larger than
        # zero.
        prosim.activate_dataref("system.switches.S_MIP_ISFD_APP", 0)
        sm_state = StateMachine.RUN
    elif sm_state == StateMachine.RUN:
        # To see the value use interval > 0
        print(
            "FC: ",
            prosim.get_value("system.switches.S_MIP_ISFD_APP"),
        )

        # Finally write the dataref
        prosim.set_value("system.switches.S_MIP_ISFD_APP", 1)
        time.sleep(1)
        prosim.set_value("system.switches.S_MIP_ISFD_APP", 0)
        time.sleep(1)

    time.sleep(0.25)
