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

Règles du répertoire :

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
