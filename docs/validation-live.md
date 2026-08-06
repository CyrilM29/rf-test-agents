# Première validation live du cycle : runbook et résultats

Objectif : dérouler une fois, en conditions réelles, le cycle complet
`/rf-plan → /rf-generate → /rf-heal` (avec dérive simulée) sur une vraie
application web, et cocher la case « First live validation » de CLAUDE.md.

> **✅ Effectuée le 2026-07-24 sur https://www.saucedemo.com, cycle validé de
> bout en bout.** Résultats et enseignements en fin de document ; le déroulé
> ci-dessous reste le mode d'emploi pour rejouer la validation ailleurs.

## Pré-requis (état vérifié le 2026-07-24)

- [x] `robotframework` 7.4.2, `robotframework-browser` 20.0.0, Playwright
      installés ; `rfbrowser init` déjà exécuté (node_modules présents).
- [x] `.mcp.json` corrigé : le serveur se lance via le script console
      `robotmcp` (le paquet installé (fork `sap-robotmcp`) n'expose pas
      `python -m robotmcp`).
- [ ] **Redémarrer la session Claude Code** : les serveurs MCP se chargent à
      l'ouverture de session ; la correction de `.mcp.json` ne prend effet
      qu'après redémarrage. Vérification : les outils `mcp__rf-mcp__*`
      doivent être joignables (le planner échouera immédiatement sinon).

## Cible proposée

[https://www.saucedemo.com](https://www.saucedemo.com), boutique de
démonstration publique de Sauce Labs, faite pour l'entraînement à
l'automatisation. Identifiants publics documentés sur la page de connexion
(`standard_user` / `secret_sauce`) : publics, mais on respecte quand même la
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
   (dry run, `check_conventions.py`, run live) au vert : avec le mot de passe
   passé en `-v "SAUCE_PASSWORD: Secret:..."`.

3. **Simuler une dérive et guérir** : dans le page object de la page de
   connexion, remplacer le locator du bouton de connexion par une valeur
   fausse (ex. `id=login-button` → `id=login-button-old`) : c'est l'équivalent
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
| `/rf-plan` (rf-planner, 56 appels d'outils) | `specs/saucedemo-connexion-panier.md` : 3 scénarios, ~25 ancres relevées live, 12 points de vigilance, 0 identifiant écrit |
| `/rf-generate` (rf-generator, 57 appels) | `tests/robot/ui/web/saucedemo_connexion_panier.robot` + 3 page objects + `common.resource` + `variables/env_demo.yaml`. Gates : dry run `3/3`, `check_conventions` OK, **run live `3 tests, 3 passed`** |
| Dérive simulée | `${SD_INVENTORY_CONTAINER}` : `inventory-container` → `inventory-list-container` ; suite passée à `1 passed, 2 failed` |
| `/rf-heal` (rf-healer, 49 appels) | Cause diagnostiquée **sans indice**, correction d'une seule ligne dans le page object, **run final `3 tests, 3 passed`**, 1<sup>re</sup> entrée du `heal-journal` |

Vérifications indépendantes après coup : run live `3/3 PASS`, les deux gardes
au vert, 26 tests unitaires OK, et `secret_sauce` absent des fichiers
versionnés **comme** de `results/**/output.xml` (convention #6 tenue de bout en
bout).

### Ce que le live a appris (et qui n'aurait pas été trouvé sur le papier)

1. **Syntaxe des variables typées `Secret:`**, RF 7.4 exige une **espace après
   le deux-points du nom** : `-v "MDP: Secret:valeur"`. Sans elle la variable
   vaut la chaîne littérale `Secret:valeur` et `Fill Secret` la rejette. Le
   piège est silencieux ; l'exigence est désormais explicite dans CLAUDE.md.
2. **Un `Secret` ne se fabrique pas depuis un littéral** (`${X: secret}  v` →
   `Value must have type 'Secret'`) : d'où deux primitives de saisie, `Fill
   Secret` pour le mot de passe réel et `Fill Text` pour le faux mot de passe
   du scénario négatif.
3. **`Wait For Elements State` exige un `timeout=` nommé** : l'appel positionnel
   échoue (`got multiple values for argument 'timeout'`). Relevé par le planner,
   consigné en point de vigilance, jamais reproduit par le generator : la
   boucle de rétroaction planner → generator a fonctionné.
4. **L'échelle d'ancres a une exception réelle** : le healer a écarté l'échelon
   `id` (normalement prioritaire) parce que `#inventory_container` matche
   **2 éléments** sur cette page : preuve à l'appui, et note laissée dans le
   `heal-journal` à l'intention du planner. C'est exactement le comportement
   attendu : la sonde live prime sur la règle générale.
5. **rf-mcp crée `.robotmcp_artifacts/`** à la racine du dépôt : ajouté au
   `.gitignore`.
6. **`.mcp.json` était cassé** (`python -m robotmcp` : le fork installé n'expose
   pas de `__main__`) : corrigé vers le script console `robotmcp`. Sans ce
   correctif, aucun agent n'aurait pu ouvrir de session.

---

## Re-validation du 2026-07-25 (rf-mcp 0.35.0)

Objectif : vérifier **live** que les modifications des trois derniers commits
(notes de compatibilité 0.35.0, chat modes générés + `check_guidance_sync.py`,
liens docs) tiennent en conditions réelles, et pas seulement sur le papier.

| Contrôle | Résultat |
|---|---|
| Gardes locales | 47 tests unitaires OK ; `check_spec_sync`, `check_conventions`, `check_guidance_sync`, `regen_agent_definitions --check` au vert |
| Environnement | rf-mcp **0.35.0**, script console `robotmcp` présent, RF 7.4.2, Browser 20.0.0, Playwright 1.60.0 |
| Rituel de session rf-mcp (web) | session créée, `New Browser` / `New Page`, `get_session_state` → **DOM complet + snapshot ARIA** : le canal de perception des agents est intact sur 0.35 |
| Suite existante en live | `saucedemo_connexion_panier.robot` → **3 tests, 3 passed** |
| Dérive simulée | `${SD_LOGIN_ERROR_CLOSE}` : `data-test="error-button"` → `data-test="error-close"` ; suite à **2 passed, 1 failed** |
| `/rf-heal` (agent rf-healer, 28 appels d'outils) | cause diagnostiquée **sans indice**, correctif d'une ligne dans le page object, **3 tests, 3 passed**, entrée ajoutée au `heal-journal` |

Bonus du healer : il a comparé la variable fautive à `git show HEAD` et
diagnostiqué que la dérive était **locale et non commitée** (donc un exercice,
pas un changement de saucedemo.com), sans que rien dans la consigne ne le
suggère. Il a aussi refusé de poser un marqueur PÉRIMÉE, la spec ayant raison
depuis le début.

### Deux corrections sorties de ce live

1. **Le piège de classification desktop visait le mauvais point d'entrée.** La
   note de compatibilité l'attribuait à `manage_session init` ; mesure faite :
   `init` **ne classe rien** depuis son texte `scenario` (`session_type` reste
   `unknown`). C'est **`analyze_scenario`** qui classe, et il classe sur le
   TEXTE : un scénario purement web contenant le mot « desktop » donne
   `detected_session_type: desktop_testing` **même avec `context="web"` passé
   explicitement**, sans charger la moindre librairie web
   (`libraries_loaded: ["BuiltIn"]`, `PlatynUI.BareMetal` en tête du search
   order). Pire, la classification est **collante** : importer `Browser`
   ensuite et ouvrir la bonne URL rétablit `is_browser_session: true` mais
   **pas** la perception : `get_session_state` continue de servir
   `page_source: "<!-- Browser Library Page: None -->…"` et
   `aria_snapshot: null` alors que `current_url` est correcte. Seule sortie :
   ouvrir une nouvelle session. Enjeu réel : les instructions du serveur rf-mcp
   poussent activement vers `analyze_scenario` (« NEVER call
   manage_session(action='init') ») ; le rituel du projet diverge donc
   **délibérément**, et les quatre copies le disent désormais explicitement.
2. **`PYTHONIOENCODING=utf-8:surrogateescape`** (valeur de cet environnement)
   fait crasher le writer console de Robot Framework, `LookupError: unknown
   encoding: utf-8:surrogateescape`, dès qu'une ligne part sur stderr, sous
   PowerShell. Le run meurt sur l'affichage, pas sur le test. Contournement :
   lancer `robot` depuis Bash, ou forcer `PYTHONIOENCODING=utf-8`.
