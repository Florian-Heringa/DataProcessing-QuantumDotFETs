import numpy as np
import matplotlib.pyplot as plt
import sys
import re
from os import listdir, getcwd
from os.path import isfile, join
import matplotlib.cm as cm

class Derivatives:

    def __init__(self, xs, yset):

        # [first_derivative, second_derivative]
        self.derivatives = [None, None]
        self.derivatives[0] = self.Derivative(xs, yset)
        self.derivatives[1] = self.Derivative(xs, self.derivatives[0])

    def Derivative(self, xs, yset):

        tmp = []
        for ys in yset:
            dy = np.zeros(ys.shape, np.float)
            dy[0:-1] = np.diff(ys)/np.diff(xs)
            dy[-1] = (ys[-1] - ys[-2])/(xs[-1] - xs[-2])
            tmp.append(dy)

        return tmp

class Data:

    ## Initialisation
    def __init__(self, filename, typeMeas, description=""):

        self.filename = filename
        self.description = description
        self.typeMeas = typeMeas
        self.fit = None
        self.derivatives = None
        if typeMeas == "Vds":
            self.toDataVds()
        elif typeMeas == "Vgate":
            self.toDataGate()
        elif typeMeas == "time":
            self.toTimeData()

    def __str__(self):
        return "%s-type: %s" % (self.typeMeas, self.description)

    def toTimeData(self):

        with open(self.filename) as f:

            header = f.next().rstrip().split(',')
            data = []

            for line in f:
                data.append([float(num) for num in line.rstrip().split(',')])

        self.header = header[2]
        data = np.transpose(np.array(data))
        start_time = data[0, 0]
        self.x_axis = [t - start_time for t in data[0]]
        self.data = [data[2]]

        print len(self.data)
        print len(self.x_axis)

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
        self.data = data[2].reshape(-1, 1).reshape((N, n))[::, :-self.padding - 1:]
        self.x_axis = data[1][:n - self.padding - 1:]
        self.header = ["Vgate %.2f" % (vg) for vg in data[0][::n]]

    ## Read data file and convert to array
    def toDataGate(self):

        data = []

        with open(self.filename) as f:
            self.header = f.next().rstrip().split(',')

            # Put each line into an array
            for line in f:
                data.append([float(i) for i in line.rstrip().split(',')])
        # Way data is saved requires a transpose of data array for easier use
        data = np.transpose(np.array(data)).tolist()
        # First row is Vgate values
        self.x_axis = data[0]
        # Rest is DS current values
        self.data = data[1:]

    def fitData(self):

        self.fit = []
        self.slope = []
        for y in self.data:
            z = np.polyfit(self.x_axis, y, 1)
            self.slope.append(z[0])
            fit = np.poly1d(z)
            self.fit.append(fit(self.x_axis))

    def derivative(self):

        self.derivatives = Derivatives(self.x_axis, self.data)

    def plotData(self, derivative=False, fit=False):

        fig, ax = plt.subplots(1, 1)

        colors = cm.rainbow(np.linspace(0, 1, len(self.data)))

        if self.fit and fit:
            for y, y_fit, slope, lbl, c in zip(self.data, self.fit, self.slope, self.header, colors):
                ax.plot(self.x_axis, y, label="%s\nSlope: %.4E" % (lbl, slope), color=c)
                ax.plot(self.x_axis, y_fit, color=c, linestyle='--')
        elif self.derivatives and derivative:
            for y, y_x, y_xx, lbl, c in zip(self.data, self.derivatives.derivatives[0], self.derivatives.derivatives[1], self.header, colors):
                ax.plot(self.x_axis, y, label="%s" % (lbl), color=c)
                ax.plot(self.x_axis, y_x, color=c, linestyle='--', label="%s\_x"%(lbl))
                ax.plot(self.x_axis, y_xx, color=c, linestyle='-.', label="%s\_xx"%(lbl))
        else:
            for y, lbl in zip(self.data, self.header):
                ax.plot(self.x_axis, y, label=lbl)

        ax.set_xlim([min(self.x_axis), max(self.x_axis)])

        if self.typeMeas == "Vgate":
            ax.set_xlabel("Gate Voltage (V)")
            ax.set_ylabel("Drain-Source Current (A)")
        if self.typeMeas == "Vds":
            ax.set_xlabel("Drain-Source Voltage (V)")
            ax.set_ylabel("Drain-Source Current (A)")
        if self.typeMeas == "time":
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("Drain-Source Current (A)")
        ax.ticklabel_format(style="sci", axis="y", scilimits=(0,0), useMathText=True)
        ax.legend(framealpha=.5, loc="lower left", bbox_to_anchor=(1, 0))
        ax.set_title(self.typeMeas)
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

def ls(data_arr):
    for i in range(len(data_arr)):
        print "%d -- %s" % (i, data_arr[i])
    print ""

def listAvail():

    mypath = getcwd() + "\\Data"
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    for i in range(0, len(files)):
        print "%d : %s" % (i, files[i])

def doThis(data_arr, cmd):

    ls(data_arr)
    try:
        index = input("Which data do you want to %s:" % (cmd))
        data_selection = data_arr[index]
        action(data_selection, cmd)
    except Exception as e:
        print "Something went wrong: %s" % e

def action(data_selection, cmd):

    if cmd == 'fit':
        data_selection.fitData()
        data_selection.plotData(fit=True)
    elif cmd == 'derive':
        data_selection.derivative()
        data_selection.plotData(derivative=True)
    elif cmd == 'plot':
        data_selection.plotData()

def addData():

    acceptedData = ['gate', 'sweep', 'time']
    global data_arr

    # findPath returns None when incorrectly specified
    path = findPath()
    if path == None:
        print "Incorrect path"
        return

    measType = raw_input("Type of data: ")
    # Catch wrong typename of data
    if measType not in acceptedData:
        print "Not an accepted data type"
        return

    dscr = raw_input("Enter a description: ")

    if measType == 'gate':
        data_arr.append(Data(path, "Vgate", description=dscr))
    elif measType == 'sweep':
        data_arr.append(Data(path, "Vds", description=dscr))
    elif measType == 'time':
        data_arr.append(Data(path, "time", description=dscr))
    else:
        print "Unknown command"
        return
###############################################

data_arr = []

def main():

    global data_arr

    print "Quantum Dot Fet Data Visualisation script"
    print "(Enter 'h' for help)"
    inp = raw_input("Enter Command: ")

    while inp != 'q':

        if inp == 'h':
            help()
        elif inp == 'avail':
            listAvail()
        elif inp == 'derive' or inp == 'fit' or inp == 'plot':
            doThis(data_arr, inp)
        elif inp == 'add':
            addData()
        elif inp == 'ls':
            ls(data_arr)
        else:
            print "Unknown command"

        print ""
        inp = raw_input("Enter Command:")

    print "Exiting..."

def help():
    print "Commands:"
    print "\th - This help text"
    print "\tadd - Enter data, enter 'gate' for Vgate sweep data and\n\t\t'ds' for Vds sweep data"
    print "\tls - List all currently loaded data"
    print "\tavail - List all available data in the ~\Data directory"
    print "\tplot - Plot data saved at chosen index"
    print "\tderive - Calculate and plot first and second derivatives of data and plot"
    print "\tfit - fit all data given in a selected data object"

main()

## TODO: plot with parameters from repl. Interactive mpl env.
##       Choose directory where files are stored within ~\Data
