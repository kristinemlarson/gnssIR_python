#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SNR reading - meant to be easier to port to heroku
import numpy as np

# library for reading snr files - 
# still learning python
# 2019 kristine m. larson

def read_snr_simple(obsfile):
    """
    author: Kristine Larson
    input: SNR observation filenames and a boolean for 
    whether you want just the first day (twoDays)
    output: contents of the SNR file, withe various other metrics
    """
#   defaults so all returned vectors have something stored in them
    sat=[]; ele =[]; azi = []; t=[]; edot=[]; s1=[];
    s2=[]; s5=[]; s6=[]; s7=[]; s8=[];
    snrE = np.array([False, True, True,False,False,True,True,True,True],dtype = bool)
#   
    allGood = 1
    try:
        f = np.genfromtxt(obsfile,comments='%')
        r,c = f.shape
        print('read_snr_simple, Number of rows:', r, ' Number of columns:',c)
        sat = f[:,0]; ele = f[:,1]; azi = f[:,2]; t =  f[:,3]
        edot =  f[:,4]; s1 = f[:,6]; s2 = f[:,7]; s6 = f[:,5]
        s1 = np.power(10,(s1/20))  
        s2 = np.power(10,(s2/20))  
        s6 = s6/20; s6 = np.power(10,s6)  
#   make sure s5 has default value?
        s5 = []
        if c > 8:
            s5 = f[:,8]
            if (sum(s5) > 0):
                s5 = s5/20; s5 = np.power(10,s5)  
            print(len(s5))
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
            snrE[5] = False; print('no s5 data')
        if (np.sum(s6) == 0):
            print('no s6 data'); snrE[6] = False
        if (np.sum(s7) == 0):
            print('no s7 data'); snrE[7] = False
        if (np.sum(s8) == 0):
            snrE[8] = False; print('no s8 data')
    except:
        print('problem reading the SNR file')
        allGood = 0
    return allGood, sat, ele, azi, t, edot, s1, s2, s5, s6, s7, s8, snrE
