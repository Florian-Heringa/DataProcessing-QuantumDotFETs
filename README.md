# DataProcessing-QuantumDotFETs
Quantum Dot FET data processing script

This repository holds some helper scripts for data acquired with LabView VIs.
The data is related to Colloïdal Quantum Dots deposited on a FET structure.


The "read-sweep" script is not finished and likelty will never be. It was a trial to make a 
comprehensive interface for interacting with the data. This turned out to not be necessary as loading the data into
any data analysis program is much more efficient.

The other two scripts are used for converting the data of the drain-source sweeps into a proper csv format.
By an error in the program the data was saved in an extremely inconvenient format. Because of this some
conversion is required.

The "convert_VDSsweep.py" script converts a single file by being called from the commandline with the filename (as a string) as the argument.

The "convert_VDSsweep_all.py" script tries to convert all files in the folder it is placed in. A try/except block tries to capture all files that
are not in the correct format. Since the block does this naively, there is no guarantee that an error will always point
to an incorrect file. Always check if conversion was succesful!
Use this script by placing it into the folder where your data is, and run it from the commandline without any arguments.
