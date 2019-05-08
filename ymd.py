# -*- coding: utf-8 -*-
"""
converts ymd to doy
kristine larson
Updated: April 3, 2019
"""
import gps as g
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("year", help="year ", type=int)
parser.add_argument("month", help="month ", type=int)
parser.add_argument("day", help="day ", type=int)

args = parser.parse_args()
year = args.year
month = args.month
day = args.day


# compute filename to find out if file exists
doy,cdoy,cyyyy,cyy = g.ymd2doy(year, month, day )
print(cdoy)



