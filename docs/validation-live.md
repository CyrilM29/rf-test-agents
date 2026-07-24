# Première validation live du cycle — runbook et résultats

Objectif : dérouler une fois, en conditions réelles, le cycle complet
`/rf-plan → /rf-generate → /rf-heal` (avec dérive simulée) sur une vraie
application web, et cocher la case « First live validation » de CLAUDE.md.

> **✅ Effectuée le 2026-07-24 sur https://www.saucedemo.com — cycle validé de
> bout en bout.** Résultats et enseignements en fin de document ; le déroulé
> ci-dessous reste le mode d'emploi pour rejouer la validation ailleurs.

## Pré-requis (état vérifié le 2026-07-24)

- [x] `robotframework` 7.4.2, `robotframework-browser` 20.0.0, Playwright
      installés ; `rfbrowser init` déjà exécuté (node_modules présents).
- [x] `.mcp.json` corrigé : le serveur se lance via le script console
      `robotmcp` (le paquet installé — fork `sap-robotmcp` — n'expose pas
      `python -m robotmcp`).
- [ ] **Redémarrer la session Claude Code** : les serveurs MCP se chargent à
      l'ouverture de session ; la correction de `.mcp.json` ne prend effet
      qu'après redémarrage. Vérification : les outils `mcp__rf-mcp__*`
      doivent être joignables (le planner échouera immédiatement sinon).

## Cible proposée

[https://www.saucedemo.com](https://www.saucedemo.com) — boutique de
démonstration publique de Sauce Labs, faite pour l'entraînement à
l'automatisation. Identifiants publics documentés sur la page de connexion
(`standard_user` / `secret_sauce`) — publics, mais on respecte quand même la
convention : passés en variable `Secret:` à l'exécution, jamais écrits dans un
fichier.

## Déroulé

1. **Planifier** :

   ```
   /rf-plan le parcours de connexion puis l'ajout d'un article au panier sur https://www.saucedemo.com (user standard_user, mot de passe affiché sur la page)
   ```

   Attendu : `specs/saucedemo-connexion-panier.md` (ou slug proche), chaque
   fait observé live (ids `user-name`, `password`, `login-button`,
   `data-test` des produits…), liste des keywords métier manquants.

2. **Générer** :

   ```
   /rf-generate specs/<slug produit à l'étape 1>.md
   ```

   Attendu : `tests/robot/ui/web/<slug>.robot` + page objects sous
   `resources/page_objects/`, marqueur de provenance stampé, les trois gates
   (dry run, `check_conventions.py`, run live) au vert — avec le mot de passe
   passé en `-v "SAUCE_PASSWORD: Secret:..."`.

3. **Simuler une dérive et guérir** : dans le page object de la page de
   connexion, remplacer le locator du bouton de connexion par une valeur
   fausse (ex. `id=login-button` → `id=login-button-old`) — c'est l'équivalent
   d'un re-render qui aurait changé l'id. Vérifier que la suite passe au
   rouge, puis :

   ```
   /rf-heal tests/robot/ui/web/<slug>.robot
   ```

   Attendu : le healer reproduit l'échec, perçoit la page live, restaure une
   ancre stable, re-run vert, entrée ajoutée à `docs/heal-journal.md`.

4. **Clore** : `python scripts/check_spec_sync.py` et
   `python scripts/check_conventions.py` au vert, cocher la case dans
   CLAUDE.md § Status, noter les frictions rencontrées (elles valent de l'or :
   les reporter dans les définitions d'agents).

---

## Résultats de la validation du 2026-07-24

Cible : `https://www.saucedemo.com` (Browser/Playwright, chromium headless).
Les trois agents ont tourné sans intervention manuelle sur leur périmètre.

| Étape | Résultat |
|---|---|
| `/rf-plan` (rf-planner, 56 appels d'outils) | `specs/saucedemo-connexion-panier.md` — 3 scénarios, ~25 ancres relevées live, 12 points de vigilance, 0 identifiant écrit |
| `/rf-generate` (rf-generator, 57 appels) | `tests/robot/ui/web/saucedemo_connexion_panier.robot` + 3 page objects + `common.resource` + `variables/env_demo.yaml`. Gates : dry run `3/3`, `check_conventions` OK, **run live `3 tests, 3 passed`** |
| Dérive simulée | `${SD_INVENTORY_CONTAINER}` : `inventory-container` → `inventory-list-container` ; suite passée à `1 passed, 2 failed` |
| `/rf-heal` (rf-healer, 49 appels) | Cause diagnostiquée **sans indice**, correction d'une seule ligne dans le page object, **run final `3 tests, 3 passed`**, 1<sup>re</sup> entrée du `heal-journal` |

Vérifications indépendantes après coup : run live `3/3 PASS`, les deux gardes
au vert, 26 tests unitaires OK, et `secret_sauce` absent des fichiers
versionnés **comme** de `results/**/output.xml` (convention #6 tenue de bout en
bout).

### Ce que le live a appris (et qui n'aurait pas été trouvé sur le papier)

1. **Syntaxe des variables typées `Secret:`** — RF 7.4 exige une **espace après
   le deux-points du nom** : `-v "MDP: Secret:valeur"`. Sans elle la variable
   vaut la chaîne littérale `Secret:valeur` et `Fill Secret` la rejette. Le
   piège est silencieux ; l'exigence est désormais explicite dans CLAUDE.md.
2. **Un `Secret` ne se fabrique pas depuis un littéral** (`${X: secret}  v` →
   `Value must have type 'Secret'`) : d'où deux primitives de saisie, `Fill
   Secret` pour le mot de passe réel et `Fill Text` pour le faux mot de passe
   du scénario négatif.
3. **`Wait For Elements State` exige un `timeout=` nommé** — l'appel positionnel
   échoue (`got multiple values for argument 'timeout'`). Relevé par le planner,
   consigné en point de vigilance, jamais reproduit par le generator : la
   boucle de rétroaction planner → generator a fonctionné.
4. **L'échelle d'ancres a une exception réelle** : le healer a écarté l'échelon
   `id` (normalement prioritaire) parce que `#inventory_container` matche
   **2 éléments** sur cette page — preuve à l'appui, et note laissée dans le
   `heal-journal` à l'intention du planner. C'est exactement le comportement
   attendu : la sonde live prime sur la règle générale.
5. **rf-mcp crée `.robotmcp_artifacts/`** à la racine du dépôt — ajouté au
   `.gitignore`.
6. **`.mcp.json` était cassé** (`python -m robotmcp` : le fork installé n'expose
   pas de `__main__`) — corrigé vers le script console `robotmcp`. Sans ce
   correctif, aucun agent n'aurait pu ouvrir de session.
