# -*- coding: utf-8 -*-
"""
# can make a lot of snr files
"""
import sys
import os
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import cProfile

import gps as g
import argparse

import datetime

# set an environment variable for where you are keeping your LSP
# instructions and input files 
# CHANGE FOR YOUR MACHINE
# i now define this in my .bashrc file
#os.environ['REFL_CODE'] = '/home/kristine/research'
# not sure this needs to be here
xdir = os.environ['REFL_CODE']
 
#
# user inputs the observation file information
parser = argparse.ArgumentParser()
parser.add_argument("station", help="station name", type=str)
parser.add_argument("year", help="year", type=int)
parser.add_argument("doy1", help="doy1", type=int)
parser.add_argument("doy2", help="doy2", type=int)
parser.add_argument("snrEnd", help="snrEnd", type=str)
args = parser.parse_args()
#
# rename the user inputs as variables
#
station = args.station
year = args.year
doy1= args.doy1
doy2= args.doy2
snrt = args.snrEnd
#
orbtype = 'nav'

doy_list = list(range(doy1, doy2+1))

# for each day in the doy list
for doy in doy_list:
    g.quick_rinex_snr(year, doy, station, snrt, orbtype)
