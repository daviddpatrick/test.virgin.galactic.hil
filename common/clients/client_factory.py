from common.clients.api_client import ApiClient


class ClientFactory(object):

    def create(self, name, base_url, logger, auth_token=None, extra_headers=None):
        while name:
            api_clients = {
                "ApiClient": lambda: ApiClient(
                    base_url,
                    logger,
                    auth_token=auth_token,
                    extra_headers=extra_headers,
                ),
            }
            try:
                return api_clients[name]()
            except KeyError:
                raise ValueError(f"Invalid client name: {name}")
