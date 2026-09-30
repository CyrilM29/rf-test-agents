# specs/istqb/ : plans de test et cas de test ISTQB

Documents de **conception de test** au gabarit ISTQB / ISO 29119-3, un fichier
par domaine métier (`<slug>.istqb.md`, kebab-case), produits par l'agent
**rf-istqb** (`/rf-istqb`) depuis les plans `specs/` du planner et les sorties
d'enregistrement (le recorder frère rf-web-recorder émet le même gabarit en
brouillon anglais depuis sa 0.6.0 : entrée « ISTQB test plan (.istqb.md) » de
son menu export).

Chaque document couvre les deux niveaux :

- **plan de test** : identifiant `TP-<slug>`, objectif et périmètre,
  préconditions et données, critères d'entrée/sortie, risques ;
- **cas de test** : un `TC-nn` par scénario, tableau
  `# | Action | Données | Résultat attendu`, postconditions, et un bloc
  `replay` YAML **normalisé** : actions neutres vis-à-vis du framework
  (`click`, `fill`, `press_key`, `assert_text`…), cible en langage humain (le
  nom accessible ou le libellé métier), localisateur relevé relégué en `hint`
  (moteur = la stratégie de localisation, repli éventuel). C'est ce bloc qui
  rend le cas rejouable par une IA avec n'importe quel framework de test.

## `revues/` : la revue ISTQB des suites générées

Le second mode de **rf-istqb** (`/rf-istqb revue <suite ou slug>`) audite une
suite générée face à son plan et écrit un rapport daté dans
`specs/istqb/revues/<slug>.revue.md`. La revue est **systématique** : chaque
suite que `rf-generator` produit en reçoit une, après le passage du
`rf-verifier` (le vérificateur juge l'invariant métier et les preuves, la
revue ISTQB juge la conception du test).

Un rapport porte : l'objet revu, l'invariant propagé du sidecar, le verdict
(`approved`, `approved_with_recommendations`, `changes_requested`,
`not_reviewable`, distincts de ceux du vérificateur), la couverture du plan par
les suites, les constats numérotés `F<n>` par sévérité (Bloquant, Recommandé,
Remarque) sur six axes (traçabilité, conception des cas, force des assertions,
maintenabilité, indépendance et sûreté, honnêteté de la cible et du canal), les
cas de test à ajouter, et, dès la deuxième revue, le suivi des constats
précédents. Une nouvelle revue du même sujet MET À JOUR le fichier : les
numéros de constats restent stables, aucun constat levé n'est effacé.

La revue ne modifie rien d'autre que son rapport : jamais `tests/robot/`,
`resources/`, les plans ni les sidecars. Un constat est une recommandation
pour le générateur ou pour un humain, pas un correctif.

## Règles du répertoire :

- **Ancré dans l'observé** : toute valeur, tout localisateur, tout résultat
  attendu vient d'une source (plan, enregistrement, suite) ; ce qu'aucune
  source n'appuie reste « à compléter ».
- **Résultats attendus robustes** : comptages, nombres extraits, rôles ARIA +
  noms accessibles ; jamais un texte localisé fragile quand la source offre
  un ancrage robuste.
- **Aucune attente fixe** dans les blocs replay : une attente est toujours une
  condition (fin de chargement, élément visible), jamais une durée.
- **Aucun identifiant** : un pas de connexion référence le contrat de
  variables (`Secret:` en ligne de commande), jamais une valeur.
- Ces documents sont de la documentation : ils ne remplacent jamais les suites
  exécutables de `tests/robot/` et restent hors du périmètre de
  `check_spec_sync.py` (qui ne suit que les plans `specs/*.md` liés aux
  suites par leur marqueur de provenance).
