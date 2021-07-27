import time
from influxdb import InfluxDBClient
import config
import utils


flux_client = InfluxDBClient(host=config.influxdb_ip,
                             port=config.influxdb_port,
                             username=config.influxdb_user,
                             password=config.influxdb_password)


midnight  = int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 23:59:59", "%m/%d/%Y %H:%M:%S"))) + 1

print(time.ctime(midnight))


utils.fill_blanks(flux_client, midnight)
