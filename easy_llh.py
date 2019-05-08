# -*- coding: utf-8 -*-
"""
# this is my effort to write a pseudorange nav solution in python
# Kristine m. Larson
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
parser.add_argument("station", help="station ", type=str)
args = parser.parse_args()
station = args.station
x=args.x; y=args.y; z=args.z
xyz = [x, y, z] 
# calculate llh in degrees (and meters)
lat,lon,h = g.xyz2llhd(xyz)
print("%s Lat %12.7f Lon %12.7f Ht %9.3f (m) " % (station, lat, lon, h) )

