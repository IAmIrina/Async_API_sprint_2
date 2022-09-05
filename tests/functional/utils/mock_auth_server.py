from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
from threading import Thread


class MockServerAuthRequestHandler(BaseHTTPRequestHandler):
    USERS_PATTERN = re.compile(r'/user/check_roles')

    def do_POST(self):
        if re.search(self.USERS_PATTERN, self.path):
            self.send_response(HTTPStatus.OK)

            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            response = []
            response_content = json.dumps(response)
            self.wfile.write(response_content.encode('utf-8'))
            return


def start_auth_mock_server(host, port):
    mock_server = HTTPServer((host, port), MockServerAuthRequestHandler)
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()
