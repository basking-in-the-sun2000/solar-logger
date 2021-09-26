import config
import time
from gpiozero import LED
from gpiozero.pins.mock import MockFactory
import gpiozero
global loads


def activate(load):
    if (config.loads[load]["state"] != 1):
        if config.diverters_io[load][0] == "gpio":
            gpiozero.Device.pin_factory = MockFactory()  ######### disable for actual use

            relay = LED(config.diverters_io[load][1])
            relay.on()
        print("turning on ", load)

def deactivate(load):
    if (config.loads[load]["state"] != 0):
        if config.diverters_io[load][0] == "gpio":
            gpiozero.Device.pin_factory = MockFactory()  ######### disable for actual use

            relay = LED(config.diverters_io[load][1])
            relay.off()

        print("turning off ", load)

def check(p_available, flux_client):
    divert = config.divert[int(time.strftime("%H"))]
    temp = {}
    current_time = int(time.time())

######### disable for actual use. This for loop is to simulate loads being used
    for p in config.loads:
        if (config.loads[p]["state"] == 1):
            p_available -= config.diverters_loads[p]
#########


    for x in divert:
        if x[0] in config.loads:
            if config.debug:
                print(x[0], time.ctime(config.loads[x[0]]['time']), config.loads[x[0]]["state"])
            if config.loads[x[0]]["state"] == 1:
                if current_time - config.loads[x[0]]['time'] >= abs(x[4]) + 45:
                    p_available = p_available + config.diverters_loads[x[0]]
        else:
            config.loads[x[0]] = {'time' : 0, 'state' : -1, 'last' : 0}

    if config.debug:
        print(time.ctime(current_time))
        print("power ", p_available)

    s = "select max(M_P)/mean(M_P) as spiky from Huawei where time >= now() -10m group by time(5m)"

    zeros=flux_client.query(s, database=config.influxdb_database)
    m = list(zeros.get_points(measurement=config.model))

    spiky = 0
    for x in m:
        try:
            spiky = max(spiky, x["spiky"])
        except:
            pass

    for x in sorted(divert, key=lambda tup: (tup[1], tup[2]), reverse=True):
        if x[1] == -1:
            temp[x[0]] = 0
            if config.debug:
                print("disabled")
            continue
        if (current_time - config.loads[x[0]]['time'] < abs(x[4]) + 45) and (config.loads[x[0]]['state'] == 1):
            temp[x[0]] = 1
            if config.debug:
                print("cant turn off")
            continue
        if (current_time - config.loads[x[0]]['time'] < abs(x[5]) + 120) and (config.loads[x[0]]['state'] == 0):
            temp[x[0]] = 0
            if config.debug:
                print("cant turn on")
            continue
        if config.debug:
            print(x)
        temp[x[0]] = 0
        if p_available >= config.diverters_loads[x[0]] and config.loads[x[0]]['state'] == 1:
            temp[x[0]] = 1
            p_available = p_available - config.diverters_loads[x[0]]
        elif p_available >= x[2]:
            if spiky > x[6]:
                continue
            if current_time - config.loads[x[0]]['last'] > 15 * 60:
                temp[x[0]] = 1
                p_available = p_available - x[2]
            else:
                if config.debug:
                    print("too soon")
                temp[x[0]] = 0
        if config.debug:
            print(p_available)

    if config.debug:
        print(p_available)
        print(temp)

    changes = {}
    for x in temp:
        if config.debug:
            print(x, config.loads[x])
        if config.loads[x]["state"] != temp[x]:
            changes[x] = temp[x]
            if temp[x] == 1:
                config.loads[x]['last'] = config.loads[x]['time']
                activate(x)
                print(time.ctime(current_time), spiky)
            else:
                deactivate(x)
            config.loads[x]['time'] = current_time
            config.loads[x]['state'] = temp[x]

    if config.debug:
        print(config.loads)
        print(changes)
    return changes
