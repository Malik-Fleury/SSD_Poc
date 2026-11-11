# Le projet : datacenter de smartphones recyclés (Suisse)

## Idée

Réutiliser des smartphones en fin de vie (écran cassé, obsolètes, mais SoC fonctionnel) comme **nœuds de calcul** regroupés dans un "datacenter" hébergé en Suisse. Vieux PC possibles en appoint, mais focus téléphones.

## Arguments de valeur (à étayer par des chiffres)

- **Économie circulaire** : prolonge la vie d'appareils qui finiraient en déchets électroniques.
- **Faible consommation** : un smartphone consomme quelques watts en charge (à mesurer).
- **Coût matériel quasi nul** : récupération / dons / partenariats recyclage.
- **Hébergement suisse** : souveraineté des données, image de qualité/fiabilité.

## Cas d'usage envisagés (à prioriser)

- Hébergement web léger / API / services statiques.
- Tâches parallélisables (CI, batch, scraping, calcul distribué).
- Edge / IoT, stockage froid (limité).

## Contraintes techniques connues

- Hétérogénéité des modèles (CPU ARM, RAM, versions Android).
- **Batteries** : gonflement et risque incendie si branchées 24/7 → retrait de batterie, limitation de charge, ou alimentation directe. Point clé pour la sécurité et l'assurance.
- OS : Android + Termux, LineageOS, ou Linux mobile (postmarketOS) selon support du modèle.
- Thermique, durée de vie du stockage flash, absence de port Ethernet natif.
- Réseau : voir [reseau.md](reseau.md).

## Questions ouvertes

- [ ] Modèle(s) de téléphone pour le prototype
- [ ] Stack logicielle cible (conteneurs ? k3s ? simple service web ?)
- [ ] Mesures réelles : W/téléphone, requêtes/s par téléphone
- [ ] Modèle économique (qui paie, pour quoi)
