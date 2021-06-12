from pymodbus.client.sync import ModbusTcpClient as ModbusClient 
import time


def connect_bus(ip="192.168.8.1", PortN = 502, timeout = 3):
    client = ModbusClient(host=ip, port=PortN, timeout=timeout, RetryOnEmpty = True, retries = 3)
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
            result = client.read_holding_registers(int(data['addr']), nb, unit=UnitID)
        elif data['method'] == "input":
            result = client.read_input_registers(int(data['addr']), nb, unit=UnitID)
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

