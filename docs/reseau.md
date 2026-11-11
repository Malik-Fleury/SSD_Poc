# Architecture réseau

## Options étudiées

| | 1. Wi-Fi | 2. Hôte + téléphones en USB | 3. Adaptateur USB-Ethernet par téléphone |
|---|---|---|---|
| Principe | Chaque téléphone sur un point d'accès | Un PC hôte, téléphones en USB tethering (RNDIS/NCM) ; l'hôte fait reverse proxy / load balancer | Chaque téléphone a son lien Ethernet vers un switch |
| Coût / téléphone | ~0 | Câble + part de hub USB alimenté | Hub USB-C avec Ethernet **+ Power Delivery** (~20-30 CHF) |
| Alimentation ⚠️ *non traitée, problème à régler* | Câble séparé | Piste : le même câble USB (charge + données, à vérifier) | Piste : via le hub PD (sinon le port USB est pris) |
| Débit / fiabilité | Partagé, interférences, latence variable | Bon (USB 2.0 ~ 100-300 Mb/s réels) | Bon et stable (100 Mb/s - 1 Gb/s) |
| Passage à l'échelle | Mauvais (>20-30 appareils par AP) | Limité par hôte (contrôleur USB, ~10-20 tél.) | Bon : switch standard |
| Point de défaillance | AP | **L'hôte** | Switch (classique) |
| Image "datacenter" | Faible | Moyenne | Forte |

## Compatibilité USB des téléphones — ⚠️ HYPOTHÈSE, NON VÉRIFIÉE

Intuition de l'équipe (souvenir, pas une source) : les téléphones seraient peu compatibles avec des périphériques USB externes. **Ne pas présenter comme un fait tant que ce n'est pas testé ou sourcé.**

Raisonnement qui en découle, à confirmer :
- **Option 2** : le téléphone reste en mode **périphérique USB** (celui utilisé pour le brancher à un PC). Hypothèse : USB tethering, `adb` et charge simultanée fonctionnent sur la grande majorité des modèles.
- **Option 3** : le téléphone doit être **hôte USB (OTG)**. Points de friction possibles :
  - support OTG absent/partiel sur certains vieux modèles ?
  - driver de la puce Ethernet (ex. Realtek RTL8152/8153, ASIX AX88179) présent ou non selon le constructeur ?
  - charge + OTG simultanés supportés ou non ?
- Si l'hypothèse se confirme, c'est un argument fort pour l'option 2 vu le parc **ancien et hétérogène**. Si elle est fausse, l'option 3 redevient sérieuse (meilleure scalabilité, pas de point de défaillance unique).

**Test à faire** : sur 3-5 modèles d'âges différents, essayer (a) USB tethering + charge vers un PC, (b) adaptateur USB-Ethernet via hub PD. Noter ce qui marche.

## Recommandation

**Option 2 pour le prototype et comme brique de base, organisée en "unités" modulaires.**

- Une **unité** = 1 hôte (vieux PC ou mini-PC) + N téléphones (≈8-16) via **hubs USB alimentés**.
- L'hôte sert de passerelle : DHCP sur les interfaces USB, reverse proxy / load balancer (HAProxy ou nginx), monitoring, et redémarrage des téléphones via `adb`.
- Les hôtes sont reliés entre eux en **Ethernet** classique → on scale en ajoutant des unités (scale horizontal facile à expliquer à un investisseur), et ça donne un vrai rôle aux vieux PC.
- Option 1 (Wi-Fi) : seulement pour les tout premiers tests.
- Option 3 : en réserve. Son sort dépend du test de compatibilité ci-dessus (non encore fait).

## Points à vérifier dans le prototype

- [ ] Le USB tethering se réactive-t-il automatiquement au reboot ? (sinon `adb`/root/script)
- [ ] Courant fourni par les hubs : ≥1-2 A par port en charge
- [ ] Nombre max de téléphones stables par contrôleur USB de l'hôte
- [ ] Débit réel et latence hôte ↔ téléphone
- [ ] Comportement batterie branchée en continu (limite de charge, température)
