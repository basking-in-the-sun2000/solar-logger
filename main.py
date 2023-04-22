import os
if not os.path.exists("config.py"):
    import shutil
    shutil.copy2("config.default.py", "config.py")

import emails
import config
import utils
import divert
from modbus import connect_bus, read_registers, close_bus
import time
import datetime
import solcast
import pytz
from datetime import timedelta
from influxdb import InfluxDBClient
import supla_api
import re


def to_str(s):
    str = ""
    for i in range(0, len(s)):
        high, low = divmod(s[i], 0x100)
        if high != 0:
            str = str + chr(high)

        if low != 0:
            str = str + chr(low)

    return str

def to_U16(i):
    return i[0] & 0xffff

def to_I16(i):
    i = i[0] & 0xffff
    return (i ^ 0x8000) - 0x8000

def to_U32(i):
    return ((i[0] << 16) + i[1])

def to_I32(i):
    i = ((i[0] << 16) + i[1])
    i = i & 0xffffffff
    return (i ^ 0x80000000) - 0x80000000

def to_Bit16(i):
    return i[0]

def to_Bit32(i):
    return (i[0] << 16) + i[1]

def call_function(method_name, values):
    global ok
    method_name = "to_" + method_name
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(method_name)
    if not method:
        ok = False
        return -1

    try:
        return method(values)

    except Exception as e:
        print("call_function error: %s" % str(e))
        if config.debug:
            print("error in call_function")
            print(method_name, values)
#       close_bus(client)
#       gc.collect()
        ok = False
        return -1

def do_map(config, inverter):
    global client
    global register
    global measurement
    global info
    global status
#   global y_exp
    global c_exp
    global y_gen
    global c_gen
#   global y_tot
    global c_tot
    global c_peak
    global tmax
    global min_ins
    global c_stop
    global c_start
    global ok


    client = connect_bus(ip=config.inverter_ip,
                     PortN = config.inverter_port,
                     timeout = config.timeout)

    for register in inverter._register_map:
        k = 0
        while k < 4:
            try:
                result = read_registers(client, config.slave, inverter._register_map[register])
                if (result == -1) or (not ok):
                    ok = False
                    return False
                if result.isError():
                    time.sleep(2)
                    k += 1
                    if config.debug:
                        print("read register error", register, k)
                else:
                    break

            except Exception as e:
                time.sleep(2)
                k += 1
                if config.debug:
                    print("do_map error: %s" % str(e))
                    print("trying to recover", register, k)
            time.sleep(0.25)

        if k > 3:
            return True

        value = call_function(inverter._register_map[register]['type'], result.registers )
        if not ok:
            return False

        if ((inverter._register_map[register]['type'] != 'str') and (inverter._register_map[register]['scale'] != 1)):
            value = value / inverter._register_map[register]['scale']

        if (inverter._register_map[register]['units'] == 's' ):
            if (value > 2600000000):
                continue

            value = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(value))
        elif (inverter._register_map[register]['use'] == "stat"):
            value = inverter.status(register, value)
        else:
            j = 0

        if register == "P_daily":
            if value != 0:
                c_gen = value

            else:
                if c_gen != 0:
                    y_gen = c_gen

        elif register == "M_PExp":
            c_exp = value

        elif register == "M_PTot":
            c_tot = value

        elif register == "P_peak":
            c_peak = max(value,c_peak)

        elif register == "Temp":
            if 0 < value < 150:
                tmax = max(tmax, value)

        elif register == "Insulation":
            if 0 < value < 20:
                min_ins = min(min_ins, value)

        elif re.match("PV_U\d", register) != None:
            try:
                measurement["PV_Un"] = value + measurement["PV_Un"]
            except:
                measurement["PV_Un"] = value
        elif re.match("PV_I\d", register) != None:
            try:
                measurement["PV_In"] = value + measurement["PV_In"]
            except:
                measurement["PV_In"] = value

        elif register == "Start":
            c_start = value

        elif register == "Shutdown":
            c_stop = value

        if inverter._register_map[register]['use'] == "stat":
            status[register] = value

        elif (inverter._register_map[register]['use'] == "data") or (inverter._register_map[register]['use'] == "mult"):
            measurement[register] = value

        elif inverter._register_map[register]['use'] == "info":
            info[register] = value

    close_bus(client)
    return False

def forecast(h, midnight):
    def forehour(h):
        global c_start
        global c_stop

        p = " (\d\d):"
        t_start = re.findall(p, c_start)
        t_stop = re.findall(p, c_stop)
        try:
            t_start = int(t_start[0])
        except:
            t_start = 8

        try:
            t_stop = int(t_stop[0])
        except:
            t_stop = 20

        if config.debug:
            print(time.ctime(h))

        if config.site_UUID3 != "":
            i = 15
        elif config.site_UUID2 != "":
            i = 23
        else:
            i = 46

        forecast_time = h + int(max((t_stop - t_start) * 3600 / i, 25 * 60))

        if config.debug:
            print(t_start)
            print(t_stop)
            print(time.ctime(forecast_time))

        t = int(time.strftime("%H", time.localtime(forecast_time)))

        if t > t_stop - 1:
            forecast_time = time.mktime(time.strptime(time.strftime('%Y-%m-%d ' + str(t_start - 1) + ':45:00', time.localtime(time.time() + 24 * 3600)), "%Y-%m-%d %H:%M:%S"))

        elif t < t_start:
            forecast_time = time.mktime(time.strptime(time.strftime('%Y-%m-%d ' + str(t_start - 1) + ':45:00', time.localtime()), "%Y-%m-%d %H:%M:%S"))

        if config.debug:
            print("next forecast " + time.ctime(forecast_time))
        return int(forecast_time)

    global flux_client
    global forecast_array
    global daily_forecast
    global status
    global f_ratio

    if config.debug:
        print("in forecast")
#    print(status)

    forecast_time = forehour(time.time())
    t = time.time()

    if (h - t > 60):
        return(h)
    elif (forecast_time - t > 60 * 60):
        return(forecast_time)

    try:
        if (config.solfor == 1):
            r1 = solcast.get_rooftop_forecasts(config.site_UUID, hours=252, api_key=config.solcast_key)
            if config.site_UUID2 != "":
                r12 = solcast.get_rooftop_forecasts(config.site_UUID2, hours=252, api_key=config.solcast_key)
                for i in range(0, len(r12.content['forecasts'])):
                    if r1.content['forecasts'][i]["period_end"] == r12.content['forecasts'][i]["period_end"]:
                        r1.content['forecasts'][i]["pv_estimate"] = min((r1.content['forecasts'][i]["pv_estimate"] + r12.content['forecasts'][i]["pv_estimate"]) * f_ratio, config.forecast_capacity)
                        r1.content['forecasts'][i]["pv_estimate10"] = min((r1.content['forecasts'][i]["pv_estimate10"] + r12.content['forecasts'][i]["pv_estimate10"]) * f_ratio, config.forecast_capacity)
                        r1.content['forecasts'][i]["pv_estimate90"] = min((r1.content['forecasts'][i]["pv_estimate90"] + r12.content['forecasts'][i]["pv_estimate90"]) * f_ratio, config.forecast_capacity)
            if config.site_UUID3 != "":
                r12 = solcast.get_rooftop_forecasts(config.site_UUID3, hours=252, api_key=config.solcast_key)
                for i in range(0, len(r12.content['forecasts'])):
                    if r1.content['forecasts'][i]["period_end"] == r12.content['forecasts'][i]["period_end"]:
                        r1.content['forecasts'][i]["pv_estimate"] = min(r1.content['forecasts'][i]["pv_estimate"] + r12.content['forecasts'][i]["pv_estimate"] * f_ratio, config.forecast_capacity)
                        r1.content['forecasts'][i]["pv_estimate10"] = min(r1.content['forecasts'][i]["pv_estimate10"] + r12.content['forecasts'][i]["pv_estimate10"] * f_ratio, config.forecast_capacity)
                        r1.content['forecasts'][i]["pv_estimate90"] = min(r1.content['forecasts'][i]["pv_estimate90"] + r12.content['forecasts'][i]["pv_estimate90"] * f_ratio, config.forecast_capacity)
            if daily_forecast:
                r2 = solcast.get_wpv_power_forecasts(config.latitude, config.longitude, config.forecast_capacity,
                                                    tilt=config.tilt, azimuth=config.azimuth,
                                                    install_date = config.install_date, hours = 24,
                                                    api_key=config.solcast_key)

                daily_forecast = False
                sum1 = 0
                t1 = 0
                dtday = 0
                times = []
                for x in r1.content['forecasts'][:60]:
                    if x['pv_estimate']  == 0:
                        continue
                    dt = x['period_end']
                    dt = dt.replace(tzinfo=pytz.timezone('UTC'))
                    dt = dt.astimezone(pytz.timezone(config.time_zone))
                    dt = dt.timetuple()
                    if dt.tm_hour < 14:
                        if dtday == 0:
                            dtday = dt.tm_yday
                    if dtday != dt.tm_yday:
                        continue
                    dt = time.mktime(dt)
                    times.append(dt)
                    sum1 = sum1 + x['pv_estimate'] * 0.5
                    t1 = t1 + 0.5

                sum2= 0
                t2 = 0
                for x in r2.content['forecasts'][:60]:
                    if x['pv_estimate']  == 0:
                        continue
                    t2 = t2 + 0.5
                    dt = x['period_end']
                    dt = dt.replace(tzinfo=pytz.timezone('UTC'))
                    dt = dt.astimezone(pytz.timezone(config.time_zone))
                    dt = dt.timetuple()
                    dt = time.mktime(dt)
                    if dt in times:
                        pass
                    else:
                        continue

                    sum2 = sum2 + x['pv_estimate'] * 0.5


        elif (config.solfor == 2):
            r1 = solcast.get_wpv_power_forecasts(config.latitude, config.longitude, config.forecast_capacity,
                                                 tilt=config.tilt, azimuth=config.azimuth,
                                                 install_date = config.install_date, hours = 48,
                                                 api_key=config.solcast_key)

        else:
            return forehour(int(time.time() + 6 * 3600))

    except Exception as e:
        print("forecast error: %s" % str(e))
        print("solcast off-line")
        return forehour(int(time.time() + 30 * 60))

    try:
        forecast_array = {}
        for x in r1.content['forecasts']:
            dt = x['period_end']
            dt = dt.replace(tzinfo=pytz.timezone('UTC'))
            dt = dt.astimezone(pytz.timezone(config.time_zone))
            dt = time.mktime(dt.timetuple())
            if (config.solfor == 1):
                measurement = {'power': float(x['pv_estimate']), 'power10': float(x['pv_estimate10']), 'power90': float(x['pv_estimate90']) }

            elif (config.solfor == 2):
                measurement = {'power': float(x['pv_estimate'])}

            forecast_array[int(dt)] =  float(x['pv_estimate'])

            utils.write_influx(flux_client, measurement, "forcast", config.influxdb_database, int(dt) * 1000000000)

        if config.debug:
            print("done getting forecast")

    except Exception as e:
        print("forecast 1 error: %s" % str(e))
        print("error in forecast")
        return forehour(min(int(time.time() + 6 * 3600), midnight - time.altzone))

    return(forecast_time)

def supla():
    #api key
    token = config.supla_api
    try:
        api_client = supla_api.ApiClient(token, lambda msg: print(msg), lambda msg: print(msg))
        api_client.url == "https://svr28.supla.org/api/v2.3.16/"
        #id of meter  from server
        abc = api_client.find_channel(config.supla_dev_id)
        t = time.time()
        fazy = abc["state"]["phases"]
        for x in fazy:
            utils.write_influx(flux_client, x, "supla", config.influxdb_database, t)
            time.sleep(3)

    except Exception as e:
        print("supla error: %s" % str(e))
#        pass

def do_fratio(j):
    if config.sol_comp:
        try:
            if config.solfor == 1 or config.solfor == 2:
                s = "SELECT mean(r) as m, STDDEV(r) as av from (SELECT (P_daily / f_power * f_ratio) as r FROM Huawei_daily WHERE time >= " + str(j) + "ms -7d and time <= " + str(j) + "ms fill(1) tz('"+config.time_zone+"'))"
                if config.debug:
                    print(s)

                zeros=flux_client.query(s, database=config.influxdb_longterm)
                m = list(zeros.get_points(measurement=config.model+"_daily"))
                av = m[0]['m']
                sd = m[0]['av']

                if config.debug:
                    print("f_ratio average")
                    print(s)
                    print(m)
                    print(av, sd)

                s= "SELECT HOLT_WINTERS_WITH_FIT(first(r), 1, 7)  from (SELECT (P_daily / f_power * f_ratio) as r FROM Huawei_daily WHERE time >=  " + str(j) +"ms -10d and time <= " + str(j) +"ms tz('"+config.time_zone+"')) group by time(1d) tz('"+config.time_zone+"')"

                zeros=flux_client.query(s, database=config.influxdb_longterm, epoch="ms")
                m = list(zeros.get_points(measurement=config.model+"_daily"))

                if config.debug:
                    print(s)

                if len(m) > 0:
                    t = m[-1]['time'] + 24 * 3600 * 1000

                    if config.debug or True:
                        print("Holt")
                        print(s)
                        print(m)

                    if len(m) > 0 and t > 0:
                        q = round(m[-1]['holt_winters_with_fit'],4)
                        if av > 0.5 and av < 1:
                            if q > av + 2 * sd:
                                q = av + 2 * sd
                            if q < av - 2 * sd:
                                q = av - 2 * sd
                        if q > 1 or q < 0.5:
                            q = 1.0

                        if config.debug or True:
                            print("q= ", q)
                            return(float(q))
                else:
                    if av < 1 and av > 0.5:
                        print("no holt found")
                        return(float(av))
            else:
                if config.debug:
                    print("no forecasts")
                return(1.0)
        except Exception as e:
            print("do_fratio error: %s" % str(e))
            return(1.0)
    else:
        if config.debug:
            print("not sol_comp")
        return(1.0)


def main():
    global register
    global measurement
    global info
    global status
    global y_exp
    global c_exp
    global y_gen
    global c_gen
    global y_tot
    global c_tot
    global c_peak
    global tmax
    global min_ins
    global c_stop
    global c_start
    global client
    global flux_client
    global ok
    global forecast_array
    global loads
    global loops
    global daily_forecast
    global f_ratio

    config.loads = {}
    inverter_file = config.model
    if not os.path.exists(inverter_file + ".py"):
        import shutil
        shutil.copy2(inverter_file + ".default.py", inverter_file + ".py")


    inverter = __import__(inverter_file)
    if config.debug:
        print("Loaded: " + inverter_file)

    if config.debug:
        print("statring setup")
        print("opening modbus")

    client = connect_bus(ip=config.inverter_ip,
                         PortN = config.inverter_port,
                         timeout = config.timeout)
    if (client.socket == None):
        if config.debug:
            print("bad inverter ip")
            print("trying to find inverter")
        inverter_ip = inverter.inv_address()
        print(inverter_ip)
        if inverter_ip == "":
            close_bus(client)
            raise Exception("Can't find inverter")
        config.inverter_ip =inverter_ip

        client = connect_bus(ip=config.inverter_ip,
                         PortN = config.inverter_port,
                         timeout = config.timeout)

    print(config.inverter_ip)
    close_bus(client)
    time.sleep(1)

    if config.debug:
        print("opening db")

    try:
        flux_client = InfluxDBClient(host=config.influxdb_ip,
                                     port=config.influxdb_port,
                                     username=config.influxdb_user,
                                     password=config.influxdb_password)

    except Exception as e:
        print("main error: %s" % str(e))
        flux_client = None
        print("problem openning db")

    if config.debug:
        print("setting db")

    flux_client.create_database(config.influxdb_database)
    flux_client.create_database(config.influxdb_longterm)
    flux_client.create_database(config.influxdb_downsampled)
    if config.debug:
        print("setting params")

    last_loop = 0
    info_time = 0
    last_status = {}
    y_exp = 0
    c_exp = 0
    y_tot = 0
    c_tot = 0
    y_gen = 0
    c_gen = 0
    c_peak = 0
    c_start = ""
    c_stop = ""
    tmax = 0
    min_ins = 1000
    thread_time = [1]
    thread_mean = 1
    sleep = 0
    forecast_time = 0
    daily_forecast = True
    f_ratio = 1

    midnight = (int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 00:00:00", "%m/%d/%Y %H:%M:%S"))))
    s = ('SELECT %s FROM "%s" WHERE time >= %s and time <= %s and P_daily > 0') % ('max("M_PExp") as "M_PExp", max("M_PTot") as "M_PTot", max("P_accum") as "P_accum", max("P_daily") as "P_daily", max("Temp") as "Temp"', config.model, str((midnight - 24 * 3600)*1000000000), str(midnight*1000000000))
    zeros=flux_client.query(s, database=config.influxdb_database)
    m = list(zeros.get_points(measurement=config.model))
    try:
        y_exp = m[0]['M_PExp']
        y_tot = m[0]['M_PTot']
        y_gen = m[0]['P_daily']
        tmax  = m[0]['Temp']

    except Exception as e:
        print("main 1 error: %s" % str(e))
        y_exp = 0
        y_tot = 0
        y_gen = 0
        tmax = 0

    s = ('SELECT %s FROM "%s_info" WHERE time >= %s and time <= %s and Insulation > 0') % ('min("Insulation") as "Insulation"', config.model, str((midnight - 3600 * 24)*1000000000), str(midnight*1000000000))
    zeros=flux_client.query(s, database=config.influxdb_database)
    m = list(zeros.get_points(measurement=config.model+"_info"))
    try:
        if config.debug:
            print(m[0])

        min_ins = m[0]['Insulation']

    except Exception as e:
        print("main 2 error: %s" % str(e))
        if config.debug:
            print(s)

        min_ins = 1000

    if config.sol_comp:
        try:
            f_ratio = 1
            s = "SELECT f_ratio FROM Huawei_daily where time >= "+ str(midnight * 1000) +  "ms fill(1) tz('"+config.time_zone+"')"

            zeros=flux_client.query(s, database=config.influxdb_longterm, epoch="ms")
            m = list(zeros.get_points(measurement=config.model+"_daily"))

            if len(m) == 0 or m[0]['f_ratio'] == 1:
                f_ratio = do_fratio(midnight * 1000)
                measurement = {'f_ratio': f_ratio}
                utils.write_influx(flux_client, measurement, config.model + "_daily", config.influxdb_longterm, midnight * 1000000000)
            else:
                f_ratio = m[0]['f_ratio']

        except Exception as e:
            print("main f_ratio error: %s" % str(e))
            if config.debug:
                print(s)
            f_ratio = 1
    else:
        f_ratio = 1

    midnight = int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 23:59:59", "%m/%d/%Y %H:%M:%S"))) + 1

    utils.fill_blanks(flux_client, midnight)
    forecast_time = forecast(forecast_time, midnight)
    if ((float(time.strftime("%S")) % 60) > 1):
        time.sleep(59 - float(time.strftime("%S")))

    if config.debug:
        print("loop")

    ok = True
    low_prod = time.time() + 300

    while ok:
        current_time = time.time()
        if (current_time - last_loop + thread_mean >= int(config.scan_interval)):
            last_loop = current_time
            measurement = {}
            info = {}
            status = {}
            j = 0
            while do_map(config, inverter):
                j += 1
                if config.debug:
                    print(time.ctime(), register)
                    print("map looping")

                time.sleep(10)
                if j > 10:
                    if config.debug:
                        print("map infinite loop")

                    ok = False

                if not ok:
                    return -1

            if not ok:
                return -1

            current_time = time.time()
            if (current_time - info_time > config.info_interval):
                utils.write_influx(flux_client, info, config.model + "_info", config.influxdb_database)
                info_time = current_time
                if config.debug:
                    print(info)
                    print(y_exp)
                    print(c_exp)
                    print(y_tot)
                    print(c_tot)
                    print(y_gen)
                    print(c_gen)
                    print(c_peak)
                    print(c_start)
                    print(c_stop)
                    print(tmax)
                    print(min_ins)
                if info["Insulation"] > 0 and info["Insulation"] < 1.5:
                    emails.send_mail("Insulation low: " + str(info["Insulation"]))

            if config.debug:
                print("looking at low production")
                print(measurement)
                print(low_prod)

            i = 0
            j = 0

            measurement["PV_Un"] = measurement["PV_Un"] / config.strings

            try:
                for j in forecast_array:
                    if j > current_time:
                        break
                    i = j
                if float(time.strftime("%H")) > 12:
                    i = j
                if i == 0:
                    i = j
                if config.debug:
                    print(i)
                    print(j)
                    print(forecast_array[i])

                if (measurement["P_active"] * 2 < forecast_array[i]):
                    if (current_time > low_prod + 300):
                        emails.send_mail("low production: " + measurement["P_active"])
                else:
                    low_prod = current_time
            except:
                if config.debug:
                    print("no forcast in low production")
                    print(measurement["P_active"])
                    print(time.strftime("%H"))
                if measurement["P_active"] == 0:
                    if float(time.strftime("%H")) > 11 and float(time.strftime("%H")) < 15:
                        if (current_time > low_prod + 300):
                            emails.send_mail("low production: " + measurement["P_active"])
                else:
                    low_prod = current_time


            x = config.scan_interval - (float(time.strftime("%S")) % config.scan_interval)
            if x == 30:
                x = 0

            if (0.5 < x < 6):
                time.sleep(x - 0.05)

            if (config.diverters):
                changes = divert.check(measurement['M_P'], flux_client)
                for x in changes:
                    measurement["load_" + str(x)] = changes[x]
#                print(changes)
#                print(measurement)

            utils.write_influx(flux_client, measurement, config.model, config.influxdb_database)

            if (status != last_status):
#                print(status)
#                print(last_status)
                last_status = status.copy()
                if config.debug:
                    print(status)
                if ((status["Alarm1"] != "") or (status["Alarm2"] != "") or (status["Alarm3"] != "") or (status["Fault"] != '0')):
                    emails.send_mail("Help\r\n" + str(status))
                utils.write_influx(flux_client, status, config.model + "_stat", config.influxdb_database)

            if (measurement["Temp"] > 60):
                emails.send_mail("Temperatur high: " + str(measurement["Temp"]))

            if (config.supla_api != ""):
                #read from supla
                supla()

            thread_time.insert(0, time.time() - last_loop)
            if len(thread_time) > 5:
                thread_time.pop()

            loops = 0

            thread_mean = sum(thread_time) / len(thread_time)
            if (int(time.time()) > midnight):
                daily = {}
                daily['Insulation'] = float(min_ins)
                min_ins = 1000
                daily['Temp'] = float(tmax)
                tmax = 0
                s = 'SELECT cumulative_sum(integral("power90")) /3600  as power90, cumulative_sum(integral("power10")) /3600  as power10, cumulative_sum(integral("power")) /3600  as power FROM "forcast" WHERE time > now() -22h group by time(1d)'
                zeros = flux_client.query(s, database=config.influxdb_database)
                m = list(zeros.get_points(measurement="forcast"))
                daily['f_power'] = float(m[0]['power'])
                try:
                    daily['f_power90'] = float(m[0]['power90'])
                    daily['f_power10'] = float(m[0]['power10'])

                except Exception as e:
                    if config.debug:
                        print("main 3 error: %s" % str(e))
                    daily['f_power90'] = float(m[0]['power'])
                    daily['f_power10'] = float(m[0]['power'])


                s = 'SELECT cumulative_sum(integral("power90")) /3600  as power90, cumulative_sum(integral("power10")) /3600  as power10, cumulative_sum(integral("power")) /3600  as power FROM "forcast" WHERE time > now() and time < now() + 22h  group by time(1d)'
                zeros = flux_client.query(s, database=config.influxdb_database)
                m = list(zeros.get_points(measurement="forcast"))
                tomorrow = float(m[0]['power'])


                if config.debug:
                    print(midnight)
                    print(c_gen)
                    print(y_gen)
                    print(c_peak)

                if y_exp != 0 and y_tot != 0:
                    daily['P_Load'] = float(c_gen - (c_exp - y_exp) + (c_tot - y_tot))

                daily['P_daily'] = float(c_gen)
                c_gen = 0
                if (y_exp != 0):
                    daily['P_Exp'] = float(c_exp - y_exp)

                y_exp = c_exp
                if (y_tot != 0):
                    daily['P_Grid'] = float(c_tot - y_tot + config.extra_load * 24 / 1000)

                y_tot = c_tot
                daily['P_peak'] = float(c_peak)
                c_peak = 0
                daily['Start'] = c_start
                daily['Shutdown'] = c_stop

                utils.write_influx(flux_client, daily, config.model + "_daily", config.influxdb_longterm, (midnight - 24 * 3600) * 1000000000)
                if config.debug:
                    print(time.ctime(midnight - 24 * 3600))
                    print(daily)

#                utils.send_measurements(midnight - 24 * 3600 * 4, midnight, flux_client)

                if config.solfor == 1 or config.solfor == 2:
                    try:
                        s = "SELECT P_daily, f_power FROM Huawei_daily where f_power > 0  fill(null) order by time desc limit 1 tz('"+config.time_zone+"')"

                        if config.debug:
                            print("doing forecast adjustment")
                            print(s)

                        zeros=flux_client.query(s, database=config.influxdb_longterm, epoch="ms")
                        m = list(zeros.get_points(measurement=config.model+"_daily"))

                        t = m[0]['time']
                        f_ratio_old = f_ratio
                        f_ratio = do_fratio(t)

#                       s = "SELECT mean(r) as m, STDDEV(r) as av from (SELECT (P_daily / f_power * f_ratio) as r FROM Huawei_daily WHERE time >= now() -7d fill(1))"
#                       if config.debug:
#                           print(s)
#
#                       zeros=flux_client.query(s, database=config.influxdb_longterm, epoch="ms")
#                       m = list(zeros.get_points(measurement=config.model+"_daily"))
#                       av = m[0]['m']
#                       sd = m[0]['av']
#
#                       s= "SELECT HOLT_WINTERS_WITH_FIT(first(r), 1, 7)  from (SELECT (P_daily / f_power * f_ratio) as r FROM Huawei_daily WHERE time >=  " + str(t) +"ms -10d and time <= " + str(t) +"ms tz('"+config.time_zone+"')) group by time(1d) tz('"+config.time_zone+"')"
#
#                       if config.debug:
#                           print(s)
#
#
#                       zeros=flux_client.query(s, database=config.influxdb_longterm)
#                       m = list(zeros.get_points(measurement=config.model+"_daily"))
#                       if config.debug:
#                           print(m)

                        if t > 0:
                            t = t + 24 * 3600 * 1000
                            measurement = {'f_ratio': f_ratio}
                            t = t * 1000000

                            metrics = {}
                            tags = {}
                            metrics['time'] = t
                            metrics['measurement'] = config.model + "_daily"
                            tags['location'] = config.location
                            metrics['tags'] = tags
                            metrics['fields'] = measurement
                            metrics =[metrics, ]

                            target=flux_client.write_points(metrics, database=config.influxdb_longterm)

                    except Exception as e:
                        print("forecast adjustment error: %s" % str(e))


                if config.daily_reports:
                    s = "Daily values for the day of " + time.ctime(midnight - 24 * 3600) + "\r\n\r\n\r\n"
                    s = s + f"Insulation: {daily['Insulation']:3.2f}\r\n"
                    s = s + f"Temp: {daily['Temp']:2.0f}\r\n\r\n"
                    s = s + f"Forecasted: {daily['f_power']:3.1f} ({f_ratio_old:.1%})\r\n"
                    s = s + f"Daily: {daily['P_daily']:3.1f}\r\n\r\n"
                    s = s + f"Load: {daily['P_Load']:3.1f}\r\n"
                    s = s + f"Exported: {daily['P_Exp']:3.1f}\r\n"
                    s = s + f"Grid: {daily['P_Grid']:3.1f}\r\n\r\n"
                    s = s + f"Peak: {daily['P_peak']:3.1f}\r\n"
                    s = s + f"Tomorrow: {tomorrow:3.1f} ({f_ratio:.1%})\r\n"

                    emails.send_mail(s)

                print("doing period balance")
                diff = 1
                dt = datetime.datetime.fromtimestamp(midnight - (config.billing_date + diff) * 24 * 3600)
                print(dt)

                window = 12

                billing_month = dt.month - config.billing_offset
                billing_month = (billing_month + window) % window
                if (billing_month == 0):
                    billing_month = window

                billing_month = (int(billing_month % config.billing_period != 0) + int(billing_month / config.billing_period)) * config.billing_period + config.billing_offset + 1
                billing_month = (billing_month + window) % window
                if (billing_month == 0):
                    billing_month = window

                dt = datetime.datetime.fromtimestamp(midnight - (config.billing_date + diff - 1) * 24 * 3600)
                print(dt)

                billing_day = dt.day

                print(billing_month)
                print(billing_day)

                dt = datetime.datetime.fromtimestamp(time.time())
                print(dt)
                print(dt.month)

                if (billing_month == dt.month and billing_day == 1):
                    print('updating balance')
                    utils.update_balance(flux_client, midnight)

                midnight = int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 23:59:59", "%m/%d/%Y %H:%M:%S"))) + 1
                daily_forecast = True


            if (int(time.time()) > forecast_time):
                forecast_time = forecast(forecast_time, midnight)

        else:
            sleep = config.scan_interval - (float(time.strftime("%S")) % config.scan_interval) - thread_mean * 1.1
            if sleep == config.scan_interval:
                sleep = 0.0

    #       sleep = 0.95 * (config.scan_interval - (time.time() - last_loop)) + 0.05
            if ((int(time.time() + sleep)) > midnight):
                sleep = midnight - int(time.time())

            if sleep < 0.16:
                sleep = 0.1

    #       if sleep < 0:
    #           sleep = 1
            time.sleep(sleep)

        try:
            pass

        except Exception as e:
            print("main 4 error: %s" % str(e))
            ok = False
            return -1

global client

utils.check_default_files()
emails.send_mail("Starting solar logger")
loops = 0
while True:
    print("starting")
    print(time.strftime("%c"))
    try:
        main()
        close_bus(client)
        del client
        flux_client.close()
        del flux_client

    except Exception as e:
        print("top error: %s" % str(e))
        print("something went wrong")
        loops = loops + 1
        if loops > 9:
            emails.send_mail("Doing the loopy loop \r\n" + str(e))
        time.sleep(150)
    print("done")
