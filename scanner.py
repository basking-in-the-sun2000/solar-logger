#!/usr/bin/env python
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus import mei_message
import time
import random
import config

#import logging
#
#logging.basicConfig()
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)

def toStr(data, nb):
    str = ""
    for i in range(0, nb):
        high, low = divmod(data[i], 0x100)
        str = str + chr(high) + chr(low)
    return str

def toU16(i):
    return i & 0xffff

def toI16(i):
    i = i & 0xffff
    return (i ^ 0x8000) - 0x8000

def toU32(i):
    return ((i[0] << 16) + i[1])

def toI32(i):
    i = ((i[0] << 16) + i[1])
    i = i & 0xffffffff
    return (i ^ 0x80000000) - 0x80000000

def read_holding(client, UnitID, i, nb):
    result = client.read_holding_registers(i, nb, unit=UnitID)
    ns = time.time()
    while (time.time() - ns < 1.5):
        try:
            j = result.registers[nb - 1]
            break
        except Exception as Error:
            if 'exception_code' in vars(result):
                break
            time.sleep(0.1)
            continue
    return result


ip = config.inverter_ip
PortN = config.inverter_port
num_reg = 29000
nb_reg = 1
UnitID = config.slave
j = 0

print("openning")
client = ModbusClient(host=ip, port=PortN, timeout=5)
time.sleep(1)
print(time.strftime("%a, %d %b %Y %H:%M:%S"))
if client.connect():
    time.sleep(2)
    i = num_reg - 1
    while ( i < 30000):
        i += 1
#       print("trying " + str(i))
        result = read_holding(client, UnitID, i, 1)
        try:
            j = result.registers[0]
            print("reading " + str(i) + " 1")
            print(result.registers)
            continue
        except Exception as Error:
            result = read_holding(client, UnitID, i, 2)
            try:
                j = result.registers[1]
                print("reading " + str(i) + " 2")
                print(result.registers)
                i += 1
            except Exception as Error:
                j = 0
            continue

#       print(toLong(result.registers))



#   print("printing")
#   for i in range(200, 257):
#       req = mei_message.ReadDeviceInformationRequest(unit=i,read_code=0x01)
#       rr = client.execute(req)
#       try:
#           print(str(i) + " " + str(rr.information))
#       except Exception as ex:
#           print(str(i))
#       time.sleep(5)
client.close()
print(time.strftime("%a, %d %b %Y %H:%M:%S"))
