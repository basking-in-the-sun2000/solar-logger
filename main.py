import config
from modbustcp import connect_bus, read_registers, close_bus
import time
import datetime
import solcast
import pytz
from datetime import timedelta
from influxdb import InfluxDBClient
#import sys
import gc # Garbage Collector
import solcast


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
    except:
        if config.debug:
            print("error in call_function")
            print(method_name, values)

#       close_bus(client)
#       gc.collect()
        ok = False
        return -1

def do_map(client, config, inverter):
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
    
    time.sleep(0.5)

    for register in inverter._register_map:
        k = 0
        while k < 4:
            try:
                result = read_registers(client, config.slave, inverter._register_map[register]) 
                result.registers
                break
            except:
                time.sleep(0.3)
                k += 1
                if config.debug:
                    print("trying to recover", register, k)
                if k > 3:
                    return True


        if (result == -1):
            continue

        value = call_function(inverter._register_map[register]['type'], result.registers )
        if not ok:
            return -1
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
    return False



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
            if not target:
                if config.debug:
                    print(vars(target))
#                   print(metrics)
            return target
        except:
            ok = False
            if config.debug:
                print("error")
                print(metrics)
            return False

def forcast():
    global flux_client
    print("in forcast")
    try:
        if (config.solfor == 1):
            r1 = solcast.get_rooftop_forcasts(config.site_UUID)
        elif (config.solfor == 2):
            r1 = solcast.get_wpv_power_forecasts(config.latitude, config.longitude, config.forcast_capacity, 
                                                 tilt=config.tilt, azimuth=config.azimuth, install_date = config.install_date, hours = 48)
        else:
            return int(time.time() + 24 * 3600)

    except:
        print("solcast off-line")
        return int(time.time() + 15 * 60)

    for x in r1.content['forecasts']:
        dt = x['period_end'] 
        dt = dt.replace(tzinfo=pytz.timezone('UTC'))
        dt = dt.astimezone(pytz.timezone(config.time_zone))
        dt = time.mktime(dt.timetuple())

    if (config.solfor == 1):
        measurement = {'power': float(x['pv_estimate']), 'power10': float(x['pv_estimate10']), 'power90': float(x['pv_estimate90']) }
    elif (config.solfor == 2):
        measurement = {'power': float(x['pv_estimate'])}


        write_influx(flux_client, measurement, "forcast", config.influxdb_database, int(dt) * 1000000000)


    print("done getting forcast")
    forcast_time = float(time.strftime("%H"))
    if (8 <= forcast_time < 16):
        forcast_time = 2 - (forcast_time % 2)
    else:
        forcast_time = 4 - (forcast_time % 4)

    forcast_time *= 3600
    forcast_time = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d %H:00:00', time.localtime(time.time()+forcast_time)), "%Y-%m-%d %H:%M:%S")))

    print("next forcast " + time.ctime(forcast_time))

    return forcast_time

def send_measurements(midnight, flux_client):
    if (not config.soltun) or (config.solfor != 1):
        return
    slices = 5
    s = ('SELECT mean("P_active") as "power" FROM "%s"  WHERE time >= %s and time <= %s GROUP BY time(%sm) fill(none)') % (config.model, str(midnight*1000000000), str((midnight + 24 * 3600 )*1000000000), slices)

    if config.debug:
        print(s)
        print(time.ctime(midnight))

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
        roof = solcast.post_rooftop_measurements(config.site_UUID, measurements)
    except:
        print("solcast not receiving tuning")
        if config.debug:
            print(vars(roof))


def fill_blanks(flux_client, midnight):
    k = 0
    s = ('SELECT first("P_Exp") as "P_Exp" FROM "%s_daily" where time < %s group by time(1d)') % (config.model, str((midnight - 24 * 3600) * 1000000000))

    zeros=flux_client.query(s, database=config.influxdb_longterm)

    daily = list(zeros.get_points(measurement=config.model+"_daily"))

    for i in daily:

        if not ((i['P_Exp'] == None) or (i['P_Exp'] == 0)):
            continue

        j = (int(time.mktime(time.strptime(i['time'], "%Y-%m-%dT%H:%M:%SZ"))))

        s = ('SELECT first(M_PTot) as M_PTot_first, last(M_PTot) as M_PTot_last, first(M_PExp) as M_PExp_first, last(M_PExp) as M_PExp_last, first(P_accum) as P_accum_first, last(P_accum) as P_accum_last, max(P_daily) as P_daily, max(P_peak) as P_peak, max(Temp) as Temp  FROM "%s" where time > %s and time < %s and time < %s') % (config.model, str(j * 1000000000), str((j + 24 *3600) * 1000000000), str((midnight - 24 * 3600) * 1000000000))

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

                k += 1
                write_influx(flux_client, daily, config.model+"_daily", config.influxdb_longterm, (j * 1000000000))

        except:
            continue
            
        if config.debug:
            print("filled "+str(k)+" daily blanks")


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

    inverter_file = config.model
    inverter = __import__(inverter_file)
     
    if config.debug:
        print("got it")
    
    inverter_ip = inverter.inv_address()
    if inverter_ip != "":
        config.inverter_ip = inverter_ip
        
    print(config.inverter_ip)

    client = connect_bus(ip=config.inverter_ip, 
                         PortN = config.inverter_port,
                         timeout = config.timeout)

    try:
        flux_client = InfluxDBClient(host=config.influxdb_ip,
                                     port=config.influxdb_port,
                                     username=config.influxdb_user,
                                     password=config.influxdb_password)


                # config.influxdb_database                  
    except:
        flux_client = None
        print("problem openning db")

    flux_client.create_database(config.influxdb_database)
    flux_client.create_database(config.influxdb_longterm)

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

    midnight = (int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 00:00:00", "%m/%d/%Y %H:%M:%S"))))

    s = ('SELECT %s FROM "%s" WHERE time >= %s and time <= %s and P_daily > 0') % ('max("M_PExp") as "M_PExp", max("M_PTot") as "M_PTot", max("P_accum") as "P_accum", max("P_daily") as "P_daily", max("Temp") as "Temp"', config.model, str((midnight - 24 * 3600)*1000000000), str(midnight*1000000000))

    zeros=flux_client.query(s, database=config.influxdb_database)

    m = list(zeros.get_points(measurement=config.model))

    try:
        y_exp = m[0]['M_PExp']
        y_tot = m[0]['M_PTot']
        y_gen = m[0]['P_daily']
        tmax = m[0]['Temp']
    except:
        y_exp = 0
        y_tot = 0
        y_gen = 0
        tmax = 0


    s = ('SELECT %s FROM "%s_info" WHERE time >= %s and time <= %s and Insulation > 0') % ('min("Insulation") as "Insulation"', config.model, str((midnight - 3600 * 24)*1000000000), str(midnight*1000000000))

    zeros=flux_client.query(s , database=config.influxdb_database)

    m = list(zeros.get_points(measurement=config.model+"_info"))

    try:
        if config.debug:
            print(m[0])
        min_ins = m[0]['Insulation']
    except:
        if config.debug:
            print(s)
        min_ins = 1000

    midnight = int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 23:59:59", "%m/%d/%Y %H:%M:%S"))) + 1


    if ((float(time.strftime("%S")) % 60) > 1):
        time.sleep(59 - float(time.strftime("%S")))

    fill_blanks(flux_client, midnight)

    forcast_time = forcast()

    if config.debug:
        print("loop")

    ok = True
    
    while ok:
        current_time = time.time()
        if (current_time - last_loop + thread_mean >= int(config.scan_interval)):
            last_loop = current_time
            measurement = {}
            info = {}
            status = {}

            j = 0
            while do_map(client, config, inverter):
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
                write_influx(flux_client, info, config.model + "_info", config.influxdb_database)               
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


            if (status != last_status):
                write_influx(flux_client, status, config.model + "_stat", config.influxdb_database)             
                last_status = status
                if config.debug:
                    print(status)

            x = config.scan_interval - (float(time.strftime("%S")) % config.scan_interval)

            if x == 30:
                x = 0

            if (0.5 < x < 6):
                time.sleep(x - 0.05)

            write_influx(flux_client, measurement, config.model, config.influxdb_database)

            thread_time.insert(0, time.time() - last_loop)

            if len(thread_time) > 5:
                thread_time.pop()

            thread_mean = sum(thread_time) / len(thread_time)

            if (int(time.time()) > midnight):

                daily = {}
                daily['Insulation'] = min_ins
                min_ins = 1000

                daily['Temp'] = tmax
                tmax = 0
                
                s = 'SELECT cumulative_sum(integral("power90")) /3600 * 0.82  as power90, cumulative_sum(integral("power10")) /3600 * 0.82  as power10, cumulative_sum(integral("power")) /3600 * 0.82  as power FROM "forcast" WHERE time > now() -22h group by time(1d)'

                zeros = flux_client.query(s, database=config.influxdb_database)
                m = list(zeros.get_points(measurement="forcast"))

                daily['f_power'] = m[0]['power']
                try:
                    daily['f_power90'] = m[0]['power90']
                    daily['f_power10'] = m[0]['power10']
                except:
                    daily['f_power90'] = m[0]['power']
                    daily['f_power10'] = m[0]['power']
                    
                
                
                if config.debug:
                    print(midnight)
                    print(c_gen)
                    print(y_gen)
                    print(c_peak)

                if y_exp != 0 and y_tot != 0:
                    daily['P_Load'] = c_gen - (c_exp - y_exp) + (c_tot - y_tot)

                daily['P_daily'] = c_gen
                c_gen = 0

                if (y_exp != 0):
                    daily['P_Exp'] = c_exp - y_exp
                y_exp = c_exp

                if (y_tot != 0):
                    daily['P_Grid'] = c_tot - y_tot
                y_tot = c_tot

                daily['P_peak'] = c_peak

                daily['Start'] = c_start
                daily['Shutdown'] = c_stop

                write_influx(flux_client, daily, config.model + "_daily", config.influxdb_longterm, (midnight - 24 * 3600) * 1000000000)
                
                if config.debug:
                    print(time.ctime(midnight - 24 * 3600))
                    print(daily)

                send_measurements(midnight - 24 * 3600, flux_client)

                midnight = int(time.mktime(time.strptime(time.strftime( "%m/%d/%Y ") + " 23:59:59", "%m/%d/%Y %H:%M:%S"))) + 1
                
            if (int(time.time()) > forcast_time):
                forcast_time = forcast()



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
        except:
            ok = False
            return -1

while True: 
    print("starting")
    try:
        main()
        close_bus(client)
        flux_client.close()
        del flux_client
    except:
        print("something went wrong")

    print("done")
