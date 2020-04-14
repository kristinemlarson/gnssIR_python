# gnssIR_lomb.py, rinex2snr.py, and quickLook.py

gnssIR_lomb.py computes reflector heights (RH) from GNSS data.

rinex2snr.py translates the RINEX files into SNR files, which are fed into gnssIR_lomb.py

quickLook.py will try to give you a quick assessment of a file wihtout dealing
with the details associated with gnssIR_lomb.py.

Other things to know: I only support python3. The library dependencies 
are provided in the pyproject.toml file (I am using a package 
manager called poetry). 

The RH estimation depends on satellite elevation angle, not time. This can
cause complications for tides where large RH changes occur and time matters.
Data arcs should not cross midnite because you can end up using data that are 
as much as 24 hours apart to compute a single RH.
This doesn't matter for snow applications.
When I get a chance, I will be adding a RH dot correction which is needed for tides.
Again, this effect can be ignored for snow/ice reflections.

A simple refraction error correction has been added to gnssIR_lomb.py. You can turn
it on/off by setting the RefractionCorrection variable


April 2020
Added an optional year_end option so you can process multiple years with one command.
works the same way as doy_end.

Changed the source of the nav messages. It checks CDDIS, SOPAC, and the NGS.

July 2, 2019
I have added another code (quickLook.py) that will give you a "quick and dirty" evaluation
of the data for a single site. It has the nice advantage that it will make a SNR file for you if your
RINEX file is in your working directory or if it is stored at one of three main archives (UNAVCO, SOPAC, and SONEL).

September 13, 2019
gnssIR_lomb.py will now attempt to make a SNR file for you if one does not exist on your machine.
This will be GPS satellites only.

September 22, 2019
I have added a lot of error checking to make sure you are using proper inputs 
and that you have put the required files in the correct place (i.e. executables
and inputs).


WARNING: These codes do not calculate soil moisture.

# Installing the code

You need to define (at least) three environment variables:

* EXE = where the Fortran translator executables will live. Also the code that
translates certain kinds of RINEX files is needed and will be stored in this directory.  
I do not control these codes - but they are very important
modules in the GPS/GNSS communities.

* ORBITS = where the GPS/GNSS orbits will be stored (nav directory for GPS only and 
sp3 subdirectory for multi GNSS). These files are only 
used in the Fortran conversion code from RINEX to SNR.

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
RINEX rabbit hole. There is a list of static executables at the 
bottom of this page, http://www.unavco.org/software/data-processing/teqc/teqc.html
It needs to be stored in the EXE directory.


# Making SNR files

The python driver is called rinex2snr.py. 

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
option if you want to do true multi-GNSS reflectometry. 
2. sp3 - is using the IGS sp3 file, so again, your RINEX file does not have to be be GPS only, but
you won't get any non-GPS data because it doesn't have the orbit.
3. gbm - is currently my only option for getting a multi-GNSS orbit file.  This is also 
in sp3 format. The gbm file comes from the group at GFZ.  


If the orbit files don't already exist on your system, the rinex2snr.py code attempts 
to pick them up for you. They are then stored in the ORBITS directory.

Unless the RINEX data are sitting in your working directory, I believe the code attempts to 
pick up your RINEX file from UNAVCO, SOPAC, and SONEL. There is a high-rate option, but I have 
not extensively tested it.  It only works for UNAVCO. There is also a decimator, but it uses teqc 
to do that decimation.

The SNR files created by this code are stored in REFL_CODE/YYYY/snr

It is very common for GPS archives to store files in the Hatanaka (compressed) format. 
You cannot do GNSS IR without the ability to read Hatanaka files.  In particular, you 
need the Hatanaka decompression code (see above) to translate this.  
You need to put it in the EXE area. It is called CRX2RNX.

# Running the reflector height (gnssIR_lomb.py) code


* It needs a SNR file. It tries ot make it for you if it does not exist. But if you do this, it will assume 
you only have GPS data.


* The code assumes you are going to have a working directory for input and outputfiles.  
The environment variable for this - REFL_CODE - is described above.  

* put the gpt_1wa.pickle file in the REFL_CODE/input area. This file is used for the refraction correction.

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

* User inputs for the Lomb Scargle Periodogram calculation  

This should be stored in a file called REFL_CODE/input/aaaa 
See sample file called input_smm3_example. I also have a python script that will make
this file for you: make_input_file.py
It requires several inputs, so use the help option. 
It requires lat/lon/height does not need to be very precise.  This 
is only used for the refraction correction, so you can enter 0,0,0 if you aren't using that.

* Output: Your output files will go in REFL_CODE/YYYY/results/aaaa 
This is basically a text listing of individual arc reflector heights. 

```sh
maxF is the reflector height in meters
sat is satellite number, where 1-32 is for GPS, 
101-199 is for Glonass, 201-299 is for Galileo, 301-399 for Beidou
Azim is average azimuth over a given track, in degrees.
Amp is the peak spectral amplitude in volts/volts
eminO and emaxO are the observed min and max elevation angles in the track
Nv: number of observations used in the Lomb Scargle Periodogram (LSP)
```

freq is the frequency used. There is no industry standard here - so 
I am defining them as follows:
```sh
1 GPS L1
2 GPS L2
20 GPS L2C (using current list of L2C transmitting satellites)
5 GPS L5
101 Glonass L1
102 Glonass L2
201, 205, 206, 207, 208: Galileo frequencies
302, 306, 307 : Beidou  
 ```

rise is an integer value to tell you whether a satellite arc is rising (1) or setting (-1)

PkNoise is the spectral amplitude divided by an average noise value calculated
for a reflector height range you prescribe in the code.

DelT is the arc length in minutes

MJD is modified julian date  

refr-appl is 1 if refraction correction applied and otherwise 0


# Usage- some examples


* Compute reflector heights based entirely on your input instructions
  ```sh
  python gnssIR_lomb.py aaaa YYYY doy nn plt
  ```
plt is 1 for a plot and 0 for not. nn is the snr type again (e.g. 99)

* I also made an option that is meant to let you look at a particular frequency, rather than
all frequencies.  Such an example would be:
  ```sh
  python gnssIR_lomb.py aaaa YYYY doy nn plt -fr 20 -amp 15
  ```
which would mean only show L2C frequency (which I call 20) and use 15 as the amplitude requirement

As an example, I'm providing an snr98 file for smm3 on doy 253 and year 2018. Only one arc
of satellite 1 is stored here, so as to reduce the size of the file.

There is also the ability to look at the results for a single satellite. 

# Usage of quickLook Code
The gnssIR_lomb.py code requires you have set up some instructions for analyzing your data, i.e.
which frequencies you want to use, the lat/long/ht for the refraction correction.
If you don't want to bother with all of that - and just want a quick look to see if it is even worth
your time to analyze the data at a site, you can try quickLook.py.  You just give 
it the station name, year, doy of year,
and SNR format (99 is usually a good start). It will go pick up 
the RINEX data and translate it for you.
There are stored defaults for analyzing the spectral characteristics of 
the data.  If you want to override those
run quickLook.py -h 

This code needs the environment variables to exist, i.e. ORBITS and REFL_CODE and EXE. 

Examples:

*  python quickLook.py gls1 2011 271 99  (this uses defaults, which are usually ok for cryosphere)
ice/snow reflections)
* python quickLook.py rec1 2008 271 99  (this is an example where the system fails to find this file at UNAVCO)
* python quickLook.py smm3 2019 100 99 -h1 10 -h2 20 -e1 5 -e2 15  (example for overriding the defaults because this is a tall site)


# Publications
* There are A LOT of publications about GPS/GNSS interferometric reflectometry.
If you want something with a how-to flavor, try this, which is open option: 
https://link.springer.com/article/10.1007/s10291-018-0744-8

Also look to my website, https://kristinelarson.net
