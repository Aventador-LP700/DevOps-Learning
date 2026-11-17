"""Small dependency-free deployment target; no deliberately vulnerable HTTP routes."""
import argparse
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

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")
    try:
        server = ThreadingHTTPServer((args.host, args.port), Handler)
    except OSError as exc:
        parser.exit(1, f"Unable to start API: {exc}\n")
    print(f"PipelineProof API: http://{args.host}:{server.server_port} (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
