import datetime
import json

from solcast.base import Base


class RooftopMeasurement(Base):
    end_point = 'rooftop_sites/{}/measurements'

    def __init__(self, resource_id, period_end: datetime.datetime, period, total_power, *args, **kwargs):
        self.end_point = self.end_point.format(resource_id)
        self.period_end = str(period_end)
        self.period = period
        self.total_power = total_power

        self.measurement = None
        self.params = {}

        payload = dict(period_end=self.period_end, period=self.period, total_power=self.total_power)
        data = '{{ "measurement":{} }}'.format(json.dumps(payload, default=lambda a: a.__dict__))

        self._request('post', data=data, headers={"Content-Type": "application/json"}, *args, **kwargs)

        if self.ok:
            self.measurement = self.content['measurement']
