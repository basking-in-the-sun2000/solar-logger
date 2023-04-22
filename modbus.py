import time
import config
if config.inverter_type == "TCP":
    from pymodbus.client import ModbusTcpClient as ModbusClient
elif config.inverter_type == "RTU":
    from pymodbus.client import ModbusSerialClient as ModbusClient

#import logging
#FORMAT = ('%(asctime)-15s %(threadName)-15s '
#          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
#logging.basicConfig(format=FORMAT)
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)


def connect_bus(ip=config.inverter_ip, PortN = config.inverter_port, timeout = 5):
    if config.inverter_type == "TCP":
        client = ModbusClient(host=ip, port=PortN, timeout=timeout, RetryOnEmpty = True, retries = 5 )
    elif config.inverter_type == "RTU":
        client = ModbusClient(method = "rtu", port=config.connection_port, timeout=timeout, stopbits = config.connection_stopbits,
                 bytesize = config.connection_bytesize, parity = config.connection_parity, baudrate=config.connection_baudrate)
    else:
        raise Exception("Unknown modbus type")
    time.sleep(1)
    client.connect()
    time.sleep(1)
    return client

def close_bus(client):
    client.close()
    time.sleep(5)


def read_registers(client, UnitID, data):
    global ok
    try:
        nb = int(data['registers'])
        if data['method'] == "hold":
            result = client.read_holding_registers(address = int(data['addr']), count=nb, slave=UnitID)
        elif data['method'] == "input":
            result = client.read_input_registers(address =  int(data['addr']), count=nb, slave=UnitID)

        ns = time.time()
        while (time.time() - ns < 1.5):
            try:
                if not result.isError():
                    j = result.registers[nb - 1]
                    break
            except Exception as e:
                print("modbus read_registers error 1: %s" % str(e))
                time.sleep(0.2)
                if 'exception_code' in vars(result):
                    break
                continue
        time.sleep(0.025)
        return result
    except Exception as e:
        print("modbus read_registers error: %s" % str(e))
        ok = False
        return -1
