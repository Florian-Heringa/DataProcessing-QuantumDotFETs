import sys
import numpy as np
import re
from os import listdir, getcwd
from os.path import isfile, join
import math

### Call Program by using 'convert_VDSsweep "filename"' on the commandline
### from the folder where the file is placed.
## New file will be saved as 'filename_EDITED' in the same folder as the
## original file.

def convert(filename):

    data = []
    x_axis = []
    pattern = "\d*\.*\d+$"
    try:
        with open(filename) as f:

            # Get data from header to use in conversion
            startVds = float(re.search(pattern, f.next().rstrip()).group())
            stopVds = float(re.search(pattern, f.next().rstrip()).group())
            stepSizeVds = float(re.search(pattern, f.next().rstrip()).group())
            pointsPerStep = float(re.search(pattern, f.next().rstrip()).group())
            gateVoltageStart = float(re.search(pattern, f.next().rstrip()).group())
            gateVoltageEnd = float(re.search(pattern, f.next().rstrip()).group())
            gateVoltageStep = float(re.search(pattern, f.next().rstrip()).group())
            NPLC = float(re.search(pattern, f.next().rstrip()).group())
            padding = float(re.search(pattern, f.next().rstrip()).group())
            lbl = f.next().rstrip().split(',')

            # Store actual data
            for line in f:
                data.append([float(num) for num in line.rstrip().split(',')])

            # Calculate empty steps and amount of datapoints
            n = math.ceil(((stopVds - startVds) / stepSizeVds)) + padding + 1
            N = ((gateVoltageEnd - gateVoltageStart) / gateVoltageStep) + 1 if gateVoltageStep > 0 else 1

            # Put data into np array, makes operations easier
            data = np.transpose(np.array(data))
            # Reshape data to correct format
            current = data[2].reshape(-1, 1).reshape((N, n))[::, :-padding:]
            x_axis = data[1][:n - padding:]
            header = ["Vgate %.2f" % (vg) for vg in data[0][::n]]

        # Change to transposed form to save in filename
        x_axis = np.transpose(x_axis)
        current = np.transpose(current)

        newFile = filename + "_EDITED.csv"
        f = open(newFile, "w")
        f.close()
        with open(newFile, 'a') as fN:
            # Write header
            fN.write("Vds, ")
            for h in header:
                fN.write(h + ",")
            fN.write("\n")
            # Write data line by line
            for dataLine in np.hstack((x_axis[:, None], current)):
                for point in dataLine:
                    fN.write(str(point) + ",")

                fN.write("\n")

        print "DONE"

    except:
        print "Incorrect file format detected, conitnue..."

        
mypath = getcwd()
files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for i in range(0, len(files)):
    if files[i] == sys.argv[0]:
        continue
    convert(files[i])
