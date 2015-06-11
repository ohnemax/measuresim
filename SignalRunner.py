from PyQt4.QtCore import *
from time import sleep
from time import time

import RPi.GPIO as GPIO

from SignalPulse import SignalPulse

class SignalRunner(QObject):
    'Object managing the simulation'
 
    disableButtons = pyqtSignal(bool, name = 'disableButtons')
    pressRun = pyqtSignal(bool, name = 'pressRun')
    checkRates = pyqtSignal(int, name = 'checkRates')
    checkSpectrum = pyqtSignal(int, name = 'checkSpectrum')
    endRun = pyqtSignal(float, name = 'endRun')

    def __init__(self):
        super(SignalRunner, self).__init__()
        self._step = 0
        self._isRunning = True
        self._maxSteps = 10000
        self.timing = time()
        self.timetocheck = 10

    def setSignals(self, signals):
        self.signals = signals
       
    def runBackground(self):
        GPIO.setmode(GPIO.BCM)

        self.disableButtons.emit(True)
        self.pressRun.emit(True)

        for i in range(len(self.signals)):
            self.signals[i].gpioinit()
            self.signals[i].nextNow()

        # reset
        if not self._isRunning:
            self._isRunning = True
            self._step = 0

        self.starttime = time()
        self.nextRateCheck = time() + self.timetocheck

        while self._isRunning == True:
            curtime = time()
            if(self.nextRateCheck < curtime):
                self.checkRates.emit(self.timetocheck)
                self.checkSpectrum.emit(curtime - self.starttime)
                self.nextRateCheck += self.timetocheck
            for i in range(len(self.signals)):
                if(self.signals[i].nextping < curtime):
                   self.signals[i].execute()
                   self.signals[i].getNext()
 
 
    def stop(self):
        self.disableButtons.emit(False)
        self.pressRun.emit(False)
        self.endRun.emit(self.timetocheck - (self.nextRateCheck - time()))

        self._isRunning = False
