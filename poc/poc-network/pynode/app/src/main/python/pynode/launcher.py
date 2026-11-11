"""Lanceur du serveur web de PyNode (appelé depuis Kotlin via Chaquopy).

Charge l'appli WSGI de l'utilisateur (Flask, Django...) depuis le dossier de
l'appli sur le téléphone et la sert en HTTP, et en HTTPS si cert.pem et
key.pem sont présents. Configuration optionnelle : pynode.json (voir DEFAULTS).
"""
import collections
import importlib
import json
import logging
import logging.handlers
import os
import re
import ssl
import sys
import threading
import time
import traceback
from pathlib import Path

from werkzeug.serving import make_server

from . import node

log = logging.getLogger("pynode")

DEFAULTS = {
    "app": None,         # "module:objet" ; None → "app:app" si app.py existe, sinon appli intégrée
    "host": "0.0.0.0",
    "port": 8080,        # même port que phone/server.py → connect.sh / lb.py inchangés
    "https_port": 8443,
    "cert": "cert.pem",
    "key": "key.pem",
    "node_name": None,   # défaut : modèle du téléphone
    "env": {},           # variables d'environnement, ex. {"DJANGO_SETTINGS_MODULE": "mysite.settings"}
}

_lines = collections.deque(maxlen=300)
_servers = []
_lock = threading.Lock()
_state = {"dir": None, "app": None, "urls": [], "error": None}
_ANSI = re.compile(r"\x1b\[[0-9;]*m")


class _Formatter(logging.Formatter):
    def format(self, record):
        return _ANSI.sub("", super().format(record))  # werkzeug colore ses logs


class _RingHandler(logging.Handler):
    def emit(self, record):
        _lines.append(self.format(record))


def _setup_logging(app_dir):
    root = logging.getLogger()
    for h in [h for h in root.handlers if getattr(h, "pynode", False)]:
        root.removeHandler(h)
        h.close()
    fmt = _Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%H:%M:%S")
    file_handler = logging.handlers.RotatingFileHandler(
        app_dir / "server.log", maxBytes=1_000_000, backupCount=1, encoding="utf-8")
    for h in (_RingHandler(), file_handler):
        h.pynode = True
        h.setFormatter(fmt)
        root.addHandler(h)
    root.setLevel(logging.INFO)


def _config(app_dir):
    cfg = dict(DEFAULTS)
    path = app_dir / "pynode.json"
    if path.exists():
        try:
            cfg.update(json.loads(path.read_text()))
        except Exception as e:
            log.error("pynode.json illisible (%s), valeurs par défaut utilisées", e)
    return cfg


def _forget_modules(app_dir):
    """Oublie les modules importés depuis le dossier, pour que « Recharger » relise le code."""
    root = os.path.realpath(app_dir) + os.sep
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if f and os.path.realpath(f).startswith(root):
            del sys.modules[name]


def _load_app(spec):
    module_name, _, attr = spec.partition(":")
    return getattr(importlib.import_module(module_name), attr or "app")


def _serve(app, host, port, ssl_ctx=None):
    srv = make_server(host, port, app, threaded=True, ssl_context=ssl_ctx)
    threading.Thread(target=srv.serve_forever, name=f"pynode-{port}", daemon=True).start()
    _servers.append(srv)
    url = f"{'https' if ssl_ctx else 'http'}://{host}:{port}"
    _state["urls"].append(url)
    log.info("Écoute sur %s", url)


def _stop_servers():
    while _servers:
        srv = _servers.pop()
        srv.shutdown()
        srv.server_close()
    _state["urls"] = []


def start(app_dir, context=None):
    with _lock:
        _stop_servers()
        app_dir = Path(str(app_dir))
        app_dir.mkdir(parents=True, exist_ok=True)
        _setup_logging(app_dir)
        cfg = _config(app_dir)
        for k, v in cfg["env"].items():
            os.environ[k] = str(v)

        spec = cfg["app"] or ("app:app" if (app_dir / "app.py").exists() else None)
        node.configure(cfg["node_name"], context)
        _state.update(dir=str(app_dir), app=spec or "intégrée", error=None)

        app = node.app
        if spec:
            for p in (app_dir / "site-packages", app_dir):  # app_dir finit en tête de sys.path
                if p.is_dir():
                    if str(p) in sys.path:
                        sys.path.remove(str(p))
                    sys.path.insert(0, str(p))
            _forget_modules(app_dir)
            try:
                app = node.with_node_routes(_load_app(spec))
                log.info("Appli chargée : %s", spec)
            except Exception:
                _state["error"] = traceback.format_exc()
                log.error("Échec du chargement de %s, appli intégrée servie à la place :\n%s",
                          spec, _state["error"])

        try:
            _serve(app, cfg["host"], cfg["port"])
            cert, key = app_dir / cfg["cert"], app_dir / cfg["key"]
            if cert.exists() and key.exists():
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx.load_cert_chain(cert, key)
                _serve(app, cfg["host"], cfg["https_port"], ctx)
            else:
                log.info("Pas de %s/%s dans le dossier : HTTPS désactivé", cfg["cert"], cfg["key"])
        except Exception:
            _state["error"] = traceback.format_exc()
            log.error("Échec du démarrage du serveur :\n%s", _state["error"])
        return status_text()


def stop():
    with _lock:
        if _servers:
            _stop_servers()
            log.info("Serveur arrêté")


def is_running():
    return bool(_servers)


def status_text():
    lines = ["● En marche" if _servers else "○ Arrêté",
             f"Appli : {_state['app'] or '-'}",
             f"Dossier : {_state['dir'] or '-'}"]
    lines += _state["urls"]
    if _state["error"]:
        lines.append("Erreur : " + _state["error"].strip().splitlines()[-1])
    return "\n".join(lines)


def logs():
    return "\n".join(_lines)


if __name__ == "__main__":
    # Test sur PC, hors Android : python -m pynode.launcher <dossier>
    print(start(sys.argv[1] if len(sys.argv) > 1 else "."))
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        stop()
