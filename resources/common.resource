*** Settings ***
Documentation     Cross-page business vocabulary — global Setup/Teardown
...               wrappers and keywords shared by several pages/screens.
...               Page-scoped keywords and locators belong to
...               resources/page_objects/<page>.resource, never here.
...               Populated by rf-generator as suites are generated; repaired
...               by rf-healer. Locators live in this layer, never in tests.
...
...               Sauce Demo (canal web) : ouverture/fermeture du navigateur,
...               connexion, déconnexion et en-tête partagé (menu latéral,
...               icône panier) — l'en-tête est commun à /inventory.html et
...               /cart.html, il n'appartient donc à aucun page object.
...               Ancres sondées live le 2026-07-24 (rf-mcp, Browser chromium
...               headless). Données d'environnement : variables/env_demo.yaml.
Library           Browser
Resource          page_objects/saucedemo_login_page.resource
Resource          page_objects/saucedemo_inventory_page.resource
Resource          page_objects/saucedemo_cart_page.resource


*** Variables ***
# En-tete partage (id stables cote React pour le menu, data-test pour le panier ;
# le lien panier n'a ni id ni href, seul data-test est fiable).
${SD_BURGER_BUTTON}             css=#react-burger-menu-btn
${SD_LOGOUT_LINK}               css=#logout_sidebar_link
${SD_CART_LINK}                 css=[data-test="shopping-cart-link"]
# Badge panier : ABSENT du DOM quand le panier est vide (ce n'est pas un « 0 »).
${SD_CART_BADGE}                css=[data-test="shopping-cart-badge"]
${SD_VIEWPORT}                  {'width': 1280, 'height': 900}
${SD_HEADER_TIMEOUT}            10s
${SD_HEADER_SHORT_TIMEOUT}      5s


*** Keywords ***
Ouvrir Le Navigateur Sauce Demo
    [Documentation]    Suite Setup : démarre le navigateur (chromium headless).
    New Browser    ${BROWSER}    headless=${HEADLESS}

Fermer Le Navigateur Sauce Demo
    [Documentation]    Suite Teardown : ferme tous les navigateurs ouverts.
    Close Browser    ALL

Ouvrir La Boutique Sauce Demo
    [Documentation]    Test Setup : contexte navigateur neuf (donc panier vide,
    ...    l'état panier vivant dans la session navigateur) puis page de
    ...    connexion sur l'URL de base.
    New Context    viewport=${SD_VIEWPORT}
    New Page    ${BASE_URL}
    La Page De Connexion Doit Être Affichée

Fermer La Session Navigateur
    [Documentation]    Test Teardown : ferme le contexte (et sa session).
    Close Context    CURRENT

Se Connecter Avec
    [Documentation]    Connexion nominale : le mot de passe doit être une
    ...    variable typée `Secret:`. Se synchronise sur la liste produits.
    [Arguments]    ${identifiant}    ${mot_de_passe}
    Saisir Les Identifiants    ${identifiant}    ${mot_de_passe}
    Valider La Connexion
    Attendre La Liste Produits

Tenter Une Connexion Avec
    [Documentation]    Tentative de connexion vouée à l'échec : aucune attente de
    ...    navigation, l'application reste sur la page de connexion.
    [Arguments]    ${identifiant}    ${mot_de_passe}
    Saisir Des Identifiants Volontairement Invalides    ${identifiant}    ${mot_de_passe}
    Valider La Connexion

Ouvrir Le Menu Latéral
    [Documentation]    Le panneau latéral existe dans le DOM même fermé
    ...    (0 × 0 px, aria-hidden) : il faut ouvrir le burger avant tout clic.
    Click    ${SD_BURGER_BUTTON}
    Wait For Elements State    ${SD_LOGOUT_LINK}    visible    timeout=${SD_HEADER_SHORT_TIMEOUT}

Se Déconnecter
    [Documentation]    Déconnexion via le menu latéral ; retour au formulaire.
    Ouvrir Le Menu Latéral
    Click    ${SD_LOGOUT_LINK}
    Wait For Elements State    ${SD_LOGIN_BUTTON}    visible    timeout=${SD_HEADER_TIMEOUT}

Ouvrir Le Panier
    [Documentation]    Ouvre le panier via l'icône de l'en-tête.
    Click    ${SD_CART_LINK}
    Attendre La Liste Du Panier

Le Badge Du Panier Doit Indiquer
    [Documentation]    Badge présent avec le nombre d'articles attendu.
    [Arguments]    ${nombre_attendu}
    Wait For Elements State    ${SD_CART_BADGE}    visible    timeout=${SD_HEADER_SHORT_TIMEOUT}
    Get Text    ${SD_CART_BADGE}    ==    ${nombre_attendu}

Le Panier Doit Être Vide
    [Documentation]    Panier vide = badge ABSENT du DOM, jamais un texte « 0 ».
    Wait For Elements State    ${SD_CART_BADGE}    detached    timeout=${SD_HEADER_SHORT_TIMEOUT}
    Get Element Count    ${SD_CART_BADGE}    ==    ${0}
