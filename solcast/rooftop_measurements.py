import datetime
import json

from solcast.base import Base


class RooftopMeasurements(Base):
    end_point = 'rooftop_sites/{}/measurements'

    def __init__(self, resource_id, measurements: list, *args, **kwargs):
        self.end_point = self.end_point.format(resource_id)

        self.measurements = None
        self.params = {}

#        payload = [dict(zip(['period_end', 'period', 'total_power'], measurement)) for measurement in measurements]
        payload = measurements

        for measurement in payload:
            if isinstance(measurement['period_end'], datetime.datetime):
                measurement['period_end'] = str(measurement['period_end'])

        data = '{{ "measurements": {} }}'.format(json.dumps(payload, default=lambda a: a.__dict__))

        self._request('post', data=data, headers={"Content-Type": "application/json"}, *args, **kwargs)

        if self.ok:
            self.measurements = self.content['measurements']
