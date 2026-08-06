# specs/ : les plans de test métier

**Contrat du répertoire** : un fichier Markdown par domaine métier, produit par
l'agent **rf-planner** (exploration live via rf-mcp), consommé par l'agent
**rf-generator** (génération de la suite `.robot`, chaque étape exécutée live
avant écriture).

Règles :

- Le plan est la **source de vérité** : la suite générée porte un marqueur de
  provenance (`Spec: specs/<plan>.md (sha256:…)`) vérifié par
  `python scripts/check_spec_sync.py`. Un plan modifié sans régénération rend
  la suite périmée (le garde échoue).
- Le plan parle **métier** : pas de CSS/XPath dans les étapes de scénario. Les
  identifiants techniques observés (ids stables, rôles ARIA, champs JSON)
  n'apparaissent que sous « Données observées » / « Points de vigilance »,
  comme notes factuelles pour le generator.
- Chaque fait cité a été **observé live**, jamais supposé.
- **Marqueurs de cycle de vie** (posés/levés par les agents, jamais ignorés) :
  - `> **Statut : PÉRIMÉE (AAAA-MM-JJ)**, …` en tête de plan : posé par
    **rf-healer** quand le flux métier lui-même a changé ; le garde
    `check_spec_sync.py` échoue tant qu'il est présent ; **rf-planner** le
    retire en ré-explorant le flux.
  - `## Écarts constatés à la génération` : section où **rf-generator**
    consigne (datées) les divergences entre le plan et la réalité observée,
    avant de re-stamper ; **rf-planner** résout ces écarts dans les scénarios
    puis supprime la section à sa passe suivante.
- `couverture-proposee.md` (mode discovery du planner) est une feuille de
  route, pas un plan : chaque entrée repasse par une exploration dédiée.
- Le sous-répertoire `istqb/` accueille les **plans de test + cas de test
  ISTQB** (`*.istqb.md`) produits par l'agent **rf-istqb** (`/rf-istqb`) :
  documentation de conception de test au gabarit ISTQB / ISO 29119-3, chaque
  cas de test portant un bloc `replay` YAML normalisé rejouable par une IA
  quel que soit le framework. Voir `specs/istqb/README.md` ; ces documents ne
  sont pas des plans à générer par rf-generator et restent hors du périmètre
  de `check_spec_sync.py`.

Gabarit : voir la section « The plan you write » de
[.claude/agents/rf-planner.md](../.claude/agents/rf-planner.md).
