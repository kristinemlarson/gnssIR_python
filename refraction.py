import gps as g
import numpy as np
from scipy.interpolate import interp1d
import os
import pickle
import datetime
import sys


def read_4by5(station, dlat,dlon,hell):
    """
    author: kristine m. larson
    input station name (4 char), lat,long,elevation in deg/deg/meters
    requires that an environment variable exists for REFL_CODE
    """
#
    xdir = str(os.environ['REFL_CODE'])
    obsfile = xdir + '/input/' + station + '_refr.txt'
    print('reading from station refraction file: ', obsfile)
    x = np.genfromtxt(obsfile,comments='%')
    max_ind = 4
    pgrid = np.zeros((4,5))
    Tgrid = np.zeros((4,5))
    Qgrid = np.zeros((4,5))
    dTgrid = np.zeros((4,5))
    u = np.zeros((4,1))
    Hs = np.zeros((4,1)) 
    ahgrid = np.zeros((4,5))
    awgrid = np.zeros((4,5))
    lagrid = np.zeros((4,5))
    Tmgrid = np.zeros((4,5))

    for n in [0,1,2,3]:
        ij = 0
        u[n]= x[n*5,6]
        Hs[n]= x[n*5,7]
        for m in range(n*5, n*5+5):
            pgrid[n,ij] = x[m,2] 
            Tgrid[n,ij] = x[m,3] 
            Qgrid[n,ij] = x[m,4]/1000
            dTgrid[n,ij] = x[m,5]/1000
            ahgrid[n,ij] = x[m,8]/1000
            awgrid[n,ij] = x[m,9]/1000
            lagrid[n,ij] = x[m,10] 
            Tmgrid[n,ij] = x[m,11] 
            ij +=1

    return pgrid, Tgrid, Qgrid, dTgrid, u, Hs, ahgrid, awgrid, lagrid, Tmgrid
#
def gpt2_1w (station, dmjd,dlat,dlon,hell,it):
    """
    converted by kristine larson from posted TUVienna code
    input parameters:
    station: station name
    dmjd:  modified Julian date (scalar, only one epoch per call is possible)
    dlat:  ellipsoidal latitude in radians [-pi/2:+pi/2] (vector)
    dlon:  longitude in radians [-pi:pi] or [0:2pi] (vector)
    hell:  ellipsoidal height in m (vector)
    it:    case 1: no time variation but static quantities
           case 0: with time variation (annual and semiannual terms)
    output parameters:
    p:    pressure in hPa
    T:    temperature in degrees Celsius 
    dT:   temperature lapse rate in degrees per km 
    Tm:   mean temperature of the water vapor in degrees Kelvin 
    e:    water vapor pressure in hPa 
    ah:   hydrostatic mapping function coefficient at zero height (VMF1) 
    aw:   wet mapping function coefficient (VMF1) 
    la:   water vapor decrease factor 
    undu: geoid undulation in m 
    """

#  need to find diffpod and difflon
    if (dlon < 0):
        plon = (dlon + 2*np.pi)*180/np.pi;
    else:
        plon = dlon*180/np.pi;
# transform to polar distance in degrees
    ppod = (-dlat + np.pi/2)*180/np.pi; 

#       % find the index (line in the grid file) of the nearest point
#  	  % changed for the 1 degree grid (GP)
    ipod = np.floor(ppod+1); 
    ilon = np.floor(plon+1);
    
#   normalized (to one) differences, can be positive or negative
#	% changed for the 1 degree grid (GP)
    diffpod = (ppod - (ipod - 0.5));
    difflon = (plon - (ilon - 0.5));


# change the reference epoch to January 1 2000
    print('Modified Julian Day', dmjd)
    dmjd1 = dmjd-51544.5 

    pi2 = 2*np.pi
    pi4 = 4*np.pi

# mean gravity in m/s**2
    gm = 9.80665;
# molar mass of dry air in kg/mol
    dMtr = 28.965E-3 
#    dMtr = 28.965*10^-3 
# universal gas constant in J/K/mol
    Rg = 8.3143 

# factors for amplitudes, i.e. whether you want time varying
    if (it==1):
        print('>>>> no refraction time variation ')
        cosfy = 0; coshy = 0; sinfy = 0; sinhy = 0;
    else: 
        cosfy = np.cos(pi2*dmjd1/365.25)
        coshy = np.cos(pi4*dmjd1/365.25) 
        sinfy = np.sin(pi2*dmjd1/365.25) 
        sinhy = np.sin(pi4*dmjd1/365.25) 
    cossin = np.matrix([1, cosfy, sinfy, coshy, sinhy])
# initialization of new vectors
    p =  0; T =  0; dT = 0; Tm = 0; e =  0; ah = 0; aw = 0; la = 0; undu = 0;
    undul = np.zeros(4)
    Ql = np.zeros(4)
    dTl = np.zeros(4)
    Tl = np.zeros(4)
    pl = np.zeros(4)
    ahl = np.zeros(4)
    awl = np.zeros(4)
    lal = np.zeros(4)
    Tml = np.zeros(4)
    el = np.zeros(4)
#
    pgrid, Tgrid, Qgrid, dTgrid, u, Hs, ahgrid, awgrid, lagrid, Tmgrid = read_4by5(station,dlat,dlon,hell)
#
    for l in [0,1,2,3]:
        KL = l   #silly to have this as a variable like this 
#  transforming ellipsoidal height to orthometric height:
#  Hortho = -N + Hell
        undul[l] = u[KL] 
        hgt = hell-undul[l] 
#  pressure, temperature at the height of the grid
        T0 = Tgrid[KL,0] + Tgrid[KL,1]*cosfy + Tgrid[KL,2]*sinfy + Tgrid[KL,3]*coshy + Tgrid[KL,4]*sinhy;
        tg = float(Tgrid[KL,:] *cossin.T)
#     print(T0,tg)

        p0 = pgrid[KL,0] + pgrid[KL,1]*cosfy + pgrid[KL,2]*sinfy + pgrid[KL,3]*coshy + pgrid[KL,4]*sinhy;
 
#       humidity 
        Ql[l] = Qgrid[KL,0] + Qgrid[KL,1]*cosfy + Qgrid[KL,2]*sinfy + Qgrid[KL,3]*coshy + Qgrid[KL,4]*sinhy;
 
# reduction = stationheight - gridheight
        Hs1 = Hs[KL]
        redh = hgt - Hs1;

# lapse rate of the temperature in degree / m
        dTl[l] = dTgrid[KL,0] + dTgrid[KL,1]*cosfy + dTgrid[KL,2]*sinfy + dTgrid[KL,3]*coshy + dTgrid[KL,4]*sinhy;
   
# temperature reduction to station height
        Tl[l] = T0 + dTl[l]*redh - 273.15;

#  virtual temperature
        Tv = T0*(1+0.6077*Ql[l])   
        c = gm*dMtr/(Rg*Tv) 
        
# pressure in hPa
        pl[l] = (p0*np.exp(-c*redh))/100 
            
#  hydrostatic coefficient ah
        ahl[l] = ahgrid[KL,0] + ahgrid[KL,1]*cosfy + ahgrid[KL,2]*sinfy + ahgrid[KL,3]*coshy + ahgrid[KL,4]*sinhy;
            
# wet coefficient aw
        awl[l] = awgrid[KL,0] + awgrid[KL,1]*cosfy + awgrid[KL,2]*sinfy + awgrid[KL,3]*coshy + awgrid[KL,4]*sinhy;
					 
# water vapor decrease factor la - added by GP
        lal[l] = lagrid[KL,0] + lagrid[KL,1]*cosfy + lagrid[KL,2]*sinfy + lagrid[KL,3]*coshy + lagrid[KL,4]*sinhy;
					 
# mean temperature of the water vapor Tm - added by GP
        Tml[l] = Tmgrid[KL,0] +  Tmgrid[KL,1]*cosfy + Tmgrid[KL,2]*sinfy + Tmgrid[KL,3]*coshy + Tmgrid[KL,4]*sinhy;
					 		 
# water vapor pressure in hPa - changed by GP
        e0 = Ql[l]*p0/(0.622+0.378*Ql[l])/100; # % on the grid
        aa = (100*pl[l]/p0)
        bb = lal[l]+1
        el[l] = e0*np.power(aa,bb)  # % on the station height - (14) Askne and Nordius, 1987
           
    dnpod1 = np.abs(diffpod); # % distance nearer point
    dnpod2 = 1 - dnpod1;   # % distance to distant point
    dnlon1 = np.abs(difflon);
    dnlon2 = 1 - dnlon1;
        
#   pressure
    R1 = dnpod2*pl[0]+dnpod1*pl[1];
    R2 = dnpod2*pl[2]+dnpod1*pl[3];
    p = dnlon2*R1+dnlon1*R2;
            
#   temperature
    R1 = dnpod2*Tl[0]+dnpod1*Tl[1];
    R2 = dnpod2*Tl[2]+dnpod1*Tl[3];
    T = dnlon2*R1+dnlon1*R2;
        
#   temperature in degree per km
    R1 = dnpod2*dTl[0]+dnpod1*dTl[1];
    R2 = dnpod2*dTl[2]+dnpod1*dTl[3];
    dT = (dnlon2*R1+dnlon1*R2)*1000;
            
#   water vapor pressure in hPa - changed by GP
    R1 = dnpod2*el[0]+dnpod1*el[1];
    R2 = dnpod2*el[2]+dnpod1*el[3];
    e = dnlon2*R1+dnlon1*R2;
            
#   hydrostatic
    R1 = dnpod2*ahl[0]+dnpod1*ahl[1];
    R2 = dnpod2*ahl[2]+dnpod1*ahl[3];
    ah = dnlon2*R1+dnlon1*R2;
           
#   wet
    R1 = dnpod2*awl[0]+dnpod1*awl[1];
    R2 = dnpod2*awl[2]+dnpod1*awl[3];
    aw = dnlon2*R1+dnlon1*R2;
        
#  undulation
    R1 = dnpod2*undul[0]+dnpod1*undul[1];
    R2 = dnpod2*undul[2]+dnpod1*undul[3];
    undu = dnlon2*R1+dnlon1*R2;

#   water vapor decrease factor la - added by GP
    R1 = dnpod2*lal[0]+dnpod1*lal[1];
    R2 = dnpod2*lal[2]+dnpod1*lal[3];
    la = dnlon2*R1+dnlon1*R2;
		
#   mean temperature of the water vapor Tm - added by GP
    R1 = dnpod2*Tml[0]+dnpod1*Tml[1];
    R2 = dnpod2*Tml[2]+dnpod1*Tml[3];
    Tm = dnlon2*R1+dnlon1*R2; 

    return p, T, dT,Tm,e,ah,aw,la,undu

def readWrite_gpt2_1w(xdir, station, site_lat, site_lon):
    """
    makes a grid for refraction correction
    xdir - directory for output
    station name
    lat and lon in degrees (NOT RADIANS)
    kristine m. larson
    """
#   this should use the environment variable
    outfile = xdir + '/input/' + station + '_refr.txt'
    if os.path.isfile(outfile):
        print('refraction file for this station already exists')
    else:
        print('refraction output file will be written to ', outfile)

#   change to radians
        dlat = site_lat*np.pi/180 
        dlon = site_lon*np.pi/180 

#   read VMF gridfile in pickle format 
        pname = xdir + '/input/' + 'gpt_1wA.pickle'
        print('large refraction file is stored here:', pname)
        try:
            f = open(pname, 'rb')
            [All_pgrid, All_Tgrid, All_Qgrid, All_dTgrid, All_U, All_Hs, All_ahgrid, All_awgrid, All_lagrid, All_Tmgrid] = pickle.load(f)
            f.close()
        except:
            print('I did not find the large refraction file where it is supposed to be, but I will try looking in your home directory')
            try:
                pname =  'gpt_1wA.pickle'
                f = open(pname, 'rb')
                [All_pgrid, All_Tgrid, All_Qgrid, All_dTgrid, All_U, All_Hs, All_ahgrid, All_awgrid, All_lagrid, All_Tmgrid] = pickle.load(f)
                f.close()
            except:
                print('hmm, failed again. Go into gnssIR_lomb.py, set RefractionCorrection to false, and rerun the code.... ')
                sys.exit()

#    print(np.shape(All_pgrid))
# really should e zero to four, but whatever
        indx = np.zeros(4,dtype=int)
        indx_lat = np.zeros(4,dtype=int)
        indx_lon = np.zeros(4,dtype=int)


#figure out grid index
# % only positive longitude in degrees
        if (dlon < 0):
            plon = (dlon + 2*np.pi)*180/np.pi;
        else:
            plon = dlon*180/np.pi 
#
#  transform to polar distance in degrees
        ppod = (-dlat + np.pi/2)*180/np.pi  

#% find the index (line in the grid file) of the nearest point
# % changed for the 1 degree grid (GP)
        ipod = np.floor(ppod+1)  
        ilon = np.floor(plon+1) 
    
#    % normalized (to one) differences, can be positive or negative
# % changed for the 1 degree grid (GP)
        diffpod = (ppod - (ipod - 0.5)) 
        difflon = (plon - (ilon - 0.5)) 
#    % added by HCY
# % changed for the 1 degree grid (GP)
        if (ipod == 181):
            ipod = 180 
        if (ilon == 361):
            ilon = 1 
        if (ilon == 0):
            ilon = 360

#     get the number of the corresponding line
#	 changed for the 1 degree grid (GP)
        indx[0] = (ipod - 1)*360 + ilon 
#  save the lat lon of the grid points
        indx_lat[0] = 90-ipod+1  
        indx_lon[0] = ilon-1   
# % near the poles: nearest neighbour interpolation, otherwise: bilinear
# % with the 1 degree grid the limits are lower and upper (GP)

        bilinear = 0 
        max_ind = 1 
        if (ppod > 0.5) and (ppod < 179.5):
            bilinear = 1           
        if (bilinear == 1):
            max_ind =4 

#    % bilinear interpolation
#    % get the other indexes 
 
        ipod1 = ipod + np.sign(diffpod) 
        ilon1 = ilon + np.sign(difflon) 
# % changed for the 1 degree grid (GP)
        if (ilon1 == 361):
            ilon1 = 1 
        if (ilon1 == 0):
            ilon1 = 360 
#         get the number of the line
# changed for the 1 degree grid (GP)
# four indices ???
        indx[1] = (ipod1 - 1)*360 + ilon; # % along same longitude
        indx[2] = (ipod  - 1)*360 + ilon1;# % along same polar distance
        indx[3] = (ipod1 - 1)*360 + ilon1;# % diagonal
#
# save the lat lon of the grid points  lat between [-90 ;90]  lon [0 360] 
        indx_lat[1] =   90 - ipod1+np.sign(diffpod)     
        indx_lon[1] = ilon-1 
        indx_lat[2] =   90-ipod +1
        indx_lon[2] =  ilon1 - np.sign(difflon) 
        indx_lat[3] =   90 -ipod1+np.sign(diffpod)     
        indx_lon[3] = ilon1- np.sign(difflon);

# extract the new grid
# will need to do 0-4 instead of 1-5 because stored that way in python
# which values to use in the bigger array
# assign the correct values
        indx = indx - 1
        indx_list = indx.tolist()
#    print(indx_list)
#    print(indx)
#print(np.shape(indx_lat))
#print(np.shape(indx_lon))
        w = 0
# need to write values for a given station to a plain text file
#
        fout = open(outfile, 'w+')
        for a in indx_list:
            for k in [0,1,2,3,4]:
                fout.write(" {0:4.0f} {1:5.0f} {2:13.4f} {3:10.4f} {4:10.6f} {5:10.4f} {6:12.5f} {7:12.5f} {8:10.6f} {9:10.6f} {10:10.6f} {11:10.4f} \n".format( indx_lat[w], indx_lon[w],All_pgrid[a,k],All_Tgrid[a,k],All_Qgrid[a,k]*1000,All_dTgrid[a,k]*1000,All_U[a,0],All_Hs[a,0], All_ahgrid[a,k]*1000, All_awgrid[a,k]*1000, All_lagrid[a,k], All_Tmgrid[a,k] ))

            w+=1
        fout.close()
        print('file written')


def corr_el_angles(el_deg, press, temp):
    """
    inputs are elevation angles (in degrees)
    Pressure in hPa and Temperature in degrees C.
    outputs are corrected elevation angles (in degrees)
    """

#  Formula in python from Strandberg, originally from Astronomy journal
    corr_el_arc_min = 510/(9/5*temp + 492) * press/1010.16 * 1/np.tan(np.deg2rad(el_deg + 7.31/(el_deg + 4.4)))
    correction = corr_el_arc_min/60 
     
    corr_el_deg = el_deg + correction   
    return corr_el_deg


