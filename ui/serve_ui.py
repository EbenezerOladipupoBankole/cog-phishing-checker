"""Inbox Guard web page.

Serves ui/index.html and passes "Check" requests to the cog's own web API
(start that first with `pixi run serve`). The browser only talks to this one
address, so no extra browser permissions are needed, and nothing in src/ is
changed. Standard library only.

    python3 ui/serve_ui.py            # then open http://127.0.0.1:8094
"""
import json
import os
import pathlib
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = pathlib.Path(__file__).resolve().parent
PORT = int(os.environ.get("INBOX_GUARD_PORT", "8094"))
COG = os.environ.get("INBOX_GUARD_COG", "http://127.0.0.1:8093")
MAX_BODY = 200_000
TIMEOUT = 1900  # a little longer than the cog's own 1800 s model timeout


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, (HERE / "index.html").read_bytes(),
                              "text/html; charset=utf-8")
        if self.path == "/api/health":
            try:
                with urllib.request.urlopen(COG + "/health", timeout=5) as r:
                    return self._send(200, r.read())
            except Exception:
                return self._send(503, {"ok": False, "detail": "cog web API is not running"})
        self._send(404, {"error": "not-found"})

    def do_POST(self):
        if self.path != "/api/ask":
            return self._send(404, {"error": "not-found"})
        length = int(self.headers.get("Content-Length") or 0)
        if not 0 < length <= MAX_BODY:
            return self._send(400, {"error": "bad-request"})
        data = self.rfile.read(length)
        req = urllib.request.Request(COG + "/ask", data=data,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return self._send(r.status, r.read())
        except urllib.error.HTTPError as e:
            return self._send(e.code, e.read())
        except Exception:
            return self._send(503, {"error": "cog-unreachable",
                                    "detail": "Start the cog first with: pixi run serve"})

    def log_message(self, fmt, *a):
        pass


if __name__ == "__main__":
    print(f"Inbox Guard page: http://127.0.0.1:{PORT}")
    print(f"  passing checks to the cog at {COG}  (start it with: pixi run serve)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
