import itertools
import collections
from collections import OrderedDict
from datetime import datetime, timedelta
from urllib.parse import urljoin

from isodate import parse_datetime, parse_duration
import requests

from solcast.base import Base


class RadiationEstimatedActuals(Base):

    end_point = 'radiation/estimated_actuals'

    def __init__(self, latitude, longitude, *args, **kwargs):

        self.latitude = latitude
        self.longitude = longitude
        self.latest = kwargs.get('latest', False)
        self.estimated_actuals = None
        self.last_estimated = None

        self.params = {'latitude' : self.latitude, 'longitude' : self.longitude}

        if self.latest:
            self.end_point = self.end_point + '/latest'

        self._get(*args, **kwargs)

        if self.ok:
            #self._generate_est_acts_dict()
            self._get_last_observed_point()
            period = kwargs.get('hours')
            if period == 24:
                self._get_last_24_hours()
            else:
                self._generate_est_acts_dict()

    def _generate_est_acts_dict(self):

        self.estimated_actuals = []

        for est_act in self.content.get('estimated_actuals'):

            # Convert period_end and period. All other fields should already be
            # the correct type

            #est_act['period_end'] =  parse_datetime(est_act['period_end'])
            #est_act['period'] = parse_duration(est_act['period'])

            self.estimated_actuals.append(est_act)

    def _get_last_observed_point(self):

        self.last_estimated = None
        last_date = parse_datetime("2010-01-01T00:00:00.0000000Z")
        for est_act in self.content.get('estimated_actuals'):
            current_date = parse_datetime(est_act['period_end'])
            if last_date < current_date:
                self.last_estimated = est_act
                last_date = current_date

    def _get_last_24_hours(self):

        self.estimated_actuals = []
        dict_data = {}
        for est_act in self.content.get('estimated_actuals'):
            dict_data[parse_datetime(est_act['period_end'])] = est_act
        dict_data = OrderedDict(sorted(dict_data.items()))
        lastt_24 = itertools.islice(dict_data.items(), 0, 48)
        for key, value in lastt_24:
            self.estimated_actuals.append(value)