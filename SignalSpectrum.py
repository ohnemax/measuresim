from time import sleep
from time import time
from numpy.random import uniform as u
from math import log as ln
import os.path
import numpy

from Adafruit_MCP4725 import MCP4725

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)


class SignalSpectrum():
    def __init__(self, filename, triggerport, rate=1):
        self.triggerport = triggerport
        self.rate = rate
        self.filename = filename
        self.nextping = time()
        self.logchannels = [0] * 4096
        GPIO.setup(self.triggerport, GPIO.OUT)
        GPIO.output(self.triggerport, False)
        self.dac = MCP4725(0x60)
        self.dac.setVoltage(0)


    def execute(self):
        newu = u()
        idx = 0
        for idx in range(4096):
            if(newu < self.cumudata[idx]):
                break
        self.logchannels[idx] += 1
        self.dacsignal(idx)
        
    def dacsignal(self, channel):
        self.setDac(channel)
        self.trigger()
        self.setDac(0)

    def setDac(self, channel):
        if(channel >= 0 and channel < 4096):
            self.dac.setVoltage(channel)
        else:
            print("ERROR: wrong channel for DAC output")
            print("Channel was %d") % channel
            exit(1)


    def getNext(self):
       self.nextping += -ln(u()) / self.rate

    def nextNow(self):
        self.nextping = time()

    def setRate(self, rate):
        self.rate = rate
#        print("set trigger rate to %d") % rate

    def trigger(self):
        GPIO.output(self.triggerport, True)
        sleep(0.0001)
        GPIO.output(self.triggerport, False)
        
    def setSpectrum(self, filename):
        self.filename = filename


    def loadSpectrum(self):
        # check if file exist
        fullfile = self.filename
        if(not os.path.isfile(fullfile)):
            print "could not load file"
            # ADD ERROR MESSAGE HERE
            exit(1)

        # load file lines into array
        data = numpy.loadtxt(fullfile)
        self.datacount = len(data)
        if(self.datacount > 4096):
            print "ERROR: Spectrum is too long!"
            exit(1)
        
        # expand to 4096
        self.multiplechannels = 4096 // self.datacount
        count = 0
        self.outputchannels = [0] * (self.datacount * self.multiplechannels)
        for i in range(self.datacount):
            for j in range(self.multiplechannels):
                self.outputchannels[count] = data[i]
                count += 1
        self.totalcounts = sum(self.outputchannels)
        self.cumudata = [0] * (self.datacount * self.multiplechannels)
        last = 0;
        for index, value in enumerate(self.outputchannels):
            self.cumudata[index] = self.outputchannels[index] / self.totalcounts + last;
            last = self.cumudata[index]

    