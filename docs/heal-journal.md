# Journal de guérison (heal journal)

Mémoire des dérives réparées par **rf-healer** — une entrée par session de
réparation ayant modifié au moins un fichier. C'est l'anti-amnésie du cycle :
des entrées récurrentes sur le même page object ou la même famille d'ancres
(ids générés qui meurent à chaque re-render, libellés localisés…) signalent au
**rf-generator** et au **rf-planner** qu'une ancre plus stable s'impose à cet
endroit. Le planner lit ce journal avant d'écrire ses notes de localisation.

Format d'une entrée (append-only, la plus récente en haut) :

```markdown
## AAAA-MM-JJ — <suite>.robot
- **Classe** : locator drift | timing | data drift | changement fonctionnel
- **Réparation** : `<fichier>` : `avant` → `après` (une ligne par changement)
- **Preuve** : <l'observation live qui a justifié la réparation>
```

---

## 2026-07-25 — saucedemo_connexion_panier.robot

- **Classe** : locator drift
- **Réparation** : `resources/page_objects/saucedemo_login_page.resource` :
  `${SD_LOGIN_ERROR_CLOSE}` : `css=[data-test="error-close"]` →
  `css=[data-test="error-button"]`
- **Preuve** : sonde live rf-mcp (Browser chromium headless, page de connexion
  après `standard_user` / mot de passe erroné) — le `h3` du bandeau est
  `<h3 data-test="error"><button class="error-button" data-test="error-button"
  type="button"></button>Epic sadface: …</h3>` ; `[data-test="error-close"]`
  → **0 élément**, `[data-test="error-button"]` → visible, puis `Click` →
  `[data-test="error"]` **detached** et `value` du champ identifiant toujours
  `standard_user` (la chaîne complète du scénario 2 rejouée live avant
  écriture). Suite re-jouée : **3 tests, 3 passed, 0 failed**.
- **Origine** : dérive **locale non commitée** — `git show HEAD` porte déjà
  `css=[data-test="error-button"]` ; seule la copie du working tree avait été
  altérée (exercice de dérive simulée, comme le 2026-07-24). Rien n'a changé
  côté saucedemo.com : la réparation ramène le fichier à son état commité,
  `git diff` sur ce fichier est donc vide après correction.
- **Note d'ancrage (pour rf-planner / rf-generator)** : l'ancre altérée
  contredisait le **commentaire du fichier lui-même** (« seul
  `data-test=error-button` est exploitable ») et la spec (§ Localisateurs,
  ligne 27) — la vérité était écrite deux fois à côté de la variable fausse,
  et la spec a suffi à trancher sans ambiguïté. Ce bouton n'a
  **aucun nom accessible** (ARIA : `button` nu dans le `heading`), donc
  l'échelle id → `data-test` → rôle + nom accessible s'arrête ici à
  `data-test` : pas de repli rôle+nom possible, c'est structurellement la
  surface la plus fragile de cette page. Deuxième dérive consécutive sur ce
  site portant sur le **nom** d'une ancre `data-test` (après
  `inventory-list-container`) : la famille `data-test` reste la bonne, mais
  toute réparation ici doit vérifier l'ancre contre la spec avant de la
  réécrire.

## 2026-07-24 — saucedemo_connexion_panier.robot

- **Classe** : locator drift
- **Réparation** : `resources/page_objects/saucedemo_inventory_page.resource` :
  `${SD_INVENTORY_CONTAINER}` : `css=[data-test="inventory-list-container"]` →
  `css=[data-test="inventory-container"]`
- **Preuve** : sonde live rf-mcp (Browser chromium headless, `/inventory.html`
  après connexion `standard_user`) — `[data-test="inventory-list-container"]`
  → **0 élément** (l'ancre n'existe plus après la mise à jour applicative),
  `[data-test="inventory-container"]` → **1 élément**, et
  `[data-test="inventory-container"] [data-test="inventory-item"]` → **6**,
  conforme au `${NOMBRE_PRODUITS_ATTENDU}` du plan. `Wait For Elements State
  … visible timeout=5s` rejoué OK sur la nouvelle ancre avant toute écriture.
- **Note d'ancrage (pour rf-planner / rf-generator)** : sur cette page, **ne
  pas ancrer par l'id** — `#inventory_container` matche **2 éléments** (un
  `div` vide sans classe ni `data-test`, plus le vrai conteneur
  `div.inventory_container`), donc l'id n'y est pas unique ; seul
  `data-test="inventory-container"` désigne le conteneur sans ambiguïté. Le
  reste de la chaîne du scénario 3 (bouton d'ajout ancré par nom exact +
  `[data-test^="add-to-cart"]`, mutation vers `[data-test^="remove"]`, badge
  panier, `cart-list`, quantité, prix, burger + `#logout_sidebar_link`) a été
  resondé live un par un : **aucune autre dérive**. La famille d'ancres
  `data-test` reste la bonne pour ce site ; c'est le nom de l'ancre du
  conteneur, pas sa famille, qui a changé.
