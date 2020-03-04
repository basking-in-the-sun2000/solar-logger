import itertools
import collections
from collections import OrderedDict
from datetime import datetime, timedelta
from urllib.parse import urljoin

from isodate import parse_datetime, parse_duration
from collections import OrderedDict
import requests

from solcast.base import Base


class RadiationForecasts(Base):

    end_point = 'radiation/forecasts'

    def __init__(self, latitude, longitude, *args, **kwargs):

        self.latitude = latitude
        self.longitude = longitude
        self.forecasts = None
        self.next_forecast = None

        self.params = {'latitude' : self.latitude,
                       'longitude' : self.longitude}

        self._get(*args, **kwargs)

        if self.ok:
            self._get_next_forecast_point()
            period = kwargs.get('hours')
            if period == 24:
                self._get_next_24_hours()
            else:
                self._generate_forecasts_dict()

    def _generate_forecasts_dict(self):

        self.forecasts = []

        for forecast in self.content.get('forecasts'):

            # Convert period_end and period. All other fields should already be
            # the correct type
            #forecast['period_end'] = parse_datetime(forecast['period_end'])
            #forecast['period'] = parse_duration(forecast['period'])

            self.forecasts.append(forecast)

    def _get_next_forecast_point(self):

        self.next_forecast = None
        dict_data = {}
        for est_act in self.content.get('forecasts'):
            dict_data[parse_datetime(est_act['period_end'])] = est_act
        dict_data = OrderedDict(sorted(dict_data.items()))
        last = itertools.islice(dict_data.items(), 0, 1)
        for key, value in last:
            self.next_forecast = value
    
    def _get_next_24_hours(self):

        self.forecasts = []
        dict_data = {}
        for est_act in self.content.get('forecasts'):
            dict_data[parse_datetime(est_act['period_end'])] = est_act
        dict_data = OrderedDict(sorted(dict_data.items()))
        lastt_24 = itertools.islice(dict_data.items(), 0, 48)
        for key, value in lastt_24:
            self.forecasts.append(value)