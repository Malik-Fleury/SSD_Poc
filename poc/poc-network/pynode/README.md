# PyNode — appli Android « serveur web Python » (Chaquopy)

Alternative à Termux pour le POC réseau : une seule APK qui embarque Python 3.11 + Flask + Django et sert **ton** code Python, déposé dans un dossier du téléphone. Pas de root, pas de Play Store.

```
PC ──adb push──> /sdcard/Android/data/ch.phonedc.pynode/files/   (ton appli : app.py, mysite/, pynode.json, cert.pem…)
                         │
APK PyNode : service premier plan → Python (Chaquopy) → werkzeug → ton appli WSGI
                         └── :8080 HTTP (même port que phone/server.py → connect.sh / lb.py / dashboard.py inchangés)
                         └── :8443 HTTPS si cert.pem + key.pem présents
```

## Ce que fait l'appli

- Service au premier plan + wake lock + wifi lock : continue écran éteint ; redémarre au boot s'il tournait.
- Charge l'appli WSGI du dossier : `app.py` avec un objet `app` (Flask) par défaut, ou ce que dit `pynode.json`.
- Si le dossier est vide ou si l'appli plante au chargement, sert une **appli intégrée identique à `phone/server.py`** : même page (`phone/index.html`, copiée dans l'APK au build), mêmes routes (`/`, `/api`, `/health`), mêmes champs JSON. Le nœud reste vivant pour le LB, et l'erreur s'affiche à l'écran et dans `server.log`. Nom du nœud : modèle du téléphone, ou `node_name` dans `pynode.json` (équivalent de `setup.sh a5-01`).
- Toujours disponibles : `/_node/health`, `/_node/info`. `/health` et `/api` aussi, si ton appli ne les définit pas.
- Batterie lue via l'API Android (`BatteryManager`), donc sans root. Utilisable dans ton code : `from pynode import node; node.info()`.
- Écran : Démarrer / Arrêter / Recharger, IP du téléphone, journal en direct.

`pynode.json` (tout est optionnel) :
```json
{ "app": "mysite.wsgi:application", "port": 8080, "https_port": 8443,
  "node_name": "a5-01", "env": {"MA_VARIABLE": "x"} }
```

## 1. Compiler l'APK (une fois)

Versions figées : Chaquopy 16.1.0, **Python 3.11** (dernière avec `armeabi-v7a`, l'ABI 32 bits des vieux téléphones), AGP 8.9.3, minSdk 24 (**Android 7.0**, comme Termux).

- **Android Studio** : ouvrir le dossier `pynode/`, Build → Build APK.
- **En ligne de commande** : JDK 17+ et Android SDK (installé ici dans `~/Android/Sdk` via les *command-line tools* : `platforms;android-35`, `build-tools;35.0.0`, `platform-tools` ; chemin dans `local.properties` : `sdk.dir=...`), puis
  ```
  ./gradlew assembleDebug        # → app/build/outputs/apk/debug/app-debug.apk
  adb install -r app/build/outputs/apk/debug/app-debug.apk
  ```

L'APK pèse plusieurs dizaines de Mo (Python + Django × 3 ABI). Pour l'alléger : ne garder que `armeabi-v7a` dans `abiFilters`.

## 2. Déployer une appli

```
cd ../host
./push-app.sh ../pynode/examples/flask-demo     # tous les téléphones branchés
./push-app.sh ../pynode/examples/django-demo    # ou -s <serial> pour un seul
./connect.sh && curl localhost:9001/            # puis lb.py / dashboard.py comme avant
```

`push-app.sh` copie le dossier, puis fait `force-stop` + redémarrage (processus Python neuf, nécessaire pour Django). Le bouton « Recharger » de l'écran recharge à chaud, ce qui suffit pour Flask.

Pilotage depuis le PC : `adb shell am start -n ch.phonedc.pynode/.MainActivity -a ch.phonedc.pynode.{START|STOP|RESTART}`. Journal : `adb shell cat /sdcard/Android/data/ch.phonedc.pynode/files/server.log`.

**Dépendances** : Flask et Django sont dans l'APK. D'autres paquets **pur Python** se mettent dans `requirements.txt` du dossier (lister aussi leurs dépendances : `--no-deps`) ; `push-app.sh` les télécharge dans `site-packages/`. Un paquet compilé (numpy, Pillow…) doit être ajouté dans `app/build.gradle.kts` (`pip { install(...) }`), puis il faut recompiler, si Chaquopy le propose pour l'ABI.

**HTTPS** : `./make-cert.sh <dossier-appli>` (auto-signé) avant `push-app.sh`. `connect.sh` redirige `localhost:9401` → téléphone `:8443` : `curl -k https://localhost:9401/`.

## 3. Test sur PC sans téléphone

```
python3 -m venv venv && venv/bin/pip install "flask>=3,<4" "django>=5.1,<5.2"
cd app/src/main/python && ../../../../venv/bin/python -m pynode.launcher ../../../../examples/flask-demo
```

## État et mesures

| Point | Statut |
|---|---|
| Lanceur Python (Flask, Django + SQLite, HTTPS, repli si l'appli plante, `/health` pour lb.py) | ✅ testé sur PC (2026-11-10), Python 3.12 |
| `pip --only-binary --platform any --no-deps` de `push-app.sh` | ✅ testé sur PC (flask-cors, requests) |
| Compilation de l'APK (`./gradlew assembleDebug`, 1er build ~4 min) | ✅ 2026-11-10 — APK debug **53 Mo** (3 ABI) |
| Tourne sur le Galaxy A5 2016 (SM-A510F, **Android 7.0, armeabi-v7a**) | ✅ 2026-11-10 — appli intégrée, Flask, Flask en HTTPS, Django + SQLite 3.45.3 |
| Batterie via l'API Android, sans root | ✅ niveau, état, température remontés |
| Appli intégrée = Termux : page HTML identique à `phone/index.html` (diff), mêmes champs JSON | ✅ 2026-11-10 sur le téléphone |
| Délai déploiement → 1re réponse (`push-app.sh`, démarrage à froid) | ✅ ~6 s Flask, ~16 s Django |
| Débit séquentiel, Django `/api`, via `adb forward` (200 requêtes curl) | ✅ **~40 req/s**, 200/200 OK (1 mesure) |
| RAM du processus (PSS, `dumpsys meminfo`, Django chargé) | ✅ ~86 Mo |
| Tient écran éteint 30 min / survit au reboot (BootReceiver) | à valider |
| Comparaison avec Termux (même mesure de débit) | à mesurer |

Le build avertit `Failed to compile to .pyc` : le Python du PC (3.12) ≠ celui de l'appli (3.11), donc le bytecode est compilé sur le téléphone au 1er lancement. Installer `python3.11` sur le PC (et `buildPython("python3.11")`) accélérerait probablement le démarrage ⚠️ non mesuré.

`push-app.sh` n'efface pas le dossier : des fichiers d'un déploiement précédent (ex. `cert.pem`, `app.py`) restent en place.

⚠️ Serveur werkzeug = serveur de développement multi-thread : bien pour un POC, pas un serveur de production. Le dossier `Android/data/...` est lisible par adb/MTP mais pas par les gestionnaires de fichiers sur Android 11+.
