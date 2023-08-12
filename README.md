# Python wrapper for ProSim Simulator

This project is a small and simple wrapper to access ProSim using Python.

The implementation benefits from [pythonnet](https://github.com/pythonnet/pythonnet) to import ProSim SDK and wrap around some of its methods.
For more special usages, the SDK class can also be accessed directly.

The idea of this implementation is to create a simple and fast access to all datarefs in order to connect
then with external hardware.

For convenience I have included the ProSim SDK DLL file in this project, nevertheless the SDK can be found here:

https://download.prosim-ar.com/ProSimSDK/

## Getting Started

### Requirements
This implementation has been tested with ```Python 3.11```. I highly recommend to use this version.

To run the examples I recommend to use a virtual env of your choice.

Install requirements:

```Bash
pip install -r requirements.txt
```

### Running Examples

In the route directory of this repository run:

```Bash
python examples/<name of the example here>.py
```

## Contributing

Contributing is always welcome, please submit the issues/improvements to this project to keep a good documentation.

Make sure you use Formatting: ```Black```

## License
This code is licensed under MIT license.

## Current Status
ProSim provides many features which can be accessed from their SDK. Not all features have been implemented, but this implementation is a good basis to start something bigger (I believe).

### Points to Improve
1. Error handling can be improved digesting the original ProSim exception to extract the reason of failure and finally create a pyprosim exception class. (Just thinking loud)