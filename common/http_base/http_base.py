"""
Base Class for HTTP Client we use to interact with APIs
"""
import json
import logging
import requests
import urllib3  # pylint: disable=E0401
from random import choice
from string import ascii_uppercase

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # pylint: disable=E1101

line_separator = '\n' + 80 * '_'


def request_to_curl(req, linesep='\\\n  '):
    parts = ['curl', ]
    add = parts.append
    add('-X')
    add(req.method)
    add(linesep)
    for hdr, val in list(req.headers.items()):
        if hdr != 'Accept-Encoding':
            add('-H')
            add('"{}: {}"'.format(hdr, val))
            add(linesep)
    if req.body:
        add('-d')
        add("'{}'".format(req.body))
    add('"{}"'.format(req.url))
    return ' '.join(parts)


def response_to_curl(resp, linesep='\n'):
    parts = []
    add = parts.append
    parts.append(request_to_curl(resp.request))
    parts.append('HTTP {} {}'.format(resp.status_code, resp.reason))
    for hdr, val in list(resp.headers.items()):
        add('{}: {}'.format(hdr, val))
    add('{!r}'.format(resp.content))
    return linesep.join(parts)


class HttpClientBase(object):
    """
    :param auth_token: a 32 char uppercase hex string representing API key
    :type auth_token: str
    :param base_url: the base url to connect to
    :type base_url: str
    :param http_timeout: the amount of time to timeout
    :type http_timeout: int
    """

    def __init__(self,
                 base_url,
                 logger,
                 auth_token=None,
                 http_timeout=(6.05, 30),
                 content_type='application/json',
                 max_retries=0,
                 extra_headers=None):
        self.base_url = base_url
        # http headers
        self.headers = {}
        if content_type:
            self.headers['Content-Type'] = content_type
        if auth_token is not None:
            self.headers['Authorization'] = auth_token
        if extra_headers is not None:
            self.headers.update(extra_headers)
        self.http_timeout = http_timeout
        self.logger = logger

        self.session = requests.Session()
        http_adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
        https_adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
        self.session.mount('http://', http_adapter)
        self.session.mount('https://', https_adapter)

    def _get(self, url, params=None):
        """HTTP GET with params"""
        url = self.base_url + '/' + url
        self.logger.info(line_separator)
        resp = self.session.get(url, headers=self.headers, verify=False, timeout=self.http_timeout,
                                params=params)
        self.logger.debug(response_to_curl(resp))
        self.logger.info("GET URL = %s" % resp.request.url)
        self.logger.info("STATUS CODE = %s" % resp.status_code)
        self.logger.info("TIME ELAPSED = %s" % resp.elapsed.total_seconds())
        return resp

    def _patch(self, url, data):
        """HTTP PATCH with params"""
        url = self.base_url + '/' + url
        self.logger.info(line_separator)
        resp = self.session.patch(url, headers=self.headers, data=json.dumps(data), verify=False,
                                  timeout=self.http_timeout)
        self.logger.debug(response_to_curl(resp))
        self.logger.info("PATCH URL = %s" % resp.request.url)
        self.logger.info("STATUS CODE = %s" % resp.status_code)
        self.logger.info("TIME ELAPSED = %s" % resp.elapsed.total_seconds())
        return resp

    def _put(self, url, data=None, params=None, json_data_type=True):
        """HTTP PUT with params"""
        url = self.base_url + '/' + url
        self.logger.info(line_separator)
        if (json_data_type):
            resp = self.session.put(url, headers=self.headers, data=json.dumps(data), verify=False,
                                    timeout=self.http_timeout)
        else:
            resp = self.session.put(url, headers=self.headers, data=data, verify=False,
                                    timeout=self.http_timeout)

        self.logger.debug(response_to_curl(resp))
        self.logger.info("PUT URL = %s" % resp.request.url)
        self.logger.info("STATUS CODE = %s" % resp.status_code)
        self.logger.info("TIME ELAPSED = %s" % resp.elapsed.total_seconds())
        return resp

    def _post(self, url, data=None, params=None, files=None, payload_binary=False):
        """HTTP PUT with params"""
        url = self.base_url + '/' + url
        self.logger.info(line_separator)
        if payload_binary:
            resp = self.session.post(url,
                                     headers=self.headers,
                                     data=data,
                                     verify=False,
                                     timeout=self.http_timeout,
                                     params=params,
                                     files=files)
        elif data is not None:
            resp = self.session.post(url,
                                     headers=self.headers,
                                     data=json.dumps(data),
                                     verify=False,
                                     timeout=self.http_timeout,
                                     params=params,
                                     files=files)

        else:
            resp = self.session.post(url,
                                     headers=self.headers,
                                     verify=False,
                                     timeout=self.http_timeout,
                                     params=params,
                                     files=files)
        self.logger.debug(response_to_curl(resp))
        self.logger.info("POST URL = %s" % resp.request.url)
        self.logger.info("STATUS CODE = %s" % resp.status_code)
        self.logger.info("TIME ELAPSED = %s" % resp.elapsed.total_seconds())
        return resp

    def _delete(self, url, data=None):
        url = self.base_url + '/' + url
        self.logger.info(line_separator)
        headers = self.headers
        resp = self.session.delete(url, headers=headers, verify=False, data='' if data is None else json.dumps(data),
                                   timeout=self.http_timeout)
        self.logger.debug(response_to_curl(resp))
        self.logger.info("DELETE URL = %s" % url)
        self.logger.info("STATUS CODE = %s" % resp.status_code)
        self.logger.info("RESPONSE: %s" % resp.text)
        self.logger.info("TIME ELAPSED = %s" % resp.elapsed.total_seconds())
        return resp

    def _get_diagnostics(self, servicename="service", adminurl=None):
        """HTTP PUT with params"""
        if adminurl != None:
            if "v3" in adminurl:
                adminurl = adminurl[:adminurl.index("/v3")]
            url = adminurl + "/" + "v3/" + servicename + '/_/' + 'diagnostics'
        else:
            if "v3" in self.base_url:
                self.base_url = self.base_url[:self.base_url.index("/v3")]
            url = self.base_url + "/" + "v3/" + servicename + '/_/' + 'diagnostics'
            self.logger.info(line_separator)

        resp = self.session.get(url,
                                headers=self.headers,
                                verify=False,
                                timeout=self.http_timeout)
        self.logger.debug(response_to_curl(resp))
        self.logger.info("GET URL = %s" % resp.request.url)
        self.logger.info("STATUS CODE = %s" % resp.status_code)
        self.logger.info("TIME ELAPSED = %s" % resp.elapsed.total_seconds())
        return resp

    def _get_health_status(self, status="health", servicename="service", adminurl=None):
        """HTTP GET health status

        Args:
            status: "health" OR "metrics"
            admin_url : if admin_end points are different than url
        """
        if adminurl != None:
            if "v3" in adminurl:
                adminurl = adminurl[:adminurl.index("/v3")]
            url = adminurl + "/" + "v3/" + servicename + '/_/' + status
        else:
            if "v3" in self.base_url:
                self.base_url = self.base_url[:self.base_url.index("/v3")]
            url = self.base_url + "/v3/" + servicename + '/_/' + status
        self.logger.info(line_separator)
        resp = self.session.get(url, headers=self.headers, verify=False, timeout=self.http_timeout)
        self.logger.debug(response_to_curl(resp))
        self.logger.info(response_to_curl(resp).split("{")[1])
        self.logger.info("STATUS CODE = %s" % resp.status_code)
        self.logger.info("TIME ELAPSED = %s" % resp.elapsed.total_seconds())
        return resp

    def _post_queries(self, query_url, data):

        if "v3" in self.base_url:
            self.base_url = self.base_url[:self.base_url.index("/v3")]
            url = self.base_url + '/' + query_url
        else:
            url = self.base_url + '/' + query_url

        self.logger.info(line_separator)

        if data is not None and data is not {}:
            resp = self.session.post(url, headers=self.headers,
                                     data=json.dumps(data),
                                     verify=False,
                                     timeout=self.http_timeout)
        else:
            resp = self.session.post(url, headers=self.headers,
                                     verify=False,
                                     timeout=self.http_timeout)

        self.logger.info(response_to_curl(resp))
        self.logger.info("GET URL = %s" % resp.request.url)
        self.logger.info("STATUS CODE = %s" % resp.status_code)
        self.logger.info("TIME ELAPSED = %s" % resp.elapsed.total_seconds())
        return resp

    @staticmethod
    def _extended_text(rng):
        return ''.join(choice(ascii_uppercase) for i in range(rng))

    def close(self):
        self.session.close()
