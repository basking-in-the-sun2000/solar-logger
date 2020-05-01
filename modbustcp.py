from pymodbus.client.sync import ModbusTcpClient as ModbusClient 
import time


def connect_bus(ip="192.168.88.250", PortN = 502, timeout = 3):
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
                j = result.registers[nb - 1]
                break
            except:
                if 'exception_code' in vars(result):
                    break
                time.sleep(0.05)
                continue
        time.sleep(0.025)
        return result
    except:
        return -1
        
