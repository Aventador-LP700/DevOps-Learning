"""Small dependency-free deployment target; no deliberately vulnerable HTTP routes."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        routes = {
            "/": {"project": "PipelineProof", "message": "Attack. Detect. Harden. Prove."},
            "/health": {"status": "ok"},
            "/version": {"version": "1.0.0"},
        }
        body = json.dumps(routes.get(self.path, {"error": "not found"})).encode()
        self.send_response(200 if self.path in routes else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
