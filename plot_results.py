import os
import numpy as np
import matplotlib.pyplot as plt
import sys
import argparse
import datetime
# some very simple code to pick up all the RH results and make a plot.
# only getting rid of the biggest outliers using a median filter
# Kristine Larson May 2019
#
# wisconsin data
# ftp://amrc.ssec.wisc.edu/pub/aws/iridium/Lorne/2019/04/Lorne_04_2019.dat

# where the results are stored
# default end year is 2019
xdir = str(os.environ['REFL_CODE'])
# required inputs 
parser = argparse.ArgumentParser()
parser.add_argument("station", help="station name", type=str)
parser.add_argument("year1", help="first year", type=int)
parser.add_argument("medfilter", help="median filter", type=float)
# optional inputs: filename to output daily RH results 
parser.add_argument("-txtfile", "--txtfile", default='None', type=str, help="txtfile for output")
args = parser.parse_args()
station = args.station
year1= args.year1
medfilter= args.medfilter
txtfile = args.txtfile
# outliers, in meters
howBig = medfilter;
k=0
n=6
# putting the results in a np.array, year, doy, RH, Nvalues, month, day
tv = np.empty(shape=[0, n])
obstimes = []
medRH = []
meanRH = []
plt.figure()
plt.subplot(211)

year_list = np.arange(year1,2020,1)
print('Years to examine: ',year_list)
for yr in year_list:
    direc = xdir + '/' + str(yr) + '/results/' + station + '/'
    print('looking at ', yr)
    try:
        all_files = os.listdir(direc)
        for f in all_files:
            fname = direc + f
            a = np.loadtxt(fname,skiprows=3,comments='%').T
            y = a[0] +a[1]/365.25
            rh = a[2] 
            doy = int(np.mean(a[1]))
            # change from doy to month and day in datetime
            d = datetime.date(yr,1,1) + datetime.timedelta(doy-1)
            obstimes.append(datetime.datetime(year=yr, month=d.month, day=d.day, hour=12, minute=0, second=0))
            medv = np.median(rh)
            medRH =np.append(medRH, medv)
            # try this
            cc = (rh < (medv+howBig))  & (rh > (medv-howBig))
            good =rh[cc]; goodT =y[cc]
            rh = good
#            good =  good[  rh > (medv-howBig)]
#            goodT = goodT[ rh > (medv-howBig)]
            plt.plot(goodT, good,'.')
            # store the meanRH after the outliers are removed using simple median filter
            meanRHtoday = np.mean(good)
            meanRH =np.append(meanRH, meanRHtoday)
            # add month and day just cause some people like that instead of doy
            newl = [yr, doy, meanRHtoday, len(rh), d.month, d.day]
            tv = np.append(tv, [newl],axis=0)
            k += 1
    except:
        print(' no results this year or something went funny ')
        
#plt.xlabel('year')
plt.gca().invert_yaxis()
plt.ylabel('Reflector Height (m)')
plt.title('GNSS station: ' + station)
plt.grid()
#
plt.subplot(212)
plt.plot(obstimes,meanRH,'.')
plt.xlabel('date')
plt.ylabel('Reflector Height (m)')
plt.title('Daily Mean Reflector Height')
plt.grid()
plt.gca().invert_yaxis()
plt.show()
if txtfile == 'None':
    print('no txt output')
else:
    print('yes to making an output file')
    # sort the time tags
    ii = np.argsort(obstimes)
    # apply time tags to a new variable
    ntv = tv[ii,:]
    N,M = np.shape(ntv)
    fout = open(txtfile, 'w+')
    fout.write("# year doy   RH(m) numval month day \n")
    for i in np.arange(0,N,1):
        fout.write(" {0:4.0f}   {1:3.0f} {2:7.3f} {3:3.0f} {4:2.0f} {5:2.0f} \n".format(ntv[i,0], ntv[i,1], ntv[i,2],ntv[i,3],ntv[i,4],ntv[i,5]))
    fout.close()

