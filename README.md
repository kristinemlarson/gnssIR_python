# gnssIR_lomb.py
This is a first cut at a python code that will compute reflector heights fairly automatically.
Some things to know:

This is for python3. 

The library dependencies are at the top of the two main python scripts: gnssIR_lomb.py and gps.py.
The latter is a bunch of helper scripts I have written - not all are for reflector height calculation.

I do not (yet) check for data arcs that cross midnite.  This has to be fixed
for tides. This has much more limited impact on snow where daily averages are typically
used.  

I have added some python codes that allows the user to make snr files. It still expects you
to use the fortran translator, but it is called within python.

A simple refraction error correction has been added.

I will be adding a RH dot correction which is needed for tides.

I have added a python script called rinex2snr.py which allows you to make SNR files more 
directly.  It needs station name, year, doy span (i.e. starting day and ending day) and
a few other choices.  More details to come.


# Environment variables

EXE = where the fortran translator executables live

REFL_CODE = where the reflection code inputs (snr files and instructions) and outputs (reflector heights) 
will be stored (see below)

ORBITS = where the GNSS orbits will be (nav for GPS only and sp3 for multi GNSS). These files are only 
used in the fortran conversion code.

COORDS = where the coordinates are kept for sites with large speeds, i.e. Greenland and Antarctica.
See knut.txt for sample. This is only used in the fortran conversion code.

# Inputs for Rinex translation code

The driver is rinex2snr.py It will need to know where the the gpsSNR.e or gnssSNR.e translator
codes are (for GPS only or GNSS) so make sure the EXE environment variable is set. Those 
codes are available on this gitHub in the gpsonlySNR and gnssSNR folders. If I have more
users of these codes, I will probably change to python Rinex readers.

Sample call of rinex2snr.py would be

python3 rinex2snr.py at01 2019 75 80 66 gbm

where at01 is the station name, 2019 is the year, 70 and 80 and the starting and ending day of years.
66 is the snr option type (see the translator code for more inforamtion).  The last input is the 
orbit type. Basically:

nav - is using the GPS nav message, so your Rinex file should be GPS only

sp3 - is using the IGS sp3 file, so again, yoru Rine file should be GPS only.

gbm - is now my only option for getting a GNSS orbit file.  It is also in sp3 format. It comes from
the group at GFZ.  

Unless the rinex data are sitting there in your work directory, the code attempts to 
pick up your rinex file at UNAVCO. Currently it only uses the default low-rate files.
Eventually I will add the high-rate directories. Code to download files from SOPAC is also in gps.py
but is not currently called.

One more thing- it is very comon for GPS archives to store files in the Hatanaka format.
So currently it tries to get the regular Rinex file but if that fails, it tries to download
Hatanaka format. You need the Hatanaka decompression code to translate this.  Look for 
CRX2RNX in gps.py to see where my code assumes that it lives.  

# Inputs for reflector code


The expected SNR files must be translated from RINEX before you run this code. 
This code is called gnssSNR (all GNSS using sp3 file) or RinexSNR (GPS only using nav file) 
and was distributed at the GPS Tool Box. These are now available on my gitHub account.

https://www.ngs.noaa.gov/gps-toolbox/GNSS-IR.htm

The paper that describes these (and other) tools is open access here:
https://link.springer.com/article/10.1007/s10291-018-0744-8

The code assumes you are going to have a working directory for input and outputfiles.  
An environment variable is set at the top of gnssIR_lomb.py, so you should change that for your work area.
If I call that REFL, then your snr files should be in REFL/YYYY/snr/aaaa, where YYYY is 4 character
year and aaaa is station name.  

* SNR file. You must use the following name conventions:

  aaaaDDD0.yy.snrnn

```sh
where aaaa is a 4 character station name
DDD is day of year
yy is two character year
0 is always zero (it comes from the RINEX spec)
nn is a specific kind of snr file (99, 77, and 50 are the most commonly used)
```

* Input instructions

This should be stored in a file called REFL_CODE/input/aaaa 
See sample file called input_smm3_example. 

* Output
Your output files will go in REFL_CODE/YYYY/results/aaaa 
This is basically a text listing of individual arc reflector heights. 

```sh
maxF is the reflector height in meters
sat is satellite number, where 1-32 is for GPS, 101-199 is for Glonass, 201-299 is for Galileo, 301-399 for Beidou
Azim is average azimuth over a given track, in degrees.
Amp is the spectral amplitude in volts/volts
eminO and emaxO are the observed min and max elevation angles in the track
Nv: number of observations used in the Lomb Scargle Periodogram (LSP)
```

freq is the frequency used:
```sh
1 GPS L1
2 GPS L2
20 GPS L2C
5 GPS L5
101 Glonass L1
102 Glonass L2
201, 205, 206, 207, 208: Galileo frequencies
301 etc: Beidou  
 ```
rise is an integer value, rise = 1 and set = -1

PkNoise is the spectral amplitude divided by an average noise value calculated
for a reflector height range you prescribe in the code.


EXAMPLE year, doy, maxF,sat,UTCtime, Azim, Amp,  eminO, emaxO,  Nv,freq,rise,Edot, PkNoise
 ```sh
 2018 253 15.200   1 15.367 105.22  29.95   5.03  14.97  288   1 -1 -0.00693   5.26
 2018 253 15.260   1 10.454 201.50  26.56   5.02  14.97  273   1  1  0.00731   4.70
 2018 253 14.725   1  2.785 303.43  25.90   5.03  14.99  362   1 -1 -0.00553   4.89
 2018 253 15.175   2  3.501  74.13  21.63   5.02  14.98  360   1  1  0.00556   4.42
 2018 253 15.280   2 20.175 179.09  32.12   5.01  14.97  279   1 -1 -0.00717   4.85
 2018 253 15.060   2 15.264 271.00  38.34   5.03  14.97  297   1  1  0.00672   4.64
 2018 253 15.170   3 17.150  77.74  35.24   5.00  14.98  291   1 -1 -0.00688   4.68
 ```



# Usage

* Compute reflector heights based entirely on your input instructions
  ```sh
  python3 gnssIR_lomb.py aaaa YYYY doy nn plt
  ```
plt is 1 for a plot and 0 for not. nn is the snr type again (e.g. 99)

* I also made an option that is meant to let you look at a particular frequency, rather than
all frequencies.  Such an example would be:
  ```sh
  python3 gnssIR_lomb.py aaaa YYYY doy nn plt -fr 20 -amp 15
  ```
which would mean only show L2C frequency (which I call 20) and use 15 as the amplitude requirement

As an example, I'm providing an snr98 file for smm3 on doy 253 and year 2018. Only one arc
of satellite 1 is stored here, so as to reduce the size of the file.


There is also the ability to look at a single satellite. Type gnssIR_lomb.py to see options.
