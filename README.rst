This is a datalogger for a solar inverter. Tried to make it so it can be used with any other inverter, if you create a file with all the register and status constants

I'm certain that by not having access to other inverters and only knowing mine, I did throw in some bias into the code. However, hope it isn't bad

So for now it is configured for a Huawei's Sun2000 usl0 version, but probably should run with other residential models



This code was inspired on a series of other repositories to as a guideline to create the current datalogger. Including portions from https://github.com/meltaxa/solariot/

You will need these python packages pymodbus, influxdb, pytz 

Also influxdb (the database itself) and grafana

Also included the solcast folder from basking-in-the-sun2000/Radiation, hopefully FidFenix will incorporate the changes and keep it current

For grafana you will need these plugins:
-agenty-flowcharting-panel
-blackmirror1-singlestat-math-panel
-graph
-yesoreyeram-boomtable-panel


Description of files

-write_solar populates the db with expected production values. These are daily average for the month in kWh. The values should account for your system, layout, shadowing, depreciation, etc, throughout the life of the system

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

-grafana.json is the main dashboard for the logger

-status.json shows the historical values of the status registers



Setup
After installing influxdb, grafana, the required python packages and grafana plugins, you might want to change the config.py values to suit your installation.

Operation
Running it shouldn't need much if all the requirements are satisfied

cd to the directory with the code
python3 main.py

It should be able to run in the background by adding an ampersand (&) at the end. Been running it off a raspberry pi 4 and has behaved well.  Influx is a bit demanding, up to 40% of the cpu


Notes
It uses solcast.com, so you need to create an account (free) and a rooftop site. It pulls the forecast several times during the day, but only sends the measurements at midnight. 

Also updates the daily summary data at midnight. In case you missed that time, there are tools that allow you to send data to solcast or update the daily db

After tuning (sending your data), they claim I'm getting 0.97 correlation of the data. There is a adjustment factor in the Energy pane of grafana, for 0.82. I'm hoping with use it will improve. The time period is hardwired to 5 minutes, not sure it makes much difference if you use 10m or even 30m. However, since we are only sending data for the active production once a day, it sounded as a reasonable value.

Also in grafana, there are several limits that show values in different colors. You can adjust these to suit your site. The solcast forecasts include all 3 sets. These are the regular, the 10th percentile (low scenario), and 90th percentile (high scenario) estimates. If you rather, you can delete the ones that don't suit you.

My system is new, so I have panes that show the behaviour throughout the day. If yours is older or don't care, you can swap the panes for daily behaviour instead. Just scroll down and move the panes up, or make your own.

