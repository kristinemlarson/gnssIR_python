# gnssIR_lomb.py, rinex2snr.py, and wrapper_quickLook.py

gnssIR_lomb.py computes reflector heights (RH) fairly automatically.
rinex2snr.py translates the RINEX files into SNR files, which are fed into gnssIR_lomb.py
wrapper_quickLook.py will try to give you a quick assessment of a file wihtout dealing
with the details associated with gnssIR_lomb.py.

Some things to know:

I only support python3. 

The library dependencies are provided in the pyproject.toml file (I am using a package manager called poetry).


The RH estimation depends on satellite elevation angle, not time. This can
cause complications for tides where large RH changes occur and time matters.
Data arcs should not cross midnite because you can end up using data that are 
as much as 24 hours apart to compute a single RH.
This doesn't matter for snow applications.
When I get a chance, I will be adding a RH dot correction which is needed for tides.
Again, this effect can be ignored for snow/ice reflections.

I recently added another code (rinex2snr.py) that allows the user 
to make the input files for the gnssIR_lomb.py code. I call these the SNR files. These are 
created from RINEX files. RINEX is the standard format for GPS/GNSS files.

A simple refraction error correction has been added.

July 2, 2019
I have added another code (wrapper_quickLook.py) that will give you a "quick and dirty" evaluation
of a single site. It has the nice advantage that it will make a SNR file for you if your
RINEX file is in your working directory or if it is stored at one of three archive (unavco,sopac, and sonel).


WARNING: These codes do not calculate soil moisture.

# Installing the code

You need to define three environment variables:

* EXE = where the Fortran translator executables will live. Also the code that
translates certain RINEX files is needed and will be stored in this directory.  
I do not control these codes - but they are very important
modules in the GPS/GNSS communities.

* ORBITS = where the GPS/GNSS orbits will be stored (nav directory for GPS only and 
sp3 subdirectory for multi GNSS). These files are only 
used in the fortran conversion code from RINEX to SNR.

* REFL_CODE = where the reflection code inputs (SNR files and instructions) and outputs (RH) 
will be stored (see below)

Optional environment variable 

* COORDS = where the coordinates are kept for sites with large 
position speeds, i.e. Greenland and Antarctica icesheets.
This is only used in the fortran conversion code - and samples are given 
with the source code.  If this file does not exist, it does not matter. 


Make sure you have installed all the required python libraries. 

Unless you already have codes to make my SNR files, you will need to 
install RINEX translators.  I have two of them. One is for people that only have 
GPS data - and thus uses the nav file for the orbits. 
The other translates all GNSS signals and uses a sp3 file.  Both 
codes are hosted at GitHub. 

# Non-Python Code 

* RINEX translator for multi-GNSS, which must be called gnssSNR.e, https://github.com/kristinemlarson/gnssSNR 
If the executable from this code is not gnssSNR.e, please change it and move it to the EXE directory

* RINEX Translator for GPS, which must be called gpsSNR.e, https://github.com/kristinemlarson/gpsonlySNR

* CRX2RNX, Compressed to Uncompressed RINEX, http://terras.gsi.go.jp/ja/crx2rnx.html This must be stored 
in the EXE directory.

* teqc is not required, but highly recommended if you are going down the 
RINEX rabbit hole.  There is a list of static executables at the 
bottom of this page, http://www.unavco.org/software/data-processing/teqc/teqc.html
It needs to be stored in the EXE directory.


# Making SNR files

The python driver is called rinex2snr.py. Make sure EXE is defined and the relevant 
executables are there.

A sample call of of the python driver rinex2snr.py would be:

python3 rinex2snr.py at01 2019 75 80 66 gbm

* at01 is the station name 
* 2019 is the year 
* 75 and 80 are the starting and ending day of years.
* 66 is the snr option type (see the translator code for more information).  
* The last input is the orbit type.

The snr options are always two digit numbers.  Choices are:

* 99 is elevation angles of 5-30 degrees 
* 88 is elevation angles of 5-90 degrees
* 66 is elevation angles less than 30 degrees
* 50 is elevation angles less than 10 degrees

Legal orbit types:

1. nav - is using the GPS nav message. The main plus is that it is available in near 
real-time.  A nav file only has GPS orbits in it, so you should not use this 
option if you want to do true multi-GNSS 
reflectometry. I pick my file up from SOPAC, but you can use other archives if you prefer.
2. sp3 - is using the IGS sp3 file, so again, your RINEX file should be GPS only. 
3. gbm - is now my only option for getting a multi-GNSS orbit file.  This is also 
in sp3 format. The gbm file comes from the group at GFZ.  


If the orbit files don't already exist on your system, the rinex2snr.py code attempts 
to pick them up for you. They are then stored in the ORBITS directory.

Unless the RINEX data are sitting there in your working directory, the code attempts to 
pick up your RINEX file from UNAVCO, SOPAC, and SONEL. I think there is a high-rate option, but I have 
not extensively tested it.  It only works for UNAVCO. 

The SNR files created by this code are stored in REFL_CODE/YYYY/snr

One more thing- it is very comon for GPS archives to store files in the Hatanaka (compressed) format.
So currently it tries to get the regular RINEX file but if that fails, it tries to download
Hatanaka format. You need the Hatanaka decompression code (see above) to translate this.  
You need to put it in the EXE area. It is called CRX2RNX.

# Running the RH (gnssIR_lomb.py) code


* The expected SNR files must be translated from RINEX before you run this code. 

* There are A LOT of publications about GPS/GNSS interferometric reflectometry.
If you want something with a how-to flavor, try this: 
https://link.springer.com/article/10.1007/s10291-018-0744-8

* The code assumes you are going to have a working directory for input and outputfiles.  
The environment variable for this - REFL_CODE - is described above.  

* put the gpt_1wa.pickle file in the REFL_CODE/input area

* Input: your snr files need to live in REFL_CODE/YYYY/snr/aaaa, where YYYY is 4 character
year and aaaa is station name.  The SNR file must use my naming conventions: 

  aaaaDDD0.yy.snrnn

```sh
where aaaa is a 4 character station name
DDD is day of year
yy is two character year
0 is always zero (it comes from the RINEX spec)
nn is a specific kind of snr file (99, 77, and 50 are the most commonly used)
```

* User inputs for the lomb scargle periodogram calculation  

This should be stored in a file called REFL_CODE/input/aaaa 
See sample file called input_smm3_example. 

* Output: Your output files will go in REFL_CODE/YYYY/results/aaaa 
This is basically a text listing of individual arc reflector heights. 

```sh
maxF is the reflector height in meters
sat is satellite number, where 1-32 is for GPS, 
101-199 is for Glonass, 201-299 is for Galileo, 301-399 for Beidou
Azim is average azimuth over a given track, in degrees.
Amp is the spectral amplitude in volts/volts
eminO and emaxO are the observed min and max elevation angles in the track
Nv: number of observations used in the Lomb Scargle Periodogram (LSP)
```

freq is the frequency used. There is no industry standard here - so 
I am defining them as follows:
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

(Note: this has changed since I wrote this description. I will update this when I 
get a chance) 

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


# Usage- some examples


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

There is also the ability to look at the results for a single satellite. 
Run gnssIR_lomb.py -h to see options.

# Usage of quickLook Code
The gnssIR_lomb.py code requires you have set up some instructions for analyzing your data, i.e.
which frequencies you want to use, the lat/long/ht for the refraction correction, blah blah blah.
And it requires you have previously translated a RINEX file into SNR format.
If you don't want to bother with all of that - and just want a quick look to see if it is even worth
your time to look at a site, you can try quickLook.py.  You just give it the station name, year, doy of year,
and translate format (99 is usually a good start). It will go pick up the RINEX data and translate it for you.
There are stored defaults for analyzing the spectral characteristics of the data.  If you want to override those
run quickLook.py -h 

Examples:

*  python quickLook.py gls1 2011 271 99  (uses defaults, which are usually ok for cryosphere 
ice/snow reflections)
* python quickLook.py rec1 2008 271 99 - example where the system fails to find this file at UNAVCO


