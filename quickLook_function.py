import sys
import os
import numpy as np
import matplotlib.pyplot as plt
# i do not think these are used
# import warnings
# warnings.filterwarnings("ignore")
# import cProfile
# added SOPAC

import gps as g
import scipy.interpolate
import scipy.signal
import quick_read_snr as q
from matplotlib.figure import Figure


def quickLook_function(station, year, doy, snr_type,f,e1,e2,minH,maxH,reqAmp,pele,webapp):
    """
    inputs:
    station name (4 char), year, day of year
    snr_type is the file extension (i.e. 99, 66 etc)
    f is frequency (1, 2, 5), etc
    e1 and e2 are the elevation angle limits in degrees for the LSP
    minH and maxH are the allowed LSP limits in meters
    reqAmp is LSP amplitude significance criterion
    pele is the elevation angle limits for the polynomial removal.  units: degrees
    """
    # titles in 4 quadrants - for webApp
    titles = ['Northwest', 'Southwest','Northeast', 'Southeast']
    # define where the axes are located
    bx = [0,1,0,1]; by = [0,0,1,1]
    bz = [1,3,2,4]
    Simplify = True

    # various defaults - ones the user doesn't change in this quick Look code
    delTmax = 70
    polyV = 4 # polynomial order for the direct signal
    desiredP = 0.01 # 1 cm precision
    ediff = 2 # this is a QC value, eliminates small arcs
    #four_in_one = True # put the plots together
    PkNoise = 2
    minNumPts = 20 
    NReg = [0.35, 6] # noise region for LSP QC. these are meters
    # for quickLook, we use the four geographic quadrants - these are azimuth angles in degrees
    azval = [270, 360, 180, 270, 0, 90, 90, 180]
    naz = int(len(azval)/2) # number of azimuth pairs
    pltname = 'temp.png'
    requireAmp = reqAmp[0]

# to avoid having to do all the indenting over again
# this allows snr file to live in main directory
    obsfile = g.define_quick_filename(station,year,doy,snr_type)
    print('the SNR filename is', obsfile)
    if os.path.isfile(obsfile):
        print('>>>> WOOHOOO - THE SNR FILE EXISTS ',obsfile)
    else:
        if True:
            print(' look for it elsewhere')
            obsfile,obsfileCmp = g.define_filename(station,year,doy,snr_type)
            print(obsfile)
            if (not os.path.isfile(obsfile)) :
                print('>>>> Sigh, - SNR the file does not exist ',obsfile)
                print('because I am a nice person I will try to pick up a RINEX file ')
                print('and translate it for you. This will be GPS only.')
                rate = 'low'; dec_rate = 0
                g.quick_rinex_snr(year, doy, station, snr_type, 'nav',rate, dec_rate)
                if os.path.isfile(obsfile):
                    print('the SNR file now exists')  
                else:
                    print('the RINEX file did not exist, so no SNR file.')
    allGood,sat,ele,azi,t,edot,s1,s2,s5,s6,s7,s8,snrE = q.read_snr_simple(obsfile)
    if allGood == 1:
        minEdataset = np.min(ele)
        print('min elevation angle for this dataset ', minEdataset)
        if minEdataset > (e1+0.5):
            print('It looks like the receiver had an elevation mask')
            e1 = minEdataset
        if webapp:
            fig = Figure(figsize=(10,6), dpi=120)
            axes = fig.subplots(2, 2)
        else:
            plt.figure()
        for a in range(naz):
            if not webapp:
                plt.subplot(2,2,bz[a])
                plt.title(titles[a])
            az1 = azval[(a*2)] ; az2 = azval[(a*2 + 1)]
            satlist = g.find_satlist(f,snrE)
            for satNu in satlist:
                x,y,Nv,cf,UTCtime,avgAzim,avgEdot,Edot2,delT= g.window_data(s1,s2,s5,s6,s7,s8,sat,ele,azi,t,edot,f,az1,az2,e1,e2,satNu,polyV,pele) 
                if Nv > minNumPts:
                    maxF, maxAmp, eminObs, emaxObs,riseSet,px,pz= g.strip_compute(x,y,cf,maxH,desiredP,polyV,minH) 
                    nij =   pz[(px > NReg[0]) & (px < NReg[1])]
                    Noise = 0
                    if (len(nij) > 0):
                        Noise = np.mean(nij)
                        iAzim = int(avgAzim)
                    else:
                        Noise = 1; iAzim = 0 # made up numbers
                    if (delT < delTmax) & (eminObs < (e1 + ediff)) & (emaxObs > (e2 - ediff)) & (maxAmp > requireAmp) & (maxAmp/Noise > PkNoise):
                        print('SUCCESS Azimuth {0:3.0f} RH {1:.2f} m, Sat {2:2.0f} Freq {3:.0f} Amp {4:3.1f} '.format( iAzim,maxF,satNu,f,maxAmp))
                        if not webapp:
                            plt.plot(px,pz)
                        else:
                            axes[bx[a],by[a]].plot(px,pz)
                            axes[bx[a],by[a]].set_title(titles[a])

            # i do not know how to add a grid using these version of matplotlib
            tt = 'GNSS-IR results: ' + station.upper() + ' Freq:' + str(f) + ' ' + str(year) + '/' + str(doy)
            if (a == 3) or (a==1):
                plt.xlabel('reflector height (m)')
        plt.suptitle(tt, fontsize=12)
        if webapp:
            fig.savefig('temp.png', format="png")
        else:
            plt.show()
    else: 
        print('some kind of problem with SNR file, so I am exiting the code politely.')
#                        if (a == 1) | (a == 3):
#                            axes[bx[a],by[a]].set_xlabel('refl. ht (m)')
