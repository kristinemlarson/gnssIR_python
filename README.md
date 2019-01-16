#gnssIR_lomb
This is a first cut at a python code that will compute reflector heights fairly automatically.
Some things to know:

This is for python3. 

The library dependencies are at the top of the two main python scripts: gnssIR_lomb.py and gps.py.
The latter is a bunch of helper scripts I have written - not all are for reflector height calculation.

I do not (yet) check for data arcs that cross midnite.  This has to be fixed
for tides. This has much more limited impact on snow where daily averages are typically
used.  The refraction error correction needs to be added for tides.
I will also be adding a RH dot correction.

# Inputs

The expected SNR files must be translated from RINEX before you run this code. 
This code is called gnssSNR or RinexSNR and was distributed at the GPS Tool Box. 
(when the US government is open)

https://www.ngs.noaa.gov/gps-toolbox/GNSS-IR.htm

The paper that describes these (and other) tools is open access here:
https://link.springer.com/article/10.1007/s10291-018-0744-8

The code assumes you are going to have a working diretory for input and outputfiles.  
An environment variable is set at the top of gnssIR_lomb.py, so you should change that for your work area.
If I call that REFL, then your snr files should be in REFL/YYYY/snr/aaaa, where YYYY is 4 character
year and aaaa is station name.  

* SNR file. You must use the following name conventions:

  aaaaDDD0.yy.snrnn

where aaaa is a 4 character station name
DDD is day of year
yy is two character year
0 is always zero (it comes from the RINEX spec)
nn is a specific kind of snr file (99, 77, and 50 are the most commonly used)


* Input instructions

This should be stored in a file called REFL/input/aaaa where aaaa is station name. 
See sample file called input_smm3_example. 

* Output
Your output files will go in REFL/YYYY/results/aaaa 
This is basically a text listing of individual arc reflector heights. 

maxF is the reflector height in meters
sat is satellite number, where 1-32 is for GPS, 101-199 is for Glonass, 201-299 is for Galileo
Azim is average azimuth over a given track, in degrees.
Amp is the spectral amplitude in volts/volts
eminO and emaxO are the observed min and max elevation angles in the track
Nv: number of observations used in the Lomb Scargle Periodogram (LSP)

freq is the frequency used:
1 GPS L1
2 GPS L2
20 GPS L2C
5 GPS L5
101 Glonass L1
102 Glonass L2
201, 205, 206, 207, 208: Galileo frequencies
301 etc: Beidou  
rise is an integer value, rise = 1 and set = -1
PkNoise is the spectral amplitude divided by an average noise value calculated
for a reflector height range you prescribe in the code.

EXAMPLE year, doy, maxF,sat,UTCtime, Azim, Amp,  eminO, emaxO,  Nv,freq,rise,Edot, PkNoise
 2018 253 15.200   1 15.367 105.22  29.95   5.03  14.97  288   1 -1 -0.00693   5.26
 2018 253 15.260   1 10.454 201.50  26.56   5.02  14.97  273   1  1  0.00731   4.70
 2018 253 14.725   1  2.785 303.43  25.90   5.03  14.99  362   1 -1 -0.00553   4.89
 2018 253 15.175   2  3.501  74.13  21.63   5.02  14.98  360   1  1  0.00556   4.42
 2018 253 15.280   2 20.175 179.09  32.12   5.01  14.97  279   1 -1 -0.00717   4.85
 2018 253 15.060   2 15.264 271.00  38.34   5.03  14.97  297   1  1  0.00672   4.64
 2018 253 15.170   3 17.150  77.74  35.24   5.00  14.98  291   1 -1 -0.00688   4.68



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

* As a tide example, use station at01 from Alaska.  
  ```sh
python3 strip_snrfile.py at01 2018 182 98 1 -fr 5 -amp 10
  ```
This example only shows L5 data.  The file has Glonass and Galileo data in it, so you can try that too.
Sample output is in example3.png

There is also the ability to look at a single satellite. Type strip_snrfile.py to see options.
