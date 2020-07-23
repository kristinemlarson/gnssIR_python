# -*- coding: utf-8 -*-
"""
This python code reads a snr file (created by one of my RINEX translators) 
and computes Lomb Scargle Periodograms (LSP) 
so that a reflector height (RH) can be estimated.
It currently makes a plot if requested.
Kristine M. Larson
#
This is not currently optimized for tide gauges - the RH dot correction 
is not implemented.

Please note that you need to set a REFL_CODE environment variable to
define the location of your input (and output) files
#
I have set this up so that you can run it in the background (no plots and all
frequencies from a list of instructions), or just one frequency 
(or one satellite) and look at the data/periodograms
# 
19mar01, added refraction and MJD to output
19mar02, added multiple days
19mar13, snow (one day only) vs water levels (midnite crossing corrected by using
the day before)
19apr20, changed location of compressed rinex executable
19jun28, change result file naming convetion to include snr file type
toggle for overwriting LSP results (default will be overwritten, but
for cron jobs, nice not to)
19sep13, code will attempt to make an SNR file for you if one does not exist. 
It will be GPS only. i.e. uses nav file
2019sep22 added error checking on required inputs
added subprocess import
2020mar01 added seekRinex logical. Originally my thinking was to have 
everymake their snr files using a separate utility (rinex2snr.py).  But after
numerous comments, I added the feature that it would at least try to make it for you
if it could find a RINEX file. The problem with this feature is that of course 
it keeps looking for RINEX files even when they do not exist and will never exist.
so I have a logical called seekRinex.  It is set to False. If you want this 
code to look for RINEX files and make snr files for you, by all means change it to True.
#
20jul15 do not allow the "peak" to be at either edge of your spectrum - which I had not
ported from my previous version

"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import cProfile
import subprocess

import gps as g
import argparse
import scipy.interpolate
import scipy.signal
import read_snr_files as snr

# my internal codes for the refraction correction, which are based on
# codes from TU Vienna
import refraction as refr
import datetime

seekRinex =False 
# pick up the environment variable for where you are keeping your LSP data
xdir = os.environ['REFL_CODE']
# make sure the input directory exists, if not, create it
outputdir  = xdir + '/input'
if not os.path.isdir(outputdir):
    subprocess.call(['mkdir',outputdir])
else:
    print('The directory for analysis instruction exists.')
 
# if you want the SNR files to be xv compressed after using them.
# this is now an optional input
wantCompression = False
#wantCompression = True 

# for some applications, allowing tracks that cross midnite is fine (such as snow)
# but for tides, these is illegal. 
allowMidniteCross = False

# eventually we will use something else but this restricts arcs to two hours
# units are in minutes
delTmax = 120
#
# user inputs the observation file information
parser = argparse.ArgumentParser()
# required arguments
parser.add_argument("station", help="station", type=str)
parser.add_argument("year", help="year", type=int)
parser.add_argument("doy", help="doy", type=int)
parser.add_argument("snrEnd", help="snr file ending", type=int)
parser.add_argument("plt", help="plot to screen? 1 is yes, 0 is no", type=int)



# these are the addons (not required)
parser.add_argument("-fr", "--onefreq", default=None, type=int, help="try -fr 1 for GPS L1 only, or -fr 101 for Glonass L1")
parser.add_argument("-amp", "--ampl", default=None, type=float, help="try -amp 10 for minimum spectral amplitude")
parser.add_argument("-sat", "--sat", default=None, type=int, help="allow individual satellite")
parser.add_argument("-pltname", "--pltname", default='None', type=str, help="plot name")
parser.add_argument("-doy_end", "--doy_end", default=None, type=int, help="doy end")
parser.add_argument("-year_end", "--year_end", default=None, type=int, help="year end")
parser.add_argument("-azim1", "--azim1", default=None, type=int, help="lower limit azimuth")
parser.add_argument("-azim2", "--azim2", default=None, type=int, help="upper limit azimuth")
parser.add_argument("-nooverwrite", "--nooverwrite", default=None, type=int, help="use any integer to not overwrite")
parser.add_argument("-extension", "--extension", default=None, type=str, help="extension for result file, useful for testing strategies")
parser.add_argument("-compress", "--compress", default=None, type=str, help="xz compress SNR files after use")
parser.add_argument("-screenstats", "--screenstats", default=None, type=str, help="some stats printed to screen(default is True)")
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

exitS = g.check_inputs(station,year,doy,snr_type)
if exitS:
    sys.exit()

# though I would think not many people would do this ... 
if (args.compress != None):
    if args.compress == 'True':
        wantCompression = True
    else:
        wantCompression = False

# make sure directories are there for orbits
ann = g.make_nav_dirs(year)

screenstats = True
if args.screenstats == 'False':
    screenstats = False

# in case you want to analyze multiple days of data
if args.doy_end == None:
    doy_end = doy
else:
    doy_end = args.doy_end

# in case you want to analyze multiple years of data
if args.year_end == None:
    year_end = year
else:
    year_end = args.year_end

# this makes no sense
if args.onefreq == None:
    InputFromScreen = False
else:
    InputFromScreen = True

# Setting some defaults
# use the refraction correction
RefractionCorrection = True
#RefractionCorrection = False
if RefractionCorrection:
    irefr = 1
else:
    irefr = 0

# allow people to have an extension to the output file name so they can run different analysis strategies
# this is undocumented and only for Kristine at the moment
if args.extension == None:
    extension = ''
else:
    extension = args.extension

# make directories for the LSP results 
g.result_directories(station,year,extension)

# default will be to overwrite
if args.nooverwrite == None:
    overwriteResults = True
    print('results will be overwritten')
else:
    overwriteResults = False
    print('results will not be overwritten')


# this defines the minimum number of points in an arc.  This depends entirely on the sampling
# rate for the receiver, so you should not assume this value is relevant to your case.
minNumPts = 20 


# get the month and day and the modified julian day, 
# currently using fake date since we are not using
# time varying refraction yet
d = g.doy2ymd(year,doy); month = d.month; day = d.day
dmjd, fracS = g.mjd(year,month,day,0,0,0)


# retrieve the inputs needed to window the data and compute Lomb Scargle Periodograms 
# changed long to lon
lat,lon, ht,elval,azval,freqs,reqAmp,polyV,desiredP,Hlimits,ediff,pele,NReg,PkNoise = g.read_inputs(station) 

# You should not use the peak periodogram value unless it is significant. Using a 
# peak to noise value is one way of defining that significance (not the only way).
# I often use 3, but for now it is set to 2.7. For snow, I would suggest 3.5
if PkNoise == 0:
    PkNoise = 2.7
    print('You have not set a peak 2 noise ratio in the input file for station ', station)
    print('Default value being used: ', PkNoise)

# You can have peaks in two regions, and you may only be interested in one of them.
# You can refine the region you care about here.
# minimum and maximum LSP limits
minH = Hlimits[0]; maxH = Hlimits[1]

# elevation angle limit values for the Lomb Scargle
e1 = elval[0]; e2 = elval[1]

# number of azimuth regions from the standard data input file (came out of read_inputs)
naz = int(len(azval)/2)
print('number of azimuth pairs:',naz)
# in case you want to look at a restricted azimuth range from the command line 
setA = 0
if args.azim1 == None:
    azim1 = 0
else:
    setA = 1
    azim1 = args.azim1

if args.azim2 == None:
    azim2 = 360
else:
    azim2 = args.azim2
    setA = setA + 1

if (setA == 2):
    naz = 1; azval[0] = azim1; azval[1] = azim2

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
# this is only done once per site 
if RefractionCorrection:
    refr.readWrite_gpt2_1w(xdir, station, lat, lon)
# time varying is set to no for now (it = 1)
    it = 1
    dlat = lat*np.pi/180; dlong = lon*np.pi/180
    p,T,dT,Tm,e,ah,aw,la,undu = refr.gpt2_1w(station, dmjd,dlat,dlong,ht,it)
    print("Pressure {0:8.2f} Temperature {1:6.1f} \n".format(p,T))


# only doing one day at a time for now - but have started defining the needed inputs for using it
twoDays = False
obsfile2= '' # dummy value for name of file for the day before, when we get to that

year_list = list(range(year, year_end+1))
doy_list = list(range(doy, doy_end+1))
# for each day in the doy list
for year in year_list:
    for doy in doy_list:
        fname, resultExist = g.LSPresult_name(station,year,doy,extension) 
        if (resultExist):
            print('Results already exist on disk')
# find the observation file name and try to read it
        if (overwriteResults == False) & (resultExist == True):
            allGood = 0
            print('>>>>> The result file exists for this day and you have selected the do not overwrite option')
        else:
            print('go ahead and access SNR data - first define SNR filename')
            #obsfile,obsfileCmp = g.define_filename(station,year,doy,snr_type)
            obsfile, obsfileCmp, snre = g.define_and_xz_snr(station,year,doy,snr_type) 
            # turning this off for now
            # print('SNR filename for previous day')
            # obsfile2, obsfile2Cmp, snre2 = g.define_and_xz_snr(station,year,doy-1,snr_type) 
        #  compressed function is pretty silly in the day of large disks
            if (not snre) and (not seekRinex):
                print('SNR file does not exist and you have set the seekRinex variable to False')
                print('Use rinex2snr.py to make SNR files')
            if (not snre) and seekRinex:
                print('SNR file does not exist. I will try to make a GPS only file.')
                rate = 'low'; dec_rate = 0; orbtype = 'nav'
                g.quick_rinex_snrC(year, doy, station, snr_type, orbtype,rate, dec_rate)

#   define two datasets - one from one day snr file and the other with 24 hours that
#   have three hours from before midnite and first 21 hours on the given day
            allGood,sat,ele,azi,t,edot,s1,s2,s5,s6,s7,s8,snrE = snr.read_snr_multiday(obsfile,obsfile2,twoDays)
#   if desired , compress files here
            snr.compress_snr_files(wantCompression, obsfile, obsfile2,twoDays) 
#   twoDays = True  - for now using only one day at a time
        if (allGood == 1):
            if RefractionCorrection:
                print('<<<<<< apply refraction correction >>>>>>') 
                corrE = refr.corr_el_angles(ele, p,T)
                ele = corrE
            ct = 0
# good arcs saved to a plain text file, rejected arcs to local file. Open those file names
            fout,frej = g.open_outputfile(station,year,doy,extension) 
#  main loop
# for a given list of frequencies
            total_arcs = 0
            for f in freqs:
       # If you want to make a plot for each frequency?
                g.open_plot(plt_screen)
                rj = 0
                gj = 0
                print('**** looking at frequency ', f, ' ReqAmp', reqAmp[ct], ' doy ', doy, ct)
#   get the list of satellites for this frequency
                if onesat == None:
                    satlist = g.find_satlist(f,snrE)
                else:
                    satlist = [onesat]
# for a given satellite
                for satNu in satlist:
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
#  this is the main QC statement
                            iAzim = int(avgAzim)
                            okPk = True
                            if abs(maxF - minH) < 0.10: #  peak too close to min value
                                # even better check would be to compare frequencies ... :wq
                                okPk = False
                                print('found a peak too close to the edge')
                            if okPk & (delT < delTmax) & (eminObs < (e1 + ediff)) & (emaxObs > (e2 - ediff)) & (maxAmp > reqAmp[ct]) & (maxAmp/Noise > PkNoise):
                                fout.write(" {0:4.0f} {1:3.0f} {2:6.3f} {3:3.0f} {4:6.3f} {5:6.2f} {6:6.2f} {7:6.2f} {8:6.2f} {9:4.0f} {10:3.0f} {11:2.0f} {12:8.5f} {13:6.2f} {14:7.2f} {15:12.6f} {16:1.0f} \n".format(year,doy,maxF,satNu, UTCtime, avgAzim,maxAmp,eminObs,emaxObs,Nv, f,riseSet, Edot2, maxAmp/Noise, delT, MJD,irefr))
                                if screenstats:
                                    print('SUCCESS Azimuth {0:3.0f} Sat {1:3.0f} RH {2:7.3f} m PkNoise {3:4.1f} AMp {4:4.1f} Fr{5:3.0f}'.format(iAzim,satNu,maxF,maxAmp/Noise,maxAmp, f))
                                gj +=1
                                g.update_plot(plt_screen,x,y,px,pz)
                            else:
                                if eminObs > 15:
                                    if screenstats:
                                        print('useless tiny arc')
                                else:
                                    if screenstats:
                                        print('failed QC for Azimuth {0:.1f} Satellite {1:2.0f} '.format( iAzim,satNu))
                                        g.write_QC_fails(delT,delTmax,eminObs,emaxObs,e1,e2,ediff,maxAmp, Noise,PkNoise,reqAmp[ct])
                                    rj +=1
                print('     good arcs:', gj, ' rejected arcs:', rj)
                ct += 1
                total_arcs = gj + total_arcs
# close the output files
                g.quick_plot(plt_screen, total_arcs,station,pltname,f)
            fout.close() ; frej.close()
#        g.quick_plot(plt_screen, total_arcs,station,pltname,f)
# plot to the screen
