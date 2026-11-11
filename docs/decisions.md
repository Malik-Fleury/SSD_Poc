# Journal des décisions

Format : `ADR-NNN — Titre (date) — Statut` puis contexte / décision / conséquences en 2-3 lignes.

## ADR-001 — Focus smartphones (2026-11-10) — Accepté

- Contexte : le projet initial envisage smartphones et vieux PC.
- Décision : les smartphones sont les nœuds de calcul ; les vieux PC servent d'hôtes/passerelles si besoin.
- Conséquences : le design matériel et réseau est pensé autour des contraintes des téléphones.

## ADR-002 — Réseau : unités "hôte + téléphones en USB" (2026-11-10) — Proposé

- Contexte : 3 options (Wi-Fi, hôte USB, USB-Ethernet par téléphone), détail dans [reseau.md](reseau.md).
- Décision : option 2 pour le prototype, structurée en unités modulaires reliées en Ethernet.
- Justification : simplicité, modularité, rôle pour les vieux PC. L'alimentation des téléphones n'est pas encore traitée (problème à régler) ; faire passer le courant par le même câble USB est une piste, pas un acquis. Argument supplémentaire **non vérifié** : l'option 3 serait moins compatible (OTG/driver/charge) — voir test prévu dans [reseau.md](reseau.md).
- Conséquences : l'hôte est un point de défaillance par unité ; à revalider après mesures du prototype.

## ADR-003 — Logiciel du nœud : APK dédiée (Chaquopy) en plus de Termux (2026-11-10) — Proposé

- Contexte : Termux demande une installation manuelle par téléphone (setup, mot de passe SSH, wake lock) et sert des scripts maison.
- Décision : prototyper PyNode ([poc/poc-network/pynode](../poc/poc-network/pynode/README.md)), une APK qui embarque Python 3.11 + Flask/Django ; le code client est déposé par `adb push` et déployé sur tous les téléphones d'un coup.
- Conséquences : Python figé en 3.11 (support `armeabi-v7a`), paquets compilés seulement via recompilation de l'APK. À comparer à Termux (débit, RAM, stabilité) avant de choisir.
