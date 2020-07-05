import argparse
import numpy as np
import os
import subprocess

import check_gnss as cgps
import gps as g

# user inputs the observation file information
parser = argparse.ArgumentParser()
# required arguments
parser.add_argument("station", help="station", type=str)
parser.add_argument("year", help="year", type=int)
parser.add_argument("doy", help="doy", type=int)
parser.add_argument("snrEnd", help="snr file ending", type=int)
parser.add_argument("goal", help="which constellations(0,100,200,300)", type=int)
parser.add_argument("dec_rate", help="decimation for RINEX", type=int)
parser.add_argument("sample_rate", help="low or high", type=str)

args = parser.parse_args()

# rename the user inputs as variables
#
station = args.station
year = args.year
doy= args.doy
snrEnd = args.snrEnd
goal = args.goal
dec_rate = args.dec_rate
sample_rate = args.sample_rate

cgps.check_gnss(station, year, doy, snrEnd, goal, dec_rate,sample_rate)


