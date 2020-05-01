import solcast
from influxdb import InfluxDBClient
import time
import config

flux_client = InfluxDBClient(host=config.influxdb_ip,
                             port=config.influxdb_port,
                             username=config.influxdb_user,
                             password=config.influxdb_password)


midnight = (int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 00:00:00", "%m/%d/%Y %H:%M:%S"))))

slices = 5

s = ('SELECT mean("P_active") as "power" FROM "%s" where time > now() GROUP BY time(%sm) fill(none)') % (config.model, slices)

zeros=flux_client.query(s, database=config.influxdb_database)
    
m = list(zeros.get_points(measurement=config.model))


measurements = []
for i in m:
    if i['power'] == 0:
        continue
    temp = {}
    temp['total_power'] = str(round(i['power'],3))
    j = int(time.mktime(time.strptime(i["time"], "%Y-%m-%dT%H:%M:%SZ")))

    temp['period_end'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(j + 60 * slices ))
    temp['period'] = 'PT'+str(slices)+'M'
    measurements.append(temp)

roof = solcast.post_rooftop_measurements(config.site_UUID, measurements)
