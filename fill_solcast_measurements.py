import solcast
from influxdb import InfluxDBClient
import time
import config
import utils

flux_client = InfluxDBClient(host=config.influxdb_ip,
                             port=config.influxdb_port,
                             username=config.influxdb_user,
                             password=config.influxdb_password)


midnight = (int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 00:00:00", "%m/%d/%Y %H:%M:%S"))))

utils.send_measurements(0, midnight, flux_client)
