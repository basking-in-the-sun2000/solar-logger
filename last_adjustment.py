import time
import datetime
from datetime import timedelta
from influxdb import InfluxDBClient
import config

flux_client = InfluxDBClient(host=config.influxdb_ip,
                             port=config.influxdb_port,
                             username=config.influxdb_user,
                             password=config.influxdb_password)


#midnight = int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 23:59:59", "%m/%d/%Y %H:%M:%S"))) + 1

midnight = int(time.mktime(time.strptime( "2/18/2020 00:00:00", "%m/%d/%Y %H:%M:%S"))) 


#measurement = {'Insulation': 2.786, 'Temp': 35.8, 'P_Load': 33.330000000000126, 'P_daily': 29.53, 'P_Exp': 23.099999999999966, 'P_Grid': 26.90000000000009, 'P_peak': 9.669, 'Start': '2020-01-26 07:33:36', 'Shutdown': '2020-01-26 18:31:49'}
measurement = {'P_Exp': 0.0, 'P_Grid': 0.0, 'Adj': -45.3}

t = midnight

if flux_client is not None:
    metrics = {}
    tags = {}
    if t > 0:
        metrics['time'] = t * 1000000000
    metrics['measurement'] = config.model + "_daily"
    tags['location'] = config.location
    metrics['tags'] = tags
    metrics['fields'] = measurement
    metrics =[metrics, ]

    target=flux_client.write_points(metrics, database=config.influxdb_longterm)

