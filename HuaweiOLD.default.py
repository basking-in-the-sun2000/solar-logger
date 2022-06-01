import socket
import time
import config
import emails

# Change use to ext for type you won't use or aren't defined by your inverter

_register_map =  {
    'SN':         {'addr': '32003', 'registers': 10, 'name': 'Serial Number',                    'scale': 1,    'type': 'str',  'units': ''    , 'use': 'info',  'method': 'hold'},
    'Insulation': {'addr': '32323', 'registers': 1,  'name': 'Insulation resistance',            'scale': 1000, 'type': 'U16',  'units': 'MΩ'  , 'use': 'info',  'method': 'hold'},
    'Start':      {'addr': '32325', 'registers': 2,  'name': 'Startup time',                     'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'info',  'method': 'hold'},
    'Shutdown':   {'addr': '32327', 'registers': 2,  'name': 'Shutdown time',                    'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'info',  'method': 'hold'},
    'Time':       {'addr': '40000', 'registers': 2,  'name': 'Current time',                     'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'info',  'method': 'hold'},
    'State1':     {'addr': '32319', 'registers': 1,  'name': 'Status 1',                         'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'State2':     {'addr': '32320', 'registers': 1,  'name': 'Status 2',                         'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'State3':     {'addr': '32321', 'registers': 2,  'name': 'Status 3',                         'scale': 1,    'type': 'Bit32','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm1':     {'addr': '50000', 'registers': 1,  'name': 'Alarm 1',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm2':     {'addr': '50001', 'registers': 1,  'name': 'Alarm 2',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm3':     {'addr': '50002', 'registers': 1,  'name': 'Alarm 3',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm4':     {'addr': '50003', 'registers': 1,  'name': 'Alarm 1',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm5':     {'addr': '50004', 'registers': 1,  'name': 'Alarm 2',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm6':     {'addr': '50005', 'registers': 1,  'name': 'Alarm 3',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm7':     {'addr': '50006', 'registers': 1,  'name': 'Alarm 1',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm8':     {'addr': '50007', 'registers': 1,  'name': 'Alarm 2',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm9':     {'addr': '50008', 'registers': 1,  'name': 'Alarm 3',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm10':     {'addr': '50009', 'registers': 1,  'name': 'Alarm 1',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm17':     {'addr': '50016', 'registers': 1,  'name': 'Alarm 2',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Status':     {'addr': '32287', 'registers': 1,  'name': 'Device status',                    'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'stat',  'method': 'hold'},
    'PV_P':       {'addr': '32294', 'registers': 2,  'name': 'Input power',                      'scale': 1000, 'type': 'U32',  'units': 'kW'  , 'use': 'data',  'method': 'hold'},
    'U_A-B':      {'addr': '32274', 'registers': 1,  'name': 'Line Voltage A-B',                 'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
    'U_B-C':      {'addr': '32275', 'registers': 1,  'name': 'Line Voltage B-C',                 'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'ext' ,  'method': 'hold'},
    'U_C-A':      {'addr': '32276', 'registers': 1,  'name': 'Line Voltage C-A',                 'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'ext' ,  'method': 'hold'},
    'U_A':        {'addr': '32277', 'registers': 1,  'name': 'Phase Voltage A',                  'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
    'U_B':        {'addr': '32278', 'registers': 1,  'name': 'Phase Voltage B',                  'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
    'U_C':        {'addr': '32279', 'registers': 1,  'name': 'Phase Voltage C',                  'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'ext' ,  'method': 'hold'},
    'I_A':        {'addr': '32280', 'registers': 1,  'name': 'Phase Current A',                  'scale': 1000, 'type': 'I32',  'units': 'A'   , 'use': 'data',  'method': 'hold'},
    'I_B':        {'addr': '32281', 'registers': 1,  'name': 'Phase Current B',                  'scale': 1000, 'type': 'I32',  'units': 'A'   , 'use': 'ext' ,  'method': 'hold'},
    'I_C':        {'addr': '32282', 'registers': 1,  'name': 'Phase Current C',                  'scale': 1000, 'type': 'I32',  'units': 'A'   , 'use': 'ext' ,  'method': 'hold'},
    'P_peak':     {'addr': '32288', 'registers': 2,  'name': 'Peak Power',                       'scale': 1000, 'type': 'I32',  'units': 'kW'  , 'use': 'data',  'method': 'hold'},
    'P_active':   {'addr': '32290', 'registers': 2,  'name': 'Active power',                     'scale': 1000, 'type': 'I32',  'units': 'kW'  , 'use': 'data',  'method': 'hold'},
    'P_reactive': {'addr': '32292', 'registers': 2,  'name': 'Reactive power',                   'scale': 1000, 'type': 'I32',  'units': 'kVar', 'use': 'data',  'method': 'hold'},
    'PF':         {'addr': '32284', 'registers': 1,  'name': 'Power Factor',                     'scale': 1000, 'type': 'I16',  'units': ''    , 'use': 'data',  'method': 'hold'},
    'Frequency':  {'addr': '32283', 'registers': 1,  'name': 'Grid frequency',                   'scale': 100,  'type': 'U16',  'units': 'Hz'  , 'use': 'data',  'method': 'hold'},
    'η':          {'addr': '32285', 'registers': 1,  'name': 'Efficiency',                       'scale': 100,  'type': 'U16',  'units': '%'   , 'use': 'data',  'method': 'hold'},
    'Temp':       {'addr': '32286', 'registers': 1,  'name': 'Internal temperature',             'scale': 10,   'type': 'I16',  'units': '°C'  , 'use': 'data',  'method': 'hold'},
    'P_accum':    {'addr': '32306', 'registers': 2,  'name': 'Accumulated energy yield',         'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},
    'P_daily':    {'addr': '32300', 'registers': 2,  'name': 'Daily energy yield',               'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},
    'ModelID':    {'addr': '32001', 'registers': 1,  'name': 'Model ID',                         'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
    'PF_comp':    {'addr': '40122', 'registers': 1,  'name': 'Reactive power compensation',      'scale': 1000, 'type': 'I16',  'units': ''    , 'use': 'data',  'method': 'hold'},
    'Q/S':        {'addr': '40123', 'registers': 1,  'name': 'Reactive power compensation(Q/S)', 'scale': 1000, 'type': 'I16',  'units': ''    , 'use': 'data',  'method': 'hold'},
    'Derating':   {'addr': '40125', 'registers': 1,  'name': 'Active power derating percent',    'scale': 10,   'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
    'Power_on':   {'addr': '40200', 'registers': 1,  'name': 'Power on',                         'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
    'Power_off':  {'addr': '40201', 'registers': 1,  'name': 'Power off',                        'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
    'Grid':       {'addr': '42072', 'registers': 1,  'name': 'Grid Code',                        'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
#not impl but must be checked    'TZ':         {'addr': '43006', 'registers': 1,  'name': 'Time Zone',                        'scale': 1,    'type': 'I16',  'units': 'min' , 'use': 'info',  'method': 'hold'}
}

if (config.strings > 1):
    for i in range(1, config.strings + 1):
        _register_map.update({
            'PV_U' + str(i):      {'addr': str(32260 + i * 2 if i<=6 else 32300 + i * 2), 'registers': 1,  'name': 'PV' + str(i) + ' voltage',                      'scale': 10,   'type': 'I16',  'units': 'V'   , 'use': 'mult',  'method': 'hold'},
            'PV_I' + str(i):      {'addr': str(32261 + i * 2 if i<=6 else 32301 + i * 2), 'registers': 1,  'name': 'PV' + str(i) + ' current',                      'scale': 10,  'type': 'I16',  'units': 'A'   , 'use': 'mult',  'method': 'hold'}})
else:
    _register_map.update({
        'PV_Un':      {'addr': '32262', 'registers': 1,  'name': 'PVn voltage',                      'scale': 10,   'type': 'I16',  'units': 'V'   , 'use': 'mult',  'method': 'hold'},
        'PV_In':      {'addr': '32263', 'registers': 1,  'name': 'PVn current',                      'scale': 100,  'type': 'I16',  'units': 'A'   , 'use': 'mult',  'method': 'hold'}})


_status_map = {
    0x0000: 'Standby: initializing',
    0x0001: 'Standby: detecting insulation resistance',
    0x0002: 'Standby: detecting irradiation',
    0x0003: 'Standby: grid detecting',
    0x0100: 'Starting',
    0x0200: 'On-grid (Off-grid mode: running)',
    0x0201: 'Grid connection: power limited (Off-grid mode: running: power limited)',
    0x0202: 'Grid connection: self-derating (Off-grid mode: running: self-derating)',
    0x0300: 'Shutdown: fault',
    0x0301: 'Shutdown: command',
    0x0302: 'Shutdown: OVGR',
    0x0303: 'Shutdown: communication disconnected',
    0x0304: 'Shutdown: power limited',
    0x0305: 'Shutdown: manual startup required',
    0x0306: 'Shutdown: DC switches disconnected',
    0x0307: 'Shutdown: rapid cutoff',
    0x0308: 'Shutdown: input underpower',
    0x0401: 'Grid scheduling: cos F-P curve',
    0x0402: 'Grid scheduling: Q-U curve',
    0x0403: 'Grid scheduling: PF-U curve',
    0x0404: 'Grid scheduling: dry contact',
    0x0405: 'Grid scheduling: Q-P curve',
    0x0500: 'Spot-check ready',
    0x0501: 'Spot-checking',
    0x0600: 'Inspecting',
    0x0700: 'AFCI self check',
    0x0800: 'I-V scanning',
    0x0900: 'DC input detection',
    0x0a00: 'Running: off-grid charging',
    0xa000: 'Standby: no irradiation'
}
def test_bit(n, b):
    n &= (1<<b)
    n = (n  == (1<<b))
    return n

def status(register, value):
    s = ""
    value = int(value)
    if (register == 'State1'):
        if (test_bit(value,0)):
            s += 'standby | '
        if (test_bit(value,1)):
            s += 'grid-connected | '
        if (test_bit(value,2)):
            s += 'grid-connected normally | '
        if (test_bit(value,3)):
            s += 'connection with derating due to power rationing | '
        if (test_bit(value,4)):
            s += 'grid connection with derating due to internal causes of the solar inverter | '
        if (test_bit(value,5)):
            s += 'normal stop | '
        if (test_bit(value,6)):
            s += 'stop due to faults | '
        if (test_bit(value,7)):
            s += 'stop due to power rationing | '
        if (test_bit(value,8)):
            s += 'shutdown | '
        if (test_bit(value,9)):
            s += 'spot check '
    elif (register == 'State2'):
        if (test_bit(value,0)):
            s += 'unlocked | '
        else:
            s += 'locked | '
    elif (register == 'State3'):
        if (test_bit(value,0)):
            s += 'ZVRT protection ON |'
        if (test_bit(value,1)):
            s += 'LVRT protection ON | '
        if (test_bit(value,2)):
            s += 'anti-islanding ON | '
    elif (register == 'Alarm1'):
        if (test_bit(value,1)):
            s += 'Abnormal String 1 | '
        if (test_bit(value,2)):
            s += 'Abnormal String 2 | '
        if (test_bit(value,3)):
            s += 'Abnormal String 3 | '
        if (test_bit(value,4)):
            s += 'Abnormal String 4 | '
        if (test_bit(value,5)):
            s += 'Abnormal String 5 | '
        if (test_bit(value,6)):
            s += 'Abnormal String 6 | '        
        if (test_bit(value,10)):
            s += 'SW ver Unmatch | '
        if (test_bit(value,12)):
            s += 'Upgrade Failed | '
        if (test_bit(value,13)):
            s += 'Flash Fault | '
        if (test_bit(value,14)):
            s += 'License Expired | '                  
    elif (register == 'Alarm2'):
        if (test_bit(value,1)) or (test_bit(value,2)):
            s += ' SW ver Unmatch| '
        if (test_bit(value,3)) or (test_bit(value,4)) or (test_bit(value,4)):
            s += 'System Fault| '
        if (test_bit(value,5)):
            s += 'Abnormal DC Current | '
        if (test_bit(value,6)):
            s += 'Abnormal inverter Current | '
        if (test_bit(value,7)):
            s += 'Abnormal Resuidal Current | '
        if (test_bit(value,8)):
            s += 'Overtemperature | '
        if (test_bit(value,10)):
            s += 'System Fault | '
        if (test_bit(value,12)):
            s += 'Abnormal SPI Comm | '
    elif (register == 'Alarm3'):
        if (test_bit(value,0)):
            s += 'Low Insulation resistance | '
        if (test_bit(value,1)) or (test_bit(value,3)) or (test_bit(value,4)):
            s += 'AFCI Self-Check Fail | '
        if (test_bit(value,2)):
            s += 'DC Arc Fault | '
        if (test_bit(value,5)):
            s += 'Abnormal Inv.Circuit | '
        if (test_bit(value,7)) or (test_bit(value,8)) or (test_bit(value,15)):
            s += 'System Fault | '
        if (test_bit(value,9)):
            s += 'String 3 Reversed | '
        if (test_bit(value,12)) or (test_bit(value,13)) or (test_bit(value,14)):
            s += 'DC Arc Fault | '
    elif (register == 'Alarm4'):
        if (test_bit(value,1)):
            s += 'String 1 Reversed | '
        if (test_bit(value,2)):
            s += 'String 2 Reversed | '
        if (test_bit(value,3)):
            s += 'Abnormal DC Circuit | ' 
        if (test_bit(value,6)):
            s += 'String 4 Reversed | '
        if (test_bit(value,7)):
            s += 'String 5 Reversed | '
        if (test_bit(value,8)):
            s += 'String 6 Reversed | '
        if (test_bit(value,9)) or (test_bit(value,10)) or (test_bit(value,11)) or (test_bit(value,12)):
            s += 'High DC Input Voltage | '
        if (test_bit(value,15)):
            s += 'Abnirmal DC Circuit | '        
    elif (register == 'Alarm5'):
        if (test_bit(value,2)):
            s += 'String 1 Reversed | '
        if (test_bit(value,3)):
            s += 'String 2 Reversed | '
        if (test_bit(value,4)) or (test_bit(value,5)):
            s += 'String 7 Reversed | '
        if (test_bit(value,6)) or (test_bit(value,7)):
            s += 'String 8 Reversed | '
        if (test_bit(value,8)) or (test_bit(value,9)) or (test_bit(value,10)) or (test_bit(value,11)):
            s += 'Abnormal PV String connection | '
        if (test_bit(value,12)):
            s += 'String 3 Reversed | '
        if (test_bit(value,13)):
            s += 'String 4 Reversed | '
        if (test_bit(value, 14)):
            s += 'String 5 Reversed | '
        if (test_bit(value,15)):
            s += 'String 6 Reversed | '            
    elif (register == 'Alarm6'):
        if (test_bit(value,1)) or (test_bit(value,4)) or (test_bit(value,5)) or (test_bit(value,6)):
            s += 'Abnormal DC Circuit | '
        if (test_bit(value,2)):
            s += 'String 2 Reversed | '
        if (test_bit(value,7)) or (test_bit(value,8)) or (test_bit(value,9)) or (test_bit(value,1 )):
            s += 'BST Inductor connection Abnormal | '
    elif (register == 'Alarm7'):
        if (test_bit(value,6)):
            s += 'System Fault | '
        if (test_bit(value,10)) or (test_bit(value,12)):
            s += 'Abnormal inverter Circuit | '
    elif (register == 'Alarm8'):
        if (test_bit(value,1)):
            s += 'Abnormal inverter Circuit | '
        if (test_bit(value,5)):
            s += 'System Fault | '
    elif (register == 'Alarm9'):
        if (test_bit(value,0)) or (test_bit(value,3)) or (test_bit(value,8)) or (test_bit(value,9)) or (test_bit(value,11)):
            s += 'Abnormal Grid Voltage | '
        if (test_bit(value,6)) or (test_bit(value,7)) or (test_bit(value,12)):
            s += 'Abnormal Grid Frequency | '
        if (test_bit(value,10)):
            s += 'Abnormal Grounding | '
    elif (register == 'Alarm10'):
        if (test_bit(value,0)) or (test_bit(value,1)) or (test_bit(value,2)) or (test_bit(value,8)):
            s += 'Abnormal Grid Voltage | '
    elif (register == 'Alarm17'):
        if (test_bit(value,0)):
            s += 'Abnormal String 1 | '
        if (test_bit(value,1)):
            s += 'Abnormal String 2 | '      
        if (test_bit(value,2)):
            s += 'Abnormal String 3 | '
        if (test_bit(value,3)):
            s += 'Abnormal String 4 | '   
        if (test_bit(value,4)):
            s += 'Abnormal String 5 | '
        if (test_bit(value,5)):
            s += 'Abnormal String 6 | '   
        if (test_bit(value,6)):
            s += 'Abnormal String 7 | '
        if (test_bit(value,7)):
            s += 'Abnormal String 8 | '           
    elif (register == 'Status'):
        s = _status_map[value]
 
    if s.endswith(' | '):
        s = s[:-3]
    return s
