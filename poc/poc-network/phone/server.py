#!/usr/bin/env python3
"""Mini serveur web à lancer dans Termux sur le téléphone.

Répond en JSON avec l'identité du nœud et quelques métriques lues sans root
(si Android les expose ; sinon la valeur vaut null).
  /        → page HTML pour un navigateur, JSON sinon (curl, lb.py)
  /api     → JSON
  /health  → "ok"
"""
import json
import os
import socket
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = int(os.environ.get("PORT", 8080))
NODE = os.environ.get("NODE_NAME", socket.gethostname())
START = time.time()


def read(path, cast=str):
    try:
        with open(path) as f:
            return cast(f.read().strip())
    except Exception:
        return None


def metrics():
    bat = "/sys/class/power_supply/battery"
    temp = read(f"{bat}/temp", int)
    load = read("/proc/loadavg")
    return {
        "battery_pct": read(f"{bat}/capacity", int),
        "battery_status": read(f"{bat}/status"),
        "battery_temp_c": temp / 10 if temp is not None else None,
        "loadavg": load.split()[:3] if load else None,
    }


PAGE = Path(__file__).with_name("index.html")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        wants_html = "text/html" in self.headers.get("Accept", "")
        if self.path == "/health":
            body = b"ok"
            ctype = "text/plain"
        elif self.path == "/" and wants_html:
            body = PAGE.read_bytes()
            ctype = "text/html; charset=utf-8"
        else:
            body = json.dumps({
                "node": NODE,
                "uptime_s": round(time.time() - START),
                "path": self.path,
                **metrics(),
            }, indent=2).encode()
            ctype = "application/json"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[{NODE}] {self.address_string()} {fmt % args}")


if __name__ == "__main__":
    print(f"{NODE} écoute sur 0.0.0.0:{PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
