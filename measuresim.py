import time, sys
import os.path

from PyQt4.QtCore  import *
from PyQt4.QtGui import *

from PyQt4 import QtGui
#from PyQt4.QtCore import Qt

from SignalRunner import SignalRunner
from SignalPulse import SignalPulse
from SignalSpectrum import SignalSpectrum
from MainWindow import Ui_MainWindow

TYPE_PULSE = 1
TYPE_SPECTRUM = 2

setupio = [
    {'type': TYPE_PULSE, 'port': 20, 'rate': 300, 'name': 'Detector A, Golden Sample', 'ratename': 'rate1'},
    {'type': TYPE_PULSE, 'port': 21, 'rate': 450, 'name': 'Detector B, Golden Sample', 'ratename': 'rate2'},
    {'type': TYPE_PULSE, 'port': 19, 'rate': 300, 'name': 'Detector A, Correct Item', 'ratename': 'rate3'},
    {'type': TYPE_PULSE, 'port': 26, 'rate': 450, 'name': 'Detector B, Correct Item', 'ratename': 'rate4'},
    {'type': TYPE_PULSE, 'port': 16, 'rate': 400, 'name': 'Detector A, Failing Item', 'ratename': 'rate5'},
    {'type': TYPE_PULSE, 'port': 13, 'rate': 800, 'name': 'Detector B, Failing Item', 'ratename': 'rate6'},
    {'type': TYPE_SPECTRUM, 'filename': 'na22.dat', 'triggerport': 12, 'rate': 400, 'name': 'Spectrum', 'ratename': 'spectrumrate'}
]

SPECTRA_PATH = os.path.dirname(os.path.realpath(__file__)) + "/spectra/"

print(SPECTRA_PATH)

class SimulationUi(QtGui.QMainWindow):
    'PyQt interface'
 
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
#        super(SimulationUi, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        

 
        self.simulThread = QThread()
        self.simulThread.start()
 
        self.simulRunner = SignalRunner()
        self.simulRunner.moveToThread(self.simulThread)
        self.simulRunner.stepIncreased.connect(self.ui.spectrumstat.setPlainText)
 
        # call stop on simulRunner from this (main) thread on click
        self.ui.stop.clicked.connect(lambda: self.simulRunner.stop())
        self.ui.run.clicked.connect(self.simulRunner.runBackground)

        self.ui.rate1.valueChanged.connect(self.test)
        self.ui.rate2.valueChanged.connect(self.test)
        self.ui.rate3.valueChanged.connect(self.test)
        self.ui.rate4.valueChanged.connect(self.test)
        self.ui.rate5.valueChanged.connect(self.test)
        self.ui.rate6.valueChanged.connect(self.test)
        self.ui.spectrumrate.valueChanged.connect(self.test)

        self.list = []
        for i in range(len(setupio)):
            if(setupio[i]['type'] == TYPE_PULSE):
                tmp = SignalPulse(setupio[i]['port'], setupio[i]['rate'])
                self.list.extend([tmp])
            if(setupio[i]['type'] == TYPE_SPECTRUM):
                tmp = SignalSpectrum(setupio[i]['filename'], setupio[i]['triggerport'], setupio[i]['rate'])
                self.list.extend([tmp])
        self.signalsToRunner()

    def test(self):
        sender = self.sender()
        foundidx = -1
        for i in range(len(setupio)):
            if(sender.objectName() == setupio[i]['ratename']):
                foundidx = i
        if(foundidx != -1):
            self.list[foundidx].setRate(sender.value())
        
    def signalsToRunner(self):
        self.simulRunner.setSignals(self.list)

    def setRate(self, idx, rate):
        if(idx >= 0 and idx < len(self.list)):
            self.list[idx].setRate(rate)

    def setSpectrum(filename):
       self.signals[0].setSpectrum(filename)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    simul = SimulationUi()
    simul.show()
    sys.exit(app.exec_())
