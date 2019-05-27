# -*- coding: utf-8 -*-
"""
this is my effort to write code that will pick up a RINEX file from unavco
if station is auto, assume the person wants the nav file
Kristine m. Larson
2018 August 20
Updated: April 3, 2019
May 22, 2019 - observation downloads go to $REFL_CODE/Files
should change so that day of year allowed
changed os.system commands to subprocess
"""
import argparse
import subprocess
import sys
import os

import gps as g

parser = argparse.ArgumentParser()
parser.add_argument("station", help="station name ", type=str)
parser.add_argument("year", help="year ", type=int)
parser.add_argument("month", help="month ", type=int)
parser.add_argument("day", help="day ", type=int)
parser.add_argument("-rate", default=None, type=str, help="low/high (not required)")

args = parser.parse_args()
station = args.station
year = args.year
month = args.month
day = args.day

if args.rate == None:
    rate = 'low'
else:
    rate = 'high'

# where Rinex observation files will be stored
xdir = os.environ['REFL_CODE'] + '/Files/'
if not os.path.exists(xdir):
    print('make an output directory')
    os.makedirs(xdir)

rinexfile,rinexfiled = g.rinex_name(station, year, month, day)
#rexist = os.path.isfile(rinexfile) == True
#status = subprocess.call(['ls','-l',xdir])
#status = subprocess.call(['ls','-l',xdir])



# compute filename to find out if file exists
doy,cdoy,cyyyy,cyy = g.ymd2doy(year, month, day )
if station == 'auto':
    fnameo = station + cdoy + '0.' + cyy + 'n'
else:
    fnameo = station + cdoy + '0.' + cyy + 'o'

print('Seeking ', fnameo)

try:
    # this is the way Radon said to do it
    f1=open(fnameo,'r')
    f1.close()
    print('rinex file already exists')
except:
    print('rinex file does not exist - will try to pick up ')
    if station == 'auto':
        # this will be stored in the appropriate area
        g.getnavfile(year, month, day)
    else:
        if rate == 'low':
            g.rinex_unavco(station, year, month, day)
        else:
            g.rinex_unavco_highrate(station, year, month, day)

if os.path.exists(rinexfile):
    print('retrieved the rinex file - moving to Files directory')
    status = subprocess.call(['mv',rinexfile,xdir])
