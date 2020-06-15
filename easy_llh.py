# -*- coding: utf-8 -*-
"""
# Kristine m. Larson
removed station input
"""
import sys
import numpy as np
import math
import gps as g
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("x", help="X coordinate (m) ", type=float)
parser.add_argument("y", help="Y coordinate (m) ", type=float)
parser.add_argument("z", help="Z coordinate (m) ", type=float)
#parser.add_argument("station", help="station ", type=str)
args = parser.parse_args()
#station = args.station
x=args.x; y=args.y; z=args.z
xyz = [x, y, z] 
# calculate llh in degrees (and meters)
lat,lon,h = g.xyz2llhd(xyz)
print("Lat Lon Ht (deg deg m) %12.7f %12.7f %9.3f " % (lat, lon, h) )

