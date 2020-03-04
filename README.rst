This is a datalogger for a solar inverter. Tried to make it so it can be used with any other inverter, if you create a file with all the register and status constants

I'm certain that by not having access to other inverters and only knowing mine, I did throw in some bias into the code. However, hope it isn't bad

So for now it is configured for a Huawei's Sun2000 usl0 version, but probably should run with other residential models



This code is based on a series of other repositories to as a guideline to create the current datalogger

You will need these python packages pymodbus, influxdb, pytz 

Also influxdb (the database itself) and grafana

Also included the solcast folder from basking-in-the-sun2000/Radiation, hopefully FidFenix will incorporate the changes and keep it current

For grafana you will need these plugins:
-agenty-flowcharting-panel
-blackmirror1-singlestat-math-panel
-graph
-yesoreyeram-boomtable-panel


##Description of files

-scanner should allow to poll the inverterer for valid registers

-scanner2 will display the values of the registers listed in regs

-roofs_add_forcast will add the next few days forcasts from solcast to influxdb

-fill_measurements sends the recorded data from the inverter to solcast

-modbustcp utility for modbus

-last_adjustment allows to adjust the total energy balance (exported - from_grid + adj)

-Huawei contains the inverter's registers, status constants

-fill_blanks takes the data from the inverter (influxdb) and writes daily summaries

-config has the constant values for your site

-main is the code that runs all the time to gather and store data onto the database (influxdb)



##Operation
Running it shouldn't need much if all the requirements are satisfied

cd to the directory with the code
python3 main.py

It should be able to run in the background by adding an ampersand (&) at the end. Been running it off a raspberry pi 4 and has behaved well.  Influx is a bit demanding, up to 40% of the cpu