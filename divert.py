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

def check(p_available):

    changes = {}

######### disable for actual use. This for loop is to simulate loads being used
    for p in config.loads:
        if (config.loads[p]["state"] == 1):
            p_available -= config.diverters_loads[p]
#########


    divert = config.divert[int(time.strftime("%H"))]

    current_time = int(time.time())

#    for x in sorted(divert, key=lambda tup: tup[1], reverse=False):
    for x in sorted(divert, key=lambda tup: (tup[1], tup[3]), reverse=False):
        if x[1] == -1:
            continue

        if x[0] in config.loads:
            if current_time - config.loads[x[0]]['time'] < 180:
#                print("cont")
                continue
        else:
            config.loads[x[0]] = {'time' : 0, 'state' : -1, 'last' : 0}

        if p_available < x[3]:
            if config.loads[x[0]]['state'] == 0:
                continue

            print(p_available)
            print(x)
            print(config.diverters_loads)

            deactivate(x[0])
            if config.loads[x[0]]['state'] == 1:
                p_available += config.diverters_loads[x[0]]
            config.loads[x[0]]['time'] = current_time
            config.loads[x[0]]['state'] = 0
            changes[x[0]] = 0
            print(changes)

#    for x in sorted(divert, key=lambda tup: tup[1], reverse=True):
    for x in sorted(divert, key=lambda tup: (tup[1], tup[2]), reverse=True):
        if x[1] == -1:
            continue
#        print(x)

        if x[0] in config.loads:
            if current_time - config.loads[x[0]]['time'] < 180:
#                print("cont")
                continue
        else:
            config.loads[x[0]] = {'time' : 0, 'state' : -1, 'last' : 0}

        if p_available > x[2]:
            if config.loads[x[0]]['state'] == 1:
                continue

            if current_time - config.loads[x[0]]['last'] < 15 * 60:
                print('too soon')
                continue

            if current_time < time.mktime(time.strptime(config.diverters_holiday[x[0]], "%Y-%m-%d")):
                print('on holidays')
                continue


            print(p_available)
            print(x)
            print(config.diverters_loads)

            activate(x[0])
            if config.loads[x[0]]['state'] == 0:
                p_available -= config.diverters_loads[x[0]]
            config.loads[x[0]]['last'] = config.loads[x[0]]['time']
            config.loads[x[0]]['time'] = current_time
            config.loads[x[0]]['state'] = 1
            changes[x[0]] = 1
            print(config.loads[x[0]])
            print(changes)

    return changes

