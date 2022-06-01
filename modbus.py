import time
import config
if config.inverter_type == "TCP":
    from pymodbus.client.sync import ModbusTcpClient as ModbusClient
elif config.inverter_type == "RTU":
    from pymodbus.client.sync import ModbusSerialClient as ModbusClient


def connect_bus(timeout = 3):
    if config.inverter_type == "TCP":
        client = ModbusClient(host=config.inverter_ip, port=config.inverter_port, timeout=timeout, RetryOnEmpty = True, retries = 3)
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
    del client


def read_registers(client, UnitID, data):
    try:
        nb = int(data['registers'])
        if data['method'] == "hold":
            result = client.read_holding_registers(int(data['addr']), count=nb, unit=UnitID)
        elif data['method'] == "input":
            result = client.read_input_registers(int(data['addr']), count=nb, unit=UnitID)
        ns = time.time()
        while (time.time() - ns < 1.5):
            try:
                if not result.isError():
                    j = result.registers[nb - 1]
                    break
            except Exception as e:
                print("mdobus read_registers error 1: %s" % str(e))
                time.sleep(0.2)
                if 'exception_code' in vars(result):
                    break
                continue
        time.sleep(0.025)
        return result
    except Exception as e:
        print("mdobus read_registers error: %s" % str(e))
        return -1

    
