#!/usr/bin/env python3
"""Tableau de bord : quels téléphones sont connectés, en live (stdlib uniquement).

Indépendant de lb.py : interroge directement chaque téléphone de backends.txt
toutes les 2 s et sert dashboard.html sur :8001 (JSON : /status).
"""
import http.client
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LISTEN = ("0.0.0.0", 8001)
HERE = Path(__file__).parent
CHECK_EVERY_S = 2

backends = [l.strip() for l in (HERE / "backends.txt").read_text().splitlines() if l.strip()]
state = {b: {"backend": b, "node": None, "up": False, "since": time.time()} for b in backends}
lock = threading.Lock()


def node_name(backend):
    """Nom du nœud via /api, ou None si le téléphone ne répond pas."""
    host, port = backend.split(":")
    try:
        conn = http.client.HTTPConnection(host, int(port), timeout=1)
        conn.request("GET", "/api")
        return json.loads(conn.getresponse().read())["node"]
    except Exception:
        return None


def poll_loop():
    while True:
        for b in backends:
            name = node_name(b)
            with lock:
                s = state[b]
                if (name is not None) != s["up"]:
                    s["up"], s["since"] = name is not None, time.time()
                if name:
                    s["node"] = name
        time.sleep(CHECK_EVERY_S)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            now = time.time()
            with lock:
                data = [{"backend": s["backend"], "node": s["node"], "up": s["up"],
                         "since_s": round(now - s["since"])} for s in state.values()]
            body, ctype = json.dumps(data).encode(), "application/json"
        else:
            body, ctype = (HERE / "dashboard.html").read_bytes(), "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"Tableau de bord sur http://localhost:{LISTEN[1]} -> {backends}")
    threading.Thread(target=poll_loop, daemon=True).start()
    ThreadingHTTPServer(LISTEN, Handler).serve_forever()
