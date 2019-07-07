# -*- coding: utf-8 -*-
"""
trying to make a wrapper for quickLook.py
LOL!
# 
"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import cProfile

import gps as g
import argparse
import scipy.interpolate
import scipy.signal
import read_snr_files as snr
import quickLook_function as quick

# my internal codes for the refraction correction, which are based on
# codes from TU Vienna
import refraction as refr
import datetime

# set an environment variable for where you are keeping your LSP
# instructions and input files 
# CHANGE FOR YOUR MACHINE
# you can also set this in your .bashrc, which is what i am doing now
# os.environ['REFL_CODE'] = '/Users/kristine/Documents/Research'
xdir = os.environ['REFL_CODE']
 

four_in_one = True
#four_in_one = False
# eventually we will use something else but this restricts arcs to one hour
# units are in minutes
delTmax = 70
#
# user inputs the observation file information
parser = argparse.ArgumentParser()
# required arguments
parser.add_argument("station", help="station", type=str)
parser.add_argument("year", help="year", type=int)
parser.add_argument("doy", help="doy", type=int)
parser.add_argument("snrEnd", help="snrEnding", type=int)
# these are the addons (not required)
parser.add_argument("-fr", "--onefreq", default=None, type=int, help="try -fr 1 for GPS L1 only, or -fr 101 for Glonass L1")
parser.add_argument("-amp", "--ampl", default=None, type=float, help="try -amp 10 for minimum spectral amplitude")
parser.add_argument("-e1", "--e1", default=None, type=int, help="lower limit elevation angle")
parser.add_argument("-e2", "--e2", default=None, type=int, help="upper limit elevation angle")
parser.add_argument("-h1", "--h1", default=None, type=float, help="lower limit reflector height (m)")
parser.add_argument("-h2", "--h2", default=None, type=float, help="upper limit reflector height (m)")
args = parser.parse_args()
#
# rename the user inputs as variables
#
station = args.station
year = args.year
doy= args.doy
snr_type = args.snrEnd
plt_screen = 1 # always have a plot come to screen
# four reflection quadrants - use these geographical names
titles = ['Northeast', 'Southeast', 'Southwest', 'Northwest']

# in case you want to analyze multiple days of data


if args.onefreq == None:
    InputFromScreen = False
else:
    InputFromScreen = True

# Setting some defaults
# use the refraction correction
RefractionCorrection = False
irefr = 0

# this option is not used in quickLook
extension = ''

# peak to noise value is one way of defining that significance (not the only way).
# I often use 3, but here I am using much less stringent requirement
PkNoise = 2
# this defines the minimum number of points in an arc.  This depends entirely on the sampling
# rate for the receiver, so you should not assume this value is relevant to your case.
minNumPts = 20 



# get the month and day and the modified julian day, 
# currently using fake date since we are not using
# time varying refraction yet
d = g.doy2ymd(year,doy); month = d.month; day = d.day
dmjd, fracS = g.mjd(year,month,day,0,0,0)


# set some reasonable default values for LSP (Reflector Height calculation). 
# some of these can be overriden
# at the command line
polyV = 4 # polynomial order for the direct signal
desiredP = 0.01 # 1 cm precision
ediff = 2
freqs = [1] # default is to do L1 
pele = [5, 30] # elevation angle limits for removing the polynomial 
Hlimits = [0.5, 10] # RH limits in meters
elval = [5,25] # elevation angle limits
NReg = [0.5, 6]
# look at four quadrants to get started
azval = [0, 90, 90,180, 180, 270, 270, 360]
reqAmp = [10] # this is arbitrary 
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
print('start out using elevation angles: ', e1, ' and ', e2)


if (args.h1 != None):
    Hlimits[0] = args.h1
if (args.h2 != None):
    Hlimits[1] = args.h2
# minimum and maximum LSP limits
minH = Hlimits[0]; maxH = Hlimits[1]
print('using reflector height limits (m) : ', Hlimits[0], ' and ', Hlimits[1])


# number of azimuth regions from the standard data input file (came out of read_inputs)
naz = int(len(azval)/2)
print('number of azimuth pairs:',naz)
# in case you want to look at a restricted azimuth range from the command line 
# this can probably be removed

# this is for when you want to run the code with just a single frequency, i.e. input at the console
# rather than using the input restrictions
if InputFromScreen:
#    reqAmp[0] = 10
    freqs = [args.onefreq] 
    if (args.ampl == None):
        reqAmp[0] = 10
    else:
        reqAmp[0] = args.ampl

# maybe here call a function

f=freqs[0]
quick.quickLook_function(station, year, doy, snr_type,f,e1,e2,minH,maxH,azval,reqAmp)

