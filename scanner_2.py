#!/usr/bin/env python
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus import mei_message
import time
import config


def to_str(s):
    str = ""
    for i in range(0, len(s)):
        high, low = divmod(s[i], 0x100)
        str = str + chr(high) + chr(low)
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
num_reg = 0
nb_reg = 1
UnitID = 0
regs = [30068, 30070, 30071, 30072, 30073, 30075,
30077, 30079, 30081, 30109, 30111, 30112,
30114, 30116, 30118, 30120, 30122, 30124,
30126, 30128, 30130, 30207, 30209, 30211,
30213, 30215, 30217, 30219, 30220, 30221,
30222, 30223, 30224, 30225, 30226, 30227,
30228, 30229, 30230, 30231, 30232, 30233,
30234, 30299, 30301, 30302, 30303, 30304,
30305, 30306, 30307, 30308, 30309, 30310,
30311, 30312, 30313, 30314, 30315, 30316,
30317, 30318, 30319, 30320, 30321, 30322,
30323, 30500, 30502, 31999, 32000, 32001,
32003, 32007, 32009, 32010, 32014, 32016,
32017, 32018, 32019, 32020, 32021, 32022,
32023, 32064, 32066, 32067, 32068, 32069,
32070, 32071, 32072, 32074, 32076, 32078,
32080, 32082, 32084, 32085, 32086, 32087,
32088, 32089, 32090, 32091, 32093, 32106,
32108, 32110, 32112, 32114, 32116, 32118,
32154, 32156, 32158, 32160, 32162, 32164,
32166, 32168, 32170, 32172, 32174, 32212,
32214, 32216, 32218, 32251, 32253, 32254,
32255, 32256, 32257, 32258, 32259, 32260,
32261, 32262, 32263, 32264, 32265, 32266,
32267, 35009, 35020, 35022, 35023, 35024,
35037, 35039, 35040, 35041, 35042, 35043,
35044, 35102, 35104, 35105, 35111, 35113,
35115, 35122, 35248, 35250, 35252, 35263,
35265, 35266, 36032, 36050, 36999, 37000,
37001, 37003, 37004, 37005, 37006, 37007,
37009, 37013, 37015, 37017, 37019, 37024,
37046, 37048, 37099, 37101, 37103, 37105,
37107, 37109, 37111, 37113, 37115, 37117,
37118, 37119, 37120, 37121, 37122, 37123,
37124, 37125, 37126, 37128, 37130, 37132,
37134, 37136, 37138, 37199, 37201, 37202,
37203, 37204, 37205, 37206, 37207, 37208,
37210, 37249, 37251, 37252, 40000, 40001,
40121, 40122, 40123, 40124, 40125, 40126,
40127, 40128, 40195, 40196, 40199, 40200,
40201, 40204, 40205, 40500, 41999, 42000,
42001, 42002, 42003, 42013, 42015, 42017,
42019, 42021, 42023, 42043, 42045, 42046,
42047, 42053, 42055, 42060, 42062, 42063,
42064, 42066, 42068, 42072, 42074, 42079,
42081, 42082, 42087, 42089, 42090, 42091,
42096, 42098, 42099, 42100, 42101, 42102,
42103, 42104, 42105, 42111, 42113, 42118,
42120, 42121, 42122, 42127, 42129, 42130,
42137, 42139, 42140, 42142, 42144, 42145,
42146, 42147, 42148, 42149, 42192, 42289,
42291, 42293, 42294, 42296, 42297, 42299,
42300, 42302, 42303, 42305, 42306, 42308,
42309, 42311, 42312, 42314, 42315, 42317,
42318, 42320, 42321, 42323, 42324, 42326,
42327, 42329, 42330, 42332, 42333, 42335,
42336, 42337, 42338, 42339, 42341, 42342,
42344, 42345, 42346, 42347, 42348, 42350,
42351, 42353, 42354, 42356, 42357, 42359,
42360, 42362, 42363, 42399, 42589, 42591,
42593, 42595, 42596, 42597, 42729, 42778,
42899, 42901, 42902, 42903, 42904, 42905,
42906, 42907, 42908, 42909, 42910, 42911,
42999, 43001, 43002, 43003, 43004, 43005,
43006, 43017, 43019, 43020, 43021, 43022,
43064, 43066, 43096, 43098, 43145, 43147,
43163, 43196, 43198, 43200, 43202, 43204,
43206, 43287, 43289, 43310, 43341, 43343,
43358, 43369, 43379, 43381, 43429, 43431,
43432, 43498, 43564, 43566, 44999, 45001,
45003, 45005, 45006, 45007, 45008, 45010,
45011, 45013, 45015, 45025, 45036, 46200,
46217, 46253, 46257, 46369, 46371, 46372,
46373, 46999, 47000, 47001, 47002, 47003, 47004,
47026, 47069, 47071, 47072, 47073, 47074,
47075, 47077, 47079, 47081, 47082, 47083,
47084, 47086, 47087, 47099, 47119, 47139,
47141, 47149, 47151, 47152, 47153, 47154,
47155, 47299, 47301, 47302, 60000, 60002,
60003, 60100, 61000, 61002,
61003, 61004, 61006, 61008, 64199, 64201,
64306, 64308, 64310, 64311, 64313]

print("openning")
f = open("sun2000 regs" + time.strftime("%m%d-%H%M%S") + ".txt", "a")
client = ModbusClient(host=ip, port=PortN, timeout=5)
time.sleep(1)
print(time.strftime("%a, %d %b %Y %H:%M:%S"))
f.write(time.strftime("%a, %d %b %Y %H:%M:%S"))
if client.connect():
    time.sleep(2)
    num_reg = - 1
    while ( num_reg < len(regs) - 1):
        num_reg += 1
#       time.sleep(0.1)
#       print("trying " + str(i))

#       result = client.read_holding_registers(regs[num_reg], 1, unit=UnitID)
        result = read_holding(client, UnitID, regs[num_reg], 1)
        try:
            j = result.registers[0]
            print("reading " + str(regs[num_reg]) + " 1")
            f.write("reading " + str(regs[num_reg]))
            for item in result.registers:
                f.write("\t" + str(item))
            f.write("\t" + str(to_I16(result.registers)))
            f.write("\r")

            print(result.registers)
            print(to_I16(result.registers))
            continue
        except:
#           result = client.read_holding_registers(regs[num_reg], 2, unit=UnitID)
            result = read_holding(client, UnitID, regs[num_reg], 2)
            try:
                j = result.registers[1]
                print("reading " + str(regs[num_reg]) + " 2")
                f.write("reading " + str(regs[num_reg]))
                for item in result.registers:
                    f.write("\t" + str(item))

                print(result.registers)
                if (25000 > result.registers[0] > 23000):
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(to_I32(result.registers))))
                    f.write("\t" + str(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(to_I32(result.registers)))))
                else:
                    print(to_I32(result.registers))
                    f.write("\t" + str(to_I32(result.registers)))
                f.write("\r")
                i += 1
            except:
                j = 0
            continue

#       print(toLong(result.registers))


client.close()
print(time.strftime("%a, %d %b %Y %H:%M:%S"))
f.write(time.strftime("%a, %d %b %Y %H:%M:%S"))
f.close()
