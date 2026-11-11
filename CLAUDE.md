# CLAUDE.md

Projet de cours **Advanced Project Management** (Master) : reprendre le projet d'un camarade, l'analyser et le piloter avec les outils de gestion de projet. Livrable final : un rapport qui **donne envie à un investisseur de financer** le projet.

**Le projet** : un datacenter en Suisse construit à partir de **vieux smartphones** reconditionnés (et éventuellement de vieux PC en appoint). Focus actuel : les téléphones.

Ce dossier (`Technique/`) contient la partie technique. `../Documents/` contient les documents du cours / gestion de projet.

## Où trouver le contexte (lire seulement ce qui est utile à la tâche)

| Fichier | Contenu | Quand le lire |
|---|---|---|
| [docs/cours.md](docs/cours.md) | Attentes du cours, livrable, ton du rapport | Rédaction du rapport, gestion de projet |
| [docs/projet.md](docs/projet.md) | Vision, proposition de valeur, contraintes, questions ouvertes | Toute tâche sur le fond du projet |
| [docs/reseau.md](docs/reseau.md) | Options réseau étudiées + recommandation | Architecture, réseau, prototype |
| [docs/decisions.md](docs/decisions.md) | Journal des décisions (ADR courts) | Avant de remettre en cause un choix |

## Structure du dossier

```
Technique/
├── CLAUDE.md        # ce fichier (index)
├── docs/            # contexte : cours, projet, réseau, décisions
├── compte-rendu/    # comptes rendus courts (ex. réseau et logiciel des nœuds)
└── poc/             # un sous-dossier par preuve de concept, chacun avec son README.md
    └── poc-network/ # Galaxy A5 2016 sans root : Termux + serveur web, LB sur PC via adb (USB)
        ├── host/    # côté PC : connect.sh, lb.py, dashboard.py, test.sh, push-app.sh, make-cert.sh
        ├── phone/   # côté téléphone (Termux) : server.py, index.html, setup.sh
        └── pynode/  # alternative à Termux : APK Android (Chaquopy) qui sert une appli Flask/Django déposée sur le téléphone
```

Nouveau POC → nouveau dossier `poc/poc-<sujet>/` avec son propre `README.md` (but, étapes, résultats mesurés), et une ligne ajoutée ici.

## Règles de travail

- Langue : **français** (sauf code et termes techniques usuels).
- Distinguer clairement **fait vérifié**, **hypothèse** et **à valider** — un investisseur doit pouvoir faire confiance aux chiffres.
- Les intuitions de l'équipe ("de souvenir…") sont des **hypothèses** : les marquer ⚠️ et ne jamais les reformuler en faits sans test ou source.
- Toute nouvelle décision structurante → ajouter une entrée dans `docs/decisions.md`.
- Garder ces fichiers courts : un fait = un endroit, pas de duplication entre fichiers.
