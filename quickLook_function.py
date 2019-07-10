import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import cProfile

import gps as g
import argparse
import scipy.interpolate
import scipy.signal
import read_snr_files as snr

# my internal codes for the refraction correction, which are based on
# codes from TU Vienna

def quickLook_function(station, year, doy, snr_type,f,e1,e2,minH,maxH,azval,reqAmp):
    """
    """
    # titles in 4 quadrants - in matlabplot speak
    titles = ['Northwest', 'Northeast','Southeast', 'Southwest']
    # various defaults - ones the user doesn't change in this quick Look code

    delTmax = 70
    pele = [5, 30] # elevation angle limits for removing the polynomial
    polyV = 4 # polynomial order for the direct signal
    desiredP = 0.01 # 1 cm precision
    ediff = 2
    four_in_one = True
    PkNoise = 2
    minNumPts = 20 
    twoDays = False
    NReg = [0.35, 6] # these are meters
    naz = int(len(azval)/2)
    print('number of azimuth pairs:',naz)
    pltname = 'temp.png'

# to avoid having to do all the indenting over again
    obsfile = g.define_quick_filename(station,year,doy,snr_type)
    if os.path.isfile(obsfile):
        print('>>>> WOOHOOO - THE FILE EXISTS ',obsfile)
#
        allGood,sat,ele,azi,t,edot,s1,s2,s5,s6,s7,s8,snrE = snr.read_snr_multiday(obsfile,obsfile,twoDays)
#
        ct = 0
        if allGood == 1:
            minEdataset = np.min(ele)
            print('min elevation angle for this dataset ', minEdataset)
            if minEdataset > (e1+0.5):
                print('It looks like the receiver had an elevation mask')
                e1 = minEdataset
            plt.figure()
            for a in range(naz):
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
                        if (delT < delTmax) & (eminObs < (e1 + ediff)) & (emaxObs > (e2 - ediff)) & (maxAmp > reqAmp[ct]) & (maxAmp/Noise > PkNoise):
                            print('SUCCESS Azimuth {0:3.0f} RH {1:.2f} m, Sat {2:2.0f} Freq {3:.0f} Amp {4:3.1f} '.format( iAzim,maxF,satNu,f,maxAmp))
                            ijk = 220 + a + 1
                            plt.subplot(ijk)
                            plt.plot(px,pz)
                            plt.title(titles[a])
                            if a > 1:
                                plt.xlabel('refl. ht (m)')
    #    plt.savefig(pltname)
        plt.show()
    else: 
        print('some kind of problem with SNR file, so I am exiting the code politely.')
