import time, sys
import os.path
from os import listdir

from PyQt4.QtCore  import *
from PyQt4.QtGui import *

from PyQt4 import QtGui
#from PyQt4.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

from SignalRunner import SignalRunner
from SignalPulse import SignalPulse
from SignalSpectrum import SignalSpectrum
from MainWindow import Ui_MainWindow

TYPE_PULSE = 1
TYPE_SPECTRUM = 2

setupio = [
    {'type': TYPE_PULSE, 'port': 19, 'rate': 300, 'name': 'Channel 1', 'ratename': 'rate1', 'testname': 'test1'},
    {'type': TYPE_PULSE, 'port': 16, 'rate': 300, 'name': 'Channel 2', 'ratename': 'rate2', 'testname': 'test2'},
    {'type': TYPE_PULSE, 'port': 26, 'rate': 300, 'name': 'Channel 3', 'ratename': 'rate3', 'testname': 'test3'},
    {'type': TYPE_PULSE, 'port': 21, 'rate': 300, 'name': 'Channel 4', 'ratename': 'rate4', 'testname': 'test4'},
    {'type': TYPE_PULSE, 'port': 20, 'rate': 300, 'name': 'Channel 5', 'ratename': 'rate5', 'testname': 'test5'},
    {'type': TYPE_PULSE, 'port': 13, 'rate': 300, 'name': 'Channel 6', 'ratename': 'rate6', 'testname': 'test6'},
    {'type': TYPE_SPECTRUM, 'filename': 'generic.dat', 'triggerport': 12, 'rate': 100, 'name': 'Spectrum', 'ratename': 'spectrumrate'}
]

SPECTRA_PATH = os.path.dirname(os.path.realpath(__file__)) + "/spectra/"
SPECTRA_ENDING = ".dat"
print(SPECTRA_PATH)

class SimulationUi(QtGui.QMainWindow):
    'PyQt interface'
 
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
#        super(SimulationUi, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ui.plotspace.addWidget(self.canvas)

 
        self.simulThread = QThread()
        self.simulThread.start()
 
        self.simulRunner = SignalRunner()
        self.simulRunner.moveToThread(self.simulThread)

        self.simulRunner.disableButtons.connect(self.disableButtons)
        self.simulRunner.pressRun.connect(self.ui.run.setDown)
        self.simulRunner.checkRates.connect(self.updatePulseStats)
        self.simulRunner.checkSpectrum.connect(self.updateSpectrumPlot)
        self.simulRunner.endRun.connect(self.endRun)
 
        # call stop on simulRunner from this (main) thread on click
        self.ui.stop.clicked.connect(lambda: self.simulRunner.stop())
        self.ui.run.clicked.connect(self.simulRunner.runBackground)

        # self.my_button.setDisabled(True)


        self.refreshspectra()
        

        self.list = []
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_PULSE):
                tmp = SignalPulse(setupio[i]['port'], setupio[i]['rate'])
                self.list.extend([tmp])
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                tmp = SignalSpectrum(SPECTRA_PATH + setupio[i]['filename'], setupio[i]['triggerport'], setupio[i]['rate'])
                tmp.loadSpectrum()
                listindex = self.ui.spectrumlist.findText(setupio[i]['filename'])
                if( listindex != -1):
                    self.ui.spectrumlist.setCurrentIndex(listindex)
                self.list.extend([tmp])

        self.updateSpectrumStats()
        self.signalsToRunner()

        self.ui.rate1.valueChanged.connect(self.test)
        self.ui.rate2.valueChanged.connect(self.test)
        self.ui.rate3.valueChanged.connect(self.test)
        self.ui.rate4.valueChanged.connect(self.test)
        self.ui.rate5.valueChanged.connect(self.test)
        self.ui.rate6.valueChanged.connect(self.test)
        self.ui.test1.clicked.connect(self.singlepulse)
        self.ui.test2.clicked.connect(self.singlepulse)
        self.ui.test3.clicked.connect(self.singlepulse)
        self.ui.test4.clicked.connect(self.singlepulse)
        self.ui.test5.clicked.connect(self.singlepulse)
        self.ui.test6.clicked.connect(self.singlepulse)

        self.ui.spectrumrate.valueChanged.connect(self.test)
        self.ui.spectrumlistrefresh.clicked.connect(self.refreshspectra)

        self.ui.spectrumlist.activated.connect(self.setSpectrum)

        self.ui.testtrigger.clicked.connect(self.testtrigger)
        self.ui.spectrumpulse.clicked.connect(self.spectrumpulse)
        self.ui.voltagemax.clicked.connect(self.voltagemax)
        self.ui.voltageoff.clicked.connect(self.voltageoff)



    def test(self):
        sender = self.sender()
        foundidx = -1
        for i in range(len(setupio)):
            if(sender.objectName() == setupio[i]['ratename']):
                foundidx = i
        if(foundidx != -1):
            self.list[foundidx].setRate(sender.value())

    def singlepulse(self):
        sender = self.sender()
        foundidx = -1
        print("singlepulse")
        print('testname' in setupio[1])
        for i in range(len(setupio)):
            if(('testname' in setupio[i]) and sender.objectName() == setupio[i]['testname']):
                foundidx = i
        if(foundidx != -1):
            self.list[foundidx].pulse()
            self.ui.pulsestat.setPlainText("Single pulse on GPIO " + str(self.list[foundidx].port))

    def updateSpectrumPlot(self):
        spectrumidx = -1
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                ax = self.figure.add_subplot(111)
                ax.hold(False)
                self.ui.spectrumline.setText("Emitted spectrum (will be reset when Max=10e5):")
                outputdata = self.list[i].logchannels
                outputdata += [0] * (4096 - len(outputdata))
                print(len(outputdata))
                ax.plot(range(4096), outputdata)
                self.canvas.draw()
        
    def updateSpectrumStats(self):
        spectrumidx = -1
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                spectrumidx = i
        if(spectrumidx >= 0):
            text = "Spectrum Data has " + str(self.list[spectrumidx].datacount) + " channels.\n"
            text += "For each data channel " + str(self.list[spectrumidx].multiplechannels) + " output channels are used.\n"
            text += "Will output on " + str(self.list[spectrumidx].datacount * self.list[spectrumidx].multiplechannels) + " of 4096 channels."
            self.ui.spectrumstat.setPlainText(text)
            ax = self.figure.add_subplot(111)
            ax.hold(False)
            self.ui.spectrumline.setText("Spectrum from file:")
            outputdata = self.list[spectrumidx].outputchannels
            outputdata += [0] * (4096 - len(outputdata))
            print(len(outputdata))
            ax.plot(range(4096), outputdata)
            self.canvas.draw()

    def updatePulseStats(self, time):
        text = ""
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_PULSE):
                text += setupio[i]['name'] + ": " + "{:6.2f}".format(1.0 * self.list[i].count / time) + " 1/s"
                if(i % 2 == 1):
                    text += "\n"
                else:
                    text += "  "
                self.list[i].resetCount()
        self.ui.pulsestat.setPlainText(text)

    def endRun(self, time):
        print(time)
        self.updatePulseStats(time)
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                ax = self.figure.add_subplot(111)
                ax.hold(False)
                self.ui.spectrumline.setText("Emitted spectrum:")
                outputdata = self.list[i].logchannels
                outputdata += [0] * (4096 - len(outputdata))
                print(len(outputdata))
                ax.plot(range(4096), outputdata)
                self.canvas.draw()

    def signalsToRunner(self):
        self.simulRunner.setSignals(self.list)

    def setRate(self, idx, rate):
        if(idx >= 0 and idx < len(self.list)):
            self.list[idx].setRate(rate)

    def setSpectrum(self, text):
        filename = str(self.ui.spectrumlist.currentText())
        filename = os.path.join(SPECTRA_PATH, filename)
        print("spectrum changed")
        print(filename)
#        filename??
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                self.list[i].setSpectrum(filename)
                self.list[i].loadSpectrum()
        self.updateSpectrumStats()


    def refreshspectra(self):
        self.ui.spectrumlist.clear()
        onlyfiles = [ f for f in listdir(SPECTRA_PATH) if (os.path.isfile(os.path.join(SPECTRA_PATH,f)) & f.endswith(SPECTRA_ENDING)) ]
        for file in onlyfiles:
            self.ui.spectrumlist.addItem(file)

    def disableButtons(self, disable):
        self.ui.rate1.setDisabled(disable)
        self.ui.rate2.setDisabled(disable)
        self.ui.rate3.setDisabled(disable)
        self.ui.rate4.setDisabled(disable)
        self.ui.rate5.setDisabled(disable)
        self.ui.rate6.setDisabled(disable)
        self.ui.test1.setDisabled(disable)
        self.ui.test2.setDisabled(disable)
        self.ui.test3.setDisabled(disable)
        self.ui.test4.setDisabled(disable)
        self.ui.test5.setDisabled(disable)
        self.ui.test6.setDisabled(disable)

        self.ui.spectrumrate.setDisabled(disable)
        self.ui.spectrumlistrefresh.setDisabled(disable)
        self.ui.spectrumlist.setDisabled(disable)

        self.ui.voltagemax.setDisabled(disable)
        self.ui.voltageoff.setDisabled(disable)
        self.ui.spectrumpulse.setDisabled(disable)
        self.ui.testtrigger.setDisabled(disable)

    def testtrigger(self):
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                self.list[i].trigger()

    def spectrumpulse(self):
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                self.list[i].dacsignal(4095)

    def voltagemax(self):
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                self.list[i].setDac(4095)

    def voltageoff(self):
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                self.list[i].setDac(0)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    simul = SimulationUi()
    simul.show()
    GPIO.cleanup()
    sys.exit(app.exec_())
