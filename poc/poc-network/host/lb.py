#!/usr/bin/env python3
"""Load balancer round-robin minimal (stdlib uniquement).

Lit backends.txt (une ligne host:port par téléphone), vérifie la santé de
chaque backend toutes les 2 s via /health et répartit les requêtes entre les
backends vivants. Remplaçable plus tard par HAProxy/nginx.
"""
import http.client
import itertools
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LISTEN = ("0.0.0.0", 8000)
BACKENDS_FILE = Path(__file__).with_name("backends.txt")
CHECK_EVERY_S = 2

backends = [l.strip() for l in BACKENDS_FILE.read_text().splitlines() if l.strip()]
alive = set(backends)
rr = itertools.cycle(backends)
lock = threading.Lock()


def fetch(backend, path, timeout=3, headers=None):
    host, port = backend.split(":")
    conn = http.client.HTTPConnection(host, int(port), timeout=timeout)
    conn.request("GET", path, headers=headers or {})
    resp = conn.getresponse()
    return resp.status, resp.getheader("Content-Type", "text/plain"), resp.read()


def health_loop():
    while True:
        for b in backends:
            try:
                ok = fetch(b, "/health", timeout=1)[0] == 200
            except Exception:
                ok = False
            with lock:
                if ok and b not in alive:
                    print(f"[health] {b} UP")
                    alive.add(b)
                elif not ok and b in alive:
                    print(f"[health] {b} DOWN")
                    alive.discard(b)
        time.sleep(CHECK_EVERY_S)


def next_backend():
    with lock:
        for _ in backends:
            b = next(rr)
            if b in alive:
                return b
    return None


class Proxy(BaseHTTPRequestHandler):
    def do_GET(self):
        b = next_backend()
        if b is None:
            self.send_error(503, "Aucun téléphone disponible")
            return
        try:
            status, ctype, body = fetch(b, self.path, headers={"Accept": self.headers.get("Accept", "*/*")})
        except Exception as e:
            with lock:
                alive.discard(b)
            self.send_error(502, f"{b} injoignable: {e}")
            return
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Backend", b)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"LB sur http://localhost:{LISTEN[1]} -> {backends}")
    threading.Thread(target=health_loop, daemon=True).start()
    ThreadingHTTPServer(LISTEN, Proxy).serve_forever()
