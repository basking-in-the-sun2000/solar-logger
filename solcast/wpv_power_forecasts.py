from datetime import datetime, timedelta
from urllib.parse import urljoin

from isodate import parse_datetime, parse_duration
import requests

from solcast.base import Base


class WPvPowerForecasts(Base):

    end_point = 'world_pv_power/forecasts'

    def __init__(self, latitude, longitude, capacity, *args, **kwargs):

        self.latitude = latitude
        self.longitude = longitude
        self.capacity = capacity
        self.tilt = kwargs.get('tilt')
        self.azimuth = kwargs.get('azimuth')
        self.install_date = kwargs.get('install_date')
        self.loss_factor = kwargs.get('loss_factor')
        self.hours = kwargs.get('hours', 48)
        self.forecasts = None

        self.params = {'latitude' : self.latitude,
                       'longitude' : self.longitude,
                       'capacity' : self.capacity,
                       'tilt' : self.tilt,
                       'azimuth' : self.azimuth,
                       'install_date' : self.install_date,
                       'loss_factor' : self.loss_factor
                      }

        self._get(*args, **kwargs)

        if self.ok:
            self._generate_forecast_dict()

    def _generate_forecast_dict(self):

        self.forecasts = []

        for forecast in self.content.get('forecasts'):

            # Convert period_end and period. All other fields should already be
            # the correct type

            forecast['period_end'] = parse_datetime(forecast['period_end'])
            forecast['period'] = parse_duration(forecast['period'])

            self.forecasts.append(forecast)
