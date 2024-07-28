import clr, System
from pathlib import Path
from typing import Callable, Dict


class PyProsimDLLException(Exception):
    pass


class PyProsimImportException(Exception):
    pass


class PyProsimTypeException(Exception):
    pass


class PyProsimDatarefException(Exception):
    pass


class PyProsim:
    class Dataref:
        """Class to represent a PyProsim dataref.
        This class also holds the actual prosim
        dataref object.
        """

        def __init__(
            self,
            parent: "PyProsim",
            name: str,
            description: str,
            data_type: object,
            data_unit: str,
            can_read: bool,
            can_write: bool,
        ):
            """Dataref class initialization

            Args:
                parent (PyProsim): PyProsim parent class. This is to access Prosim SDK
                name (str): Dataref name
                description (str): Dataref description
                data_type (object): Dataref data type. This follows the C# data type,
                                    for example: System.Double or System.Int32
                data_unit (str): No information about what Prosim tries to represent with this.
                can_read (bool): Dataref is readable
                can_write (bool): Dataref is writable
            """
            self._parent = parent
            self._name = name
            self._description = description
            self._data_type = data_type
            self._data_unit = data_unit
            self._can_read = can_read
            self._can_write = can_write
            # The variable dataref_obj is the actual prosim dataref class
            # This object will be created when this dataref is activated.
            self._dataref_obj: object = None
            self._interval = 0
            # Flag to indicate that this PyProsim dataref has been initialized.
            self._active = False

        @property
        def name(self) -> str:
            return self._name

        @property
        def description(self) -> str:
            return self._description

        @property
        def data_type(self) -> object:
            return self._data_type

        @property
        def data_unit(self) -> str:
            return self._data_unit

        @property
        def can_read(self) -> bool:
            return self._can_read

        @property
        def can_write(self) -> bool:
            return self._can_write

        @property
        def interval(self) -> int:
            return self._interval

        @property
        def active(self) -> bool:
            return self._active

        @property
        def value(self) -> object:
            """Getter for Dataref value

            Raises:
                PyProsimDatarefException: This exception indicates when the dataref
                                        has not been initialized.

            Returns:
                object: Value with type corresponding to dataref data_type definition.
            """
            if self._dataref_obj == None:
                raise PyProsimDatarefException(
                    f'Dataref "{self.name}" has not been initialized'
                )
            return self._dataref_obj.value

        @value.setter
        def value(self, value):
            """Dataref value setter

            Args:
                value (_type_): Value to set dataref with. The type
                                is not restricted, but this setter
                                will attempt to 'cast' the given value
                                to the C# type for this dataref. If the
                                'cast' is not possible an exception will
                                be raised.

            Raises:
                PyProsimDatarefException: This dataref cannot be written
                PyProsimTypeException: The given value type cannot be casted to
                                       the C# type.
            """
            if self._can_write == False:
                raise PyProsimDatarefException(
                    f'Dataref "{self.name}" is not writable!'
                )
            try:
                self._dataref_obj.value = self._data_type(value)
            except System.AggregateException as e:
                raise PyProsimTypeException(e)

        def activate(self, interval: int, on_change_callback: Callable = None):
            """Dataref activate. This activation means that the prosim dataref
            object is being instantiated, hence prosim has knowledge that we
            want to read or write this dataref.

            Args:
                interval (int): How frequent Prosim should send this dataref to us (in milliseconds)
                on_change_callback (Callable, optional): Method to be called when this dataref changes.
                                                         Defaults to None.
            """
            # Create Prosim dataref object
            dr = DataRef(self.name, interval, self._parent.sdk)

            # Set callback on change if needed
            if on_change_callback is not None:
                dr.onDataChange += on_change_callback

            # Store dataref object
            self._dataref_obj = dr
            self._interval = interval
            self._active = True

    def __init__(
        self,
        prosimsdk_path: Path,
        on_connect_callback: Callable = None,
        on_disconnect_callback: Callable = None,
    ):
        """PyProsim class init

        Args:
            prosimsdk_path (Path): Path to prosim SDK DLL library
            on_connect_callback (Callable, optional): Callable object which will be called once we
                                                      are connected to prosim. Defaults to None.
            on_disconnect_callback (Callable, optional): Callable object which will be called once
                                                         prosim disconnects. Defaults to None.

        Raises:
            PyProsimDLLException: CLR space could not be loaded
            PyProsimImportException: Prosim components could not be imported
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
        self._on_connect_cb = on_connect_callback
        self.sdk.onConnect += self._on_connect
        if on_disconnect_callback is not None:
            self.sdk.onDisconnect += on_disconnect_callback

        # Init main dictionary which will hold Prosim datarefs objects
        self._datarefs: Dict[PyProsim.Dataref] = {}

    def _on_connect(self):
        """Callback when PyProsim gets a connection with Prosim software"""
        # Read dataref database from Prosim software
        self._parse_supported_datarefs()
        # Call external callback if has been defined
        if self._on_connect_cb is not None:
            self._on_connect_cb()

    def _parse_supported_datarefs(self):
        """Request and parse Prosim dataref database"""
        self._datarefs: Dict[PyProsim.Dataref] = {}
        for dr in self.sdk.getDataRefDescriptions():
            # Parse data type
            if dr.DataType == "System.Boolean":
                data_type = System.Boolean
            elif dr.DataType == "System.Byte":
                data_type = System.Byte
            elif dr.DataType == "SystemSByte":
                data_type = System.SByte
            elif dr.DataType == "System.Char":
                data_type = System.Char
            elif dr.DataType == "System.Decimal":
                data_type = System.Decimal
            elif dr.DataType == "System.Double":
                data_type = System.Double
            elif dr.DataType == "System.Single":
                data_type = System.Single
            elif dr.DataType == "System.Int32":
                data_type = System.Int32
            elif dr.DataType == "System.UInt32":
                data_type = System.UInt32
            elif dr.DataType == "System.IntPtr":
                data_type = System.IntPtr
            elif dr.DataType == "System.UIntPtr":
                data_type = System.UIntPtr
            elif dr.DataType == "System.Int64":
                data_type = System.Int64
            elif dr.DataType == "System.UInt64":
                data_type = System.UInt64
            elif dr.DataType == "System.Int16":
                data_type = System.Int16
            elif dr.DataType == "System.UInt16":
                data_type = System.UInt16
            elif dr.DataType == "System.String":
                data_type = System.String
            else:
                PyProsimTypeException(f'Data Type "{dr.DataType}" unknown')

            # Create PyProsim dataref class
            self._datarefs[dr.Name] = self.Dataref(
                parent=self,
                name=dr.Name,
                description=dr.Description,
                data_type=data_type,
                data_unit=dr.DataUnit,
                can_read=dr.CanRead,
                can_write=dr.CanWrite,
            )

    def connect(self, ip_addr: str, synchronous: bool = True) -> None:
        """Open connection with Prosim Server

        Args:
            ip_addr (str): Host IP address when ProSim is running. Use "localhost"
                           if prosim runs in the same PC as this script.
            synchronous (bool, optional): Blocking mode when True. Defaults to True.
        """
        self.sdk.Connect(ip_addr, synchronous)

    def activate_dataref(
        self, dataref_name: str, interval: int, on_change_callback: Callable = None
    ) -> None:
        """Inform Prosim we want to read/write this dataref. Adding interval > 0
        Prosim software will periodically send this value back to us.

        Args:
            dataref_name (str): Prosim dataref name
            interval (int): How frequent prosim should send this dataref in miliseconds
            on_change_callback (Callable, optional): Callable object which will be called when dataref
                                                     changes. Defaults to None.

        Raises:
            PyProsimDatarefException: Unknown dataref name. Not part of prosim database
        """
        if dataref_name not in self._datarefs:
            raise PyProsimDatarefException(
                f'Dataref "{dataref_name}" is not in Prosim database'
            )

        self._datarefs[dataref_name].activate(interval, on_change_callback)

    def get_value(self, dataref_name: str) -> object:
        """Get dataref value

        Args:
            dataref_name (str): Prosim dataref name

        Raises:
            PyProsimDatarefException: Unknown dataref name. Not part of prosim database.

        Returns:
            object: Dataref value with type as specified by prosim dataref database
        """
        if dataref_name not in self._datarefs:
            raise PyProsimDatarefException(
                f'Dataref "{dataref_name}" is not in Prosim database'
            )

        return self._datarefs[dataref_name].value

    def get_dataref_database(self) -> dict:
        """Returns dictionary with all available Prosim datarefs

        Returns:
            dict: All available Prosim datarefs
        """
        dataref_database = {}
        for name, dr in self._datarefs.items():
            dataref_database[dr.name] = {
                "description": dr.description,
                "data_type": dr.data_type.__name__,
                "data_unit": dr.data_unit,
                "read_access": dr.can_read,
                "write_access": dr.can_write,
            }
        return dataref_database

    def get_info(self) -> dict:
        """General Prosim information like licensee and etc.

        Returns:
            dict: General information.
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

    def set_value(self, dataref_name: str, value: object):
        """Set dataref value

        Args:
            dataref_name (str): Prosim dataref name
            value (object): Value to set dataref with. The type
                            is not restricted, but this setter
                            will attempt to 'cast' the given value
                            to the C# type for this dataref. If the
                            'cast' is not possible an exception will
                            be raised.

        Raises:
            PyProsimDatarefException: Unknown dataref name. Not part of prosim database.
        """
        if dataref_name not in self._datarefs:
            raise PyProsimDatarefException(
                f'Dataref "{dataref_name}" is not in Prosim database'
            )

        self._datarefs[dataref_name].value = value
