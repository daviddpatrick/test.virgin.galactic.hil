import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import allure
import pytest

from common.clients.api_client import ApiClient


class _ApiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/v1/health"):
            payload = {"status": "ok"}
            self._send_json(200, payload)
        else:
            self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path.startswith("/v1/echo"):
            body_len = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(body_len).decode("utf-8") if body_len else "{}"
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = {"raw": body}
            self._send_json(200, {"received": payload})
        else:
            self._send_json(404, {"error": "not_found"})

    def _send_json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        return


@pytest.fixture(scope="module")
def api_server():
    server = HTTPServer(("127.0.0.1", 0), _ApiHandler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=1)


@allure.feature("API")
@allure.story("Health endpoint")
@pytest.mark.api
def test_health_endpoint(api_server):
    logger = logging.getLogger("api.health")
    client = ApiClient(base_url=api_server, logger=logger)

    response = client.get("v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@allure.feature("API")
@allure.story("Echo endpoint")
@pytest.mark.api
def test_echo_endpoint(api_server):
    logger = logging.getLogger("api.echo")
    client = ApiClient(base_url=api_server, logger=logger)

    payload = {"command": "arming", "value": True}
    response = client.post("v1/echo", data=payload)

    assert response.status_code == 200
    assert response.json() == {"received": payload}
