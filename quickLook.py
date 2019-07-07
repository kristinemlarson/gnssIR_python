# -*- coding: utf-8 -*-
"""
# This python code reads a snr file (created by one of my RINEX translators) 
# and computes Lomb Scargle Periodograms (LSP) 
# so that a reflector height (RH) can be estimated.
# It currently makes a plot if requested.
# Kristine M. Larson
#
# This is not currently optimized for tide gauges - the RH dot correction 
# is not implemented.

# Please note that you need to set a REFL_CODE environment variable to
# define the location of your input (and output) files
#
# I have set this up so that you can run it in the background (no plots and all
# frequencies from a list of instructions), or just one frequency 
# (or one satellite) and look at the data/periodograms
# 
# 19mar01, added refraction and MJD to output
# 19mar02, added multiple days
# 19mar13, snow (one day only) vs water levels (midnite crossing corrected by using
# the day before)
# 19apr20, changed location of compressed rinex executable
# 19jun28, change result file naming convetion to include snr file type
# toggle for overwriting LSP results (default will be ot overwrite, but
# for cdron jobs, nice not to)
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



twoDays = False

# to avoid having to do all the indenting over again
obsfile = g.define_quick_filename(station,year,doy,snr_type)
if os.path.isfile(obsfile):
    print('>>>> WOOHOOO - THE FILE EXISTS ',obsfile)
else:
    print('try in your directories')
    obsfile,obsfileCmp = g.define_filename(station,year,doy,snr_type)
    if not os.path.isfile(obsfile):
        print('>>>> Sigh, - SNR the file does not exist ',obsfile)
        print('because I am a nice person I will try to pick up a RINEX file ')
        print('and translate it for you. This will be GPS only.')
        rate = 'low'; dec_rate = 0
        g.quick_rinex_snr(year, doy, station, snr_type, 'nav',rate, dec_rate)
        if os.path.isfile(obsfile):
            print('now the SNR file now exists')
        else:
            print('the RINEX file did not exist at UNAVCO, so no SNR file.')
#
allGood,sat,ele,azi,t,edot,s1,s2,s5,s6,s7,s8,snrE = snr.read_snr_multiday(obsfile,obsfile,twoDays)
#
# only one frequency for this code
ct = 0
f=freqs[0]
if (allGood == 1):
    print('successfully read the SNR file')
    minEdataset = np.min(ele)
    print('min elevation angle for this dataset ', minEdataset)
    if minEdataset > (e1+0.5):
        print('It looks like the receiver had an elevation mask, so reset minE to that apparent mask')
        e1 = minEdataset
    total_arcs = 0
    rj = 0
    gj = 0
    # open the figure
    if four_in_one:
        plt.figure()
    for a in range(naz):
        if not (four_in_one):
            g.open_plot(plt_screen)
        az1 = azval[(a*2)] ; az2 = azval[(a*2 + 1)]
        satlist = g.find_satlist(f,snrE)
        for satNu in satlist:
            x,y,Nv,cf,UTCtime,avgAzim,avgEdot,Edot2,delT= g.window_data(s1,s2,s5,s6,s7,s8,sat,ele,azi,t,edot,f,az1,az2,e1,e2,satNu,polyV,pele) 
            MJD = g.getMJD(year,month,day, UTCtime)
            if Nv > minNumPts:
                maxF, maxAmp, eminObs, emaxObs,riseSet,px,pz= g.strip_compute(x,y,cf,maxH,desiredP,polyV,minH) 
                nij =   pz[(px > NReg[0]) & (px < NReg[1])]
                Noise = 0
                if (len(nij) > 0):
                    Noise = np.mean(nij)
                    iAzim = int(avgAzim)
                    if (delT < delTmax) & (eminObs < (e1 + ediff)) & (emaxObs > (e2 - ediff)) & (maxAmp > reqAmp[ct]) & (maxAmp/Noise > PkNoise):
                        print('SUCCESS Azimuth {0:3.0f} RH {1:.2f} m, Sat {2:2.0f} Freq {3:.0f} Amp {4:3.1f} '.format( iAzim,maxF,satNu,f,maxAmp))
                        if (four_in_one):
                            ijk = 220 + a + 1
                            plt.subplot(ijk)
                            plt.plot(px,pz)
                        else:
                             g.update_plot(plt_screen,x,y,px,pz)
                        gj +=1
                    else:
                        rj +=1
        if not (four_in_one):
            g.update_quick_plot(station + ':' + titles[a],f)
        else:
            plt.title(titles[a])
    plt.show()
    if four_in_one:
        pltname = 'temp.png'
        plt.savefig(pltname)
else: 
    print('some kind of problem with SNR file, so I am exiting the code politely.')
#            plt.xlabel('reflector height (m)'); plt.title('SNR periodogram')
#            print('     good arcs:', gj, ' rejected arcs:', rj)
#            plt.subplot(211)
#            plt.xlabel('elev Angles (deg)')
#            plt.title(titles[a-1] + ' SNR Data and Frequency L' + str(f))
#            plt.subplot(212)
