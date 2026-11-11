"""Identité et métriques du nœud : même page et même JSON que phone/server.py (Termux).

Utilisable depuis l'appli de l'utilisateur : `from pynode import node; node.info()`.
"""
import json
import pkgutil
import socket
import time

START = time.time()
NAME = socket.gethostname()
_ctx = None  # Context Android (fourni par launcher.start), None hors Android


def configure(name=None, context=None):
    global NAME, _ctx
    _ctx = context
    NAME = name or _android_model() or socket.gethostname()


def _android_model():
    try:
        from java import jclass
        return str(jclass("android.os.Build").MODEL)
    except Exception:
        return None


def battery():
    """Batterie via l'API Android (pas besoin de root, contrairement à /sys sur Android récents)."""
    out = {"battery_pct": None, "battery_status": None, "battery_temp_c": None}
    if _ctx is None:
        return out
    try:
        from java import jclass
        f = jclass("android.content.IntentFilter")("android.intent.action.BATTERY_CHANGED")
        i = _ctx.registerReceiver(None, f)
        level, scale = i.getIntExtra("level", -1), i.getIntExtra("scale", -1)
        temp = i.getIntExtra("temperature", -1)
        out["battery_pct"] = round(100 * level / scale) if level >= 0 and scale > 0 else None
        out["battery_status"] = {2: "Charging", 3: "Discharging", 4: "Not charging", 5: "Full"}.get(
            i.getIntExtra("status", 1), "Unknown")
        out["battery_temp_c"] = temp / 10 if temp >= 0 else None
    except Exception:
        pass
    return out


def _loadavg():
    try:
        with open("/proc/loadavg") as f:
            return f.read().split()[:3]
    except Exception:
        return None  # bloqué par Android 8+ hors root


def info(path="/"):
    return {"node": NAME, "uptime_s": round(time.time() - START), "path": path,
            **battery(), "loadavg": _loadavg()}


def app(environ, start_response):
    """Appli intégrée, servie quand le dossier ne contient aucune appli (ou qu'elle plante).

    Mêmes routes que phone/server.py :
      /        → page HTML (phone/index.html) pour un navigateur, JSON sinon
      /api     → JSON
      /health  → "ok"
    """
    path = environ.get("PATH_INFO", "/")
    wants_html = "text/html" in environ.get("HTTP_ACCEPT", "")
    if path in ("/health", "/_node/health"):
        body, ctype = b"ok", "text/plain"
    elif path == "/" and wants_html:
        # Copiée depuis phone/index.html par le build (app/build.gradle.kts)
        body, ctype = pkgutil.get_data(__name__, "index.html"), "text/html; charset=utf-8"
    else:
        body, ctype = json.dumps(info(path), indent=2).encode(), "application/json"
    start_response("200 OK", [("Content-Type", ctype), ("Content-Length", str(len(body)))])
    return [body]


def with_node_routes(user_app):
    """Ajoute /_node/health et /_node/info à l'appli de l'utilisateur.

    /health et /api (utilisés par lb.py et dashboard.py) restent à l'appli de
    l'utilisateur ; s'il n'y répond pas (404), le nœud répond à sa place.
    """
    def wrapped(environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path.startswith("/_node/"):
            return app(environ, start_response)
        if path not in ("/health", "/api"):
            return user_app(environ, start_response)
        captured, written = [], []

        def capture(status, headers, exc_info=None):
            captured[:] = [status, headers]
            return written.append

        result = user_app(environ, capture)
        try:
            chunks = written + list(result)
        finally:
            if hasattr(result, "close"):
                result.close()
        if captured and captured[0].startswith("404"):
            return app(environ, start_response)
        start_response(*captured)
        return chunks

    return wrapped
