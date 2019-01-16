# -*- coding: utf-8 -*-
"""
# This python code reads a snr file (created by one of my RINEX translators) 
# and computes Lomb Scargle Periodograms (LSP) 
# so that a reflector height (RH) can be estimated.
# It currently makes a plot if requested.
# Kristine M. Larson
#
# This is not currently optimized for tide gauges - the RH dot correction 
# and refraction correction still needs to be added.
# 
# Please note that you need to set a REFL_CODE environment variable to
# define the location of your input files
#
# I have set this up so that you can run it in the background (no plots and all
# frequencies from a list of instructions), or just one frequency 
# (or one satellite) and look at the data/periodograms
"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

import gps as g
import argparse
import scipy.interpolate
import scipy.signal
# set an environment variable for where you are keeping your LSP
# instructions and input files 
# CHANGE FOR YOUR MACHINE
os.environ['REFL_CODE'] = '/Users/kristine/Documents/Research'
# for some applications, allowing tracks that cross midnite is fine (such as snow)
# but for tides, these is illegal. For now this is allowed.
allowMidniteCross = True
#
# user inputs the observation file information
parser = argparse.ArgumentParser()
parser.add_argument("station", help="station name", type=str)
parser.add_argument("year", help="year", type=int)
parser.add_argument("doy", help="doy", type=int)
parser.add_argument("snrEnd", help="snrEnding", type=int)
parser.add_argument("plt", help="plot", type=int)
parser.add_argument("-fr", "--onefreq", default=None, type=int, help="try -fr 1 for GPS L1 only, or -fr 101 for Glonass L1")
parser.add_argument("-amp", "--ampl", default=None, type=float, help="try -amp 10 for minimum spectral amplitude")
parser.add_argument("-sat", "--sat", default=None, type=int, help="allow individual satellite")
parser.add_argument("-pltname", "--pltname", default='None', type=str, help="allow individual satellite")
args = parser.parse_args()
#
# rename the user inputs as variables
#
station = args.station
year = args.year
onesat = args.sat
doy= args.doy
snr_type = args.snrEnd
plt_screen = args.plt
pltname = args.pltname

# You should not use the peak periodogram value unless it is significant. Using a 
# peak to noise value is one way of defining that significance (not the only way).
# I often use 3, but here I am using much less stringent requirement
PkNoise = 2
# this defines the minimum number of points in an arc.  This depends entirely on the sampling
# rate for the receiver, so you should not assume this value is relevant to your case.
minNumPts = 20 

if args.onefreq == None:
    InputFromScreen = False
else:
    InputFromScreen = True
    
# find the observation file name
obsfile = g.define_filename(station,year,doy,snr_type)

# retrieve the inputs needed to window the data and compute Lomb Scargle Periodograms 
lat,long,ht,elval,azval,freqs,reqAmp,polyV,desiredP,Hlimits,ediff,pele,NReg = g.read_inputs(station) 

# You can have peaks in two regions, and you may only be interested in one them.
# You should refine the region you care about here.
# minimum and maximum LSP limits
minH = Hlimits[0]; maxH = Hlimits[1]

# elevation angle limit values for the Lomb Scargle
e1 = elval[0]; e2 = elval[1]

# number of azimuth regions
naz = int(len(azval)/2)
print('number of azimuth pairs',naz)

# read the SNR file
try:
    sat,ele,azi,t,edot,s1,s2,s5,s6,s7,s8,med_edot,snrE = g.read_snr_file(obsfile)
    print('successfully read the SNR file')
    g.print_file_stats(ele,sat,s1,s2,s5,s6,s7,s8,e1,e2) 
except:
    print('SNR file does not exist, or there is a problem reading it.  exiting ...')
    print(obsfile)
    sys.exit()
ct = 0
# good arcs saved to a plain text file, rejected arcs to local file. Open those file names
fout,frej = g.open_outputfile(station,year,doy) 
#
# If you want to make a plot
if (plt_screen == 1):
    plt.figure()

# this is for when you want to run the code with just a single frequency, i.e. input at the console
# rather than using the input restrictions
if InputFromScreen:
    reqAmp[0] = 10
    freqs = [args.onefreq] 
    if (args.ampl == None):
        reqAmp[0] = 10
    else:
        reqAmp[0] = args.ampl
#
#  main loop
#
# for a given list of frequencies
total_arcs = 0
for f in freqs:
    rj = 0
    gj = 0
    print('**** looking at frequency ', f, ' ReqAmp', reqAmp[ct])
#   get the list of satellites for this frequency
    if onesat == None:
        satlist = g.find_satlist(f,snrE)
    else:
        satlist = [onesat]
# for a given satellite
    for satNu in satlist:
# and azimuth range
        print('>> Sat number ', satNu)
        for a in range(naz):
            az1 = azval[(a*2)] ; az2 = azval[(a*2 + 1)]
# window the data
            x,y,Nv,cf,UTCtime,avgAzim,avgEdot,Edot2= g.window_data(s1,s2,s5,s6,s7,s8,sat,ele,azi,t,edot,f,az1,az2,e1,e2,satNu,polyV,pele) 
#           this is a kluge for snr files that have non edot values in column 5
            if (med_edot > 0.01):
                avgEdot = 0.0
            if Nv > minNumPts:
#                print('>>> azimuths & NumValues ', az1, ' ',  Nv)
                maxF, maxAmp, eminObs, emaxObs,riseSet,px,pz= g.strip_compute(x,y,cf,maxH,desiredP,polyV,minH) 
                nij =   pz[(px > NReg[0]) & (px < NReg[1])]
                Noise = 0
                if (len(nij) > 0):
                    Noise = np.mean(nij)
#                    print(len(nij),NReg[0], NReg[1],eminObs,emaxObs,maxAmp/Noise)
#                   I  will write out the Edot2 value, as Edot is provided not in all snr files
                if (eminObs < (e1 + ediff)) & (emaxObs > (e2 - ediff)) & (maxAmp > reqAmp[ct]) & (maxAmp/Noise > PkNoise):
                    fout.write(" {0:4.0f} {1:3.0f} {2:6.3f} {3:3.0f} {4:6.3f} {5:6.2f} {6:6.2f} {7:6.2f} \
{8:6.2f} {9:4.0f} {10:3.0f} {11:2.0f} {12:8.5f} {13:6.2f} \n".format(year,doy,maxF,satNu, UTCtime,\
                       avgAzim,maxAmp,eminObs,emaxObs,Nv, f,riseSet, Edot2, maxAmp/Noise))
                    gj +=1
                    if (plt_screen == 1):
                        plt.subplot(211); plt.plot(x,y)
                        plt.subplot(212); plt.plot(px,pz)
                else:
                    frej.write(" {0:4.0f} {1:3.0f} {2:6.3f} {3:3.0f} {4:6.3f} {5:6.2f} {6:6.2f} {7:6.2f} \
{8:6.2f} {9:4.0f} {10:3.0f} {11:2.0f} {12:8.5f} {13:6.2f} \n".format(year,doy,maxF,satNu, UTCtime,\
                       avgAzim,maxAmp,eminObs,emaxObs,Nv, f,riseSet, Edot2,maxAmp/Noise))
                    rj +=1
    print('     good arcs:', gj, ' rejected arcs:', rj)
    ct += 1
    total_arcs = gj + total_arcs
# close the output files
fout.close() ; frej.close()
# plot to the screen
g.quick_plot(plt_screen, total_arcs,station,pltname)
