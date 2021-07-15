#!/usr/bin/env python3
from influxdb import InfluxDBClient
import config
import time
import datetime
import utils


try:
	flux_client = InfluxDBClient(host=config.influxdb_ip,
								port=config.influxdb_port,
								username=config.influxdb_user,
								password=config.influxdb_password)
	
except Exception as e:
	print("main error: %s" % str(e))
	flux_client = None
	print("problem openning db")

s = ("select Adj from Huawei_daily tz('%s');") % (config.time_zone)
zeros=flux_client.query(s, epoch='ns', database=config.influxdb_longterm)
adj = list(zeros.get_points(measurement=config.model + "_daily"))

print("adjustment data")
for i in adj:
	print(i['time'],time.ctime(i['time']/1e9), i['Adj'])
adj_index = 0


s = ("select P_Exp, P_Grid, Adj from Huawei_daily tz('%s');") % (config.time_zone)
#s = ("select P_Exp, P_Grid from Huawei_daily;")

print("\n\nrun data")
zeros=flux_client.query(s, epoch='ns', database=config.influxdb_longterm)
daily = list(zeros.get_points(measurement=config.model + "_daily"))
last = -1
sum = 0
sum_array = []
last_day = daily[0]["time"]
for i in daily:
	if (i['Adj'] == None):
		if (adj[adj_index]['time'] - i['time']) / 1e9 / 24 / 3600 < 4 and  (adj[adj_index]['time'] - i['time']) / 1e9 / 24 / 3600 > -4:
			diff = (adj[adj_index]['time'] - i['time']) / 1e9 / 24 / 3600
		else:
			diff = 0
	else:
		diff = 0

	dt = datetime.datetime.fromtimestamp(i['time']/1e9 - (config.billing_date + diff - 1) * 24 * 3600)
#	print(dt.timetuple())

#	window = config.billing_window * config.billing_period
	window = 12

	m = dt.month - config.billing_offset
	m = (m + window) % window
	if (m == 0):
		m = window
		#	print(int(m))	
		#	print(int(m % config.billing_period))
		#	print(int(m / config.billing_period) )

	m = (int(m % config.billing_period != 0) + int(m / config.billing_period)) * config.billing_period + config.billing_offset + 1
	m = (m + window) % window
	if (m == 0):
		m = window

	if m != last:
		if m + config.billing_period == last + window:
			m = last
		elif last - m == config.billing_period:
			m = last


		#	print(int(m))
	if (i['Adj'] != None):
#		diff = (adj[adj_index]['time'] - i['time']) / 1e9 / 24 / 3600
		print(time.ctime(i['time']/1e9))
		print("adj", i['Adj'] )
#		print(sum)
		sum = sum + i['Adj']
		if (last == m):
			if (31 - dt.day < 7) and ((i['time'] - last_day) / 1e9 / 24 / 3600 > config.billing_period * 23):
				m = (m + window + config.billing_period) % window
				if (m == 0):
					m = window
		adj_index = adj_index + 1
		try:
			diff = adj[adj_index]['Adj'] + 1
		except:
			adj.append({'time': ((time.time() + 1e9) * 1e9), 'Adj':0})

	else:
		if m != last:
			if (adj[adj_index]['time'] - i['time']) / 1e9 / 24 / 3600  < 7:
#				print((adj[adj_index]['time'] - i['time']) / 1e9 / 24 / 3600)
				if (adj[adj_index]['time'] - i['time']) / 1e9 / 24 / 3600  > -7:
					m = last


	sum = sum + i['P_Exp'] -i['P_Grid']
#	print(time.ctime(i['time']/1e9), i['P_Grid']  - i['P_Exp'], sum)

	
	if (last != m):
#		diff = (adj[adj_index]['time'] - i['time']) / 1e9 / 24 / 3600
		last = m
#		print(time.ctime(i['time']/1e9))
		print(time.ctime(i['time']/1e9), i['P_Exp'] - i['P_Grid'], sum)
		print("sum ", sum)
		print("days: ", (i['time'] - last_day) / 1e9 / 24 / 3600)
		if ((i['time'] - last_day) / 1e9 / 24 / 3600 > config.billing_period * 23):
			sum_array.append([i['time']/1e9, sum])
		last_day = i['time']
		sum = 0
				
print("\n\nbalancing run")
for key, value in enumerate(sum_array):
	print (key, value)
	if value[1] > 0:
		for key1, value1 in enumerate(sum_array[1 + key:1 + config.billing_window + key]):
			if value1[1] < 0:
				if sum_array[key][1] > -1 * sum_array[1 +  key + key1][1]:
					sum_array[key][1] = sum_array[key][1] + sum_array[1 + key + key1][1]
					sum_array[1 + key + key1][1] = 0
				elif sum_array[key][1] < -1 * sum_array[1 +  key + key1][1]:
					sum_array[1 + key + key1][1] = sum_array[1 + key + key1][1] + sum_array[key][1]
					sum_array[key][1] = 0

print("\n\nfinal balance data")
for value in sum_array:
	print(time.ctime(value[0]), value[1])

for value in sum_array:
	utils.write_influx(flux_client, {'Bal': float(value[1])}, config.model + "_daily", config.influxdb_longterm, int(value[0] * 1000000000))
