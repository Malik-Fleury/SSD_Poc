#!/usr/bin/env bash
# Génère un certificat auto-signé (cert.pem + key.pem) dans le dossier d'appli
# donné : PyNode active alors le HTTPS sur :8443 au prochain démarrage.
#   ./make-cert.sh ../pynode/examples/flask-demo
set -euo pipefail
DIR="${1:?Usage: $0 <dossier-appli>}"
openssl req -x509 -newkey rsa:2048 -nodes -days 365 -subj "/CN=pynode" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:192.168.42.129" \
    -keyout "$DIR/key.pem" -out "$DIR/cert.pem"
echo "cert.pem / key.pem écrits dans $DIR (auto-signé : curl -k pour tester)"
