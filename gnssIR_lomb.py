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
# 
# 19mar01, added refraction and MJD to output
# 19mar02, added multiple days
# 19mar13, snow (one day only) vs water levels (midnite crossing corrected by using
# the day before)
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
# you can also set this in your .bashrc
#os.environ['REFL_CODE'] = '/Users/kristine/Documents/Research'
xdir = os.environ['REFL_CODE']
 
# for some applications, allowing tracks that cross midnite is fine (such as snow)
# but for tides, these is illegal. 
allowMidniteCross = False

# eventually we will use something else but this restricts arcs to one hour
# units of minutes
delTmax = 60
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
parser.add_argument("-pltname", "--pltname", default='None', type=str, help="plot name")
parser.add_argument("-doy_end", "--doy_end", default=None, type=int, help="doy end")
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
#
if args.doy_end == None:
    doy_end = doy
else:
    doy_end = args.doy_end

if args.onefreq == None:
    InputFromScreen = False
else:
    InputFromScreen = True

# Setting some defaults
# use the refraction correction
RefractionCorrection = True

# You should not use the peak periodogram value unless it is significant. Using a 
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


# retrieve the inputs needed to window the data and compute Lomb Scargle Periodograms 
lat,long,ht,elval,azval,freqs,reqAmp,polyV,desiredP,Hlimits,ediff,pele,NReg = g.read_inputs(station) 

# You can have peaks in two regions, and you may only be interested in one of them.
# You should refine the region you care about here.
# minimum and maximum LSP limits
minH = Hlimits[0]; maxH = Hlimits[1]

# elevation angle limit values for the Lomb Scargle
e1 = elval[0]; e2 = elval[1]

# number of azimuth regions
naz = int(len(azval)/2)
print('number of azimuth pairs:',naz)

# this is for when you want to run the code with just a single frequency, i.e. input at the console
# rather than using the input restrictions
if InputFromScreen:
#    reqAmp[0] = 10
    freqs = [args.onefreq] 
    if (args.ampl == None):
        reqAmp[0] = 10
    else:
        reqAmp[0] = args.ampl

# use the returned lat,long,ht to compute a refraction correction profile
# 
refr.readWrite_gpt2_1w(xdir, station, lat, long)
# time varying is set to no for now (it = 1)
it = 1
dlat = lat*np.pi/180; dlong = long*np.pi/180
p,T,dT,Tm,e,ah,aw,la,undu = refr.gpt2_1w(station, dmjd,dlat,dlong,ht,it)
print("Pressure {0:8.2f} Temperature {1:6.1f} \n".format(p,T))


doy_list = list(range(doy, doy_end+1))

# for each day in the doy list
for doy in doy_list:
# find the observation file name and try to read it
    obsfile = g.define_filename(station,year,doy,snr_type)
    obsfile2 = g.define_filename_prevday(station,year,doy,snr_type)
#   define two datasets - one from one day snr file and the other with 24 hours that
#   have three hours from before midnite and first 21 hours on the given day
#
    twoDays = False
    allGood,sat,ele,azi,t,edot,s1,s2,s5,s6,s7,s8,snrE = snr.read_snr_multiday(obsfile,obsfile2,twoDays)
#
#   twoDays = True
#   21:00-23:59 day before plus 0-21:00 day of
# comment out for now - need to correct the elevation angles eventually
#   allGoodP,Psat,Pele,Pazi,Pt,Pedot,Ps1,Ps2,Ps5,Ps6,Ps7,Ps8,PsnrE = snr.read_snr_multiday(obsfile,obsfile2,twoDays)
    if (allGood == 1):
        print('successfully read the first SNR file')
        if RefractionCorrection:
            print('<<<<<< apply refraction correction >>>>>>') 
            corrE = refr.corr_el_angles(ele, p,T)
            ele = corrE
#           g.print_file_stats(ele,sat,s1,s2,s5,s6,s7,s8,e1,e2) 
        ct = 0
# good arcs saved to a plain text file, rejected arcs to local file. Open those file names
        fout,frej = g.open_outputfile(station,year,doy) 
# If you want to make a plot
        g.open_plot(plt_screen)

#  main loop
# for a given list of frequencies

        total_arcs = 0
        for f in freqs:
            rj = 0
            gj = 0
            print('**** looking at frequency ', f, ' ReqAmp', reqAmp[ct], ' doy ', doy)
#   get the list of satellites for this frequency
            if onesat == None:
                satlist = g.find_satlist(f,snrE)
            else:
                satlist = [onesat]
# for a given satellite
            for satNu in satlist:
                print('>> Sat number ', satNu)
# and azimuth range
                for a in range(naz):
                    az1 = azval[(a*2)] ; az2 = azval[(a*2 + 1)]
# window the data
                    x,y,Nv,cf,UTCtime,avgAzim,avgEdot,Edot2,delT= g.window_data(s1,s2,s5,s6,s7,s8,sat,ele,azi,t,edot,f,az1,az2,e1,e2,satNu,polyV,pele) 
#           this is a kluge for snr files that have non edot values in column 5
                    MJD = g.getMJD(year,month,day, UTCtime)
                    if Nv > minNumPts:
                        maxF, maxAmp, eminObs, emaxObs,riseSet,px,pz= g.strip_compute(x,y,cf,maxH,desiredP,polyV,minH) 
                        nij =   pz[(px > NReg[0]) & (px < NReg[1])]
                        Noise = 0
                        if (len(nij) > 0):
                            Noise = np.mean(nij)
#                    print(len(nij),NReg[0], NReg[1],eminObs,emaxObs,maxAmp/Noise)
#                   I  will write out the Edot2 value, as Edot is not provided in all snr files
#
#  this is the main QC statement
                        if (delT < delTmax) & (eminObs < (e1 + ediff)) & (emaxObs > (e2 - ediff)) & (maxAmp > reqAmp[ct]) & (maxAmp/Noise > PkNoise):
                            fout.write(" {0:4.0f} {1:3.0f} {2:6.3f} {3:3.0f} {4:6.3f} {5:6.2f} {6:6.2f} {7:6.2f} \
{8:6.2f} {9:4.0f} {10:3.0f} {11:2.0f} {12:8.5f} {13:6.2f} {14:7.2f} {15:12.6f} \n".format(year,doy,maxF,satNu, UTCtime,\
                       avgAzim,maxAmp,eminObs,emaxObs,Nv, f,riseSet, Edot2, maxAmp/Noise, delT, MJD))
                            gj +=1
                            g.update_plot(plt_screen,x,y,px,pz)
                        else:
                            frej.write(" {0:4.0f} {1:3.0f} {2:6.3f} {3:3.0f} {4:6.3f} {5:6.2f} {6:6.2f} {7:6.2f} \
{8:6.2f} {9:4.0f} {10:3.0f} {11:2.0f} {12:8.5f} {13:6.2f} {14:7.2f} {15:12.6f} \n".format(year,doy,maxF,satNu, UTCtime,\
                       avgAzim,maxAmp,eminObs,emaxObs,Nv, f,riseSet, Edot2,maxAmp/Noise,delT, MJD))
                            rj +=1
            print('     good arcs:', gj, ' rejected arcs:', rj)
            ct += 1
            total_arcs = gj + total_arcs
# close the output files
        fout.close() ; frej.close()
# plot to the screen
        g.quick_plot(plt_screen, total_arcs,station,pltname)
