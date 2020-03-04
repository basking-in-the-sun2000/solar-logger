import time
from influxdb import InfluxDBClient
import config

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


flux_client = InfluxDBClient(host=config.influxdb_ip,
							 port=config.influxdb_port,
							 username=config.influxdb_user,
							 password=config.influxdb_password)

							
midnight  = int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 23:59:59", "%m/%d/%Y %H:%M:%S"))) + 1 



s = ('SELECT first("P_Exp") as "P_Exp" FROM "%s_daily" where time < %s group by time(1d)') % (model, str((midnight ) * 1000000000))

zeros=flux_client.query(s, database=config.influxdb_longterm)
	
daily = list(zeros.get_points(measurement=config.model + "_daily"))

for i in daily:
	
	if not ((i['P_Exp'] == None) or (i['P_Exp'] == 0)):
		continue

	j = (int(time.mktime(time.strptime(i['time'], "%Y-%m-%dT%H:%M:%SZ"))))

	
	s = ('SELECT first(M_PTot) as M_PTot_first, last(M_PTot) as M_PTot_last, first(M_PExp) as M_PExp_first, last(M_PExp) as M_PExp_last, first(P_accum) as P_accum_first, last(P_accum) as P_accum_last, max(P_daily) as P_daily, max(P_peak) as P_peak, max(Temp) as Temp  FROM "%s" where time > %s and time < %s and time < %s ') % (config.model, str(j * 1000000000), str((j + 24 *3600) * 1000000000), str((midnight - 24 * 3600) * 1000000000))
		
	try:
		zeros=flux_client.query(s, database=config.influxdb_database)	
		m = list(zeros.get_points(measurement=config.model))
				
		if len(m[0]) > 0:
			daily = {}

			if m[0]['M_PTot_last'] > 0 and m[0]['M_PTot_first'] > 0:
				daily['P_Grid'] = float(m[0]['M_PTot_last'] - m[0]['M_PTot_first'])
			if m[0]['M_PExp_last'] > 0 and m[0]['M_PExp_first'] > 0:
				daily['P_Exp'] = float(m[0]['M_PExp_last'] - m[0]['M_PExp_first'])
			if m[0]['P_daily'] > 0:
				daily['P_daily'] = float(m[0]['P_daily'])
			if m[0]['Temp'] != None:
				daily['Temp'] = float(m[0]['Temp'])
			daily['P_peak'] = float(m[0]['P_peak'])
			daily['P_Load'] = float(daily['P_daily'] - daily['P_Exp'] + daily['P_Grid'])
			if len(daily) < 5:
				continue
			if daily['P_Exp'] < 10:
				continue
			
			write_influx(flux_client, daily, config.model + "_daily", config.influxdb_longterm, (j * 1000000000))
			
	except:
		continue
