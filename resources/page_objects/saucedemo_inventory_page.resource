*** Settings ***
Documentation     Page object : page inventaire Sauce Demo (/inventory.html).
...               Localisateurs sondés live le 2026-07-24 (rf-mcp, Browser
...               chromium headless). Les URLs viennent de
...               variables/env_demo.yaml, importé par la suite.
Library           Browser
Library           String


*** Variables ***
# Conteneur de la liste produits : ancre data-test, PAS l'id, sonde live du
# 2026-07-24, #inventory_container matche 2 elements (un div vide sans classe
# ni data-test + le vrai conteneur), tandis que
# [data-test="inventory-container"] en matche exactement 1.
${SD_INVENTORY_CONTAINER}       css=[data-test="inventory-container"]
${SD_INVENTORY_TITLE}           css=[data-test="title"]
${SD_INVENTORY_TITLE_TEXT}      Products
# data-test=inventory-item est REUTILISE sur la page panier : le comptage est
# donc toujours qualifie par le conteneur inventory-container.
${SD_INVENTORY_ITEMS}           css=[data-test="inventory-container"] [data-test="inventory-item"]
# Fiche produit ancree par le NOM de l'article (text-is = egalite exacte)
# plutot que par le slug du bouton : le slug est piegeux
# (Test.allTheThings() T-Shirt (Red) -> add-to-cart-test.allthethings()-t-shirt-(red)).
${SD_INVENTORY_CARD_TEMPLATE}
...    css=[data-test="inventory-container"] [data-test="inventory-item"]:has([data-test="inventory-item-name"]:text-is("{nom}"))
# Le bouton MUTE apres ajout : l'ancre add-to-cart-<slug> devient
# remove-<slug>. Deux localisateurs distincts, jamais interchangeables.
${SD_ADD_BUTTON_IN_CARD}        [data-test^="add-to-cart"]
${SD_REMOVE_BUTTON_IN_CARD}     [data-test^="remove"]
${SD_INVENTORY_TIMEOUT}         10s
${SD_INVENTORY_SHORT_TIMEOUT}   5s


*** Keywords ***
Localisateur De La Fiche Produit
    [Documentation]    Localisateur de la fiche du produit portant ce nom exact.
    [Arguments]    ${nom_article}
    ${selecteur}=    Format String    ${SD_INVENTORY_CARD_TEMPLATE}    nom=${nom_article}
    RETURN    ${selecteur}

Localisateur Du Bouton D'Ajout
    [Documentation]    Bouton « Add to cart » de la fiche produit (état initial).
    [Arguments]    ${nom_article}
    ${carte}=    Localisateur De La Fiche Produit    ${nom_article}
    ${selecteur}=    Catenate    SEPARATOR=${SPACE}    ${carte}    ${SD_ADD_BUTTON_IN_CARD}
    RETURN    ${selecteur}

Localisateur Du Bouton De Retrait
    [Documentation]    Bouton « Remove » de la fiche produit (après ajout).
    [Arguments]    ${nom_article}
    ${carte}=    Localisateur De La Fiche Produit    ${nom_article}
    ${selecteur}=    Catenate    SEPARATOR=${SPACE}    ${carte}    ${SD_REMOVE_BUTTON_IN_CARD}
    RETURN    ${selecteur}

Attendre La Liste Produits
    [Documentation]    Synchronisation sur l'affichage de la liste produits.
    Wait For Elements State    ${SD_INVENTORY_CONTAINER}    visible    timeout=${SD_INVENTORY_TIMEOUT}

La Page Inventaire Doit Être Affichée
    [Documentation]    URL, titre de section et liste produits de /inventory.html.
    Attendre La Liste Produits
    Get Url    ==    ${INVENTORY_URL}
    Get Text    ${SD_INVENTORY_TITLE}    ==    ${SD_INVENTORY_TITLE_TEXT}

Le Nombre De Produits Affichés Doit Être
    [Documentation]    Comptage des fiches produit, qualifié par le conteneur.
    [Arguments]    ${nombre_attendu}
    Get Element Count    ${SD_INVENTORY_ITEMS}    ==    ${nombre_attendu}

Ajouter L'Article Au Panier
    [Documentation]    Ajoute l'article depuis la liste produits ; se synchronise
    ...    sur la mutation de l'ancre du bouton (add-to-cart -> remove).
    [Arguments]    ${nom_article}
    ${bouton_ajout}=    Localisateur Du Bouton D'Ajout    ${nom_article}
    ${bouton_retrait}=    Localisateur Du Bouton De Retrait    ${nom_article}
    Click    ${bouton_ajout}
    Wait For Elements State    ${bouton_retrait}    visible    timeout=${SD_INVENTORY_SHORT_TIMEOUT}

L'Article Doit Être Retirable Depuis La Liste Produits
    [Documentation]    La fiche propose le retrait et n'expose plus l'ajout.
    [Arguments]    ${nom_article}
    ${bouton_ajout}=    Localisateur Du Bouton D'Ajout    ${nom_article}
    ${bouton_retrait}=    Localisateur Du Bouton De Retrait    ${nom_article}
    Wait For Elements State    ${bouton_retrait}    visible    timeout=${SD_INVENTORY_SHORT_TIMEOUT}
    Get Element Count    ${bouton_ajout}    ==    ${0}
