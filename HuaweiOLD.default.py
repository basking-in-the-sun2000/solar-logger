import socket
import time
import config
import emails

# Change use to ext for type you won't use or aren't defined by your inverter

_register_map =  {
#  search by Model_ID or by 2B Request  'Model':      {'addr': '30000', 'registers': 15, 'name': 'Model',                            'scale': 1,    'type': 'str',  'units': ''    , 'use': 'info',  'method': 'hold'},
    'SN':         {'addr': '32003', 'registers': 10, 'name': 'Serial Number',                    'scale': 1,    'type': 'str',  'units': ''    , 'use': 'info',  'method': 'hold'},
# search by Model_ID    'strings':    {'addr': '30071', 'registers': 1,  'name': 'Number of strings',                'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
# search by Model_ID       'Pn':         {'addr': '30073', 'registers': 2,  'name': 'Rated power',                      'scale': 1000, 'type': 'U32',  'units': 'kW'  , 'use': 'info',  'method': 'hold'},
# search by Model_ID       'Pmax':       {'addr': '30075', 'registers': 2,  'name': 'Maximum active power',             'scale': 1000, 'type': 'U32',  'units': 'kW'  , 'use': 'info',  'method': 'hold'},
# search by Model_ID       'Smax':       {'addr': '30077', 'registers': 2,  'name': 'Maximum apparent power',           'scale': 1000, 'type': 'U32',  'units': 'kVA' , 'use': 'info',  'method': 'hold'},
# search by Model_ID       'Qmax':       {'addr': '30079', 'registers': 2,  'name': 'Maximum reactive power to grid',   'scale': 1000, 'type': 'I32',  'units': 'kVar', 'use': 'info',  'method': 'hold'},
  #  'Qgrid':      {'addr': '30081', 'registers': 2,  'name': 'Maximum reactive power from grid', 'scale': 1000, 'type': 'I32',  'units': 'kVar', 'use': 'info',  'method': 'hold'},
    'Insulation': {'addr': '32323', 'registers': 1,  'name': 'Insulation resistance',            'scale': 1000, 'type': 'U16',  'units': 'MΩ'  , 'use': 'info',  'method': 'hold'},
    'Start':      {'addr': '32325', 'registers': 2,  'name': 'Startup time',                     'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'info',  'method': 'hold'},
    'Shutdown':   {'addr': '32327', 'registers': 2,  'name': 'Shutdown time',                    'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'info',  'method': 'hold'},
    'Time':       {'addr': '40000', 'registers': 2,  'name': 'Current time',                     'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'info',  'method': 'hold'},
#    'Time1?':     {'addr': '32110', 'registers': 2,  'name': 'some time 1',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},
#    'Time2?':     {'addr': '32156', 'registers': 2,  'name': 'some time 2',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},
#    'Time3?':     {'addr': '32160', 'registers': 2,  'name': 'some time 3',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},
#    'Time4?':     {'addr': '35113', 'registers': 2,  'name': 'some time 4',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},
#    'Time5?':     {'addr': '40500', 'registers': 2,  'name': 'some time 5',                      'scale': 1,    'type': 'U32',  'units': 's'   , 'use': 'ext',   'method': 'hold'},
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
#not use    'Alarm11':     {'addr': '50010', 'registers': 1,  'name': 'Alarm 2',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
#not use      'Alarm12':     {'addr': '50011', 'registers': 1,  'name': 'Alarm 3',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
#not use      'Alarm13':     {'addr': '50012', 'registers': 1,  'name': 'Alarm 1',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
#not use      'Alarm14':     {'addr': '50013', 'registers': 1,  'name': 'Alarm 2',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
#not use      'Alarm15':     {'addr': '50014', 'registers': 1,  'name': 'Alarm 3',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
#not use      'Alarm16':     {'addr': '50015', 'registers': 1,  'name': 'Alarm 1',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Alarm17':     {'addr': '50016', 'registers': 1,  'name': 'Alarm 2',                          'scale': 1,    'type': 'Bit16','units': ''    , 'use': 'stat',  'method': 'hold'},
    'Status':     {'addr': '32287', 'registers': 1,  'name': 'Device status',                    'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'stat',  'method': 'hold'},
#    'Fault':      {'addr': '32090', 'registers': 1,  'name': 'Fault code',                       'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'stat',  'method': 'hold'},
#    'PV_Un':      {'addr': '32016', 'registers': 1,  'name': 'PVn voltage',                      'scale': 10,   'type': 'I16',  'units': 'V'   , 'use': 'mult',  'method': 'hold'},
#    'PV_In':      {'addr': '32017', 'registers': 1,  'name': 'PVn current',                      'scale': 100,  'type': 'I16',  'units': 'A'   , 'use': 'mult',  'method': 'hold'},
    'PV_P':       {'addr': '32294', 'registers': 2,  'name': 'Input power',                      'scale': 1000, 'type': 'U32',  'units': 'kW'  , 'use': 'data',  'method': 'hold'},
    'U_A-B':      {'addr': '32274', 'registers': 1,  'name': 'Line Voltage A-B',                 'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
    'U_B-C':      {'addr': '32275', 'registers': 1,  'name': 'Line Voltage B-C',                 'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'ext' ,  'method': 'hold'},
    'U_C-A':      {'addr': '32276', 'registers': 1,  'name': 'Line Voltage C-A',                 'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'ext' ,  'method': 'hold'},
    'U_A':        {'addr': '32277', 'registers': 1,  'name': 'Phase Voltage A',                  'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
    'U_B':        {'addr': '32278', 'registers': 1,  'name': 'Phase Voltage B',                  'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
    'U_C':        {'addr': '32279', 'registers': 1,  'name': 'Phase Voltage C',                  'scale': 10,   'type': 'U16',  'units': 'V'   , 'use': 'ext' ,  'method': 'hold'},
    'I_A':        {'addr': '32280', 'registers': 2,  'name': 'Phase Current A',                  'scale': 1000, 'type': 'I32',  'units': 'A'   , 'use': 'data',  'method': 'hold'},
    'I_B':        {'addr': '32281', 'registers': 2,  'name': 'Phase Current B',                  'scale': 1000, 'type': 'I32',  'units': 'A'   , 'use': 'ext' ,  'method': 'hold'},
    'I_C':        {'addr': '32282', 'registers': 2,  'name': 'Phase Current C',                  'scale': 1000, 'type': 'I32',  'units': 'A'   , 'use': 'ext' ,  'method': 'hold'},
    'P_peak':     {'addr': '32288', 'registers': 2,  'name': 'Peak Power',                       'scale': 1000, 'type': 'I32',  'units': 'kW'  , 'use': 'data',  'method': 'hold'},
    'P_active':   {'addr': '32290', 'registers': 2,  'name': 'Active power',                     'scale': 1000, 'type': 'I32',  'units': 'kW'  , 'use': 'data',  'method': 'hold'},
    'P_reactive': {'addr': '32292', 'registers': 2,  'name': 'Reactive power',                   'scale': 1000, 'type': 'I32',  'units': 'kVar', 'use': 'data',  'method': 'hold'},
    'PF':         {'addr': '32284', 'registers': 1,  'name': 'Power Factor',                     'scale': 1000, 'type': 'I16',  'units': ''    , 'use': 'data',  'method': 'hold'},
    'Frequency':  {'addr': '32283', 'registers': 1,  'name': 'Grid frequency',                   'scale': 100,  'type': 'U16',  'units': 'Hz'  , 'use': 'data',  'method': 'hold'},
    'η':          {'addr': '32285', 'registers': 1,  'name': 'Efficiency',                       'scale': 100,  'type': 'U16',  'units': '%'   , 'use': 'data',  'method': 'hold'},
    'Temp':       {'addr': '32286', 'registers': 1,  'name': 'Internal temperature',             'scale': 10,   'type': 'I16',  'units': '°C'  , 'use': 'data',  'method': 'hold'},
    'P_accum':    {'addr': '32306', 'registers': 2,  'name': 'Accumulated energy yield',         'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},
    'P_daily':    {'addr': '32300', 'registers': 2,  'name': 'Daily energy yield',               'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},
#    'M_status':   {'addr': '37100', 'registers': 1,  'name': 'Meter status',                     'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'stat',  'method': 'hold'},
#    'M_check':    {'addr': '37138', 'registers': 1,  'name': 'Meter detection result',           'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'stat',  'method': 'hold'},
#    'M_type':     {'addr': '37125', 'registers': 1,  'name': 'Meter type'  ,                     'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'stat',  'method': 'hold'},
#    'M_P':        {'addr': '37113', 'registers': 2,  'name': 'Active Grid power',                'scale': 1,    'type': 'I32',  'units': 'W'   , 'use': 'data',  'method': 'hold'},
#    'M_Pr':       {'addr': '37115', 'registers': 2,  'name': 'Active Grid reactive power',       'scale': 1,    'type': 'I32',  'units': 'VAR' , 'use': 'data',  'method': 'hold'},
#    'M_A-U':      {'addr': '37101', 'registers': 2,  'name': 'Active Grid A Voltage',            'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
#    'M_B-U':      {'addr': '37103', 'registers': 2,  'name': 'Active Grid B Voltage',            'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
#    'M_C-U':      {'addr': '37105', 'registers': 2,  'name': 'Active Grid C Voltage',            'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
#    'M_A-I':      {'addr': '37107', 'registers': 2,  'name': 'Active Grid A Current',            'scale': 100,  'type': 'I32',  'units': 'I'   , 'use': 'data',  'method': 'hold'},
#    'M_B-I':      {'addr': '37109', 'registers': 2,  'name': 'Active Grid B Current',            'scale': 100,  'type': 'I32',  'units': 'I'   , 'use': 'data',  'method': 'hold'},
#    'M_C-I':      {'addr': '37111', 'registers': 2,  'name': 'Active Grid C Current',            'scale': 100,  'type': 'I32',  'units': 'I'   , 'use': 'data',  'method': 'hold'},
#    'M_PF':       {'addr': '37117', 'registers': 1,  'name': 'Active Grid PF',                   'scale': 1000, 'type': 'I16',  'units': ''    , 'use': 'data',  'method': 'hold'},
#    'M_Freq':     {'addr': '37118', 'registers': 1,  'name': 'Active Grid Frequency',            'scale': 100,  'type': 'I16',  'units': 'Hz'  , 'use': 'data',  'method': 'hold'},
#    'M_PExp':     {'addr': '37119', 'registers': 2,  'name': 'Grid Exported Energy',             'scale': 100,  'type': 'I32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},
#    'M_U_AB':     {'addr': '37126', 'registers': 2,  'name': 'Active Grid A-B Voltage',          'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
#    'M_U_BC':     {'addr': '37128', 'registers': 2,  'name': 'Active Grid B-C Voltage',          'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
#    'M_U_CA':     {'addr': '37130', 'registers': 2,  'name': 'Active Grid C-A Voltage',          'scale': 10,   'type': 'I32',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
#    'M_A-P':      {'addr': '37132', 'registers': 2,  'name': 'Active Grid A power',              'scale': 1,    'type': 'I32',  'units': 'W'   , 'use': 'data',  'method': 'hold'},
#    'M_B-P':      {'addr': '37134', 'registers': 2,  'name': 'Active Grid B power',              'scale': 1,    'type': 'I32',  'units': 'W'   , 'use': 'data',  'method': 'hold'},
#    'M_C-P':      {'addr': '37136', 'registers': 2,  'name': 'Active Grid C power',              'scale': 1,    'type': 'I32',  'units': 'W'   , 'use': 'data',  'method': 'hold'},
#    'M_PTot':     {'addr': '37121', 'registers': 2,  'name': 'Grid Accumulated Energy',          'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},
#    'M_RPTot':    {'addr': '37123', 'registers': 2,  'name': 'Grid Accumulated Reactive Energy', 'scale': 100,  'type': 'I32',  'units': 'KVarh','use': 'data',  'method': 'hold'},
    'ModelID':    {'addr': '32001', 'registers': 1,  'name': 'Model ID',                         'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
#search by Model_ID    'MPPT_N':     {'addr': '30072', 'registers': 1,  'name': 'MPPT Number',                      'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
    'PF_comp':    {'addr': '40122', 'registers': 1,  'name': 'Reactive power compensation',      'scale': 1000, 'type': 'I16',  'units': ''    , 'use': 'data',  'method': 'hold'},
    'Q/S':        {'addr': '40123', 'registers': 1,  'name': 'Reactive power compensation(Q/S)', 'scale': 1000, 'type': 'I16',  'units': ''    , 'use': 'data',  'method': 'hold'},
    'Derating':   {'addr': '40125', 'registers': 1,  'name': 'Active power derating percent',    'scale': 10,   'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
# not impl    'Derating_w': {'addr': '40126', 'registers': 2,  'name': 'Active power derating',            'scale': 1,    'type': 'U32',  'units': 'W'   , 'use': 'info',  'method': 'hold'},
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

#if (config.has_optim) :
    #not impl
    # _register_map.update({
    #     'Optim_tot':  {'addr': '37200', 'registers': 1,  'name': 'Number of optimizers',             'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
    #     'Optim_on':   {'addr': '37201', 'registers': 1,  'name': 'Number of online optimizers',      'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'},
    #     'Optim_opt':  {'addr': '37202', 'registers': 1,  'name': 'Optimizer Feature data',           'scale': 1,    'type': 'U16',  'units': ''    , 'use': 'info',  'method': 'hold'}})

# if (config.has_ESU) :
#not
#     _register_map.update({
#         'ESU_status':  {'addr': '37000', 'registers': 1,  'name': 'ESU status',                       'scale': 1,    'type': 'U16',  'units': ''  ,   'use': 'status',  'method': 'hold'},
#         'ESU_power':   {'addr': '37001', 'registers': 2,  'name': 'ESU power',                        'scale': 1,    'type': 'I32',  'units': 'W'   , 'use': 'data',  'method': 'hold'},
#         'ESU_voltage': {'addr': '37003', 'registers': 1,  'name': 'ESU voltage',                      'scale': 10,   'type': 'I16',  'units': 'V'   , 'use': 'data',  'method': 'hold'},
#         'ESU_soc':     {'addr': '37004', 'registers': 1,  'name': 'ESU SOC',                          'scale': 10,   'type': 'U16',  'units': '%'   , 'use': 'data',  'method': 'hold'},
#         'ESU_mode':    {'addr': '37006', 'registers': 1,  'name': 'ESU working mode b',               'scale': 1,    'type': 'U16',  'units': '%'   , 'use': 'data',  'method': 'hold'},
#         'ESU_rated_power':  {'addr': '37007', 'registers': 2,  'name': 'ESU rated power',             'scale': 1,    'type': 'U32',  'units': 'W'   , 'use': 'info',  'method': 'hold'},
#         'ESU_rated_discharge':  {'addr': '37009', 'registers': 2,  'name': 'ESU rated discharge',     'scale': 1,    'type': 'U32',  'units': 'W'   , 'use': 'info',  'method': 'hold'},
#         'ESU_fault':   {'addr': '37014', 'registers': 1,  'name': 'ESU fault id',                     'scale': 1,    'type': 'U16',  'units': '' ,    'use': 'stat',  'method': 'hold'},
#         'ESU_charge':  {'addr': '37015', 'registers': 2,  'name': 'ESU Current Charge',               'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},
#         'ESU_discharge':{'addr': '37017','registers': 2,  'name': 'ESU Current Discharge',            'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'data',  'method': 'hold'},
#         'ESU_current': {'addr': '37021', 'registers': 1,  'name': 'ESU Current',                      'scale': 10,   'type': 'I16',  'units': 'A' ,   'use': 'data',  'method': 'hold'},
#         'ESU_temp':    {'addr': '37022', 'registers': 1,  'name': 'ESU temperature',                  'scale': 10,   'type': 'I16',  'units': '°C' ,  'use': 'data',  'method': 'hold'},
#         'ESU_time':    {'addr': '37025', 'registers': 1,  'name': 'ESU remaining time',               'scale': 1,    'type': 'U16',  'units': 'min' , 'use': 'data',  'method': 'hold'},
#         'ESU_dcdc_v':  {'addr': '37026', 'registers': 10, 'name': 'ESU DC-DC version',                'scale': 1,    'type': 'str',  'units': '' ,    'use': 'info',  'method': 'hold'},
#         'ESU_bms_v':   {'addr': '37036', 'registers': 10, 'name': 'ESU BMS version',                  'scale': 1,    'type': 'str',  'units': '' ,    'use': 'info',  'method': 'hold'},
#         'ESU_max_charge': {'addr': '37046', 'registers': 2,  'name': 'ESU max charge power',          'scale': 1,    'type': 'U32',  'units': 'W' ,   'use': 'info',  'method': 'hold'},
#         'ESU_max_discharge': {'addr': '37048', 'registers': 2,  'name': 'ESU max discharge power',    'scale': 1,    'type': 'U32',  'units': 'W' ,   'use': 'info',  'method': 'hold'},
#         'ESU_serialN':  {'addr': '37052', 'registers': 10,  'name': 'ESU serial number',              'scale': 1,    'type': 'str',  'units': '' ,    'use': 'info',  'method': 'hold'},
#         'ESU_tot_charge':  {'addr': '37066', 'registers': 2,  'name': 'ESU total charge',             'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'info',  'method': 'hold'},
#         'ESU_tot_discharge':  {'addr': '37068', 'registers': 2,  'name': 'ESU total discharge',       'scale': 100,  'type': 'U32',  'units': 'kWh' , 'use': 'info',  'method': 'hold'},
#         'ESU_model':   {'addr': '47000', 'registers': 1,  'name': 'ESU battery type',                 'scale': 1,    'type': 'U16',  'units': '' ,    'use': 'info',  'method': 'hold'},
#         'ESU_charging':   {'addr': '47075', 'registers': 2,  'name': 'ESU max charging power',        'scale': 1,    'type': 'U32',  'units': 'W' ,    'use': 'info',  'method': 'hold'},
#         'ESU_discharging':   {'addr': '47077', 'registers': 2,  'name': 'ESU max discharging power',  'scale': 1,    'type': 'U32',  'units': 'W' ,    'use': 'info',  'method': 'hold'},
#         'ESU_charging_cutoff':  {'addr': '47081', 'registers': 1,  'name': 'ESU charging cutoff',     'scale': 10,   'type': 'U16',  'units': '%' ,    'use': 'info',  'method': 'hold'},
#         'ESU_discharging_cutoff': {'addr': '47082', 'registers': 1, 'name': 'ESU discharging cutoff', 'scale': 10,   'type': 'U16',  'units': '%' ,    'use': 'info',  'method': 'hold'},
#         'ESU_forced':  {'addr': '47083', 'registers': 1,  'name': 'ESU forced cutoff',                'scale': 1,    'type': 'U16',  'units': 'min' ,  'use': 'info',  'method': 'hold'},
#         'ESU_mode2':   {'addr': '47086', 'registers': 1,  'name': 'ESU mode 2',                       'scale': 1,    'type': 'U16',  'units': '' ,     'use': 'info',  'method': 'hold'},
#         'ESU_grid':    {'addr': '47087', 'registers': 1,  'name': 'ESU grid charging',                'scale': 1,    'type': 'U16',  'units': '' ,     'use': 'info',  'method': 'hold'},
#         'ESU_excess':  {'addr': '47299', 'registers': 1,  'name': 'ESU Excess energy use',            'scale': 1,    'type': 'U16',  'units': '' ,     'use': 'info',  'method': 'hold'}})


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
    #not impl elif (register == 'Fault'):
    #     s = str(value)
    # not impl elif (register == 'M_status'):
    #     if value == 1:
    #         s = "normal"
    #     else:
    #         s = "offline"
    # elif (register == 'M_type'):
    #     if value == 1:
    #         s = "three phase"
    #     else:
    #         s = "one phase"
    # else:
    #     s = 'invalid status'
    if s.endswith(' | '):
        s = s[:-3]
    return s

# def inv_address():
#     udp_message = bytes([0x5a, 0x5a, 0x5a, 0x5a, 0x00, 0x41, 0x3a, 0x04])

#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#     sock.connect(("1.1.1.1", 80))
#     ip = sock.getsockname()[0]
#     ip_self = ip
#     ip = socket.inet_aton(ip)
#     sock.close()

#     for i in ip:
#         udp_message += bytes([i])
#     if config.debug:
#         print(ip)
#         print("\n")
#         print(udp_message)
#         print("\n")

#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#     sock.settimeout(10.0)
#     sock.bind(("", 6600))
#     sock.sendto(udp_message, ('<broadcast>', 6600))
#     i = 0
#     while True:
#         try:
#             time.sleep(1)
#             data, addr = sock.recvfrom(1024)
# #        except socket.timeout:
#         except Exception as e:
#             print("huaweil inv_address error: %s" % str(e))
#             if config.debug:
#                 print('--> resend')
#             sock.sendto(udp_message, ('<broadcast>', 6600))
#             time.sleep(2)
#             i = i + 1
#             if i < 5:
#                 time.sleep(5)
#                 continue
#             else:
#                 if config.debug:
#                     print("can't find inverter")
#                 if (config.inverter_ip != ""):
#                     return ""
#                 emails.send_mail("can't find inverter" + str(e))

#         if addr[0] != ip_self:
#             addr = str(addr[0])
#             if config.debug:
#                 print("inverter address: " + addr)
#             return(addr)
