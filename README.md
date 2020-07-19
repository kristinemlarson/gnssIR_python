# Overview Comments on this Repository

The goal of this repository is to help you compute (and evaluate) GNSS 
based reflectometry parameters using geodetic data. This method is often 
called GNSS-IR, or GNSS Interferometric Reflectometry. There are three main codes:

* **rinex2snr.py** translates RINEX files into SNR files needed for analysis.

* **gnssIR_lomb.py** computes reflector heights (RH) from GNSS data.

* **quickLook.py** gives you a quick (visual) assessment of a file without dealing
with the details associated with gnssIR_lomb.py.

This code requires python3. The library dependencies 
are provided in the pyproject.toml file (I am using a package manager called poetry). 

The primary output of the code is Reflector Height (RH). RH estimation 
depends on the satellite elevation angle, not time. This can
cause complications for tides where large RH changes occur and time matters.
Data arcs should not cross midnite because you can end up using data that are 
as much as 24 hours apart to compute a single RH.
This doesn't matter much for snow applications. When I get a chance, I will be 
adding a RH dot correction which is also needed for tides.
Again, this effect can be ignored for snow/ice reflections.

A simple refraction error correction is available. You can turn
it on/off by setting the RefractionCorrection variable.

This code does not correct for antenna phase centers. This is part
of the reason that L1 will give a different answer than L2, for some sites. 
For many applications the antenna offsets do not matter. For users who want to use 
GPS signals as an ITRF-defined tide gauge, the antenna calibrations will be needed.

# Recent Updates

July 2020
I have made a lot of small changes - mostly to increase capability for multi-GNSS.
archive is now an input for rinex2snr.py. So if you know where a file is, you can set that
and the code will run faster. Currently allowed archives:

unavco, sopac, cddis, sonel, ga (geoscience Australia), nz (New Zealand), and bkg

Currently allowed orbits: 

nav - GPS broadcast 

igs (IGS final), igr (IGS rapid), jax (JAXA), gbm (GFZ rapid), grg (CNES), wum (Wuhan Ultra), sha (Shanghai)

screenstats and compress are now boolean inputs to gnssIR_lomb.py

JAX orbits required a change to gnssSNR, so you will need to download a new version.
The Wuhan orbits (which are 48 hours long) required a bit of a trick which hopefully you will not notice.

June 2020
Changed access to CDDIS archive to be secure ftp capable, per their instructions
https://cddis.nasa.gov/Data_and_Derived_Products/CDDIS_Archive_Access.html

May 2020
Added more documentation and examples. Allow peak2noise as standard input for gnssIR_lomb.py

April 2020

A boolean (wantCompression) has been added that will xz compress snr files.  Just an option 
in case you have limited disk space.

I recently added the ability to analyze RINEX 3 files. Either you provide the files or 
it looks for them at CDDIS and UNAVCO. Those are the only allowed archive options. Since the RINEX translators
require RINEX 2.11, the version 3 files are translated to 2.11 using the gfzrnx 
program.  If you don't install gfzrnx, you can't use RINEX 3 in this code.

I added an optional year_end option so you can process multiple years with one command. It 
works the same way as doy_end.

I changed the preferred source of the nav messages. It checks CDDIS, SOPAC, and then the NGS.

September 13, 2019

If you set seekRinex = True, gnssIR_lomb.py will now attempt to make a SNR 
file for you if one does not exist on your machine.
This will be GPS satellites and SNR option 99 only. The default is seekRinex =False

September 22, 2019

I have added a lot of error checking to make sure you are using proper inputs 
and that you have put the required files in the correct place (i.e. executables
and inputs).


**These codes do not calculate soil moisture.**

# Installing the code

You need to define (at least) three environment variables:

* EXE = where various RINEX executables will live.  See below for details.

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


# Python libraries
python 3.7, numpy, matplotlib, scipy, and wget 

# Non-Python Code 

All executables must be stored in the EXE directory

* RINEX Translator for GPS, the executable must be called gpsSNR.e, https://github.com/kristinemlarson/gpsonlySNR

* RINEX translator for multi-GNSS, the executable must be called gnssSNR.e, https://github.com/kristinemlarson/gnssSNR 

* CRX2RNX, Compressed to Uncompressed RINEX, http://terras.gsi.go.jp/ja/crx2rnx.html 

* teqc is not required, but highly recommended if you are going down the 
RINEX rabbit hole. There is a list of static executables at the 
bottom of [this page](http://www.unavco.org/software/data-processing/teqc/teqc.html)

* gfzrnx is only required if you plan to use the RINEX 3 option. Executables available from the GFZ,
http://dx.doi.org/10.5880/GFZ.1.1.2016.002


# Making SNR files from RINEX files

The python driver is called **rinex2snr.py**. A sample call would be:


python rinex2snr.py at01 2019 75 66 gbm

where: 

* at01 is the station name
* 2019 is the year 
* 75 is the day of year (doy)
* 66 is the snr option type (see below for more information).  
* The last input is the orbit type.

If your station name has 9 characters, the code assumes you are looking for a 
RINEX 3 file. However, it will store the SNR data using the normal 
4 character name.

I generally run a lowercase shop. I am not 100% positive that it is always required. If the archives
use capital letters, then of course, that is taken into account.  But I will then save them as lower case
after they are converted.

The snr options are always two digit numbers.  Choices are:

* 99 is elevation angles of 5-30 degrees  (most applications)
* 88 is elevation angles of 5-90 degrees
* 66 is elevation angles less than 30 degrees
* 50 is elevation angles less than 10 degrees (tall, high-rate applications)

Legal orbit types:

* nav - is using the GPS nav message. The main plus is that it is available in near 
real-time.  A nav file only has GPS orbits in it, so you should not use this 
option if you want to do true multi-GNSS reflectometry. 

* sp3 - is using the IGS sp3 file, so again, your RINEX file does not have to be be GPS only, but
you won't get any non-GPS data because it doesn't have the orbit.

* gbm - is currently my only option for getting a multi-GNSS orbit file.  This is also 
in sp3 format. The gbm file comes from the group at GFZ. There are other good multi-GNSS files,
but I picked this because it has Beidou. However, it currently takes a few days to show up 
in the archives, so you cannot use it and expect near real-time results.

If the orbit files don't already exist on your system, the rinex2snr.py code attempts 
to pick them up for you. They are then stored in the ORBITS directory.

Unless the RINEX data are sitting in your working directory, I believe the code attempts to 
pick up your RINEX file from UNAVCO, SOPAC, and SONEL, but generally 
only low-rate (15 or 30 sec) data are accessed.
There are some other download functions in gps.py - but I do have not implemented them all. 
Feel free to borrow those codes.

There is a high-rate option, but it only works for UNAVCO. Use -rate 1 to get 1 second data.

There is also a decimation option, but it uses **teqc** to do that decimation. If you have not 
installed teqc, it will not work.  Example call:  -dec 30 will decimate to 30 seconds.

The SNR files created by this code are stored in REFL_CODE/YYYY/snr in a subdirectory 
with your station name on it.

# Usage of quickLook.py Code

Before using the **gnssIR_lomb.py** code, I recommend you try **quickLook.py** first. This allows you
to quickly test various options (elevation angles, frequencies, azimuths) before spending
the time needed to set up the required inputs for the gnssIR_lomb.py code.

The required inputs are:

* station name 
* year 
* doy of year 
* SNR format (99 is usually a good start). 

If the SNR file has not been previously stored, you can provide a properly named RINEX file 
(lowercase only) in your working directory. If it doesn't find a file in either of these places, it 
will try to pick up the RINEX data from various archives and translate it for 
you into the correct SNR format. There are stored defaults for analyzing the 
spectral characteristics of the SNR data.  If you want to override those, run quickLook.py -h 

ALthough the quickLook.py code is simpler than **gnssIR_lomb.py**, it still needs the environment variables 
to exist, i.e. ORBITS, REFL_CODE, and EXE. 

**Examples:**

* python quickLook.py gls1 2011 271 99  (this uses defaults, which are usually ok for the cryosphere)
* python quickLook.py rec1 2008 271 99  (this is an example where the system fails to find this file at UNAVCO)
* python quickLook.py smm3 2019 100 99 -h1 10 -h2 20 -e1 5 -e2 15  (example for overriding the defaults because 
this site is much taller than the default, ~16 meters)

# Running the Reflector Height Code (gnssIR_lomb.py) 

put the gpt_1wa.pickle file in the REFL_CODE/input area. This file is used for the refraction correction.

**Inputs**

Your snr files need to live in REFL_CODE/YYYY/snr/aaaa, where YYYY is 4 character
year and aaaa is station name. The SNR files must use my naming conventions: 

  aaaaDDD0.yy.snrnn

```sh
where aaaa is a 4 character station name
DDD is day of year
yy is two character year
0 is always zero (it comes from the RINEX spec)
nn is a specific kind of snr file (99, 66, and 50 are the most commonly used)
```

Your analysis strategy should be stored in a file called REFL_CODE/input/aaaa, where aaaa is the station name.
See [this annotated file](input_smm3_example) for more information.

I have a python script that will make this file for you: 

make_input_file.py  

It requires several inputs, so use the help option. The lat/lon/height values do 
not need to be very precise, as this is only used for the refraction 
correction. You can enter 0,0,0 if you aren't using that.

**Outputs**

Your output files will be stored in REFL_CODE/YYYY/results/aaaa 

This is basically a text listing of each satellite arc's reflector height. 
[Here is a sample output file, with some comments on top](p038_001.txt)

I use the following conventions to define the different GNSS frequencies:

```sh
1 GPS L1
2 GPS L2
20 GPS L2C (using the list of L2C transmitting satellites from 2019)
5 GPS L5
101 Glonass L1
102 Glonass L2
201, 205, 206, 207, 208: Galileo frequencies
302, 306, 307 : Beidou  
 ```

# gnssIR_lomb.py Examples

Compute RH based entirely on your input instructions for station p041, 
year 2020, day of year 105, and SNR format type 99

  ```sh
  python gnssIR_lomb.py p041 2020 105 99 1 
  ```
The last input says to make plots.  If you set it to zero, it won't make plots.

Let's say you want to override your instructions and only look at one frequency:
  ```sh
  python gnssIR_lomb.py p041 2020 105 99 1  -fr 20 -amp 10
  ```
This means only show L2C frequency and use 10 as the amplitude requirement

Let's say you only want to look at satellite 15
  ```sh
  python gnssIR_lomb.py p041 2020 105 99 1  -sat 15 
  ```
Once you have the instruction sets up, most people want to analyze an entire dataset. If you wanted
to analyze an entire year:
  ```sh
  python gnssIR_lomb.py p041 2019 1 99 0 -doy_end 365
  ```

Note that I have turned off the plots with the zero after the 99 and I am using the optional 
doy_end flag. There is also an optional
year_end flag that you could use if you had multiple years of data.

# Cryosphere Example
LORG is a very good site for GNSS-IR. The GPS equipment was installed on the Ross Ice Shelf in November 2018 and was
removed the following year. It is pretty clear in all directions, so there is little to no azimuth restrictions
needed. It is flat - so I would suggest using most low elevation angles. It also has the 
nice attribute that the engineers that set up the site tracked **modern** GPS signals such as L2C 
and L5. The signals are in the RINEX files, so you do not have to make a special request. (Warning: This is not
always the case). Steps to follow to analyze the data from this site:

[The data for LORG are archived at unavco.](https://www.unavco.org/data/gps-gnss/data-access-methods/dai2/app/dai2.html#4Char=LORG) From the UNAVCO site, figure out the start and end date for the data. Convert the month and day to day of year using **ymd.py**.  Then use **rinex2snr.py** to pick up the files and convert them.  For 2018, it would be:

```sh
python rinex2snr.py lorg 2018 332 99 nav -doy_end 365

```

Then go ahead and make SNR files for the 2019 data.

Now look at the spectral characteristics of one day. [The default for quickLook.py is to look at L1.](LORG/Figure_1.png) 

```sh
python quickLook.py lorg 2018 350 99 
```

Reflector height is plotted on the x-axis. If you have a nice strong peak 
in the periodogram (y-axis), that means you have a good RH estimation.  The main ways this code
decides a peak is good is by requiring a minimum amplitude for the periodogram
(which you can set). The other was is to set a peak to noise ratio, which is the 
peak amplitude divided by the mean amplitude over a given region, which for most
sites is 0.5-6 meters. Why don't we include zero? You cannot reliably measure RH 
below 0.5.


The four quadrants shown are for the northwest, northeast, 
southwest, and southeast quadrants around the GPS antenna. All quadrants look reasonable (strong peaks in 
many different satellites), although
there is some residual noise at hte low RH values in the NW quadrant. 
You can eliminate that noise by setting
[the minimum h1 value explicitly](LORG/Figure_1excludeLowRH.png), i.e.

```sh
python quickLook.py lorg 2018 350 99  -h1 0.75 
```

You can also look at just the [L2C satellites](LORG/Figure_2.png)


```sh
python quickLook.py lorg 2018 350 99  -fr 20
```

If you are curious what a ["L2P" signal](LORG/Figure_2_nosonice.png)
looks like for this receiver, and why I do not like it, specify a non-L2C transmitting satellite
(in this case satellite 2) and set a very low required amplitude such as 1, i.e. 

```sh
python quickLook.py lorg 2018 350 99  -fr 2 -sat 2 -amp 1
```

Note that there are two peaks - and this does not mean there are really two reflectors. It means
the receiver is using both frequencies to retrieve your data, and that shows up in the SNR data.
The second peak is expactly where the L2 peak should be multiplied by F1/F2.

[The L5 signal is pretty nice too.](LORG/Figure_5.png)

Why are the peaks not perfectly aligned on the x-axis? Because the ice sheet is not a perfectly flat
reflector. If you want to see what flat really looks like, [find an airport. This is my own personal 
favorite airport.](LORG/Figure_2_p038.png)

To retrieve all the results for LORG you would use **gnssIR_lomb.py**. You typically will not be looking
at figures when you do that. And you need to have picked an analysis strategy, i.e. which frequencies,
which elevation angles, and RH restrictions. You can start out using mine, which should be stored
in the input directory in the filename [lorg](LORG/lorg)

```sh
python gnssIR_lomb.py lorg 2019 1 99 0 -doy_end 365 

```
```sh
python gnssIR_lomb.py lorg 2018 1 99 0 -doy_end 365 
```

You can compile and look at the RH results yourself (in REFL_CODE/2018/results/lorg and REFL_CODE/2019/results/lorg)
**plot_results.py** compiles the individual RH values and outputs a single RH each day. It uses a median filter
to eliminate gross outliers and requires a minimum number of tracks to compute a daily average.
You choose the value of both of these parameters. For the lorg example, I used this command:

```sh
python plot_results.py lorg 2018 2019 0.3 50 -txtfile lorg.txt
```

Which means 50 tracks are required each day and the median filter value was 0.3 meters.  It makes  
[a RH plot](LORG/lorg_RH.png) and if requested, [a text file](LORG/lorg.txt). If you look at the output
file of results you will see that many more than 50 values are made per day - so I could have been 
a little more retrict.  Similarly with 0.3 meters. I certainly do not discourage you from looking at the 
results for your site and making site-specific decisions. At this site I was able to use multiple frequencies.
The observation restriction would definitely depend on how many frequencies you had available.


# Publications
* There are A LOT of publications about GPS/GNSS interferometric reflectometry.
If you want something with a how-to flavor, try this paper, which is [open option](https://link.springer.com/article/10.1007/s10291-018-0744-8)

Also look to the publications page on my [personal website](https://kristinelarson.net/publications)
