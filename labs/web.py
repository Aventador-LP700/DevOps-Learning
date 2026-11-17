"""Loopback application for HTTP/browser labs. Secure mode is the default."""
import argparse
from contextlib import contextmanager
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
from urllib.parse import parse_qs, unquote, urlsplit
from labs.path_traversal.data import fixtures as file_fixtures
from labs.support import Denied


def implementation(name, vulnerable):
    return importlib.import_module(f"labs.{name}.{'vulnerable' if vulnerable else 'secure'}")

class State:
    def __init__(self, root, vulnerable=False):
        self.root, self.vulnerable = root, vulnerable
        self.lock = threading.RLock()
        self.users = {"alice": {"display_name": "Alice", "role": "user", "active": True},
                      "bob": {"display_name": "Bob", "role": "user", "active": True},
                      "admin": {"display_name": "Demo Admin", "role": "admin", "active": True}}
        self.sessions = implementation('session_fixation', vulnerable).SessionStore()
        self.login = implementation('missing_login_rate_limiting', vulnerable).LoginService()
        self.db = sqlite3.connect(':memory:', check_same_thread=False)
        self.db.execute('CREATE TABLE comments (body TEXT NOT NULL)')
        self.public = file_fixtures(root)

class Handler(BaseHTTPRequestHandler):
    server_version = 'PipelineProofLab'
    sys_version = ''

    def log_message(self, *args):
        pass

    @property
    def state(self):
        return self.server.state

    def reply(self, status, body, *, html=False, cookie=None):
        data = body.encode() if html else json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8' if html else 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        if not self.state.vulnerable:
            self.send_header('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        headers = implementation('cors_misconfiguration', self.state.vulnerable).cors_headers(self.headers.get('Origin'))
        for key, value in headers.items():
            self.send_header(key, value)
        if cookie is not None:
            self.send_header('Set-Cookie', f'pp_session={cookie}; Path=/; HttpOnly; SameSite=Strict')
        self.end_headers()
        self.wfile.write(data)

    def sid(self):
        jar = SimpleCookie()
        try:
            jar.load(self.headers.get('Cookie', ''))
        except Exception:
            return None
        return jar['pp_session'].value if 'pp_session' in jar else None

    def actor(self):
        actor = self.state.sessions.user(self.sid())
        if actor is None or not self.state.users.get(actor, {}).get('active'):
            raise Denied('Authentication required')
        return actor

    def body(self):
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            raise ValueError('Content-Type must be application/json')
        length = int(self.headers.get('Content-Length', '0'))
        if length < 1 or length > 8192:
            raise ValueError('Invalid request size')
        data = json.loads(self.rfile.read(length))
        if not isinstance(data, dict):
            raise ValueError('Expected JSON object')
        return data

    def check_host(self):
        allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        if self.headers.get('Host') not in allowed:
            raise Denied('Unexpected Host header')

    def do_GET(self):
        self.dispatch('GET')
    def do_POST(self):
        self.dispatch('POST')
    def do_OPTIONS(self):
        self.dispatch('OPTIONS')

    def dispatch(self, method):
        with self.state.lock:
            try:
                self.check_host()
                if method == 'OPTIONS':
                    return self.reply(204, {})
                if method == 'POST' and not self.state.vulnerable:
                    origin = self.headers.get('Origin')
                    own = f'http://127.0.0.1:{self.server.server_port}'
                    if origin and origin != own:
                        raise Denied('Cross-origin state changes are not allowed')
                return self.route(method)
            except Denied:
                return self.reply(403, {'error': 'Operation denied'})
            except (ValueError, KeyError, TypeError):
                return self.reply(400, {'error': 'Invalid request'})
            except Exception:
                return self.reply(500, {'error': 'Request could not be completed'})

    def route(self, method):
        parsed = urlsplit(self.path)
        path, query = parsed.path, parse_qs(parsed.query)
        if method == 'GET' and path == '/health':
            return self.reply(200, {'status': 'ok', 'mode': 'vulnerable' if self.state.vulnerable else 'secure'})
        if method == 'GET' and path == '/':
            return self.reply(200, '<!doctype html><html><head><title>PipelineProof local labs</title></head><body><h1>PipelineProof HTTP labs</h1><a href="/comments">Stored comments</a></body></html>', html=True)
        if method == 'GET' and path == '/api/session':
            return self.reply(200, {'status': 'anonymous'}, cookie=self.state.sessions.start())
        if method == 'POST' and path == '/api/login':
            data = self.body()
            user, password = data.get('user'), data.get('password')
            if not isinstance(user, str) or not isinstance(password, str) or len(user) > 64 or len(password) > 128:
                raise ValueError('Invalid credentials')
            # Only Alice's synthetic credential is supported; no real account integration.
            status, valid = self.state.login.login(user, password)
            if not valid:
                return self.reply(status, {'error': 'Login failed'})
            sid = self.sid()
            if sid not in self.state.sessions.sessions:
                sid = self.state.sessions.start()
            rotated = self.state.sessions.login(sid, 'alice')
            return self.reply(200, {'user': 'alice'}, cookie=rotated)
        if method == 'GET' and path == '/comments':
            text = implementation('stored_xss', self.state.vulnerable).render(self.state.db)
            return self.reply(200, '<!doctype html><html><head><title>Comments</title></head><body>' + text + '</body></html>', html=True)
        if method == 'POST' and path == '/api/comments':
            self.actor()
            data = self.body()
            if not isinstance(data.get('body'), str) or len(data['body']) > 2000:
                raise ValueError('Invalid comment')
            implementation('stored_xss', self.state.vulnerable).add_comment(self.state.db, data['body'])
            return self.reply(201, {'stored': True})
        if method == 'GET' and path.startswith('/api/orders/'):
            actor = self.actor()
            order = implementation('idor_bola', self.state.vulnerable).read_order(actor, unquote(path.rsplit('/', 1)[-1]))
            return self.reply(200, order)
        if path == '/api/profile':
            actor = self.actor()
            if method == 'POST':
                implementation('mass_assignment', self.state.vulnerable).update_profile(self.state.users[actor], self.body())
            return self.reply(200, self.state.users[actor])
        if method == 'POST' and path == '/api/admin/deactivate':
            actor = self.actor()
            implementation('broken_function_level_authorization', self.state.vulnerable).deactivate(actor, self.body()['target'], self.state.users)
            return self.reply(200, {'deactivated': True})
        if method == 'GET' and path == '/api/files':
            self.actor()
            text = implementation('path_traversal', self.state.vulnerable).read_file(self.state.public, query.get('name', ['welcome.txt'])[0])
            return self.reply(200, {'content': text})
        if method == 'GET' and path == '/api/debug':
            self.actor()
            def failure():
                raise RuntimeError('Synthetic backend detail')
            status, payload = implementation('debug_information_disclosure', self.state.vulnerable).handle(failure)
            return self.reply(status, payload)
        return self.reply(404, {'error': 'Not found'})

@contextmanager
def serve_lab(*, vulnerable=False, port=0):
    with tempfile.TemporaryDirectory(prefix='pipelineproof-web-') as directory:
        state = State(Path(directory), vulnerable)
        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
        server.state = state
        thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.02), daemon=True)
        thread.start()
        try:
            yield server, f'http://127.0.0.1:{server.server_port}'
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2); state.db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8081)
    parser.add_argument('--vulnerable', action='store_true')
    parser.add_argument('--enable-vulnerable-labs', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Port must be between 1 and 65535')
    if args.vulnerable != args.enable_vulnerable_labs:
        parser.error('Vulnerable services require both --vulnerable and --enable-vulnerable-labs')
    try:
        with serve_lab(vulnerable=args.vulnerable, port=args.port) as (_, origin):
            print(f"{'VULNERABLE (explicit opt-in)' if args.vulnerable else 'SECURE'} lab: {origin}", flush=True)
            threading.Event().wait()
    except KeyboardInterrupt:
        pass
    except OSError as exc:
        parser.exit(1, f'Unable to start local lab: {exc}\n')

if __name__ == '__main__':
    main()
