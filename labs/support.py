"""Synthetic fixtures and evidence helpers. No external services are contacted."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener

class Denied(ValueError):
    """A security control rejected the requested operation."""

def rejected(operation):
    try:
        operation()
    except (Denied, PermissionError):
        return True
    return False

def outcome(exploited, blocked, legitimate, evidence):
    return {"vulnerable_exploited": bool(exploited), "secure_blocked": bool(blocked),
            "legitimate_allowed": bool(legitimate), "evidence": evidence}

@contextmanager
def json_service(routes):
    requests = []
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            item = routes.get(self.path)
            body = json.dumps(item if item is not None else {"error": "not found"}).encode()
            self.send_response(200 if item is not None else 404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.02), daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", requests
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def lab_fetch(url, allowed_origins):
    """Safety envelope: both implementations may contact only allocated lab mocks."""
    parsed = urlsplit(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.username or parsed.password or parsed.fragment or origin not in allowed_origins:
        raise Denied("Destination outside allocated lab mocks")
    # Ignore proxy environment and prohibit redirects out of the safety envelope.
    opener = build_opener(ProxyHandler({}), NoRedirect())
    with opener.open(url, timeout=2) as response:
        return json.loads(response.read(65536))
