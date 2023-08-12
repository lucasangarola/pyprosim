import clr
from pathlib import Path
from typing import Callable


class PyProsimDLLException(Exception):
    pass


class PyProsimImportException(Exception):
    pass


class PyProsim:
    def __init__(
        self,
        prosimsdk_path: Path,
        on_connect_callback: Callable = None,
        on_disconnect_callback: Callable = None,
    ):
        """Py prosim class init
        Attributes:
        prosimsdk_path -- Path to prosim SDK DLL library
        on_connect_callback -- Callable object which will be called once we
                               are connected to prosim
        on_disconnect_callback -- Callable object which will be called once
                                  prosim disconnects
        """
        # Load CLR namespace
        try:
            clr.AddReference(str(prosimsdk_path))
        except Exception as e:
            raise PyProsimDLLException(e)

        # Finally import the required classes
        # Note the global definition is to make DataRef import available
        # to the rest of this implementation
        try:
            global DataRef
            from ProSimSDK import ProSimConnect, DataRef
        except Exception as e:
            raise PyProsimImportException(e)

        # Create Prosim SDK class
        self.sdk = ProSimConnect()

        # Set callbacks if required
        if on_connect_callback is not None:
            self.sdk.onConnect += on_connect_callback
        if on_disconnect_callback is not None:
            self.sdk.onDisconnect += on_disconnect_callback

        # Init main dictionary which will hold Prosim datarefs objects
        self.datarefs = {}

    def connect(self, ip_addr: str, synchronous: bool = True) -> None:
        """Simply connect to Prosim
        Attributes:
        ip_addr -- Host IP address when ProSim is running
        synchronous -- Basically blocking mode whne True

        Return:
        None
        """
        self.sdk.Connect(ip_addr, synchronous)

    def add_dataref(
        self, dataref_name: str, interval: int, on_change_callback: Callable = None
    ) -> None:
        """Add a dataref request to ProSim. Then prosim can periodically send
        this value back.
        This dataref object is then accesible through this class datarfes dictionary,
        or getter method.
        Attributes:
        dataref_name -- Prosim dataref name
        interval -- How frequent prosim should send this dataref in miliseconds
        on_change_callback -- Callable object which will be called when dataref
                              changes.
        Return:
        None
        """
        # Create Prosim dataref object
        dr = DataRef(dataref_name, interval, self.sdk)

        # Set callback on change if needed
        if on_change_callback is not None:
            dr.onDataChange += on_change_callback

        # Store dataref object
        self.datarefs[dataref_name] = dr

    def get_dataref_value(self, dataref_name: str):
        """Get dataref value.
        Attributes:
        dataref_name -- Prosim dataref name
        Return:
        Prosim dataref value or None if dataref has not been
        added yet.
        """
        return self.datarefs.get(dataref_name, None).value

    def get_all_avail_datarefs(self) -> list:
        """Request the full list of avaiable datarefs from ProSim
        Attributes:
        None
        Return:
        list -- List of dictionaries containing all info about the
                datarefs
        """
        dataref_list = []
        for dr in self.sdk.getDataRefDescriptions():
            dataref_list.append(
                {
                    "name": dr.Name,
                    "description": dr.Description,
                    "can_read": dr.CanRead,
                    "can_write": dr.CanWrite,
                    "data_type": dr.DataType,
                    "date_unit": dr.DataUnit,
                }
            )
        return dataref_list

    def get_info(self) -> dict:
        """Get simulator information
        Attributes:
        None
        Return:
        dict -- Dictionary with sim information
        """
        info = self.sdk.getLicensingInfo()
        features = []
        for f in info.Features:
            features.append(str(f))
        return {
            "mode": info.Mode,
            "features": features,
            "licensee": info.Licensee,
        }
