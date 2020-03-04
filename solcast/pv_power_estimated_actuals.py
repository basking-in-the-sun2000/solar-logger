from datetime import datetime, timedelta
from urllib.parse import urljoin

from isodate import parse_datetime, parse_duration
import requests

from solcast.base import Base


class PvPowerEstimatedActuals(Base):

    end_point = 'pv_power/estimated_actuals'

    def __init__(self, latitude, longitude, capacity, *args, **kwargs):

        self.latitude = latitude
        self.longitude = longitude
        self.capacity = capacity
        self.tilt = kwargs.get('tilt')
        self.azimuth = kwargs.get('azimuth')
        self.install_date = kwargs.get('install_date')
        self.loss_factor = kwargs.get('loss_factor')
        self.latest = kwargs.get('latest', False)
        self.estimated_actuals = None

        self.params = {'latitude' : self.latitude,
                       'longitude' : self.longitude,
                       'capacity' : self.capacity,
                       'tilt' : self.tilt,
                       'azimuth' : self.azimuth,
                       'install_date' : self.install_date,
                       'loss_factor': self.loss_factor
                      }

        if self.latest:
            self.end_point = self.end_point + '/latest'

        self._get(*args, **kwargs)

        if self.ok:
            self._generate_est_acts_dict()

    def _generate_est_acts_dict(self):

        self.estimated_actuals = []

        for est_act in self.content.get('estimated_actuals'):

            # Convert period_end and period. All other fields should already be
            # the correct type

            est_act['period_end'] =  parse_datetime(est_act['period_end'])
            est_act['period'] = parse_duration(est_act['period'])

            self.estimated_actuals.append(est_act)
