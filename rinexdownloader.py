#!/usr/bin/env python
import wget
import os
import urllib
#####################################################################################
#rinexdownloader.py
#This code will download any RINEX, nav or UNR
#time series file requested
#Written by Brendan Crowell, University of Washington
#Last edited January 10, 2019
#Broadcast navigation messages are only downloaded from CDDIS
#RINEX files will try to download from UNAVCO, then CWU, then CDDIS, then SOPAC
#Time Series files will only download from UNR, cartesian positions
#VARIABLES
#year - 4 digit string of year
#doy - 3 digit string of day of year
#site - 4 digit string of site id
#####################################################################################
#This subroutine downloads the broadcast navigation message for a given day from CDDIS
def getbcorbit(year, doy):
    """
    originally written by brendan - modified by kristine larson
    to store the files in a directory defined by environment variable ORBITS
    inputs are year (4 char) and day of year (3 char)
    """
#
    xdir = str(os.environ['ORBITS'])
    ydir = xdir + '/' + year 
    if not os.path.isdir(ydir): #if year folder doesn't exist, make it
        os.makedirs(ydir)
    zdir = ydir + '/nav' 
    if not os.path.isdir(zdir): #if nav subfolder doesn't exist, make it
        os.makedirs(zdir)
    xdir = zdir
    # compressed name
    fname = xdir + '/brdc' + doy + '0.' +  year[-2:] + 'n.Z'
    fname2 = xdir + '/brdc' + doy + '0.' +  year[-2:] + 'n'
    if (os.path.isfile(fname2) == True):
        print ('Navigation file ' + fname2 + ' already exists')
    else:
        url = 'ftp://cddis.nasa.gov/gnss/data/daily/' + year + '/' + doy + '/' + year[-2:] + 'n/brdc' + doy + '0.' +  year[-2:] + 'n.Z'
        wget.download(url,fname)
        os.system('gunzip' + ' ' + fname)

#
#This subroutine will download RINEX files given the station, year and day of year. 
def getrinex(site, year, doy):
    crxpath = '/Users/kristine/bin/RNXCMPdir/bin/'
    if not os.path.exists('rinex'): #if rinex folder doesn't exist, make it
        os.makedirs('rinex')
    fnameZ = 'rinex/' + site + doy + '0.' +  year[-2:] + 'd.Z'
    fnamebz2 = 'rinex/' + site + doy + '0.' +  year[-2:] + 'd.bz2'
    fnamed = 'rinex/' + site + doy + '0.' +  year[-2:] + 'd'
    fnameo = 'rinex/' + site + doy + '0.' +  year[-2:] + 'o'
    if (os.path.isfile(fnameo) == True):       
        print ('Rinex file ' + fnameo + ' already exists')
    else:
        try:
            url = 'ftp://data-out.unavco.org/pub/rinex/obs/' + year + '/' + doy + '/' + site + doy + '0.' +  year[-2:] + 'd.Z'
            print ('Attempting to download ' + fnamed + ' from UNAVCO')
            wget.download(url, out='rinex/')
            os.system('gunzip' + ' ' + fnameZ)
            os.system( crxpath + 'CRX2RNX' + ' ' + fnamed)
            os.remove(fnamed)
        except Exception:
            print ('File not at UNAVCO, checking CWU')
            try:
                url = 'https://www.geodesy.cwu.edu/data_ftp_pub/data/' + year+ '/' + doy + '/30sec/' + site + doy + '0.' +  year[-2:] + 'd.bz2'
                print ('Attempting to download ' + fnamed + ' from CWU')
                wget.download(url, out='rinex/')
                os.system('bzip2 -d' + ' ' + fnamebz2)
                os.system('./crx2rnx' + ' ' + fnamed)
                os.remove(fnamed)
            except Exception:
                print ('File not at CWU, checking CDDIS')
                try:
                    url = 'ftp://cddis.nasa.gov/gnss/data/daily/' + year+ '/' + doy + '/' + year[-2:] + 'd/' + site + doy + '0.' +  year[-2:] + 'd.Z'
                    print ('Attempting to download ' + fnamed + ' from CDDIS')
                    wget.download(url, out='rinex/')
                    os.system('gunzip' + ' ' + fnameZ)
                    os.system(crxpath + 'CRX2RNX' + ' ' + fnamed)
                    os.remove(fnamed)
                except Exception:
                    print ('File not at CDDIS, checking SOPAC')
                    try:
                        url = 'ftp://garner.ucsd.edu/pub/rinex/' + year+ '/' + doy + '/' + site + doy + '0.' +  year[-2:] + 'd.Z'
                        print ('Attempting to download ' + fnamed + ' from SOPAC')
                        wget.download(url, out='rinex/')
                        os.system('gunzip' + ' ' + fnameZ)
                        os.system(crxpath + 'CRX2RNX' + ' ' + fnamed)
                        os.remove(fnamed)
                    except Exception:
                        print ('File not found at SOPAC, moving onto next station')

#This subroutine will download highrate (1-Hz) RINEX files
def getrinexhr(site, year, doy):
    """
    code from brendan - various archives to pick up high rate data
    all inputs are strings, not integrs
    you need to define the path for the compressed rinex executable on your machine
    files are stored in a subdirectory called rinex_hr
    """
    crxpath = '/Users/kristine/bin/RNXCMPdir/bin/'
    if not os.path.exists('rinex_hr'): #if rinex highrate folder doesn't exist, make it
        os.makedirs('rinex_hr')
    fnameZ = 'rinex_hr/' + site + doy + '0.' +  year[-2:] + 'd.Z'
    fnamebz2 = 'rinex_hr/' + site + doy + 'i.' +  year[-2:] + 'd.bz2'
    fnamecwuo = 'rinex_hr/' + site + doy + 'i.' +  year[-2:] + 'o'
    fnamecwud = 'rinex_hr/' + site + doy + 'i.' +  year[-2:] + 'd'
    fnamed = 'rinex_hr/' + site + doy + '0.' +  year[-2:] + 'd'
    fnameo = 'rinex_hr/' + site + doy + '0.' +  year[-2:] + 'o'
    if (os.path.isfile(fnameo) == True):       
        print ('Rinex file ' + fnameo + ' already exists')
    else:
        try:
            url = 'ftp://garner.ucsd.edu/pub/rinex_highrate/' + year+ '/' + doy + '/' + site + doy + '0.' +  year[-2:] + 'd.Z'
            print (url)
            print ('Attempting to download ' + fnamed + ' from SOPAC')
            wget.download(url, out='rinex_hr/')
            os.system('gunzip' + ' ' + fnameZ)
            os.system(crxpath + 'CRX2RNX' + ' ' + fnamed)
            os.remove(fnamed)
        except Exception:
            print ('File not at SOPAC, checking UNAVCO')
            try:
                url = 'ftp://data-out.unavco.org/pub/highrate/1-Hz/rinex/' + year + '/' + doy + '/' + site + '/' + site + doy + '0.' +  year[-2:] + 'd.Z'
                print ('Attempting to download ' + fnamed + ' from UNAVCO')
                wget.download(url, out='rinex_hr/')
                os.system('gunzip' + ' ' + fnameZ)
                os.system(crxpath + 'CRX2RNX' + ' ' + fnamed)
                os.remove(fnamed)
            except Exception:
                print ('File not at UNAVCO checking CWU')
                try:
                    url = 'https://www.geodesy.cwu.edu/data_ftp_pub/data/' + year+ '/' + doy + '/01sec/' + site + doy + 'i.' +  year[-2:] + 'd.bz2'
                    print ('Attempting to download ' + fnamed + ' from CWU')
                    wget.download(url, out='rinex_hr/')
                    os.system('bzip2 -d' + ' ' + fnamebz2)
                    os.system(crxpath + 'CRX2RNX' + ' ' + fnamecwud)
                    os.rename(fnamecwuo, fnameo)
                    os.remove(fnamecwud)
                except Exception:
                    print ('File not at CWU, moving on')


#This subroutine downloads the cartesian time series in IGS08 from the UNR database to use for a priori locations
def gettseries(site):
    if not os.path.exists('tseries'): #if tseries folder doesn't exist, make it
        os.makedirs('tseries')
    siteid = site.upper()
    fname = 'tseries/' + siteid + '.IGS08.txyz2'
    if (os.path.isfile(fname) == True):       
        print ('Timeseries file ' + fname + ' already exists')
    else:
        url = 'http://geodesy.unr.edu/gps_timeseries/txyz/IGS08/' + siteid + '.IGS08.txyz2'
        wget.download(url, out='tseries/')
