from datetime import datetime, timedelta
from urllib.parse import urljoin

from isodate import parse_datetime, parse_duration
import requests


from solcast.base import Base


class RooftopForecasts(Base):
    end_point = 'rooftop_sites/{}/forecasts'

    def __init__(self, resource_id, *args, **kwargs):
        self.end_point = self.end_point.format(resource_id)
        self.hours = kwargs.get('hours', 252)

        self.params = {'hours' : self.hours}

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
