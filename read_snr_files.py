#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import numpy as np

# library for reading snr files - hopefully
# currently just a copy from gps.py

def read_snr_multiday(obsfile,obsfile2,twoDays):
    """
    input: observation filenames and whether you want just the first day (twoDays)
    output: contents of the file, withe various other metrics
    """
#   defaults so all returned vectors have something stored in them
    sat=[]; ele =[]; azi = []; t=[]; edot=[]; s1=[];
    s2=[]; s5=[]; s6=[]; s7=[]; s8=[];
    snrE = np.array([False, True, True,False,False,True,True,True,True],dtype = bool)
#
    allGood1 = 0; allGood2 = 0
    # set these for now.  should be passed 
    e1 = 5
    e2 = 15
    try:
#       this will be 24 hours - all in one calendar day 
        print('>>>>>>>>>>>>>>>>>>>>> try to read file 1:')
        sat, ele, azi, t, edot, s1, s2, s5, s6, s7, s8, snrE = read_one_snr(obsfile,1)
        allGood1 = 1
        print(len(ele))
#        stats are done above this function
#        g.print_file_stats(ele,sat,s1,s2,s5,s6,s7,s8,e1,e2)
    except:
        print('failed to read the first file')
#
#
#
    if twoDays:
#   restrict day one to first 21 hours.  will then merge iwth last three hours
#   of previous day
#       in case these observables do not exist
        Qs5=[]; Qs6=[]; Qs7=[]; Qs8=[]
        tt = t 
        hours21 = 21*3600
        print('length(tt)', len(tt))
        Qt =tt[tt < hours21]
        Qsat =sat[tt < hours21]
        Qele =ele[tt < hours21]
        Qazi =azi[tt < hours21]
        Qedot = edot[tt < hours21]
        Qs1 = s1[tt < hours21]
        Qs2 = s2[tt < hours21]
        if snrE[5]:
            Qs5 = s5[tt < hours21]
        if snrE[6]:
            Qs6 = s6[tt < hours21]
        if snrE[7]:
            Qs7 = s7[tt < hours21]
        if snrE[8]:
            Qs8 = s8[tt < hours21]
#       I think this is ok??
        QsnrE = snrE
        try:
            print('>>>>>>>>>>>>>>>>>>>>> try to read last three hours of file 2:')
            Psat, Pele, Pazi, Pt, Pedot, Ps1, Ps2, Ps5, Ps6, Ps7, Ps8, PsnrE = read_one_snr(obsfile2,2)
            allGood2 = 1
        except: 
            print('failed to read second file')
    if (twoDays) & (allGood1 == 1) & (allGood2 == 1):
        print('stack the two days')
        ele = np.hstack((Pele,Qele))
        sat = np.hstack((Psat,Qsat))
        azi = np.hstack((Pazi,Qazi))
        t =   np.hstack((Pt,Qt))
        edot= np.hstack((Pedot,Qedot))
        s1 =  np.hstack((Ps1,Qs1))
        s2 =  np.hstack((Ps1,Qs2))
        s5 =  np.hstack((Ps1,Qs5))
        s6 =  np.hstack((Ps1,Qs6))
        s7 =  np.hstack((Ps1,Qs7))
        s8 =  np.hstack((Ps1,Qs8))
    return  allGood1,sat,ele,azi,t,edot,s1,s2,s5,s6,s7,s8,snrE

def read_one_snr(obsfile,ifile):
    """
    input: observation filename 
    ifile: 1 (primary) or 2 (day before)
    output: contents of the file, withe various other metrics
    """

#SNR existance array : s0, s1,s2,s3,s4,s5,s6,s7,s8.  fields 0,3,4 are always false
#

    snrE = np.array([False, True, True,False,False,True,True,True,True],dtype = bool)
    f = np.genfromtxt(obsfile,comments='%')
    print('reading from a snr file ',obsfile)
    r,c = f.shape
    print('Number of rows:', r, ' Number of columns:',c)
#   store into new variable f
#   now only keep last three hours if previous day's file
    hoursKept = 21*3600
    if (ifile == 2):
        print('window last three hours')
        tt = f[:,3]
        f=f[tt > hoursKept]
#   save satellite number, elevation angle, azimuth value
    sat = f[:,0]
    ele = f[:,1]
    azi = f[:,2]
#   negative time tags for day before
    if (ifile == 1):
        t =  f[:,3]
    else:
        print('make timetags negative')
        t =  f[:,3] - 86400
#   ok - the rest is the same as alwasy
#   this is sometimes all zeros
    edot =  f[:,4]
    s1 = f[:,6]
    s2 = f[:,7]
#   typically there is a zero in this row, but older files may have something
#   something that should not be used 
    s6 = f[:,5]

    s1 = np.power(10,(s1/20))  
    s2 = np.power(10,(s2/20))  
#
    s6 = s6/20
    s6 = np.power(10,s6)  
#
#   sometimes these records exist, sometimes not
#   depends on when the file was made, which version was used
    if c > 8:
        s5 = f[:,8]
        if (sum(s5) > 0):
            s5 = s5/20; s5 = np.power(10,s5)  

    if c > 9:
        s7 = f[:,9]
        if (sum(s7) > 0):
            s7 = np.power(10,(s7/20))  
        else:
            s7 = []

    if c > 10:
        s8 = f[:,10]
        if (sum(s8) > 0):
            s8 = np.power(10,(s8/20))  
        else:
            s8 = []


    if (np.sum(s5) == 0):
        snrE[5] = False
        print('no s5 data')
    if (np.sum(s6) == 0):
        print('no s6 data')
        snrE[6] = False
    if (np.sum(s7) == 0):
        print('no s7 data')
        snrE[7] = False
    if (np.sum(s8) == 0):
        snrE[8] = False
        print('no s8 data')

    return sat, ele, azi, t, edot, s1, s2, s5, s6, s7, s8, snrE
