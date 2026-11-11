#!/usr/bin/env bash
# Détecte les téléphones branchés en USB (adb), redirige un port local vers
# chacun et écrit la liste des backends pour lb.py.
#
#   téléphone n°i : localhost:(9000+i) -> téléphone:8080  (serveur web)
#                   localhost:(8020+i) -> téléphone:8022  (ssh Termux)
#                   localhost:(9400+i) -> téléphone:8443  (HTTPS, appli PyNode)
set -euo pipefail
cd "$(dirname "$0")"

: > backends.txt
i=1
for serial in $(adb devices | awk 'NR>1 && $2=="device" {print $1}'); do
    web=$((9000 + i)); ssh=$((8020 + i)); https=$((9400 + i))
    adb -s "$serial" forward "tcp:$web" tcp:8080
    adb -s "$serial" forward "tcp:$ssh" tcp:8022
    adb -s "$serial" forward "tcp:$https" tcp:8443
    model=$(adb -s "$serial" shell getprop ro.product.model | tr -d '\r')
    android=$(adb -s "$serial" shell getprop ro.build.version.release | tr -d '\r')
    echo "127.0.0.1:$web" >> backends.txt
    echo "[$i] $serial ($model, Android $android) -> web :$web | https :$https | ssh -p $ssh localhost"
    i=$((i + 1))
done

[ "$i" -gt 1 ] || { echo "Aucun téléphone détecté (débogage USB activé et autorisé ?)"; exit 1; }
echo "backends.txt écrit ($((i - 1)) téléphone(s))."
