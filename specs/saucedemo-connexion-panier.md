# Sauce Demo : Connexion et ajout au panier

- **Canal** : web (Browser / Playwright, chromium headless)
- **Système / URL** : https://www.saucedemo.com/, titre de page `Swag Labs`
  (SPA React, boutique de démonstration Sauce Labs)
- **Préconditions** :
  - Compte de démonstration standard fourni en variables de ligne de commande
    typées `Secret:` : `${SAUCE_USER}` / `${SAUCE_PASSWORD}` (jamais écrites
    dans un fichier du dépôt : cf. convention #6).
  - État initial attendu : panier vide (aucun badge sur l'icône panier).
  - Aucune persistance côté serveur : l'état panier vit dans le stockage local
    de la session navigateur. Un navigateur neuf repart donc panier vide.

## Données observées

Exploration live du 2026-07-24 (rf-mcp, Browser chromium headless).

### Page de connexion, `https://www.saucedemo.com/`

| Élément | Ancre stable observée | Rôle ARIA / nom accessible |
|---|---|---|
| Champ identifiant | `id=user-name`, `data-test=username`, `name=user-name` | `textbox "Username"` |
| Champ mot de passe | `id=password`, `data-test=password`, `type=password` | `textbox "Password"` |
| Bouton de connexion | `id=login-button`, `data-test=login-button` (`input[type=submit]`, `value=Login`) | `button "Login"` |
| Conteneur d'erreur | `div.error-message-container` (vide hors erreur) | : |
| Message d'erreur | `data-test=error` (balise `h3`) | `heading [level=3]` |
| Bouton de fermeture de l'erreur | `data-test=error-button` (`button.error-button`) | `button` **sans nom accessible** |

- Les identifiants de démonstration sont affichés sur la page elle-même
  (`data-test=login-credentials` / `data-test=login-password`) : ils ne sont
  pas une donnée de test à recopier, la suite doit passer par les variables.

### Connexion en échec : faits relevés

- Identifiant valide + mot de passe erroné : **aucune navigation**, l'URL reste
  `https://www.saucedemo.com/`.
- Apparition de `data-test=error`, texte exact observé :
  `Epic sadface: Username and password do not match any user in this service`.
- Le conteneur `div.error-message-container` gagne la classe `error` et les
  deux `input` gagnent la classe `error`.
- **Le message n'est pas générique** : identifiant vide → même ancre
  `data-test=error` mais texte `Epic sadface: Username is required`. L'ancre
  seule ne discrimine donc pas le cas d'erreur ; l'assertion doit combiner
  présence de l'ancre **et** message attendu pour distinguer les causes.
- Clic sur `data-test=error-button` : le `h3` `data-test=error` est **retiré du
  DOM** (état `detached`, pas seulement masqué) et `.error-message-container`
  redevient vide. Les valeurs saisies dans les deux champs sont **conservées**.

### Page inventaire, `https://www.saucedemo.com/inventory.html`

Atteinte par redirection après connexion réussie (l'URL est le marqueur de
succès le plus robuste).

| Élément | Ancre stable observée |
|---|---|
| En-tête | `id=header_container`, `data-test=header-container` / `data-test=primary-header` |
| Titre de page | `data-test=title` (texte `Products`) |
| Bouton menu burger | `id=react-burger-menu-btn` : `button "Open Menu"` |
| Bouton fermeture menu | `id=react-burger-cross-btn` : `button "Close Menu"` |
| Menu : Tous les articles | `id=inventory_sidebar_link`, `data-test=inventory-sidebar-link` |
| Menu : À propos | `id=about_sidebar_link`, `data-test=about-sidebar-link` |
| Menu : Déconnexion | `id=logout_sidebar_link`, `data-test=logout-sidebar-link` |
| Menu : Reset App State | `id=reset_sidebar_link`, `data-test=reset-sidebar-link` |
| Lien panier | `data-test=shopping-cart-link` (`a.shopping_cart_link`, **sans `id`, sans `href`**) |
| Badge panier | `data-test=shopping-cart-badge` (`span.shopping_cart_badge`) |
| Liste produits | `data-test=inventory-container` / `id=inventory_container` |
| Fiche produit (répétée) | `data-test=inventory-item` : **6 occurrences** |
| Nom produit | `data-test=inventory-item-name` |
| Prix produit | `data-test=inventory-item-price` |
| Tri | `select` `data-test=product-sort-container` (4 options : `Name (A to Z)` sélectionnée par défaut, `Name (Z to A)`, `Price (low to high)`, `Price (high to low)`) |

- Catalogue observé (6 articles) : `Sauce Labs Backpack` ($29.99),
  `Sauce Labs Bike Light` ($9.99), `Sauce Labs Bolt T-Shirt` ($15.99),
  `Sauce Labs Fleece Jacket` ($49.99), `Sauce Labs Onesie` ($7.99),
  `Test.allTheThings() T-Shirt (Red)` ($15.99).
- Bouton d'ajout par produit : `id` = `data-test` = `add-to-cart-<slug-du-nom>`
  (slug en minuscules, espaces → tirets). Observés :
  `add-to-cart-sauce-labs-backpack`, `add-to-cart-sauce-labs-bike-light`,
  `add-to-cart-sauce-labs-bolt-t-shirt`, `add-to-cart-sauce-labs-fleece-jacket`,
  `add-to-cart-sauce-labs-onesie`,
  `add-to-cart-test.allthethings()-t-shirt-(red)`.
- **Le bouton mute après ajout** : `id`/`data-test`
  `add-to-cart-sauce-labs-backpack` → `remove-sauce-labs-backpack`,
  classe `btn_primary` → `btn_secondary`, libellé `Add to cart` → `Remove`.
  Ce n'est pas un simple changement de libellé : l'ancre elle-même change.
- Badge panier : **absent du DOM** quand le panier est vide (compte
  d'éléments = 0 vérifié avant ajout), puis présent avec le texte `1` après
  l'ajout d'un article.

### Page panier, `https://www.saucedemo.com/cart.html`

| Élément | Ancre stable observée |
|---|---|
| Titre de page | `data-test=title` (texte `Your Cart`) |
| Conteneur | `id=cart_contents_container`, `data-test=cart-contents-container` |
| Liste | `data-test=cart-list` |
| En-têtes de colonnes | `data-test=cart-quantity-label` (`QTY`), `data-test=cart-desc-label` (`Description`) |
| Ligne de panier | `data-test=inventory-item` : **1 occurrence** après l'ajout |
| Quantité | `data-test=item-quantity` (texte `1`) |
| Nom article | `data-test=inventory-item-name` (`Sauce Labs Backpack`) |
| Prix article | `data-test=inventory-item-price` (`$29.99`) |
| Retrait article | `id=remove-sauce-labs-backpack`, `data-test=remove-sauce-labs-backpack` |
| Continuer les achats | `id=continue-shopping`, `data-test=continue-shopping` |
| Commander | `id=checkout`, `data-test=checkout` |

- Après clic sur le bouton de retrait : le badge `data-test=shopping-cart-badge`
  passe à l'état `detached` et le compte de `data-test=inventory-item` retombe
  à **0** : la remise à l'état initial est donc vérifiable.

### Déconnexion et garde de session

- Le panneau latéral (`.bm-menu-wrap`) est **présent dans le DOM même fermé**,
  avec `aria-hidden="true"`, `transform: translate3d(-100%, 0, 0)` et une
  transition CSS de `0.5s` ; `#logout_sidebar_link` a alors un rectangle de
  **0 × 0 px**.
- Après ouverture du menu puis clic sur `id=logout_sidebar_link` : retour à
  `https://www.saucedemo.com/`, formulaire de connexion réaffiché, **champs
  vidés**.
- Accès direct à `/inventory.html` sans session : la navigation renvoie un
  statut HTTP `404`, l'application redirige vers `https://www.saucedemo.com/`
  et affiche `data-test=error` avec le texte
  `Epic sadface: You can only access '/inventory.html' when you are logged in.`

## Scénarios

### 1. Connexion réussie avec des identifiants valides

- **Étapes** :
  1. Ouvrir la boutique Sauce Demo (navigateur chromium headless) sur l'URL de
     base.
  2. Vérifier que le formulaire de connexion est affiché (champ identifiant,
     champ mot de passe, bouton de connexion).
  3. Se connecter avec `${SAUCE_USER}` / `${SAUCE_PASSWORD}`.
- **Résultat attendu** :
  - L'URL courante est `https://www.saucedemo.com/inventory.html`.
  - Le titre de section (`data-test=title`) vaut `Products`.
  - La liste produits (`data-test=inventory-container`) est visible et contient
    **6** fiches produit (`data-test=inventory-item`).
  - Aucun message d'erreur : `data-test=error` absent du DOM.
  - Le badge panier (`data-test=shopping-cart-badge`) est absent (panier vide).
- **Keywords métier manquants** : `Ouvrir La Boutique Sauce Demo`,
  `Se Connecter Avec`, `La Page Inventaire Doit Être Affichée`,
  `Le Nombre De Produits Affichés Doit Être`, `Le Panier Doit Être Vide`.

### 2. Connexion refusée avec un mot de passe erroné

- **Étapes** :
  1. Ouvrir la boutique Sauce Demo sur l'URL de base.
  2. Tenter une connexion avec `${SAUCE_USER}` et un mot de passe volontairement
     invalide (`${SAUCE_WRONG_PASSWORD}`, valeur de test quelconque non
     secrète).
  3. Vérifier le message d'erreur affiché.
  4. Fermer le message d'erreur via son bouton de fermeture.
- **Résultat attendu** :
  - Aucune navigation : l'URL reste l'URL de base
    `https://www.saucedemo.com/` (pas de `/inventory.html`).
  - Le bandeau d'erreur (`data-test=error`) est visible et son texte vaut
    exactement `Epic sadface: Username and password do not match any user in
    this service` : le texte est ici **discriminant** (l'ancre seule ne
    distingue pas ce cas de « champ obligatoire »), cf. § Points de vigilance.
  - Après fermeture : l'élément `data-test=error` est **détaché du DOM**, et le
    formulaire reste utilisable (les valeurs saisies sont conservées).
- **Keywords métier manquants** : `Tenter Une Connexion Avec`,
  `Un Message D'Erreur De Connexion Doit Être Affiché` (avec le message attendu
  en argument), `Fermer Le Message D'Erreur De Connexion`,
  `Aucun Message D'Erreur De Connexion Ne Doit Être Affiché`.

### 3. Ajout d'un article au panier et vérification du badge et du contenu

- **Étapes** :
  1. Ouvrir la boutique et se connecter avec `${SAUCE_USER}` /
     `${SAUCE_PASSWORD}` (réutilise le keyword du scénario 1).
  2. Constater l'état initial : panier vide (pas de badge).
  3. Ajouter au panier l'article `Sauce Labs Backpack` depuis la liste produits.
  4. Vérifier le badge du panier sur la page inventaire.
  5. Vérifier que le bouton de la fiche produit propose désormais le retrait.
  6. Ouvrir le panier via l'icône panier.
  7. Vérifier le contenu du panier (nombre de lignes, nom, quantité, prix).
  8. **Réversibilité** : retirer l'article depuis le panier.
  9. Vérifier le retour à l'état initial.
  10. Se déconnecter via le menu latéral.
- **Résultat attendu** :
  - Après l'ajout : le badge `data-test=shopping-cart-badge` est présent et son
    texte vaut `1` ; le bouton de la fiche `Sauce Labs Backpack` porte
    désormais l'ancre de retrait `remove-sauce-labs-backpack`.
  - Sur la page panier : l'URL est `https://www.saucedemo.com/cart.html`, le
    titre (`data-test=title`) vaut `Your Cart`, la liste
    (`data-test=cart-list`) contient exactement **1** ligne
    (`data-test=inventory-item`), avec `data-test=inventory-item-name` =
    `Sauce Labs Backpack`, `data-test=item-quantity` = `1` et
    `data-test=inventory-item-price` = `$29.99`.
  - Après retrait : le badge est **détaché du DOM** et le panier contient **0**
    ligne.
  - Après déconnexion : l'URL est revenue à `https://www.saucedemo.com/` et le
    formulaire de connexion est de nouveau affiché.
- **Keywords métier manquants** : `Ajouter L'Article Au Panier`,
  `Le Badge Du Panier Doit Indiquer`, `L'Article Doit Être Retirable Depuis La
  Liste Produits`, `Ouvrir Le Panier`, `La Page Panier Doit Être Affichée`,
  `Le Panier Doit Contenir L'Article`, `Le Nombre De Lignes Du Panier Doit
  Être`, `Retirer L'Article Du Panier`, `Se Déconnecter`,
  `La Page De Connexion Doit Être Affichée`.

## Points de vigilance

- **Le bouton d'ajout change d'ancre après l'ajout** : `add-to-cart-<slug>` →
  `remove-<slug>` (id ET `data-test`), avec changement de classe
  (`btn_primary` → `btn_secondary`). Ne jamais réutiliser l'ancre d'ajout pour
  vérifier l'état « ajouté » ni pour retirer l'article : ce sont deux
  localisateurs distincts, à dériver du slug du produit dans le page object.
- **Le slug produit n'est pas toujours trivial** : `Test.allTheThings()
  T-Shirt (Red)` donne `add-to-cart-test.allthethings()-t-shirt-(red)`, qui
  contient des points et des parenthèses : caractères à échapper si le
  localisateur est construit en CSS. Préférer une construction par
  `data-test=` exact, ou un ancrage relatif à la fiche produit
  (`data-test=inventory-item` filtrée sur `data-test=inventory-item-name`).
- **`data-test=inventory-item` est réutilisé sur deux pages** : 6 occurrences
  sur `/inventory.html`, 1 occurrence sur `/cart.html` après ajout. Toute
  assertion de comptage doit être qualifiée par la page courante (ou par un
  conteneur parent : `data-test=inventory-container` vs `data-test=cart-list`),
  sinon l'assertion devient ambiguë.
- **Le badge panier n'existe pas quand le panier est vide** : ce n'est pas un
  badge à `0`, l'élément est absent du DOM. « Panier vide » se vérifie par
  compte d'éléments à 0 ou par un état `detached`, jamais par un texte.
- **Menu latéral présent mais masqué** : `#logout_sidebar_link` &
  consorts existent dans le DOM avec `aria-hidden="true"` et une taille de
  0 × 0 px tant que le burger n'a pas été cliqué. Un clic direct sans ouverture
  du menu échoue. La transition CSS dure `0.5s` : synchroniser avec
  `Wait For Elements State    ...    visible` (jamais de `Sleep`,
  convention #2).
- **`Wait For Elements State` exige `timeout=` nommé** : l'appel positionnel
  `Wait For Elements State  <sel>  detached  5s` échoue avec
  `got multiple values for argument 'timeout'`. Toujours écrire
  `timeout=5s`.
- **Le bouton de fermeture du message d'erreur n'a pas de nom accessible**
  (`button.error-button` au contenu vide) : il n'est pas atteignable par
  rôle + nom, seul `data-test=error-button` fonctionne.
- **Le lien panier n'a ni `id` ni `href`** : c'est un `a.shopping_cart_link`
  sans attribut `href`, donc non exposé comme lien navigable ; seule l'ancre
  `data-test=shopping-cart-link` est fiable.
- **Textes d'erreur = ancre faible mais discriminante** : tous les messages
  partagent `data-test=error`. Le libellé (préfixé `Epic sadface:`) est le seul
  moyen de distinguer « identifiants incorrects », « champ obligatoire » et
  « accès sans session ». On l'utilise donc en assertion **complémentaire** de
  l'ancre, en gardant à l'esprit que ce texte est la surface la plus fragile du
  plan (candidat n°1 à une future entrée de `docs/heal-journal.md`).
- **Garde de session par redirection** : un accès direct à `/inventory.html`
  hors session renvoie un HTTP `404` puis redirige vers `/` avec un
  `data-test=error`. Ne pas construire de test sur un deep link supposé
  fonctionnel.
- **Pas de persistance serveur** : le panier vit dans la session navigateur.
  L'étape de retrait suffit à restaurer l'état initial ; en filet de sécurité,
  le menu latéral expose `id=reset_sidebar_link` (`Reset App State`).
- **Identifiants** : jamais en dur dans la suite ni dans `variables/`,
  `${SAUCE_USER}` / `${SAUCE_PASSWORD}` en variables de ligne de commande
  typées `Secret:` (convention #6). Les identifiants de démonstration sont
  affichés sur la page de connexion, ce qui ne change rien à cette règle.

## Écarts constatés à la génération

Génération du 2026-07-24 (rf-generator, rf-mcp + Browser 20.0.0, Robot
Framework 7.4.2). **Aucun fait métier du plan n'a été contredit** : toutes les
ancres, tous les textes et tous les comportements décrits ci-dessus ont été
rejoués live et confirmés. Les écarts ci-dessous sont d'ordre technique
(syntaxe / outillage) et n'ont pas modifié le sens des scénarios.

1. **Syntaxe des variables `Secret:` en ligne de commande.**
   *Ce que suppose le plan* : « variables de ligne de commande typées
   `Secret:` », sans syntaxe précise ; la consigne de génération proposait
   `-v "SAUCE_PASSWORD:Secret:<valeur>"`.
   *Observé* : Robot Framework 7.4.2 n'accepte le typage que sous la forme
   `NOM: <type>:<valeur>`, **avec une espace après le deux-points du nom**
   (`robot/variables/scopes.py`, motif `([^:]+): ([^:]+):(.*)`). Sans cette
   espace, la variable vaut la chaîne littérale `Secret:<valeur>` et
   `Fill Secret` la refuse (`Direct assignment of values or variables as
   'secret' is not allowed`).
   *Ce que fait la suite* : la ligne de commande documentée est
   `-v "SAUCE_PASSWORD: secret:<mot-de-passe>"` ; vérifié live, le mot de
   passe n'apparaît nulle part dans `results/output.xml`.

2. **Un `Secret` ne peut pas être fabriqué à partir d'un littéral.**
   *Observé* : `${X: secret}    valeur` dans une section `*** Variables ***`
   échoue (`Value must have type 'Secret', got string`) : par conception, un
   secret ne peut venir que de la ligne de commande ou d'un fichier de
   variables. Or `Fill Secret` refuse le texte brut.
   *Conséquence sur la couche resources* : deux primitives de saisie
   distinctes dans `saucedemo_login_page.resource` :
   `Saisir Les Identifiants` (`Fill Secret`, exige un `Secret`) pour la
   connexion nominale, et `Saisir Des Identifiants Volontairement Invalides`
   (`Fill Text`) pour le scénario 2, dont le mot de passe faux
   (`${MOT_DE_PASSE_INVALIDE}`) est une donnée de scénario et non un
   credential.

3. **Déconnexion depuis la page panier.**
   *Ce que dit le plan* : la déconnexion est décrite depuis `/inventory.html`.
   *Observé* : l'en-tête (burger `#react-burger-menu-btn`, menu latéral,
   icône panier) est identique sur `/cart.html`, et la déconnexion depuis la
   page panier ramène bien à l'URL de base avec un formulaire vidé.
   *Ce que fait la suite* : conformément à l'ordre des étapes du scénario 3,
   la déconnexion s'effectue depuis la page panier ; le vocabulaire d'en-tête
   vit donc dans `resources/common.resource` et non dans un page object.

4. **Ancrage des boutons d'ajout / de retrait.**
   Le plan recommandait déjà (§ Points de vigilance) d'éviter le slug. Sondé
   live : `[data-test="inventory-item"]:has([data-test="inventory-item-name"]:text-is("<nom>")) [data-test^="add-to-cart"]`
   sélectionne exactement 1 élément, y compris pour
   `Test.allTheThings() T-Shirt (Red)`. C'est cette construction (nom exact +
   préfixe d'ancre) qui est retenue dans les page objects, avec un
   localisateur distinct pour l'ajout et pour le retrait.
