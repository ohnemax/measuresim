from time import sleep
from time import time
from numpy.random import uniform as u
from math import log as ln

class SignalPulse():
    def __init__(self, port, rate=1, high=True):
        self.high = high
        self.port = port
        self.rate = rate
        self.nextping = time()
        self.count = 0
        print(self.port)

    def execute(self):
        self.pulse()
        
    def pulse(self):
        self.count += 1
        #add pulse

    def resetCount(self):
        self.count = 0

    def getNext(self):
       self.nextping += -ln(u()) / self.rate

    def nextNow(self):
        self.nextping = time()


    def setRate(self, rate):
        self.rate = rate
        print("set rate to %d") % rate

    