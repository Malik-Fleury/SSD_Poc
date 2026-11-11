# POC — Galaxy A5 2016 (SM-A510F) en nœud web, sans root

```
curl → PC :8000 (lb.py, round-robin + health check) ──adb forward / USB──> téléphone :8080 (Termux, server.py)
```

Variante 1 (ce POC) : trafic via `adb forward`. Variante 2 (USB tethering) : voir en bas.

## 0. Prérequis

- PC : `sudo apt install adb` (python3 et curl déjà présents).
- Téléphone : **Android 7.0** requis par Termux (Paramètres → À propos → Infos logiciel ; sinon mise à jour).
- Câble **micro-USB data** (pas un câble charge seule).

## 1. Préparer le téléphone (une fois)

1. Activer les options développeur : Paramètres → À propos → Infos logiciel → taper 7× sur « Numéro de version ».
2. Options de développement → **Débogage USB** ON. Brancher au PC, accepter l'empreinte RSA. Vérifier : `adb devices`.
3. Installer **Termux depuis GitHub, via adb** (pas de Play Store ni de compte Google nécessaire) :
   - Architecture : `adb shell getprop ro.product.cpu.abi` (`armeabi-v7a` ou `arm64-v8a`).
   - Télécharger sur le PC l'APK correspondant (ou `universal` en cas de doute) depuis la dernière release : https://github.com/termux/termux-app/releases
   - `adb install termux-app_*.apk`
4. Paramètres → Batterie / Gestion des applis → **désactiver l'optimisation batterie pour Termux** (sinon Samsung le tue).
5. Copier les fichiers : `adb shell mkdir -p /sdcard/Download/poc && adb push phone/. /sdcard/Download/poc/`
6. Dans Termux (sur le téléphone) :
   ```
   termux-setup-storage          # accepter la permission
   bash ~/storage/downloads/poc/setup.sh a5-01
   bash ~/poc/run.sh
   ```

Ensuite on peut tout faire depuis le PC en SSH : `ssh -p 8021 localhost` — **seulement après `./connect.sh` (section 2)**, c'est lui qui crée la redirection du port 8021. Mot de passe = celui choisi dans `setup.sh`.

Dépannage SSH :
- `Connection refused` → pas de redirection côté PC : `adb forward --list` doit montrer `tcp:8021 tcp:8022` ; sinon relancer `./connect.sh`.
- Connexion coupée immédiatement → `sshd` ne tourne pas dans Termux : y taper `sshd` (ou relancer `bash ~/poc/run.sh`).

## 2. Lancer depuis le PC

```
cd host
./connect.sh          # adb forward + écrit backends.txt
python3 lb.py         # LB sur :8000 (laisser tourner)
python3 dashboard.py  # optionnel : téléphones connectés en live sur :8001
./test.sh 50          # dans un autre terminal
```

Navigateur : http://localhost:8001 (tableau de bord), http://localhost:8000/ (page d'un nœud via le LB, change à chaque rafraîchissement : round-robin).

## 3. Ce qu'on mesure / note pour le rapport

| Mesure | Comment | Résultat |
|---|---|---|
| Le serveur tourne écran éteint ? | laisser 30 min, relancer `test.sh` | |
| Survit au débranchement/rebranchement ? | débrancher, rebrancher, `./connect.sh` | |
| Débit séquentiel (req/s) | `./test.sh 200` | |
| Température batterie en charge continue | colonne `battery_temp_c` | |
| Failover | arrêter `run.sh` → le LB marque DOWN | |

Les métriques batterie/charge viennent de `/sys` et `/proc` : si elles valent `null`, Android les bloque sans root (c'est aussi un résultat).

## Alternative à Termux : appli PyNode

APK qui embarque Python (Chaquopy) + Flask/Django et sert le code déposé dans un dossier du téléphone, sur le même port 8080 : voir [pynode/README.md](pynode/README.md).

## Variante 2 : USB tethering (le téléphone devient une carte réseau)

1. Téléphone : Paramètres → Connexions → Point d'accès mobile et modem → **Modem USB**.
2. PC : une interface (`usb0`/`enx…`) apparaît et reçoit une IP. Le téléphone est typiquement en `192.168.42.129` (à vérifier : `ip route`).
3. `curl http://192.168.42.129:8080/` puis mettre cette IP dans `host/backends.txt`.

À tester : le modem USB se désactive-t-il au reboot / débranchement ? `adb` reste-t-il actif en même temps ?

⚠️ **Plusieurs téléphones en tethering sur un même hôte** : sur les anciens Android, chaque téléphone utiliserait le même sous-réseau (192.168.42.x) → conflit d'adresses. À vérifier ; si confirmé, il faudra des namespaces réseau / routage par interface côté hôte, ou rester sur `adb forward`. Point important pour l'architecture.

## Sécurité

Vieille batterie en charge permanente : ne pas laisser sans surveillance, surveiller `battery_temp_c` (au-delà de ~45 °C, débrancher).
