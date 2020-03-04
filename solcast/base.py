import logging
import time
from urllib.parse import urljoin

import requests

from solcast import api_key

_BASE_URL = 'https://api.solcast.com.au/'

class Base(object):

    throttled = False
    throttle_release = None

    def _request(self, method=None, api_key=api_key, **kwargs):

        if api_key == None:
            raise TypeError('{type}() missing 1 required argument: \'api_key\''\
                            .format(type=type(self)))

        logger = logging.getLogger()

        if method == "post":
            self.method = method
        else:
            self.method = 'get'
        self.url = urljoin(_BASE_URL, self.end_point)
        self.status_code = 'Unknown'
        self.content = None
        self.api_key = api_key
        self.rate_limited = kwargs.get('rate_limited', True)
        self.throttle_release_padding = kwargs.get('throttle_release_padding', 2)
        self.data = kwargs.get('data', None)
        self.headers = kwargs.get('headers', None)

        params = self.params.copy()
        params['format'] = 'json'

        now = time.time()

        if self.rate_limited and Base.throttled and now < Base.throttle_release:
            sleep_time = int(Base.throttle_release - now +
                             self.throttle_release_padding)
            logger.info('Solcast API rate limit reached. Waiting {seconds} seconds'.\
                        format(seconds=sleep_time))

            time.sleep(sleep_time)
            Base.throttled = False

        try:

            r = requests.request(self.method, self.url, auth=(self.api_key, ''),
                                 params=params, data=self.data, headers=self.headers)


            if self.rate_limited and r.status_code == 429:
                now = time.time()
                Base.throttle_release = r.headers.get('X-Rate-Limit-Reset')

                if Base.throttle_release:
                    Base.throttle_release = float(Base.throttle_release)

                sleep_time = int(Base.throttle_release - now + self.throttle_release_padding)
                logger.info('HTTP status 429: Solcast API rate limit reached. Waiting {seconds} seconds'.\
                            format(seconds=sleep_time))

                time.sleep(sleep_time)
                Base.throttled = False


            self.status_code = r.status_code
            self.url = r.url
            self.headers = r.headers

            if self.rate_limited:
                Base.throttle_release = self.headers.get('X-Rate-Limit-Reset')

                if Base.throttle_release:
                    Base.throttle_release = float(Base.throttle_release)

                if self.headers.get('X-Rate-Limit-Remaining') == '0':
                    Base.throttled = True

        except (KeyboardInterrupt, SystemExit):
            raise

        # Attempt to open json from Request connection
        try:
            self.content = r.json()
        except:
            self.content = r.content

    def _get(self, api_key=api_key, **kwargs):
        Base._request(self, 'get', api_key, **kwargs)


    @property
    def ok(self):

        if self.status_code == 200:
            return True
        else:
            return False
