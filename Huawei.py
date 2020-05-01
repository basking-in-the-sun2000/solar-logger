import socket
import time
import config

_register_map =  {
    'Model':      {'addr': '30000', 'registers': 15, 'name': 'Model',                            'scale': 1,    'type': 'str',  'units': ''    , 'use': 'info',  'method': 'hold'},  
    'SN':         {'addr': '30015', 'registers': 10, 'name': 'Serial Number',                    'scale': 1,    'type': 'str',  'units': ''    , 'use': 'info',  'method': 'hold'},  
    'strings':    {'addr': '30071', 'registers': 1,  'name': 'Number of strings',                'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},  
    'Pn':         {'addr': '30073', 'registers': 2,  'name': 'Rated power',                      'scale': 1000, 'type': 'U32',  'units': 'kW'  , 'use': 'info',  'method': 'hold'},  
    'Pmax':       {'addr': '30075', 'registers': 2,  'name': 'Maximum active power',             'scale': 1000, 'type': 'U32',  'units': 'kW'  , 'use': 'info',  'method': 'hold'},  
    'Smax':       {'addr': '30077', 'registers': 2,  'name': 'Maximum apparent power',           'scale': 1000, 'type': 'U32',  'units': 'kVA' , 'use': 'info',  'method': 'hold'},  
    'Qmax':       {'addr': '30079', 'registers': 2,  'name': 'Maximum reactive power to grid',   'scale': 1000, 'type': 'I32',  'units': 'kVar', 'use': 'info',  'method': 'hold'},  
    'Qgrid':      {'addr': '30081', 'registers': 2,  'name': 'Maximum reactive power from grid', 'scale': 1000, 'type': 'I32',  'units': 'kVar', 'use': 'info',  'method': 'hold'},  
    'Insulation': {'addr': '32088', 'registers': 1,  'name': 'Insulation resistance',            'scale': 1000, 'type': 'U16',  'units': 'MΩ'  , 'use': 'info',  'method': 'hold'},  
    'Start':      {'addr': '32091', 'registers': 2,  'name': 'Startup time',                     'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'info',  'method': 'hold'},  
    'Shutdown':   {'addr': '32093', 'registers': 2,  'name': 'Shutdown time',                    'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'info',  'method': 'hold'},  
    'Time':       {'addr': '40000', 'registers': 2,  'name': 'Current time',                     'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'info',  'method': 'hold'},  
    'Time1?':     {'addr': '32110', 'registers': 2,  'name': 'some time 1',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},  
    'Time2?':     {'addr': '32156', 'registers': 2,  'name': 'some time 2',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},  
    'Time3?':     {'addr': '32160', 'registers': 2,  'name': 'some time 3',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},  
    'Time4?':     {'addr': '35113', 'registers': 2,  'name': 'some time 4',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},  
    'Time5?':     {'addr': '40500', 'registers': 2,  'name': 'some time 5',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},  
    'Optim_tot':  {'addr': '37200', 'registers': 1,  'name': 'Number of optimizers',             'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},  
    'Optim_on':   {'addr': '37201', 'registers': 1,  'name': 'Number of online optimizers',      'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},  
    'Optim_opt':  {'addr': '37202', 'registers': 1,  'name': 'Optimizer Feature data',           'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},  
    'State1':     {'addr': '32000', 'registers': 1,  'name': 'Status 1',                         'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},  
    'State2':     {'addr': '32002', 'registers': 1,  'name': 'Status 2',                         'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},  
    'State3':     {'addr': '32003', 'registers': 2,  'name': 'Status 3',                         'scale': 1,    'type': 'Bit32','units': ''    , 'use': 'stat',  'method': 'hold'},  
    'Alarm1':     {'addr': '32008', 'registers': 1,  'name': 'Alarm 1',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},  
    'Alarm2':     {'addr': '32009', 'registers': 1,  'name': 'Alarm 2',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},  
    'Alarm3':     {'addr': '32010', 'registers': 1,  'name': 'Alarm 3',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},  
    'Status':     {'addr': '32089', 'registers': 1,  'name': 'Device status',                    'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'stat',  'method': 'hold'},  
    'Fault':      {'addr': '32090', 'registers': 1,  'name': 'Fault code',                       'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'stat',  'method': 'hold'},  
    'PV_Un':      {'addr': '32016', 'registers': 1,  'name': 'PVn voltage',                      'scale': 10,   'type': 'I16',  'units': 'V'   , 'use': 'mult',  'method': 'hold'},  
    'PV_In':      {'addr': '32017', 'registers': 1,  'name': 'PVn current',                      'scale': 100,  'type': 'I16',  'units': 'A'   , 'use': 'mult',  'method': 'hold'},  
    'PV_P':       {'addr': '32064', 'registers': 2,  'name': 'Input power',                      'scale': 1000, 'type': 'I32',  'units': 'kW'  , 'use': 'data',  'method': 'hold'},  
    'U_A-B':      {'addr': '32066', 'registers': 1,  'name': 'Line Voltage A-B',                 'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},  
    'U_B-C':      {'addr': '32067', 'registers': 1,  'name': 'Line Voltage B-C',                 'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'ext' ,  'method': 'hold'},
    'U_C-A':      {'addr': '32068', 'registers': 1,  'name': 'Line Voltage C-A',                 'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'ext' ,  'method': 'hold'},
    'U_A':        {'addr': '32069', 'registers': 1,  'name': 'Phase Voltage A',                  'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},  
    'U_B':        {'addr': '32070', 'registers': 1,  'name': 'Phase Voltage B',                  'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},  
    'U_C':        {'addr': '32071', 'registers': 1,  'name': 'Phase Voltage C',                  'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'ext' ,  'method': 'hold'},
    'I_A':        {'addr': '32072', 'registers': 2,  'name': 'Phase Current A',                  'scale': 1000, 'type': 'I32',  'units': 'A'   , 'use': 'data',  'method': 'hold'},  
    'I_B':        {'addr': '32074', 'registers': 2,  'name': 'Phase Current B',                  'scale': 1000, 'type': 'I32',  'units': 'A'   , 'use': 'ext' ,  'method': 'hold'},
    'I_C':        {'addr': '32076', 'registers': 2,  'name': 'Phase Current C',                  'scale': 1000, 'type': 'I32',  'units': 'A'   , 'use': 'ext' ,  'method': 'hold'},
    'P_peak':     {'addr': '32078', 'registers': 2,  'name': 'Peak Power',                       'scale': 1000, 'type': 'I32',  'units': 'kW'  , 'use': 'data',  'method': 'hold'},  
    'P_active':   {'addr': '32080', 'registers': 2,  'name': 'Active power',                     'scale': 1000, 'type': 'I32',  'units': 'kW'  , 'use': 'data',  'method': 'hold'},  
    'P_reactive': {'addr': '32082', 'registers': 2,  'name': 'Reactive power',                   'scale': 1000, 'type': 'I32',  'units': 'kVar', 'use': 'data',  'method': 'hold'},  
    'PF':         {'addr': '32084', 'registers': 1,  'name': 'Power Factor',                     'scale': 1000, 'type': 'I16',  'units': ''    , 'use': 'data',  'method': 'hold'},  
    'Frequency':  {'addr': '32085', 'registers': 1,  'name': 'Grid frequency',                   'scale': 100,  'type': 'U16',  'units': 'Hz'  , 'use': 'data',  'method': 'hold'},  
    'η':          {'addr': '32086', 'registers': 1,  'name': 'Efficiency',                       'scale': 100,  'type': 'U16',  'units': '%'   , 'use': 'data',  'method': 'hold'},  
    'Temp':       {'addr': '32087', 'registers': 1,  'name': 'Internal temperature',             'scale': 10,   'type': 'I16',  'units': '°C'  , 'use': 'data',  'method': 'hold'},  
    'P_accum':    {'addr': '32106', 'registers': 2,  'name': 'Accumulated energy yield',         'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},  
    'P_daily':    {'addr': '32114', 'registers': 2,  'name': 'Daily energy yield',               'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},  
    'M_P':        {'addr': '37113', 'registers': 2,  'name': 'Active Grid power',                'scale': 1,    'type': 'I32',  'units': 'W'   , 'use': 'data',  'method': 'hold'},  
    'M_Pr':       {'addr': '37115', 'registers': 2,  'name': 'Active Grid reactive power',       'scale': 1,    'type': 'I32',  'units': 'VAR' , 'use': 'data',  'method': 'hold'},  
    'M_A-U':      {'addr': '37101', 'registers': 2,  'name': 'Active Grid A Voltage',            'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},  
    'M_B-U':      {'addr': '37103', 'registers': 2,  'name': 'Active Grid B Voltage',            'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},  
    'M_C-U':      {'addr': '37105', 'registers': 2,  'name': 'Active Grid C Voltage',            'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},  
    'M_A-I':      {'addr': '37107', 'registers': 2,  'name': 'Active Grid A Current',            'scale': 100,  'type': 'I32',  'units': 'I'   , 'use': 'data',  'method': 'hold'},  
    'M_B-I':      {'addr': '37109', 'registers': 2,  'name': 'Active Grid B Current',            'scale': 100,  'type': 'I32',  'units': 'I'   , 'use': 'data',  'method': 'hold'},  
    'M_C-I':      {'addr': '37111', 'registers': 2,  'name': 'Active Grid C Current',            'scale': 100,  'type': 'I32',  'units': 'I'   , 'use': 'data',  'method': 'hold'},  
    'M_PF':       {'addr': '37117', 'registers': 1,  'name': 'Active Grid PF',                   'scale': 1000, 'type': 'I16',  'units': ''    , 'use': 'data',  'method': 'hold'},  
    'M_Freq':     {'addr': '37118', 'registers': 1,  'name': 'Active Grid Frequency',            'scale': 100,  'type': 'I16',  'units': 'Hz'  , 'use': 'data',  'method': 'hold'},  
    'M_PExp':     {'addr': '37119', 'registers': 2,  'name': 'Grid Exported Energy',             'scale': 100,  'type': 'I32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},  
    'M_U_AB':     {'addr': '37126', 'registers': 2,  'name': 'Active Grid A-B Voltage',          'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},  
    'M_U_BC':     {'addr': '37128', 'registers': 2,  'name': 'Active Grid B-C Voltage',          'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},  
    'M_U_CA':     {'addr': '37130', 'registers': 2,  'name': 'Active Grid C-A Voltage',          'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},  
    'M_A-P':      {'addr': '37132', 'registers': 2,  'name': 'Active Grid A power',              'scale': 1,    'type': 'I32',  'units': 'W'   , 'use': 'data',  'method': 'hold'},  
    'M_B-P':      {'addr': '37134', 'registers': 2,  'name': 'Active Grid B power',              'scale': 1,    'type': 'I32',  'units': 'W'   , 'use': 'data',  'method': 'hold'},  
    'M_C-P':      {'addr': '37136', 'registers': 2,  'name': 'Active Grid C power',              'scale': 1,    'type': 'I32',  'units': 'W'   , 'use': 'data',  'method': 'hold'},  
    'M_PTot':     {'addr': '37121', 'registers': 2,  'name': 'Grid Accumulated Energy',          'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'}
}

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
        if (test_bit(value,1)):
            s += 'connected | '
        else:
            s += 'disconnected | '
        if (test_bit(value,2)):
            s += 'DSP collecting | '
        else:
            s += 'DSP not collecting | '
        
    elif (register == 'State3'):
        if (test_bit(value,0)):
            s += 'off-grid | '
        else:
            s += 'on-grid | '
        if (test_bit(value,1)):
            s += 'off-grid switch enable | '
        else:
            s += 'off-grid switch disable | '
        
    elif (register == 'Alarm1'):
        if (test_bit(value,0)):
            s += 'High String Input Voltage | '
        if (test_bit(value,1)):
            s += 'DC Arc Fault | '
        if (test_bit(value,2)):
            s += 'String Reverse Connection | '
        if (test_bit(value,3)):
            s += 'String Current Backfeed | '
        if (test_bit(value,4)):
            s += 'Abnormal String Power | '
        if (test_bit(value,5)):
            s += 'AFCI Self-Check Fail | '
        if (test_bit(value,6)):
            s += 'Phase Wire Short-Circuited to PE | '
        if (test_bit(value,7)):
            s += 'Grid Loss | '
        if (test_bit(value,8)):
            s += 'Grid Undervoltage | '
        if (test_bit(value,9)):
            s += 'Grid Overvoltage | '
        if (test_bit(value,10)):
            s += 'Grid Volt. Imbalance | '
        if (test_bit(value,11)):
            s += 'Grid Overfrequency | '
        if (test_bit(value,12)):
            s += 'Grid Underfrequency | '
        if (test_bit(value,13)):
            s += 'Unstable Grid Frequency | '
        if (test_bit(value,14)):
            s += 'Output Overcurrent | '
        if (test_bit(value,15)):
            s += 'Output DC Component Overhigh | '

    elif (register == 'Alarm2'):
        if (test_bit(value,0)):
            s += 'Abnormal Residual Current | '
        if (test_bit(value,1)):
            s += 'Abnormal Grounding | '
        if (test_bit(value,2)):
            s += 'Low Insulation Resistance | '
        if (test_bit(value,3)):
            s += 'Overtemperature | '
        if (test_bit(value,4)):
            s += 'Device Fault | '
        if (test_bit(value,5)):
            s += 'Upgrade Failed or Version Mismatch | '
        if (test_bit(value,6)):
            s += 'License Expired | '
        if (test_bit(value,7)):
            s += 'Faulty Monitoring Unit | '
        if (test_bit(value,8)):
            s += 'Faulty Power Collector | '
        if (test_bit(value,9)):
            s += 'Battery abnormal | '
        if (test_bit(value,10)):
            s += 'Active Islanding | '
        if (test_bit(value,11)):
            s += 'Passive Islanding | '
        if (test_bit(value,12)):
            s += 'Transient AC Overvoltage | '
        if (test_bit(value,13)):
            s += 'Peripheral port short circuit | '
        if (test_bit(value,14)):
            s += 'Churn output overload | '
        if (test_bit(value,15)):
            s += 'Abnormal PV module configuration | '
        
    elif (register == 'Alarm3'):
        if (test_bit(value,0)):
            s += 'Optimizer fault | '
        if (test_bit(value,1)):
            s += 'Built-in PID operation abnormal | '
        if (test_bit(value,2)):
            s += 'High input string voltage to ground | '
        if (test_bit(value,3)):
            s += 'External Fan Abnormal | '
        if (test_bit(value,4)):
            s += 'Battery Reverse Connection | '
        if (test_bit(value,5)):
            s += 'On-grid/Off-grid controller abnormal | '
        if (test_bit(value,6)):
            s += 'PV String Loss | '
        if (test_bit(value,7)):
            s += 'Internal Fan Abnormal | '
        if (test_bit(value,8)):
            s += 'DC Protection Unit Abnormal | '
        
    elif (register == 'Status'):
        s = _status_map[value]
    elif (register == 'Fault'):
        s = str(value)
    else:
        s = 'invalid status'
    if s.endswith(' | '):
        s = s[:-3]
    return s
    
def inv_address():
    udp_message = bytes([0x5a, 0x5a, 0x5a, 0x5a, 0x00, 0x41,
                         0x3a, 0x04, 0xc0, 0xa8, 0x00, 0x05])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(3.0)
    sock.bind(("", 6600))
    time.sleep(5)
    sock.sendto(udp_message, ('<broadcast>', 6600))
    i = 0
    while True:
        try:
            time.sleep(1)
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            if config.debug:
                print('--> resend')
            sock.sendto(udp_message, ('<broadcast>', 6600))
            time.sleep(2)
            i = i + 1
            if i < 5:
                time.sleep(5)
                continue
            else:
                if config.debug:
                    print("can't find inverter")
                if (config.inverter_ip != ""):
                    return config.inverter_ip
                    
        if len(data) == 30:
            addr = str(addr[0])
            if config.debug:
                print("inverter address: " + addr)
            return(addr)
