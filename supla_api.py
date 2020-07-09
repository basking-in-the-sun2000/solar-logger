import base64

import requests


class ApiClient:
    def __init__(self, token, debug, error):
        self.token = token
        split = token.split(".")
        self.url = base64.b64decode(split[1]).decode('UTF-8') + "/api/v2.3.0"
        self.default_headers = {
            "User-Agent": "supla/domoticz",
            "content-type": "application/json",
            "accept": "application/json",
            "Authorization": "Bearer " + token
        }

        self.debug = debug
        self.error = error

    def find_all_devices(self):
        return self.get("/iodevices", includes=["channels"])

    def pobierz_wskazania(self,channel_id):
        self.get("/channels/" + str(channel_id), includes=["state"])

    def update_channel(self, channel_id, action):
        self.patch("/channels/" + channel_id, action)

    def find_channel(self, channel_id):
        return self.get("/channels/" + str(channel_id), includes=["connected", "state"])

    def build_url(self, url):
        return self.url + url

    def check_response(self, response):
        if response.status_code < 200 or response.status_code > 299:
            msg = "Wrong status code! Was " + str(response.status_code)
            self.error(msg)
            raise Exception(msg)

    def get(self, url, includes=None):
        if includes is None:
            includes = []
      #  self.debug("api> get(" + self.build_url(url) + ", includes=[" + ", ".join(includes) + "])")
        params = dict()
        if len(includes) > 0:
            params["include"] = includes
        response = requests.get(self.build_url(url), headers=self.default_headers, params=params)
        self.check_response(response)
        return response.json()

    def patch(self, url, body):
     #   self.debug("api> patch(" + self.build_url(url) + ", " + str(body) + ")")
        response = requests.patch(self.build_url(url), json=body, headers=self.default_headers)
        self.check_response(response)
