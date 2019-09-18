# -*- coding: utf-8 -*-
"""
function is used to translate rinex into snr file format
These files are then used by gnss_lomb.py
author: kristine larson
date: 20 march 2019
"""
import argparse
import datetime
import os
import sys

import numpy as np

import gps as g

# set an environment variable for where you are keeping your LSP
# instructions and input files 
# DEFINE REFL_CODE on your system 

#WARNING - THIS CODE ASSUMES IF YOU USE HATANAKA RINEX
# FILES, YOU NEED THE APPROPRIATE EXECUTABLE in $EXEC
#WARNING - If you want to decimate, you need to install teqc in $EXEC 
 
#
# user inputs the observation file information
parser = argparse.ArgumentParser()
parser.add_argument("station", help="station name", type=str)
parser.add_argument("year", help="year", type=int)
parser.add_argument("doy1", help="start day of year", type=int)
parser.add_argument("doy2", help="end day of year", type=int)
parser.add_argument("snrEnd", help="snr ending", type=str)
parser.add_argument("orbType", help="orbit type, nav or sp3", type=str)
parser.add_argument("-rate", default=None, type=int, help="sampling rate(not req)")
parser.add_argument("-dec", default=0, type=int, help="decimate (seconds) requires teqc be installed")
args = parser.parse_args()
#
# rename the user inputs as variables
#
station = args.station
year = args.year
doy1= args.doy1
doy2= args.doy2
snrt = args.snrEnd
orbtype = args.orbType
if args.rate == None:
    rate = 'low'
else:
    rate = 'high'
# decimation rate
dec_rate = args.dec
#
ann = g.make_nav_dirs(year)

doy_list = list(range(doy1, doy2+1))

# for each day in the doy list
for doy in doy_list:
    g.quick_rinex_snr(year, doy, station, snrt, orbtype,rate, dec_rate)
