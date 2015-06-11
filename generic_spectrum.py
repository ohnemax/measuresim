#!/usr/bin/python


from math import log as ln
from math import factorial as fac
from math import exp as exp

peak = 200

#generate a generic spectrum

for i in range(1024):
    p = peak ** i / fac(i) * exp(-peak)
    out = p * 10000 + 102 - i / 10
    print int(out)