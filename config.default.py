global loads
loads = {}

inverter_ip = "192.168.8.1" # Default ip address in case it can't find it
inverter_type = "TCP" # connection can be TCP or RTU
connection_port = "/dev/ptyp0"
connection_baudrate = 9600
connection_stopbits = 1
connection_bytesize = 8
connection_parity = 'E'
inverter_port = 502
slave = 0x00 # seems the dongle uses 0x01 for the slave id
model = "Huawei"
location = "main"
strings = 1
timeout = 3
has_optim = True # if your inverter doesn't return optimizer info
scan_interval = 30
info_interval = 60 * 60 * 3
influxdb_ip = "127.0.0.1"
influxdb_port = 8086
influxdb_user = "user_name"
influxdb_password = "password"
influxdb_database = "logger"
influxdb_longterm = "logger_lt"
influxdb_downsampled = "logger_ds" # you don't access this one through the logger. It is updated by influxdb and you can query it through grafana
influxdb_ssl = True
influxdb_verify_ssl = False
offset_ab = -0.2
offset_a = -0.5
offset_b = 1.5
extra_load = 1.0 # watts this is a permanent load not measured by the smart meter
# 1W represents 0.72 kWh a month. Adjust this to refflect your offset
billing_date = 18
billing_period = 2
billing_offset = 1
billing_window = 6  # in number of periods. Usually billing_period * billing_window would be 12 (a year length)
                    # or 0 if you don't have net metering and you only consider the current bill
latitude = lat
longitude = longitude
forecast_capacity = 10 # in kW
tilt = my_tilt
azimuth = 180   # 0 north, 180 south
time_zone = 'your timezone'  # If you need a timezone, try https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
solcast_key = "your_key"
install_date = "20yy-mm-dd"
site_UUID = "xxxx-xxxx-xxxx-xxxx"
site_UUID2 = "" #if you have a "second site" with solcast you cand add the forecasts
site_UUID3 = ""
soltun = True # also skipped if solfor not equals 1
solfor = 1 # 0 off, 1 rooftop, 2 world pv power
supla_api = ""
supla_dev_id = 0
#  Log in to supla account. click on your MEW-01 and You have ID. Not ID from "My supla", but ID visible after click on MEW-01 device  Thanks to bdkacz for his contribution
debug = False
daily_reports = True
has_ESU = False
#emailing info
email_sent = ""
fromaddr = "datalogger@my_domain.com"
toaddrs = "me@my_domain.com"
mail_pass = "secret email password"
mail_server = ""  # mail.my_domain.com
mail_port = 465
diverters = False
#as an example using 2 diverters, but you can use as many as you want.
diverters_loads = {0: 2400, 1: 800, 2: 800}

diverters_io = {0 : ("gpio", 17), 1 : ("gpio", 27), 2 : ("gpio", 22)} #replace to reflect the output type and address
# read https://gpiozero.readthedocs.io/en/stable/recipes.html#pin-numbering

# The load won't activate until the day set below. Time is assumed to be 0 hours
diverters_holiday = {0 : "2020-10-25", 1 : "2020-11-14", 2 : "2020-11-14"}

#Higher priority will be first on and last off. If same priority any can be first or last
#If priority is -1, then it won't activate at that hour

#This would be the default schedule
#the load tuple is (load, priority, pstart, pstop, start_delay, stop_delay, spiky)
divert = {0: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
          1: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
          2: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
          3: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
          4: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
          5: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
          6: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
          7: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
          8: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
          9: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         10: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         11: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         12: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         13: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         14: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         15: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         16: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         17: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         18: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         19: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         20: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         21: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         22: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)},
         23: {(0, -1, 2800, -100, 0, 0, 1.35), (1, 5, 1000, 100, 0, 0, 1.35), (2, 1, 1000, 200, 0, 0, 1.5)}}
