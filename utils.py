import config
import time
import solcast
from influxdb import InfluxDBClient
import re
import emails


def fill_blanks(flux_client, midnight):
    k = 0
    s = ("SELECT last(P_daily) as P_daily FROM %s where time < %s group by time(1d) tz('%s');") % (config.model, str((midnight - 24 * 3600) * 1000000000), config.time_zone)
    zeros=flux_client.query(s, epoch='ns', database=config.influxdb_downsampled)
    daily = list(zeros.get_points(measurement=config.model))
    print("starting")
    for i in daily:
        if ((i['P_daily'] == None) or (i['P_daily'] == 0)):
            continue

        s = ('SELECT first(P_Exp) as P_Exp FROM %s_daily where time < %s and time > %s group by time(1d);') % (config.model, str(i['time']), str(i['time'] - 3600 * 24 * 1000000000) )
        zeros=flux_client.query(s, database=config.influxdb_longterm)
        q = list(zeros.get_points(measurement=config.model))
        if len(q) > 0:
            continue

#        j = (int(time.mktime(time.strptime(i['time'], "%Y-%m-%dT%H:%M:%SZ"))))
        s = ('SELECT first(M_PTot) as M_PTot_first, last(M_PTot) as M_PTot_last, first(M_PExp) as M_PExp_first, last(M_PExp) as M_PExp_last, first(P_accum) as P_accum_first, last(P_accum) as P_accum_last, max(P_daily) as P_daily, max(P_peak) as P_peak, max(Temp) as Temp  FROM "%s" where time < %s and time > %s and time < %s') % (config.model, str(i['time']), str(i['time'] - 24 *3600 * 1000000000), str((midnight - 24 * 3600) * 1000000000))

        try:
            zeros=flux_client.query(s, database=config.influxdb_downsampled)
            m = list(zeros.get_points(measurement=config.model))
            if (len(m) > 0 and len(m[0]) > 0):
                daily1 = {}
                if m[0]['M_PTot_last'] > 0 and m[0]['M_PTot_first'] > 0:
                    daily1['P_Grid'] = float(m[0]['M_PTot_last'] - m[0]['M_PTot_first']) + config.extra_load * 24 / 1000
                    if config.debug:
                        print(s)
                        print(daily1['P_Grid'])
                        print(float(m[0]['M_PTot_last'] - m[0]['M_PTot_first']))
                        print(config.extra_load * 24 / 1000)
                        print(str(time.ctime(i['time'] / 1000000000)))
                else:
                    daily1['P_Grid'] = config.extra_load * 24 / 1000 # bit weird adding a load to the grid when no meter

                if m[0]['M_PExp_last'] > 0 and m[0]['M_PExp_first'] > 0:
                    daily1['P_Exp'] = float(m[0]['M_PExp_last'] - m[0]['M_PExp_first'])
                else:
                    daily1['P_Exp'] = float(0.0) # no meter

                if m[0]['P_daily'] > 0:
                    daily1['P_daily'] = float(m[0]['P_daily'])

                if m[0]['Temp'] != None:
                    daily1['Temp'] = float(m[0]['Temp'])

                daily1['P_peak'] = float(m[0]['P_peak'])
                daily1['P_Load'] = float(daily1['P_daily'] - daily1['P_Exp'] + daily1['P_Grid'])

                if len(daily1) < 5:
                    continue

                if daily1['P_Exp'] < daily1['P_daily'] / 3 and daily1['P_Exp'] != 0:
                    continue
                s = ('SELECT last(Start) as Start, last(Shutdown) as Shutdown, max(Insulation) as Insulation from %s_info where time < %s and time > %s') % (config.model, str(i['time'] + 4 * 3600 * 1000000000), str(i['time'] - (24 * 3600 - 1) * 1000000000))
                zeros=flux_client.query(s, database=config.influxdb_database)
                q = list(zeros.get_points(measurement=config.model+"_info"))
                try:
                    daily1["Insulation"] = float(q[0]["Insulation"])
                except:
                    pass
                try:
                    daily1["Start"] = q[0]["Start"]
                    daily1["Shutdown"] = q[0]["Shutdown"]
                except:
                    s = ('SELECT first(P_active) from %s where P_active > 0 and time < %s and time > %s') % (config.model, str(i['time']), str(i['time'] - 24 * 3600 * 1000000000))
                    zeros=flux_client.query(s, epoch="s", database=config.influxdb_downsampled)
                    q = list(zeros.get_points(measurement=config.model))
                    try:
                        daily1["Start"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(q[0]["time"]))
                    except:
                        print("no start")

                    s = ('SELECT last(P_active) from %s where P_active > 0 and time < %s and time > %s') % (config.model, str(i['time']), str(i['time'] - 24 * 3600 * 1000000000))
                    zeros=flux_client.query(s, epoch="s", database=config.influxdb_downsampled)
                    q = list(zeros.get_points(measurement=config.model))
                    try:
                        daily1["Shutdown"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(q[0]["time"]))
                    except:
                        print("no stop")

                s = ('SELECT cumulative_sum(integral("power90")) /3600  as power90, cumulative_sum(integral("power10")) /3600  as power10, cumulative_sum(integral("power")) /3600  as power FROM "forcast" WHERE time < %s and time > %s group by time(1d)') % (str(i['time']), str(i['time'] - 24 * 3600 * 1000000000))
                zeros = flux_client.query(s, database=config.influxdb_database)
                q = list(zeros.get_points(measurement="forcast"))

                try:
                    if len(q) > 0:
                        daily1['f_power'] = float(q[0]['power'])
                        daily1['f_power10'] = float(q[0]['power10'])
                        daily1['f_power90'] = float(q[0]['power90'])
                except:
                    print("no forecasts")

                k += 1
                if config.debug:
                    print(i["time"])
                    print(time.ctime(i['time'] / 1000000000 - 24 * 3600))
                    print((daily1))

                write_influx(flux_client, daily1, config.model+"_daily", config.influxdb_longterm, i['time'] - 24 * 3600 * 1000000000)

        except Exception as e:
            print("fill_blanks error: %s" % str(e))

            print(m)
            continue

        if config.debug:
            print("filled "+str(k)+" daily blanks")

def write_influx(flux_client, measurement, iden, db, t = 0):
    if flux_client is not None:
        metrics = {}
        tags = {}
        if t > 100000000000:
            metrics['time'] = t

        metrics['measurement'] = iden
        tags['location'] = config.location
        if iden == "supla":
          for x in measurement:
             measurement[x]=float(measurement[x])

        metrics['tags'] = tags
        for x in measurement:
            if type(measurement[x]) == float:
                measurement[x]=round(measurement[x], 4)
        metrics['fields'] = measurement
        metrics =[metrics, ]
        try:
            target=flux_client.write_points(metrics, database=db)
            if not target:
                if config.debug:
                    print(vars(target))
#           print(metrics)
            return target

        except Exception as e:
            print("write_influx error: %s" % str(e))
            ok = False
            if config.debug:
                print("error")
                print(metrics)
                print(db)
                print()
            return False

def send_measurements(m_start, m_end, flux_client):
    if (not config.soltun) or (config.solfor != 1):
        return

    slices = 5
    s = ('SELECT mean("P_active") as "power" FROM "%s"  WHERE time >= %s and time <= %s GROUP BY time(%sm) fill(none)') % (config.model, str(m_start*1000000000), str(m_end*1000000000), slices)
    if config.debug:
        print(s)
        print("Start: " + time.ctime(m_start))
        print("End:   " + time.ctime(m_end))

    zeros=flux_client.query(s, database=config.influxdb_database)
    m = list(zeros.get_points(measurement=config.model))
    measurements = []
    for i in m:
        if i['power'] == 0:
            continue

        temp = {}
        temp['total_power'] = str(round(i['power'], 3))
        j = int(time.mktime(time.strptime(i["time"], "%Y-%m-%dT%H:%M:%SZ")))
        temp['period_end'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(j + 60 * slices))
        temp['period'] = 'PT'+str(slices)+'M'
        measurements.append(temp)
    #   print(measurements)
    try:
        roof = solcast.post_rooftop_measurements(config.site_UUID, measurements, api_key=config.solcast_key)

    except Exception as e:
        print("send_measurements error: %s" % str(e))
        print("solcast not receiving tuning")
        if config.debug:
            print(vars(roof))

def update_balance(flux_client, t):
    try:
        s = ("select last(Bal) from Huawei_daily where time > now() - %dd;") % (config.billing_period * 35)
    #    print(s)
        zeros=flux_client.query(s, epoch='ns', database=config.influxdb_longterm)
        last_bal = list(zeros.get_points(measurement=config.model + "_daily"))

        s = ("select P_Exp, P_Grid, Adj, Bal from Huawei_daily where time > %d;") % (last_bal[0]['time'])
    #    print(s)
        zeros=flux_client.query(s, epoch='ns', database=config.influxdb_longterm)
        last_bal = list(zeros.get_points(measurement=config.model + "_daily"))

        sum = 0
    #    print(" data")
        for i in last_bal:
            if (i['Adj'] != None):
    #            print(time.ctime(i['time']/1e9))
    #            print("adj", i['Adj'] )
                sum = sum + i['Adj']
            sum = sum + i['P_Exp'] -i['P_Grid']

            #    print("sum ", sum)
            #    print("days: ", (i['time'] - last_bal[0]['time']) / 1e9 / 24 / 3600)

        if sum < 0:
            s = ("select Bal from Huawei_daily where time > now() - %dd;") % (config.billing_period * 32 * config.billing_window)
    #        print(s)
            zeros=flux_client.query(s, epoch='ns', database=config.influxdb_longterm)
            last_bal = list(zeros.get_points(measurement=config.model + "_daily"))

    #        for i in last_bal:
    #            print(time.ctime(i['time']/1e9), i['Bal'])

    #        print("\n\nbalancing run")
            for key, value in enumerate(last_bal):
    #            print (key, value)
                if value['Bal'] > 0:
                    if last_bal[key]['Bal'] > -1 * sum:
                        last_bal[key]['Bal'] = last_bal[key]['Bal'] + sum
                        sum = 0.0
                    elif last_bal[key]['Bal'] < -1 * sum:
                        sum = sum + last_bal[key]['Bal']
                        last_bal[key]['Bal'] = 0.0

                    write_influx(flux_client, {'Bal': float(last_bal[key]['Bal'])}, config.model + "_daily", config.influxdb_longterm, int(last_bal[key]['time']))
                    if sum == 0:
                        break

#            print("\n\nfinal balance data")
#            for value in last_bal:
#                print(time.ctime(value['time']/1e9), value['Bal'])

        write_influx(flux_client, {'Bal': float(sum)}, config.model + "_daily", config.influxdb_longterm, int(t * 1e9))

    except Exception as e:
        print("update_balance error: %s" % str(e))


def check_default_files():

    errors = ''

    file = open("config.py", "r")
    file1 = re.findall("([^=\r\n ]+) =.+\n", file.read())
    file.close()

    file = open("config.default.py", "r")
    file2 =  re.findall("([^=\r\n ]+) =.+\n", file.read())
    file.close()


    for i in file2:
        if i in file1:
            pass
        else:
            print("config file missing parameter: ",'\033[1m' + i + '\033[0m')
            errors = errors + "\nconfig.py file: missing parameter: " + i


    file = open("Huawei.py", "r")
    file1 = re.findall("([^\'\": \{\},\r\n\t]+)[\'\"]:.+\n", file.read())
    file.close()

    file = open("Huawei.default.py", "r")
    file2 =  re.findall("([^\'\": \{\},\r\n\t]+)[\'\"]:.+\n", file.read())
    file.close()


    for i in file2:
        if i in file1:
            pass
        else:
            print("Huawei file missing parameter: ",'\033[1m' + i + '\033[0m')
            errors = errors + "\nHuawei.py file: missing parameter: " + i

    if errors != '':
        errors = "You need to update your files. Look in the default file for the missing parameters\n\n" + errors
        print(errors)
        emails.send_mail(errors)
        exit()
