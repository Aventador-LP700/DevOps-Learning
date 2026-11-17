import http.client
import json
from pathlib import Path
import subprocess
import sys
import unittest
from labs.web import serve_lab

class Client:
    def __init__(self, origin):
        self.origin = origin
        self.cookie = ''
    def request(self, method, path, data=None, headers=None):
        from urllib.parse import urlsplit
        url = urlsplit(self.origin)
        connection = http.client.HTTPConnection(url.hostname, url.port, timeout=3)
        final = {'Cookie': self.cookie}
        if headers: final.update(headers)
        if data is not None: final['Content-Type'] = 'application/json'
        connection.request(method, path, json.dumps(data) if data is not None else None, final)
        response = connection.getresponse()
        raw = response.read().decode()
        if response.getheader('Set-Cookie'):
            self.cookie = response.getheader('Set-Cookie').split(';')[0]
        status = response.status
        output_headers = dict(response.getheaders())
        connection.close()
        return status, raw, output_headers
    def login(self):
        return self.request('POST', '/api/login', {'user': 'alice', 'password': 'dummy-correct-horse'})

class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.fixture = serve_lab()
        self.server, origin = self.fixture.__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)
        self.client = Client(origin)
    def test_secure_default_and_authentication(self):
        self.assertEqual(self.server.server_address[0], '127.0.0.1')
        status, body, headers = self.client.request('GET', '/health')
        self.assertEqual(json.loads(body)['mode'], 'secure')
        self.assertIn("default-src 'none'", headers['Content-Security-Policy'])
        self.assertEqual(headers['Cross-Origin-Embedder-Policy'], 'require-corp')
        self.assertEqual(headers['Cross-Origin-Opener-Policy'], 'same-origin')
        self.assertEqual(self.client.request('GET', '/api/profile')[0], 403)
    def test_object_and_function_authorization(self):
        self.assertEqual(self.client.login()[0], 200)
        self.assertEqual(self.client.request('GET', '/api/orders/100')[0], 200)
        self.assertEqual(self.client.request('GET', '/api/orders/200')[0], 403)
        self.assertEqual(self.client.request('POST', '/api/admin/deactivate', {'target': 'bob'})[0], 403)
    def test_protected_fields_and_synthetic_files(self):
        self.client.login()
        self.assertEqual(self.client.request('POST', '/api/profile', {'role': 'admin'})[0], 403)
        self.assertEqual(self.client.request('POST', '/api/profile', {'display_name': 'Updated'})[0], 200)
        self.assertEqual(self.client.request('GET', '/api/files?name=../private/payroll.txt')[0], 403)
        self.assertEqual(self.client.request('GET', '/api/files?name=welcome.txt')[0], 200)
    def test_debug_response_does_not_expose_traceback(self):
        self.client.login()
        status, body, _ = self.client.request('GET', '/api/debug')
        self.assertEqual(status, 500)
        self.assertNotIn('Traceback', body)
        self.assertNotIn('Synthetic backend detail', body)
    def test_session_rotated_and_old_identifier_rejected(self):
        self.client.request('GET', '/api/session')
        old = self.client.cookie
        self.client.login()
        self.assertNotEqual(old, self.client.cookie)
        self.assertEqual(self.client.request('GET', '/api/profile')[0], 200)
        self.client.cookie = old
        self.assertEqual(self.client.request('GET', '/api/profile')[0], 403)
    def test_cross_origin_write_and_rebinding_rejected(self):
        self.client.login()
        self.assertEqual(self.client.request('POST', '/api/profile', {'display_name': 'bad'}, {'Origin': 'http://127.0.0.1:9999'})[0], 403)
        self.assertEqual(self.client.request('GET', '/health', headers={'Host': 'untrusted.invalid'})[0], 403)
    def test_vulnerable_http_is_explicitly_selected(self):
        with serve_lab(vulnerable=True) as (_, origin):
            client = Client(origin)
            client.login()
            self.assertEqual(client.request('GET', '/api/orders/200')[0], 200)
            self.assertEqual(client.request('POST', '/api/profile', {'role': 'admin'})[0], 200)
            self.assertIn('Traceback', client.request('GET', '/api/debug')[1])
    def test_cli_rejects_partial_vulnerable_opt_in(self):
        for flag in ('--vulnerable', '--enable-vulnerable-labs'):
            process = subprocess.run([sys.executable, '-m', 'labs.web', flag], text=True, capture_output=True, timeout=5)
            self.assertEqual(process.returncode, 2)
            self.assertIn('require both', process.stderr)
