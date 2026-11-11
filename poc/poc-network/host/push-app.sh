#!/usr/bin/env bash
# Déploie un dossier d'appli Python (Flask, Django...) dans PyNode sur tous les
# téléphones branchés (ou un seul avec -s), puis redémarre l'appli proprement.
#
#   ./push-app.sh ../pynode/examples/flask-demo
#   ./push-app.sh -s <serial> ../pynode/examples/django-demo
#
# Si le dossier contient requirements.txt, les dépendances sont téléchargées sur
# le PC dans site-packages/ — **pur Python uniquement** (wheels py3-none-any) :
# un paquet compilé (numpy...) doit être ajouté dans app/build.gradle.kts.
# --no-deps : Flask, Django et leurs dépendances sont déjà dans l'APK ; lister
# explicitement les autres dépendances dans requirements.txt.
set -euo pipefail
PKG=ch.phonedc.pynode
DEST=/sdcard/Android/data/$PKG/files

serials=()
if [ "${1:-}" = "-s" ]; then serials=("$2"); shift 2; fi
SRC="${1:?Usage: $0 [-s serial] <dossier-appli>}"
[ ${#serials[@]} -gt 0 ] || mapfile -t serials < <(adb devices | awk 'NR>1 && $2=="device" {print $1}')
[ ${#serials[@]} -gt 0 ] || { echo "Aucun téléphone détecté"; exit 1; }

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
cp -r "$SRC"/. "$STAGE"/
if [ -f "$STAGE/requirements.txt" ]; then
    python3 -m pip install -q --target "$STAGE/site-packages" --no-deps --only-binary=:all: \
        --platform any --python-version 3.11 --implementation py -r "$STAGE/requirements.txt"
fi
find "$STAGE" -name __pycache__ -prune -exec rm -rf {} +

for s in "${serials[@]}"; do
    echo "[$s] envoi vers $DEST"
    adb -s "$s" shell mkdir -p "$DEST"
    adb -s "$s" push "$STAGE"/. "$DEST"/ >/dev/null
    # force-stop = processus Python neuf (Django ne se recharge pas à chaud de façon fiable)
    adb -s "$s" shell am force-stop $PKG
    adb -s "$s" shell am start -n $PKG/.MainActivity -a $PKG.START >/dev/null
done
echo "OK. Journal : adb shell cat $DEST/server.log"
