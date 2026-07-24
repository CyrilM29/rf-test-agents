*** Settings ***
Documentation     Page object — page panier Sauce Demo (/cart.html).
...               Localisateurs sondés live le 2026-07-24 (rf-mcp, Browser
...               chromium headless). Les URLs viennent de
...               variables/env_demo.yaml, importé par la suite.
Library           Browser
Library           String


*** Variables ***
${SD_CART_TITLE}                css=[data-test="title"]
${SD_CART_TITLE_TEXT}           Your Cart
${SD_CART_LIST}                 css=[data-test="cart-list"]
# data-test=inventory-item est le MEME attribut que sur la page inventaire :
# le comptage des lignes est qualifie par le conteneur cart-list.
${SD_CART_ROWS}                 css=[data-test="cart-list"] [data-test="inventory-item"]
${SD_CART_ROW_TEMPLATE}
...    css=[data-test="cart-list"] [data-test="inventory-item"]:has([data-test="inventory-item-name"]:text-is("{nom}"))
${SD_CART_QUANTITY_IN_ROW}      [data-test="item-quantity"]
${SD_CART_PRICE_IN_ROW}         [data-test="inventory-item-price"]
${SD_CART_REMOVE_IN_ROW}        [data-test^="remove"]
${SD_CART_TIMEOUT}              10s
${SD_CART_SHORT_TIMEOUT}        5s


*** Keywords ***
Localisateur De La Ligne De Panier
    [Documentation]    Ligne de panier de l'article portant ce nom exact.
    [Arguments]    ${nom_article}
    ${selecteur}=    Format String    ${SD_CART_ROW_TEMPLATE}    nom=${nom_article}
    RETURN    ${selecteur}

Localisateur Dans La Ligne De Panier
    [Documentation]    Descendant d'une ligne de panier (quantité, prix, retrait).
    [Arguments]    ${nom_article}    ${suffixe}
    ${ligne}=    Localisateur De La Ligne De Panier    ${nom_article}
    ${selecteur}=    Catenate    SEPARATOR=${SPACE}    ${ligne}    ${suffixe}
    RETURN    ${selecteur}

Attendre La Liste Du Panier
    [Documentation]    Synchronisation sur l'affichage de la liste du panier.
    Wait For Elements State    ${SD_CART_LIST}    visible    timeout=${SD_CART_TIMEOUT}

La Page Panier Doit Être Affichée
    [Documentation]    URL, titre de section et liste de /cart.html.
    Attendre La Liste Du Panier
    Get Url    ==    ${CART_URL}
    Get Text    ${SD_CART_TITLE}    ==    ${SD_CART_TITLE_TEXT}

Le Nombre De Lignes Du Panier Doit Être
    [Documentation]    Comptage des lignes, qualifié par le conteneur cart-list.
    [Arguments]    ${nombre_attendu}
    Get Element Count    ${SD_CART_ROWS}    ==    ${nombre_attendu}

Le Panier Doit Contenir L'Article
    [Documentation]    Ligne présente pour cet article, avec quantité et prix.
    [Arguments]    ${nom_article}    ${quantite_attendue}    ${prix_attendu}
    ${ligne}=    Localisateur De La Ligne De Panier    ${nom_article}
    ${quantite}=    Localisateur Dans La Ligne De Panier    ${nom_article}    ${SD_CART_QUANTITY_IN_ROW}
    ${prix}=    Localisateur Dans La Ligne De Panier    ${nom_article}    ${SD_CART_PRICE_IN_ROW}
    Wait For Elements State    ${ligne}    visible    timeout=${SD_CART_SHORT_TIMEOUT}
    Get Text    ${quantite}    ==    ${quantite_attendue}
    Get Text    ${prix}    ==    ${prix_attendu}

Retirer L'Article Du Panier
    [Documentation]    Retire l'article ; se synchronise sur la disparition de
    ...    la ligne (detached, pas seulement masquée).
    [Arguments]    ${nom_article}
    ${ligne}=    Localisateur De La Ligne De Panier    ${nom_article}
    ${bouton_retrait}=    Localisateur Dans La Ligne De Panier    ${nom_article}    ${SD_CART_REMOVE_IN_ROW}
    Click    ${bouton_retrait}
    Wait For Elements State    ${ligne}    detached    timeout=${SD_CART_SHORT_TIMEOUT}
