# Consultation des pages publiques AI Cabra

- **Canal** : web (Browser / Playwright)
- **Système / URL** : site vitrine public https://www.aicabra.com/ (pages
  statiques `.html`, pas d'authentification).
- **Préconditions** : aucune. Site public, consultation en lecture seule,
  aucun formulaire soumis, aucune donnée envoyée. Navigateur `chromium`
  (validé en `headless=True`).

## Données observées

Faits relevés en direct via rf-mcp (Browser chromium headless, ARIA snapshots
`get_session_state`) le 2026-08-15.

### Navigation principale (identique sur toutes les pages consultées)

- Ancre stable : `navigation` avec nom accessible « Navigation principale »
  (attribut `aria-label="Navigation principale"`, dans le `banner`).
- Liens de menu, tous en `role=link`, ancrables par nom accessible exact :
  | Nom accessible | `/url` (href) |
  |----------------|---------------|
  | `Accueil`   | `index.html`     |
  | `SAPFX`     | `sapfx.html`     |
  | `CabrIA`    | `cabria.html`    |
  | `CabraFlow` | `cabraflow.html` |
  | `FAQ`       | `faq.html`       |
  | `Glossaire` | `glossaire.html` |
  | `EN`        | version anglaise de la page courante (href variable : `index-en.html` sur l'accueil, `sapfx-en.html` sur SAPFX, `faq-en.html` sur la FAQ) |
- Le logo est aussi un lien vers l'accueil : nom accessible
  « Logo AI Cabra AI Cabra », `/url: index.html`.

### Page d'accueil

- URL au chargement direct : `https://www.aicabra.com/` (la barre d'adresse
  reste `/` ; après un retour par un lien interne, elle devient
  `https://www.aicabra.com/index.html` : même page, deux formes d'URL).
- Titre onglet : `AI Cabra - IA pour la QA et tests logiciels automatisés`.
- Contenu principal : `heading [level=1]` de nom accessible
  « L'intelligence artificielle au service de votre QA » (unique `h1` de la
  page). Sections repères en `heading [level=2]` : « Nos programmes »,
  « Programme pilote », « Ce qui tourne déjà », « Notre expertise »,
  « Notre façon de travailler », « Sécurité et conformité »,
  « Parlons de votre chaîne de tests ».

### Page SAPFX (cible de menu)

- URL après clic sur le lien de menu `SAPFX` : `https://www.aicabra.com/sapfx.html`.
- Titre onglet : `SAPFX : tests SAP automatisés open source (SAP GUI, Fiori, API) | AI Cabra`.
- Contenu principal : `heading [level=1]` « SAPFX » (unique `h1`). Section
  repère distinctive : `heading [level=2]` « L'essentiel ».
- Pied de page (`contentinfo`) : lien `role=link` « ← Retour à l'accueil »,
  `/url: index.html`.

### Page FAQ (cible de menu alternative)

- URL après clic sur le lien de menu `FAQ` : `https://www.aicabra.com/faq.html`.
- Titre onglet : `FAQ : AI Cabra, SAPFX, CabrIA et CabraFlow | AI Cabra`.
- Contenu principal : `heading [level=1]` « Questions fréquentes » (unique
  `h1`). Sections repères en `heading [level=2]` : « AI Cabra », « SAPFX »,
  « CabrIA », « CabraFlow ». Le corps est une liste de questions en
  `heading [level=3]`.
- Pied de page (`contentinfo`) : lien « ← Retour à l'accueil », `/url: index.html`.

### Retour à l'accueil (deux chemins observés, tous deux validés live)

- Via le menu : clic sur le lien `Accueil` → `https://www.aicabra.com/index.html`,
  `h1` redevenu « L'intelligence artificielle au service de votre QA ».
- Via le pied de page : clic sur « ← Retour à l'accueil » → même URL, même `h1`.

## Scénarios

### 1. Consultation d'une page du menu depuis l'accueil (SAPFX)

- **Étapes** :
  1. Ouvrir le site sur la page d'accueil (`https://www.aicabra.com/`).
  2. Vérifier que l'accueil est bien chargé (contenu principal présent).
  3. Depuis la navigation principale, aller sur la page « SAPFX ».
  4. Lire le contenu principal de la page SAPFX.
  5. Revenir à l'accueil depuis la page SAPFX.
- **Résultat attendu** :
  - Après (2) : titre onglet exactement
    `AI Cabra - IA pour la QA et tests logiciels automatisés`, et le
    `heading [level=1]` « L'intelligence artificielle au service de votre QA »
    est visible.
  - Après (3)/(4) : URL `https://www.aicabra.com/sapfx.html`, titre onglet
    `SAPFX : tests SAP automatisés open source (SAP GUI, Fiori, API) | AI Cabra`,
    `heading [level=1]` « SAPFX » visible, et la section repère
    `heading [level=2]` « L'essentiel » présente (preuve que le contenu
    principal, pas seulement l'en-tête, est bien rendu).
  - Après (5) : URL `https://www.aicabra.com/index.html` et `heading [level=1]`
    de l'accueil de nouveau visible.

### 2. Consultation d'une seconde page du menu (FAQ)

- **Étapes** :
  1. Ouvrir le site sur la page d'accueil.
  2. Vérifier que l'accueil est chargé.
  3. Depuis la navigation principale, aller sur la page « FAQ ».
  4. Lire le contenu principal de la page FAQ.
  5. Revenir à l'accueil depuis la page FAQ.
- **Résultat attendu** :
  - Après (3)/(4) : URL `https://www.aicabra.com/faq.html`, titre onglet
    `FAQ : AI Cabra, SAPFX, CabrIA et CabraFlow | AI Cabra`,
    `heading [level=1]` « Questions fréquentes » visible, et au moins une
    section repère `heading [level=2]` (« AI Cabra » ou « SAPFX ») présente.
  - Après (5) : retour sur `https://www.aicabra.com/index.html`, `heading
    [level=1]` de l'accueil de nouveau visible.

> Note pour le generator : le scénario 2 rejoue la même mécanique que le 1 sur
> une autre cible de menu ; un keyword métier paramétré par (nom de menu, URL
> attendue, titre attendu, texte du `h1` attendu) évite la duplication.

## Points de vigilance

- **Deux formes d'URL pour l'accueil** : `https://www.aicabra.com/` au
  chargement direct, mais `https://www.aicabra.com/index.html` après un retour
  par lien interne. Toute assertion sur l'URL de l'accueil après un retour doit
  viser `.../index.html` (ou tester le suffixe), pas la racine nue.
- **Deux chemins de retour** existent (lien menu « Accueil » et lien pied de
  page « ← Retour à l'accueil »), tous deux validés live vers `index.html`.
  Ancrer le retour sur le lien de menu « Accueil » (présent et identique sur
  toutes les pages) est le choix le plus stable ; le lien de pied de page est
  un repli documenté.
- **Ancrage recommandé** : cibler les liens de menu par rôle + nom accessible
  sous le conteneur `nav[aria-label="Navigation principale"]` (échelle
  rôle + nom accessible), et le contenu principal par `heading level=1` +
  nom accessible. Éviter d'ancrer sur le lien de menu par position dans la
  liste. Aucun `data-testid` ni id technique n'a été observé sur ces ancres :
  l'échelle s'arrête ici à rôle + nom accessible (pas de repli id disponible),
  ce qui reste robuste car les noms accessibles sont des libellés de menu
  stables.
- **Lien « EN »** : son href change selon la page courante (variante `-en` de
  la page). Non couvert par ces scénarios (consultation FR uniquement), à noter
  si une extension multilingue est demandée.
- **Titres localisés** : les titres d'onglet et les `h1` cités sont en
  français et servent d'assertions ; ce sont les seuls textes affichés retenus,
  faute d'id technique sur ces pages statiques. Si le site devient multilingue
  par défaut, ces assertions devront basculer sur la variante servie.
- **Chargement** : les pages sont statiques et se chargent en < 1 s en direct ;
  s'appuyer sur l'auto-wait de Browser + `Wait For Elements State` sur le `h1`
  cible, jamais sur une pause fixe.

## Mots-clés métier manquants (à créer par le rf-generator)

Aucune ressource métier existante pour ce site (`resources/` ne contient que
des page objects saucedemo). À créer :

- `Ouvrir L'accueil AI Cabra` : ouvre le navigateur et la page
  `https://www.aicabra.com/`, attend le `h1` de l'accueil, vérifie le titre
  d'onglet de l'accueil.
- `Aller Sur La Page Du Menu` (paramétré : nom accessible du lien de menu) :
  clique le lien correspondant sous `nav[aria-label="Navigation principale"]`.
- `Vérifier Le Contenu Principal` (paramétré : texte attendu du `h1`, URL
  attendue, titre d'onglet attendu, éventuellement un `h2` repère) : assertions
  sur le contenu principal de la page cible.
- `Revenir À L'accueil` : clique le lien de menu « Accueil », attend le `h1`
  de l'accueil et vérifie l'URL `.../index.html`.

Ces keywords vivront dans un nouveau page object (ex.
`resources/page_objects/aicabra_public_site.resource`), avec les localisateurs
(conteneur de navigation, liens de menu par rôle + nom, `h1`) en tête de
fichier, conformément à la convention #1.
