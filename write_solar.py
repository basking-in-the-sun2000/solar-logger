import time
import datetime
from datetime import timedelta

from influxdb import InfluxDBClient
import config


#print(midnight)
#print(t)
#print(time.ctime(t))
#print(measurement)

solar = [{ "month":202001,  "value":33.87},
{ "month":202002,  "value":32.97},
{ "month":202003,  "value":33.06},
{ "month":202004,  "value":32.9},
{ "month":202005,  "value":32.68},
{ "month":202006,  "value":29.77},
{ "month":202007,  "value":27.13},
{ "month":202008,  "value":27.52},
{ "month":202009,  "value":25.53},
{ "month":202010,  "value":24.45},
{ "month":202011,  "value":31.67},
{ "month":202012,  "value":30.87},
{ "month":202101,  "value":33.03},
{ "month":202102,  "value":33.29},
{ "month":202103,  "value":32.23},
{ "month":202104,  "value":32.07},
{ "month":202105,  "value":31.87},
{ "month":202106,  "value":29.03},
{ "month":202107,  "value":26.45},
{ "month":202108,  "value":26.84},
{ "month":202109,  "value":24.9},
{ "month":202110,  "value":23.84},
{ "month":202111,  "value":30.87},
{ "month":202112,  "value":30.1},
{ "month":202201,  "value":32.84},
{ "month":202202,  "value":33.11},
{ "month":202203,  "value":32.03},
{ "month":202204,  "value":31.9},
{ "month":202205,  "value":31.68},
{ "month":202206,  "value":28.83},
{ "month":202207,  "value":26.29},
{ "month":202208,  "value":26.68},
{ "month":202209,  "value":24.73},
{ "month":202210,  "value":23.71},
{ "month":202211,  "value":30.7},
{ "month":202212,  "value":29.9},
{ "month":202301,  "value":32.65},
{ "month":202302,  "value":32.89},
{ "month":202303,  "value":31.84},
{ "month":202304,  "value":31.7},
{ "month":202305,  "value":31.48},
{ "month":202306,  "value":28.67},
{ "month":202307,  "value":26.13},
{ "month":202308,  "value":26.52},
{ "month":202309,  "value":24.6},
{ "month":202310,  "value":23.55},
{ "month":202311,  "value":30.5},
{ "month":202312,  "value":29.74},
{ "month":202401,  "value":32.42},
{ "month":202402,  "value":31.55},
{ "month":202403,  "value":31.65},
{ "month":202404,  "value":31.5},
{ "month":202405,  "value":31.29},
{ "month":202406,  "value":28.5},
{ "month":202407,  "value":25.97},
{ "month":202408,  "value":26.35},
{ "month":202409,  "value":24.43},
{ "month":202410,  "value":23.42},
{ "month":202411,  "value":30.33},
{ "month":202412,  "value":29.55},
{ "month":202501,  "value":32.23},
{ "month":202502,  "value":32.5},
{ "month":202503,  "value":31.48},
{ "month":202504,  "value":31.3},
{ "month":202505,  "value":31.1},
{ "month":202506,  "value":28.33},
{ "month":202507,  "value":25.81},
{ "month":202508,  "value":26.19},
{ "month":202509,  "value":24.3},
{ "month":202510,  "value":23.26},
{ "month":202511,  "value":30.13},
{ "month":202512,  "value":29.39},
{ "month":202601,  "value":32.03},
{ "month":202602,  "value":32.29},
{ "month":202603,  "value":31.29},
{ "month":202604,  "value":31.13},
{ "month":202605,  "value":30.9},
{ "month":202606,  "value":28.17},
{ "month":202607,  "value":25.68},
{ "month":202608,  "value":26.03},
{ "month":202609,  "value":24.17},
{ "month":202610,  "value":23.13},
{ "month":202611,  "value":29.97},
{ "month":202612,  "value":29.19},
{ "month":202701,  "value":31.84},
{ "month":202702,  "value":32.11},
{ "month":202703,  "value":31.1},
{ "month":202704,  "value":30.93},
{ "month":202705,  "value":30.74},
{ "month":202706,  "value":28},
{ "month":202707,  "value":25.52},
{ "month":202708,  "value":25.87},
{ "month":202709,  "value":24},
{ "month":202710,  "value":23},
{ "month":202711,  "value":29.77},
{ "month":202712,  "value":29.03},
{ "month":202801,  "value":31.68},
{ "month":202802,  "value":30.83},
{ "month":202803,  "value":30.9},
{ "month":202804,  "value":30.77},
{ "month":202805,  "value":30.55},
{ "month":202806,  "value":27.83},
{ "month":202807,  "value":25.35},
{ "month":202808,  "value":25.71},
{ "month":202809,  "value":23.87},
{ "month":202810,  "value":22.87},
{ "month":202811,  "value":29.6},
{ "month":202812,  "value":28.87},
{ "month":202901,  "value":31.48},
{ "month":202902,  "value":31.71},
{ "month":202903,  "value":30.71},
{ "month":202904,  "value":30.57},
{ "month":202905,  "value":30.35},
{ "month":202906,  "value":27.67},
{ "month":202907,  "value":25.19},
{ "month":202908,  "value":25.58},
{ "month":202909,  "value":23.73},
{ "month":202910,  "value":22.71},
{ "month":202911,  "value":29.43},
{ "month":202912,  "value":28.68},
{ "month":203001,  "value":31.29},
{ "month":203002,  "value":31.54},
{ "month":203003,  "value":30.55},
{ "month":203004,  "value":30.4},
{ "month":203005,  "value":30.19},
{ "month":203006,  "value":27.5},
{ "month":203007,  "value":25.06},
{ "month":203008,  "value":25.42},
{ "month":203009,  "value":23.57},
{ "month":203010,  "value":22.58},
{ "month":203011,  "value":29.23},
{ "month":203012,  "value":28.52},
{ "month":203101,  "value":31.1},
{ "month":203102,  "value":31.36},
{ "month":203103,  "value":30.35},
{ "month":203104,  "value":30.2},
{ "month":203105,  "value":30},
{ "month":203106,  "value":27.33},
{ "month":203107,  "value":24.9},
{ "month":203108,  "value":25.26},
{ "month":203109,  "value":23.43},
{ "month":203110,  "value":22.45},
{ "month":203111,  "value":29.07},
{ "month":203112,  "value":28.35},
{ "month":203201,  "value":30.9},
{ "month":203202,  "value":30.07},
{ "month":203203,  "value":30.16},
{ "month":203204,  "value":30.03},
{ "month":203205,  "value":29.81},
{ "month":203206,  "value":27.17},
{ "month":203207,  "value":24.74},
{ "month":203208,  "value":25.1},
{ "month":203209,  "value":23.3},
{ "month":203210,  "value":22.32},
{ "month":203211,  "value":28.9},
{ "month":203212,  "value":28.16},
{ "month":203301,  "value":30.71},
{ "month":203302,  "value":30.96},
{ "month":203303,  "value":30},
{ "month":203304,  "value":29.83},
{ "month":203305,  "value":29.65},
{ "month":203306,  "value":27},
{ "month":203307,  "value":24.61},
{ "month":203308,  "value":24.97},
{ "month":203309,  "value":23.17},
{ "month":203310,  "value":22.19},
{ "month":203311,  "value":28.73},
{ "month":203312,  "value":28},
{ "month":203401,  "value":30.55},
{ "month":203402,  "value":30.79},
{ "month":203403,  "value":29.81},
{ "month":203404,  "value":29.67},
{ "month":203405,  "value":29.45},
{ "month":203406,  "value":26.83},
{ "month":203407,  "value":24.45},
{ "month":203408,  "value":24.81},
{ "month":203409,  "value":23.03},
{ "month":203410,  "value":22.03},
{ "month":203411,  "value":28.57},
{ "month":203412,  "value":27.84},
{ "month":203501,  "value":30.35},
{ "month":203502,  "value":30.61},
{ "month":203503,  "value":29.65},
{ "month":203504,  "value":29.5},
{ "month":203505,  "value":29.29},
{ "month":203506,  "value":26.67},
{ "month":203507,  "value":24.32},
{ "month":203508,  "value":24.65},
{ "month":203509,  "value":22.9},
{ "month":203510,  "value":21.9},
{ "month":203511,  "value":28.37},
{ "month":203512,  "value":27.68},
{ "month":203601,  "value":30.16},
{ "month":203602,  "value":29.38},
{ "month":203603,  "value":29.45},
{ "month":203604,  "value":29.3},
{ "month":203605,  "value":29.1},
{ "month":203606,  "value":26.53},
{ "month":203607,  "value":24.16},
{ "month":203608,  "value":24.52},
{ "month":203609,  "value":22.73},
{ "month":203610,  "value":21.77},
{ "month":203611,  "value":28.2},
{ "month":203612,  "value":27.52},
{ "month":203701,  "value":30},
{ "month":203702,  "value":30.25},
{ "month":203703,  "value":29.29},
{ "month":203704,  "value":29.13},
{ "month":203705,  "value":28.94},
{ "month":203706,  "value":26.37},
{ "month":203707,  "value":24.03},
{ "month":203708,  "value":24.35},
{ "month":203709,  "value":22.6},
{ "month":203710,  "value":21.65},
{ "month":203711,  "value":28.03},
{ "month":203712,  "value":27.32},
{ "month":203801,  "value":29.81},
{ "month":203802,  "value":30.04},
{ "month":203803,  "value":29.1},
{ "month":203804,  "value":28.97},
{ "month":203805,  "value":28.77},
{ "month":203806,  "value":26.2},
{ "month":203807,  "value":23.87},
{ "month":203808,  "value":24.23},
{ "month":203809,  "value":22.47},
{ "month":203810,  "value":21.52},
{ "month":203811,  "value":27.87},
{ "month":203812,  "value":27.16},
{ "month":203901,  "value":29.65},
{ "month":203902,  "value":29.86},
{ "month":203903,  "value":28.94},
{ "month":203904,  "value":28.8},
{ "month":203905,  "value":28.58},
{ "month":203906,  "value":26.03},
{ "month":203907,  "value":23.74},
{ "month":203908,  "value":24.06},
{ "month":203909,  "value":22.33},
{ "month":203910,  "value":21.39},
{ "month":203911,  "value":27.7},
{ "month":203912,  "value":27},
{ "month":204001,  "value":29.45},
{ "month":204002,  "value":28.66},
{ "month":204003,  "value":28.74},
{ "month":204004,  "value":28.6},
{ "month":204005,  "value":28.42},
{ "month":204006,  "value":25.9},
{ "month":204007,  "value":23.58},
{ "month":204008,  "value":23.94},
{ "month":204009,  "value":22.2},
{ "month":204010,  "value":21.26},
{ "month":204011,  "value":27.53},
{ "month":204012,  "value":26.84},
{ "month":204101,  "value":29.29},
{ "month":204102,  "value":29.5},
{ "month":204103,  "value":28.58},
{ "month":204104,  "value":28.43},
{ "month":204105,  "value":28.26},
{ "month":204106,  "value":25.73},
{ "month":204107,  "value":23.45},
{ "month":204108,  "value":23.77},
{ "month":204109,  "value":22.07},
{ "month":204110,  "value":21.13},
{ "month":204111,  "value":27.37},
{ "month":204112,  "value":26.68},
{ "month":204201,  "value":29.1},
{ "month":204202,  "value":29.32},
{ "month":204203,  "value":28.42},
{ "month":204204,  "value":28.27},
{ "month":204205,  "value":28.06},
{ "month":204206,  "value":25.57},
{ "month":204207,  "value":23.32},
{ "month":204208,  "value":23.65},
{ "month":204209,  "value":21.93},
{ "month":204210,  "value":21},
{ "month":204211,  "value":27.2},
{ "month":204212,  "value":26.52},
{ "month":204301,  "value":28.94},
{ "month":204302,  "value":29.18},
{ "month":204303,  "value":28.23},
{ "month":204304,  "value":28.1},
{ "month":204305,  "value":27.9},
{ "month":204306,  "value":25.43},
{ "month":204307,  "value":23.16},
{ "month":204308,  "value":23.52},
{ "month":204309,  "value":21.8},
{ "month":204310,  "value":20.87},
{ "month":204311,  "value":27.03},
{ "month":204312,  "value":26.35},
{ "month":204401,  "value":28.74},
{ "month":204402,  "value":28},
{ "month":204403,  "value":28.06},
{ "month":204404,  "value":27.93},
{ "month":204405,  "value":27.74},
{ "month":204406,  "value":25.27},
{ "month":204407,  "value":23.03},
{ "month":204408,  "value":23.35},
{ "month":204409,  "value":21.67},
{ "month":204410,  "value":20.77},
{ "month":204411,  "value":26.9},
{ "month":204412,  "value":26.19},
{ "month":204501,  "value":28.58},
{ "month":204502,  "value":28.82},
{ "month":204503,  "value":27.9},
{ "month":204504,  "value":27.77},
{ "month":204505,  "value":27.58},
{ "month":204506,  "value":25.13},
{ "month":204507,  "value":22.9},
{ "month":204508,  "value":23.23},
{ "month":204509,  "value":21.53},
{ "month":204510,  "value":20.65},
{ "month":204511,  "value":26.73},
{ "month":204512,  "value":26.06},
{ "month":204601,  "value":28.42},
{ "month":204602,  "value":28.64},
{ "month":204603,  "value":27.74},
{ "month":204604,  "value":27.6},
{ "month":204605,  "value":27.42},
{ "month":204606,  "value":24.97},
{ "month":204607,  "value":22.74},
{ "month":204608,  "value":23.1},
{ "month":204609,  "value":21.43},
{ "month":204610,  "value":20.52},
{ "month":204611,  "value":26.57},
{ "month":204612,  "value":25.9},
{ "month":204701,  "value":28.23},
{ "month":204702,  "value":28.46},
{ "month":204703,  "value":27.58},
{ "month":204704,  "value":27.43},
{ "month":204705,  "value":27.26},
{ "month":204706,  "value":24.83},
{ "month":204707,  "value":22.61},
{ "month":204708,  "value":22.94},
{ "month":204709,  "value":21.3},
{ "month":204710,  "value":20.39},
{ "month":204711,  "value":26.4},
{ "month":204712,  "value":25.74},
{ "month":204801,  "value":28.06},
{ "month":204802,  "value":27.31},
{ "month":204803,  "value":27.39},
{ "month":204804,  "value":27.27},
{ "month":204805,  "value":27.1},
{ "month":204806,  "value":24.67},
{ "month":204807,  "value":22.48},
{ "month":204808,  "value":22.81},
{ "month":204809,  "value":21.17},
{ "month":204810,  "value":20.26},
{ "month":204811,  "value":26.23},
{ "month":204812,  "value":25.58},
{ "month":204901,  "value":27.9},
{ "month":204902,  "value":28.14},
{ "month":204903,  "value":27.23},
{ "month":204904,  "value":27.1},
{ "month":204905,  "value":26.94},
{ "month":204906,  "value":24.53},
{ "month":204907,  "value":22.35},
{ "month":204908,  "value":22.68},
{ "month":204909,  "value":21.03},
{ "month":204910,  "value":20.13},
{ "month":204911,  "value":26.1},
{ "month":204912,  "value":25.42}]

measurement = {}

flux_client = 0

flux_client = InfluxDBClient("127.0.0.1", 8086)

for month in solar:
    t = int(time.mktime(time.strptime(str(month["month"]) + '01', "%Y%m%d")))

    measurement["radiance"] = float(month["value"])

    if flux_client is not None:
        metrics = {}
        tags = {}
        if t > 0:
            metrics['time'] = t * 1000000000
        metrics['measurement'] = "solar"
        tags['location'] = "main"
        metrics['tags'] = tags
        metrics['fields'] = measurement
        metrics =[metrics, ]

        print(metrics)

    #    flux_client.create_database("logger_lt")


        target=flux_client.write_points(metrics, database=config.influxdb_database)

