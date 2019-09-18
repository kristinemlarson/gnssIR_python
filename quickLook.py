# -*- coding: utf-8 -*-
"""
author: kristine m. larson
wrapper for the quickLook function code
# 
"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
# i do not think these are used
#import warnings
#warnings.filterwarnings("ignore")
#import cProfile

import gps as g
import argparse
import scipy.interpolate
import scipy.signal
import read_snr_files as snr
import quickLook_function as quick

# my internal codes for the refraction correction, which are based on
# codes from TU Vienna. currently turned off for quickLook
# import refraction as refr
# i think this is only used for MJD, so turned off in quickLook
# import datetime


#
# user inputs the observation file information
parser = argparse.ArgumentParser()
# required arguments
parser.add_argument("station", help="station", type=str)
parser.add_argument("year", help="year", type=int)
parser.add_argument("doy", help="doy", type=int)
parser.add_argument("snrEnd", help="snrEnding", type=int)
# these are the addons (not required)
parser.add_argument("-fr", "--fr", default=None, type=int, help="try -fr 1 for GPS L1 only, or -fr 101 for Glonass L1")
parser.add_argument("-amp", "--amp", default=None, type=float, help="try -amp 10 for minimum spectral amplitude")
parser.add_argument("-e1", "--e1", default=None, type=int, help="lower limit elevation angle")
parser.add_argument("-e2", "--e2", default=None, type=int, help="upper limit elevation angle")
parser.add_argument("-h1", "--h1", default=None, type=float, help="lower limit reflector height (m)")
parser.add_argument("-h2", "--h2", default=None, type=float, help="upper limit reflector height (m)")
parser.add_argument("-sat", "--sat", default=None, type=float, help="satellite")
args = parser.parse_args()
#
# rename the user inputs as variables
#
station = args.station
year = args.year
doy= args.doy
snr_type = args.snrEnd
plt_screen = 1 # always have a plot come to screen

InputFromScreen = True


# peak to noise value is one way of defining that significance (not the only way).
# I often use 3, but here I am using much less stringent requirement
PkNoise = 2.7

# get the month and day and the modified julian day, 
# currently using fake date since we are not using
# time varying refraction yet
#d = g.doy2ymd(year,doy); month = d.month; day = d.day
#dmjd, fracS = g.mjd(year,month,day,0,0,0)


# set some reasonable default values for LSP (Reflector Height calculation). 
# some of these can be overriden
# at the command line
freqs = [1] # default is to do L1 
pele = [5, 30] # polynomial fit limits 
Hlimits = [0.5, 6] # RH limits in meters - this is typical for a snow setup
elval = [5,25] # elevation angle limits for estimating LSP
NReg = [0.5, 6] # noise region - again, this is for typical snow setup
# look at the four geographic quadrants to get started - these are azimuth angles
azval = [0, 90, 90,180, 180, 270, 270, 360]
reqAmp = [8] # this is arbitrary  - but generally true for L1 instruments
twoDays = False

# if user inputs these, then it overrides the default
if (args.e1 != None):
    elval[0] = args.e1
    if elval[0] < 5:
        print('have to change the polynomial limits because you went below 5 degrees')
        pele[0] = elval[0] 
if (args.e2 != None):
    elval[1] = args.e2
# elevation angle limit values for the Lomb Scargle
e1 = elval[0]; e2 = elval[1]
print('Start out using elevation angles: ', e1, ' and ', e2)


if (args.h1 != None):
    Hlimits[0] = args.h1
if (args.h2 != None):
    Hlimits[1] = args.h2
if (args.sat != None):
    sat = int(args.sat)
else:
    sat = None
# minimum and maximum LSP limits
minH = Hlimits[0]; maxH = Hlimits[1]


# this is for when you want to run the code with just a single frequency, i.e. input at the console
# rather than using the input restrictions
if args.fr != None:
    freqs = [args.fr] 
if args.amp != None:
    reqAmp[0] = args.amp
print('Using reflector height limits (m) : ', Hlimits[0], ' and ', Hlimits[1], ' and Ampl:', reqAmp[0])

# maybe here call a function

f=freqs[0]
webapp = False
print('calling the function that does everything')
quick.quickLook_function(station, year, doy, snr_type,f,e1,e2,minH,maxH,reqAmp,pele,webapp,sat)

