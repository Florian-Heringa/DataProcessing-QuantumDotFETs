import numpy as np
import matplotlib.pyplot as plt
import sys
import re
from os import listdir, getcwd
from os.path import isfile, join

test = "test"

class Data:

    ## Initialisation
    def __init__(self, filename, typeMeas, description=""):

        self.filename = filename
        self.description = description
        self.typeMeas = typeMeas
        if typeMeas == "Vds":
            self.toDataVds()
        elif typeMeas == "Vgate":
            self.toDataGate()

    def __str__(self):
        return "%s-type: %s" % (self.typeMeas, self.description)

    def toDataVds(self):

        data = []
        pattern = "\d*\.*\d+$"

        with open(self.filename) as f:

            self.startVds = float(re.search(pattern, f.next().rstrip()).group())
            self.stopVds = float(re.search(pattern, f.next().rstrip()).group())
            self.stepSizeVds = float(re.search(pattern, f.next().rstrip()).group())
            self.pointsPerStep = float(re.search(pattern, f.next().rstrip()).group())
            self.gateVoltageStart = float(re.search(pattern, f.next().rstrip()).group())
            self.gateVoltageEnd = float(re.search(pattern, f.next().rstrip()).group())
            self.gateVoltageStep = float(re.search(pattern, f.next().rstrip()).group())
            self.NPLC = float(re.search(pattern, f.next().rstrip()).group())
            self.padding = float(re.search(pattern, f.next().rstrip()).group())
            self.lbl = f.next().rstrip().split(',')

            for line in f:
                data.append([float(num) for num in line.rstrip().split(',')])

            n = ((self.stopVds - self.startVds) / self.stepSizeVds) + self.padding + 1
            N = ((self.gateVoltageEnd - self.gateVoltageStart) / self.gateVoltageStep) + 1

            data = np.transpose(np.array(data))
            # Reshape data to correct format
            self.data = data[2].reshape(-1, 1).reshape((N, n))[::, :-self.padding:]
            self.x_axis = data[1][:n - self.padding:]
            self.header = ["Vgate %.2f" % (vg) for vg in data[0][::n]]

    ## Read data file and convert to array
    def toDataGate(self):

        data = []

        with open(self.filename) as f:
            self.header = f.next().rstrip().split(',')

            for line in f:
                data.append([float(i) for i in line.rstrip().split(',')])

        data = np.transpose(np.array(data)).tolist()
        self.data = data[1:]
        self.x_axis = data[0]

    def plotData(self):

        y_labels = []
        ys = []
        max_y, min_y = 0, sys.maxint

        fig, ax = plt.subplots(1, 1)
        for y, lbl in zip(self.data, self.header):
            ax.plot(self.x_axis, y, label=lbl)

        if self.typeMeas == "Vgate":
            ax.set_xlabel("Gate Voltage (V)")
            ax.set_ylabel("Drain-Source Current (A)")
        if self.typeMeas == "Vds":
            ax.set_xlabel("Drain-Source Voltage (V)")
            ax.set_ylabel("Drain-Source Current (A)")
        ax.ticklabel_format(style="sci", axis="y", scilimits=(0,0), useMathText=True)
        ax.legend(framealpha=.5, loc="lower left", bbox_to_anchor=(1, 0))
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plt.show()

def findPath():

    mypath = getcwd() + "\\Data"
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    for i in range(0, len(files)):
        print "%d : %s" % (i, files[i])

    # Mostly catch EOF errors when just presing enter and check if enterd value
    # is a number
    try:
        f = input("Choose file number to load: ")
        f_int = int(f)
        return "Data\%s" % files[f_int]
    except:
        return None

def main():

    data_arr = []
    acceptedData = ['gate', 'sweep']

    print "Quantum Dot Fet Data Visualisation script"
    print "(Enter 'h' for help)"
    inp = raw_input("Enter Command: ")

    while inp != 'q':

        if inp == 'h':
            help()
        elif inp == 'd':
            measType = raw_input("Type of data: ")

            # Catch wrong typename of data
            if measType not in acceptedData:
                print "Not an accepted data type"
                inp = raw_input("Enter Command: ")
                continue

            path = findPath()
            dscr = raw_input("Enter a description: ")

            # findPath returns None when incorrectly specified
            if path:
                if measType == 'gate':
                    data_arr.append(Data(path, "Vgate", description=dscr))
                elif measType == 'sweep':
                    data_arr.append(Data(path, "Vds", description=dscr))
                else:
                    print "Unknown command"
            else:
                print "Incorrect path"
        elif inp == 'l':
            for i in range(len(data_arr)):
                print "%d -- %s" % (i, data_arr[i])
        elif inp == 'p':
            try:
                pIndex = input("Which data do you want to plot: ")
                pIndex = int(pIndex)
                data_arr[pIndex].plotData()
            except Exception as e:
                print "Something went Wrong : %s" % e
                inp = raw_input("Enter Command: ")
                continue
        else:
            print "Unknown command"

        print ""
        inp = raw_input("Enter Command:")

    print "Exiting..."

def help():
    print "Commands:"
    print "\th - This help text"
    print "\td - Enter data, enter 'gate' for Vgate sweep data and\n\t\t'ds' for Vds sweep data"
    print "\tl - List all currently loaded data"
    print "\tp - Plot data saved at chosen index"

main()
