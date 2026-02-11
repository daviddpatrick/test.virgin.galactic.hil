from common.http_base.http_base import HttpClientBase


class ApiClient(HttpClientBase):

    def get(self, path, params=None):
        return self._get(path, params=params)

    def post(self, path, data=None, params=None, files=None, payload_binary=False):
        return self._post(path, data=data, params=params, files=files, payload_binary=payload_binary)
