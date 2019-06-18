# -*- coding: utf-8 -*-
"""
# input llh (degrees, meters) and output x,y,z
# Kristine m. Larson
"""
import gps as g
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("lat", help="latitude (deg) ", type=float)
parser.add_argument("lon", help="longitude (deg) ", type=float)
parser.add_argument("height", help="ellipsoidal height (m) ", type=float)
args = parser.parse_args()
lat=args.lat; lon=args.lon; height=args.height
x,y,z = g.llh2xyz(lat,lon,height)
print("XYZ %15.4f %15.4f %15.4f " % ( x,y,z) )

