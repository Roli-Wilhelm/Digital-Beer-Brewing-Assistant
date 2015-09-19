Script to Automate Steps in Beer Brewing
========================================
During my trials and tribulations over the past 3 years in beer brewing, I disliked only two things:
1) Washing, sterilizing and bottling (which I have now replaced with kegging)
2) Hovering over the mash (or the wort) to measure the temperature with a candy thermometer.

I had a Raspberry Pi kicking around that I'd been playing with to develop skills in converting physical measurments into 
digital signals for environmental monitoring and other computatational work. I have designed this script to assist the 
process of beer-brewing by tracking temperature, notification of temperature thresholds and timing.It also spits out information
on total timing, estimated dates for when fermentation is complete and how long it took to ramp from mashing to boiling and from 
boiling to cooled. 

Mostly, I'm happy that I can now start the brewing process and go about my business until my phone reminds me (via e-mail)
that the next step is ready.

Usage:
=======
./MAKE_BEER.py


Detailed Requisites:
====================
- High Temp Waterproof DS18B20 Digital temperature sensor + 4.7k resistor 
- Raspberry Pi & Hardware Described HERE: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware
- The directory structure and functioning input of temperature data described HERE: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20

Notes: In order for the High Temp probe to work, I had to lower the resistance to 4.7k (the resistor that comes with the probe)
and increase the voltage to 5V (from 3.3V). You will have to do the same if you get a temperature readout of 85000.