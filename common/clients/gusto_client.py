import json
from common.clients.graphql_queries import build_members_table_payload
from common.http_base.http_base import HttpClientBase


class HTTPError(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return repr(self.status)


class GustoApiClient(HttpClientBase):

    def __init__(self,
                 base_url,
                 logger,
                 admin_url=None,
                 auth_token=None,
                 http_timeout=(5, 30),
                 content_type='application/json',
                 extra_headers=None):
        super(GustoApiClient, self).__init__(base_url=base_url,
                                             logger=logger,
                                             auth_token=auth_token,
                                             http_timeout=http_timeout,
                                             content_type=content_type,
                                             extra_headers=extra_headers)
        if extra_headers is None:
            extra_headers = {}
        self.admin_url = admin_url
        self.logger = logger
        self.logger.info("Gusto API Client")

    def members_table_via_request(self, csrf_token, role_id, variables=None):
        payload = build_members_table_payload(variables)
        request_headers = {
            "content-type": "application/json",
            "x-csrf-token": csrf_token,
            "x-role-id": str(role_id),
        }
        url = self.base_url.rstrip("/") + "/?operationName=MembersTable"
        resp = self.session.post(
            url,
            headers={**self.headers, **request_headers},
            data=json.dumps(payload),
            verify=False,
            timeout=self.http_timeout,
        )
        return resp
