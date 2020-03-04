import solcast
from influxdb import InfluxDBClient
import time
import pytz
import config

flux_client = InfluxDBClient(host=config.influxdb_ip,
							 port=config.influxdb_port,
							 username=config.influxdb_user,
							 password=config.influxdb_password)

def write_influx(flux_client, measurement, iden, db, t = 0):
	if flux_client is not None:
		metrics = {}
		tags = {}

		if t > 100000000000:
			metrics['time'] = t
		metrics['measurement'] = iden
		tags['location'] = config.location
		metrics['tags'] = tags
		metrics['fields'] = measurement
		metrics =[metrics, ]
		
		try:
			target=flux_client.write_points(metrics, database=db)
			print("ok")
		except:
			ok = False
			print("error")
			exit()

def forcast():
	global flux_client
	r1 = solcast.get_rooftop_forcasts(config.site_UUID)

	for x in r1.content['forecasts']:
		dt = x['period_end'] #- x['period']
		dt = dt.replace(tzinfo=pytz.timezone('UTC'))
		dt = dt.astimezone(pytz.timezone(config.time_zone))
		dt = time.mktime(dt.timetuple())

		measurement = {'power': float(x['pv_estimate']), 'power10': float(x['pv_estimate10']), 'power90': float(x['pv_estimate90']) }

		write_influx(flux_client, measurement, "forcast", config.influxdb_database, int(dt) * 1000000000)

	forcast_time = float(time.strftime("%H"))
	if (8 <= forcast_time < 16):
		forcast_time = 2 - (forcast_time % 2)
	else:
		forcast_time = 4 - (forcast_time % 4)

	forcast_time *= 3600
	forcast_time = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d %H:00:00', time.localtime(time.time()+forcast_time)), "%Y-%m-%d %H:%M:%S")))

	return forcast_time





forcast()