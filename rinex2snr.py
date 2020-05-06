# -*- coding: utf-8 -*-
"""
function is used to translate rinex into snr file format
These files are then used by gnss_lomb.py
author: kristine larson
date: 20 march 2019
19oct20 changed inputs to put doy_end as an optional input rather than requiring it
20apr15 tried to streamline data pick up, eventually add compression
"""
import argparse
import datetime
import os
import sys
import subprocess

import numpy as np

import gps as g

# set an environment variable for where you are keeping your LSP
# instructions and input files 
# DEFINE REFL_CODE on your system 

#WARNING - THIS CODE ASSUMES IF YOU USE HATANAKA RINEX
# FILES, YOU NEED THE APPROPRIATE EXECUTABLE in $EXEC
#WARNING - If you want to decimate, you need to install teqc in $EXEC 
 
#
print('If your station name is 9 characters long, this code assumes you plan to use a RINEX 3 file')
# user inputs the observation file information
parser = argparse.ArgumentParser()
parser.add_argument("station", help="station name", type=str)
parser.add_argument("year", help="year", type=int)
parser.add_argument("doy1", help="start day of year", type=int)
parser.add_argument("snrEnd", help="snr ending", type=str)
parser.add_argument("orbType", help="orbit type, nav or sp3", type=str)
parser.add_argument("-rate", default=None, type=int, help="sampling rate(not req)")
parser.add_argument("-dec", default=0, type=int, help="decimate (seconds) requires teqc be installed")
parser.add_argument("-doy_end", default=None, help="end day of year", type=int)
parser.add_argument("-year_end", default=None, help="end year", type=int)
parser.add_argument("-nolook", default='False', type=str, help="True means only use RINEX files on local machine")

args = parser.parse_args()
#
# rename the user inputs as variables
#
station = args.station
NS = len(station)
if (NS == 4):
    print('assume RINEX 2.11')
    version = 2
    station = station.lower()
elif (NS == 9):
    print('assume RINEX 3')
    version = 3
    station9ch = station.upper()
    station = station[0:4].lower()
else:
    print('illegal input - Station must have 4 or 9 characters')
    sys.exit()
year = args.year
doy1= args.doy1
snrt = args.snrEnd
orbtype = args.orbType
# if true ony use local RINEX files, which speeds up analysis of local datasets
# but for some goofy reason i make it a string and have to set boolean later
nolook = args.nolook
if nolook == 'True':
    nol = True
    #print('will only use RINEX on local machine')
else:
    nol = False
    #print('will look for RINEX on local machine and external archives')

if args.rate == None:
    rate = 'low'
else:
    rate = 'high'

if args.doy_end == None:
    doy2 = doy1
else:
    doy2 = args.doy_end

year1=year
if args.year_end == None:
    year2 = year 
else:
    year2 = args.year_end

# decimation rate
dec_rate = args.dec
#
ann = g.make_nav_dirs(year)

doy_list = list(range(doy1, doy2+1))
year_list = list(range(year1, year2+1))
# loop thru years and days 
for year in year_list:
    for doy in doy_list:
        cdoy = '{:03d}'.format(doy) ; cyy = '{:02d}'.format(year-2000)
        # rinex name
        # first, check to see if the SNR file exists
        snre = g.snr_exist(station,year,doy,snrt)
        if snre:
            print('snr file already exists')
        else:
            r = station + cdoy + '0.' + cyy + 'o'
            print(year, doy, ' will try to find/make from : ', r)
            if nol:
                if os.path.exists(r):
                    print('rinex file exists locally')
                    g.quick_rinex_snrC(year, doy, station, snrt, orbtype,rate, dec_rate )
            else:
                print('will look locally and externally')
                if version == 3:
                    print('rinex 3 search with orbtype ', orbtype)
                    srate = 30 # rate supported by CDDIS 
                    rinex2exists, rinex3name = g.cddis_rinex3(station9ch, year, doy,srate,orbtype)
                    if not rinex2exists:
                        # try again - unavco has 15 sec I believe
                        rinex2exists, rinex3name = g.unavco_rinex3(station9ch, year, doy,15,orbtype)
                    subprocess.call(['rm', rinex3name]) # remove rinex3 file
                    if rinex2exists:
                        g.quick_rinex_snrC(year, doy, station, snrt, orbtype,rate, dec_rate)
                    else:
                        print('rinex file does not exist for ', year, doy)
                else:
                    print('rinex 2.11 search')
                    g.quick_rinex_snrC(year, doy, station, snrt, orbtype,rate, dec_rate)

