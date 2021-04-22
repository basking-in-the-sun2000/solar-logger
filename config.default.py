global loads
loads = {}

inverter_ip = "192.168.8.1" # Default ip address in case it can't find it
inverter_port = 502
slave = 0x00
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
latitude = lat
longitude = longitude
forecast_capacity = 10 # in kW
tilt = my_tilt
azimuth = 180   # 0 north, 180 south
time_zone = 'your timezone'  # If you need a timezone, try https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
solcast_key = "your_key"
install_date = "20yy-mm-dd"
site_UUID = "xxxx-xxxx-xxxx-xxxx"
soltun = True # also skipped if solfor not equals 1
solfor = 1 # 0 off, 1 rooftop, 2 world pv power
supla_api = ""
supla_dev_id = 0
debug = False
#emailing info
email_sent = ""
fromaddr = "datalogger@my_domain.com"
toaddrs = "me@my_domain.com"
mail_pass = "secret email password"
mail_server = ""  # mail.my_domain.com
mail_port = 465
diverters = False
#as an example using 2 diverters, but you can use as many as you want.
diverters_loads = {0: 2000, 1: 800}

diverters_io = {0 : ("gpio", 10), 1 : ("gpio", 11)} #replace to reflect the output type and address

# The load won't activate until the day set below. Time is assumed to be 0 hours
diverters_holiday = {0 : "2020-10-25", 1 : "2020-10-25"}

#Higher priority will be first on and last off. If same priority any can be first or last
#If priority is -1, then it won't activate at that hour

#This would be the default schedule
#the load tuple is (load, priority, pstart, pstop)
divert = {0: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
          1: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
          2: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
          3: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
          4: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
          5: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
          6: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
          7: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
          8: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
          9: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         10: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         11: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         12: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         13: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         14: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         15: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         16: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         17: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         18: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         19: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         20: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         21: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         22: {(0, 2, 3500, 200), (1, 2, 1500, 200)},
         23: {(0, 2, 3500, 200), (1, 2, 1500, 200)}}
