# very simple code to pick up all the RH results and make a plot.
# only getting rid of the biggest outliers using a median filter
# Kristine Larson May 2019
import argparse
import datetime
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
#

# where the results are stored
xdir = os.environ['REFL_CODE'] 

# must input start and end year
parser = argparse.ArgumentParser()
parser.add_argument("station", help="station name", type=str)
parser.add_argument("year1", help="first year", type=int)
parser.add_argument("year2", help="end year", type=int)
parser.add_argument("medfilter", help="median filter", type=float)
# optional inputs: filename to output daily RH results 
parser.add_argument("-txtfile", "--txtfile", default='None', type=str, help="txtfile for output")
parser.add_argument("-noscreen", "--noscreen", default='None', type=str, help="toggle to not plot to screen")
args = parser.parse_args()
station = args.station
year1= args.year1
year2= args.year2
medfilter= args.medfilter
txtfile = args.txtfile
noscreen = args.noscreen
txtdir = xdir + '/Files'
if not os.path.exists(txtdir):
    print('make an output directory')
    os.makedirs(txtdir)

# outliers limit, defined in meters
howBig = medfilter;
k=0
n=6
# you can change this - trying out 100 for now
ReqTracks = 100
# putting the results in a np.array, year, doy, RH, Nvalues, month, day
tv = np.empty(shape=[0, n])
obstimes = []
medRH = []
meanRH = []
plt.figure()
#plt.subplot(211)
yearEnd = year2 + 1
year_list = np.arange(year1,yearEnd,1)
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
            medv = np.median(rh)
            # try this
            cc = (rh < (medv+howBig))  & (rh > (medv-howBig))
            good =rh[cc]; goodT =y[cc]
            # only save if there are some minimal number of values
            if (len(good) > ReqTracks):
                rh = good
                obstimes.append(datetime.datetime(year=yr, month=d.month, day=d.day, hour=12, minute=0, second=0))
                medRH =np.append(medRH, medv)
                plt.plot(goodT, good,'.')
            # store the meanRH after the outliers are removed using simple median filter
                meanRHtoday = np.mean(good)
                meanRH =np.append(meanRH, meanRHtoday)
            # add month and day just cause some people like that instead of doy
                newl = [yr, doy, meanRHtoday, len(rh), d.month, d.day]
                tv = np.append(tv, [newl],axis=0)
                k += 1
            else:
                print('not enough retrievals on ', yr, d.month, d.day)
    except:
        print(' no results this year or something went funny ')
plt.ylabel('Reflector Height (m)')
plt.title('GNSS station: ' + station)
plt.gca().invert_yaxis()
plt.grid()
if (noscreen == 'None'):
    plt.show()
#
#plt.subplot(211)
#plt.figure()
fig,ax=plt.subplots()
ax.plot(obstimes,meanRH,'.')
fig.autofmt_xdate()
#plt.xlabel('date')
plt.ylabel('Reflector Height (m)')
plt.title(station.upper() + ': Daily Mean Reflector Height')
plt.grid()
plt.gca().invert_yaxis()
# save the second plot to a png file
pltname = txtdir + '/' + station + '_RH.png'
plt.savefig(pltname)
print('png file goes to this ', pltname)

if (noscreen == 'None'):
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
    outfile = txtdir + '/' + txtfile
    print('output file goes to this ', outfile)
    fout = open(outfile, 'w+')
    # change comment value from # to %
    fout.write("% year doy   RH(m) numval month day \n")
    for i in np.arange(0,N,1):
        fout.write(" {0:4.0f}   {1:3.0f} {2:7.3f} {3:3.0f} {4:2.0f} {5:2.0f} \n".format(ntv[i,0], ntv[i,1], ntv[i,2],ntv[i,3],ntv[i,4],ntv[i,5]))
    fout.close()

