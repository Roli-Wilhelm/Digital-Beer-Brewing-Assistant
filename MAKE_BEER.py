#!/usr/bin/env python
import smtplib
import os, glob, time, re
import timeit
import datetime
from dateutil.relativedelta import relativedelta

##############
### Inputs ###
##############
Beer_Name = 'Age of Consent'
Mashing_Temp = 25	#In Celcius
Mashing_Duration = 1	#In Minutes
Boil_Temp = 30		#In Celcius
Boil_Duration = 1	#In Minutes
#Time_To_1st_Hopping = 0
Cool_Temp = 20		#In Celcius
Duration_of_Ferment = 8 #In Weeks

#####################
### House-keeping ###
#####################

# E-mail information
fromaddr = 'roliwilhelmr@gmail.com'
toaddrs  = 'roliwilhelm@gmail.com'
username = 'roliwilhelm'
password = 'zlzhstwzyitxzbkb'

# GPIO Probe Set-up and Locations
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# Convert Units
Mashing_Duration = Mashing_Duration * 60
Boil_Duration = Boil_Duration * 60

def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp():
	lines = read_temp_raw()

	if lines[0].strip()[-3:] == 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
		equals_pos = lines[1].find('t=')	#position of equals sign
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0

		return temp_c

# Starting Information
Start_Temp = read_temp()
Date = str(datetime.date.today())
Start = timeit.default_timer()

# Calculate End Dates for Beer
Primary_end = str(datetime.date.today() + relativedelta(days=+5))
Secondary_end = str(datetime.date.today() + relativedelta(weeks=int(Duration_of_Ferment)))

#####################
### Start Process ###
#####################
Beer = 'Mashing'

while Beer == 'Mashing':

	pi_temp = read_temp()

	print "Temperature is Now: "+str(pi_temp)+"deg C. Tracking to Mash Temp of: "+str(Mashing_Temp)+"deg C"

	# Notification of Mashing Temp
	if pi_temp > Mashing_Temp:
		print "Mash Temperature Reached..."
		Mash_Temp = pi_temp
		Mash_Start = timeit.default_timer()
		PreMash_Time = Mash_Start - Start
		PreMash_Time = PreMash_Time / 60

		# E-mail
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(fromaddr, toaddrs, 'Mash has reached '+str(Mashing_Temp)+'deg C\n')
		server.quit()

		# Let Mash for Mashing Duration
		print "Mashing for "+str(Mashing_Duration/60)+"min"
		time.sleep(int(Mashing_Duration))
		Beer = 'Boil'

		# E-mail (Notify to increase temperature for boil)
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(fromaddr, toaddrs, 'Mashing time complete. Heat to Boil')
		server.quit()
		
		Boil_Start_Temp = read_temp() 
		Boil_Start = timeit.default_timer()

	time.sleep(10)


###########
#Start Boil
###########
while Beer == 'Boil':
	pi_temp = read_temp()

	print "Temperature is Now: "+str(pi_temp)+"deg C. Tracking to Boiling Temp of: "+str(Boil_Temp)+"deg C."

	# Notification of Boiling Temp
	if pi_temp > Boil_Temp:
		print "Boil Temperature Reached..."
		Boil_Temp = pi_temp
		Boil_End = timeit.default_timer()
		Boil_Heating = Boil_End - Boil_Start
		Boil_Heating = Boil_Heating / 60

		# E-mail
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(fromaddr, toaddrs, 'Boiling temparature has been reached '+str(Boil_Temp)+'deg C\nBoiling will proceed for the next'+str(Boil_Duration)+'min\n')
		server.quit()

		# Let Boil for Boil Duration
		print "Boiling for "+str(Boil_Duration/60)+"min"
		time.sleep(Boil_Duration)
		Beer = 'Cool'

		# E-mail (Notify to turn off heat and begin cooling)
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(fromaddr, toaddrs, 'Boil time complete. Please start cooling the wort.\n')
		server.quit()

		Cool_Start_Temp = read_temp() 
		Cool_Start = timeit.default_timer()

	time.sleep(10)


##############
#Start Cooling
##############
Beer = 'Cool'

while Beer == 'Cool':
	pi_temp = read_temp()

	print "Temperature is Now: "+str(pi_temp)+"deg C. Tracking to Boiling Temp of: "+str(Cool_Temp)+"deg C."

	# Notification of Mashing Temp
	if pi_temp < Cool_Temp:
		print "Cool Temperature Reached..."
		Cool_Temp = pi_temp
		Cool_End = timeit.default_timer()
		Cool_Time = Cool_End - Cool_Start
		Cool_Time = Cool_Time / 60

		# E-mail
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(fromaddr, toaddrs, 'Wort has cooled to '+str(Cool_Temp)+'deg C\nBrewing Reminder Set Complete. Happy Fermenting!')
		server.quit()

		Beer = 'Fermentable'
		print "Beer is..."+Beer

	time.sleep(10)

# Calculate End Time
End = timeit.default_timer()
Total_Time = End - Start
Total_Time = float(Total_Time) / 60

# Calculate Rates
Mash_Ramp_Rate = str(PreMash_Time / (Start_Temp - Mash_Temp))
Boil_Ramp_Rate = str(Boil_Heating / (Boil_Start_Temp - Boil_Temp))
Cool_Ramp_Rate = str(Cool_Time / (Cool_Start_Temp - Cool_Temp))

output = open(Beer_Name+".batch.craft.history","w")

output.write(' '.join([
	"BATCH NAME:",
	Beer_Name,
	"\nBATCH DATE:",
	Date,
	"\n\nSTART TEMP:",
	str(Start_Temp) + "deg C",
	"\nSTARTED MASH @,",
	str(Mash_Temp) + "deg C",
	"\nTIME TO GET TO MASH TEMP:",
	str(PreMash_Time) + "min",
	"\nTIME TO BRING TO BOIL:",
	str(Boil_Heating) + "min",
	"\nTIME TO COOL DOWN:",
	str(Cool_Time) + "min",
	"\nTOTAL TIME FROM START TO FINISH:",
	str(Total_Time),
	"\n\nRAMPING SPEEDS:",
	"\nRAMP TO MASH TEMP:",
	str(Mash_Ramp_Rate) + "C/min",
	"\nRAMP TO BOIL:",
	str(Boil_Ramp_Rate) + "C/min",
	"\nRAMP TO COOL TEMP:",
	str(Cool_Ramp_Rate) + "C/min",
	"\n\nDATE TO TRANSFER FROM PRIMARY:",
	Primary_end,
	"\nDATE TO END FERMENTATION:",
	Secondary_end,
	"\n\nHappy Fermenting"
]))

output.close()

# E-mail
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)
server.sendmail(fromaddr, toaddrs, ' '.join([
	"BATCH NAME:",
	Beer_Name,
	"\nBATCH DATE:",
	Date,
	"\n\nSTART TEMP:",
	str(Start_Temp) + "deg C",
	"\nSTARTED MASH @,",
	str(Mash_Temp) + "deg C",
	"\nTIME TO GET TO MASH TEMP:",
	str(PreMash_Time) + "min",
	"\nTIME TO BRING TO BOIL:",
	str(Boil_Heating) + "min",
	"\nTIME TO COOL DOWN:",
	str(Cool_Time) + "min",
	"\nTOTAL TIME FROM START TO FINISH:",
	str(Total_Time),
	"\n\nRAMPING SPEEDS:",
	"\nRAMP TO MASH TEMP:",
	str(Mash_Ramp_Rate) + "C/min",
	"\nRAMP TO BOIL:",
	str(Boil_Ramp_Rate) + "C/min",
	"\nRAMP TO COOL TEMP:",
	str(Cool_Ramp_Rate) + "C/min",
	"\n\nDATE TO TRANSFER FROM PRIMARY:",
	Primary_end,
	"\nDATE TO END FERMENTATION:",
	Secondary_end,
	"\n\nHappy Fermenting"
]))

server.quit()
