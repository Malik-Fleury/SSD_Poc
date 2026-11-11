"""Exemple Flask pour PyNode : app.py avec un objet `app`, aucune config nécessaire."""
from flask import Flask, jsonify, render_template_string

from pynode import node

app = Flask(__name__)

PAGE = """<!doctype html><meta charset="utf-8"><title>{{ info.node }}</title>
<h1>Flask sur {{ info.node }}</h1>
<p>Batterie : {{ info.battery_pct }} % ({{ info.battery_status }}), {{ info.battery_temp_c }} °C</p>
<p>En ligne depuis {{ info.uptime_s }} s — <a href="/api">JSON</a></p>"""


@app.route("/")
def index():
    return render_template_string(PAGE, info=node.info())


@app.route("/api")
def api():
    return jsonify(node.info("/api"))


@app.route("/hello/<name>")
def hello(name):
    return f"Bonjour {name}, ici {node.NAME} !"
