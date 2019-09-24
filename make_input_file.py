#
# author: kristine larson
# purpose: help set up input file needed for gnssIR_lomb.py

import argparse
import os

# user inputs the observation file information
parser = argparse.ArgumentParser()
# required arguments
parser.add_argument("station", help="station", type=str)
parser.add_argument("lat", help="latitude", type=float)
parser.add_argument("long", help="longitude", type=float)
parser.add_argument("height", help="ellipsoidal height", type=float)
# these are the optional inputs 
parser.add_argument("-e1", "--e1", default=None, type=int, help="lower limit elevation angle")
parser.add_argument("-e2", "--e2", default=None, type=int, help="upper limit elevation angle")
parser.add_argument("-h1", "--h1", default=None, type=float, help="lower limit reflector height (m)")
parser.add_argument("-h2", "--h2", default=None, type=float, help="upper limit reflector height (m)")
parser.add_argument("-nr1", "--nr1", default=None, type=float, help="lower limit noise region for QC(m)")
parser.add_argument("-nr2", "--nr2", default=None, type=float, help="upper limit noise region for QC(m)")
args = parser.parse_args()
#
# rename the user inputs as variables
#
station = args.station
Lat = args.lat
Long = args.long
Height = args.height

# polynomial order for DC component
pvorder = 4
# precision of periodogram (m).  You can go smaller, but it makes the code slower and usually overkill
prec = 0.01
# this is a QC thing - gets rid of small arcs
ediff=2

# defaults for RH restrictions
h1=0.5
h2=6.0
if (args.h1 != None):
    h1 = args.h1
if (args.h2 != None):
    h2 = args.h2

# default elevation angles
e1=5
e2=25
if (args.e1 != None):
    e1 = args.e1
if (args.e2 != None):
    e2 = args.e2
# the default noise region will the same as the RH exclusion area for now
nr1=h1 
nr2=h2
if (args.nr1 != None):
    nr1 = args.nr1
if (args.nr2 != None):
    nr2 = args.nr2

xdir = os.environ['REFL_CODE']
outputdir  = xdir + '/input' 
if not os.path.isdir(outputdir):
    subprocess.call(['mkdir',outputdir])

outputfile = outputdir + '/' + station

print('opening:', outputfile)
f=open(outputfile,'w+')
line1='# comment lines start with a #'
line2='# inputs to lomb scargle code'
line3='# lat long (degrees) ellipsoidal ht (in meters)'
f.write("{0:60s} \n".format(line1))
f.write("{0:60s} \n".format(line2))
f.write("{0:60s} \n".format(line3))
f.write("{0:10.4f} {1:10.4f} {2:8.3f} \n".format(Lat, Long, Height ))

line3a='# elevation angle min and max (for the periodogram) and elevation limits for the DC removal. Both in degrees'
f.write("{0:60s} \n".format(line3a))
# elmin elmax and optionally emin/emax for polyfit
f.write("{0:7.1f} {1:7.1f} {2:7.1f} {3:7.1f} \n".format(e1,e2,5,30))


line4 ='# azimuth ranges to be used, i.e. from 0 to 45, 45 to 90 and so on.  you can edit by hand when you know which ones to use'
line5 =' 0 45 45 90 90 135  135 180 180 225 225 270 270 315 315 360'
f.write("{0:60s} \n".format(line4))
f.write("{0:60s} \n".format(line5))

line6 = '# frequencies and required amplitudes - beware - it will vary with elevation angles and frequencies...'
line7 = '# 1 is GPS L1, 2 is GPS L2, 5 is GPS L5, 101 is Glonass L1, 102 is Glonass L2'
line8 = '# 201, 205, 206, 208 are the Galileo frequencies, 30* are for Beidou'
line9 = '1 8 2 8'
f.write("{0:60s} \n".format(line6))
f.write("{0:60s} \n".format(line7))
f.write("{0:60s} \n".format(line8))
f.write("{0:60s} \n".format(line9))

line10= '# default polynomial value, periodogram precision(meters), minH(m), maxH(m), ediff (QC), Noise region (meters) used for QC'
f.write("{0:60s} \n".format(line10))

f.write("{0:3.0f} {1:7.2f} {2:7.1f} {3:7.1f} {4:5.1f} {5:7.1f} {6:7.1f} \n".format(pvorder,prec,h1,h2,ediff,nr1,nr2))

f.close()
