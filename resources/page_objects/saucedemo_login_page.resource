*** Settings ***
Documentation     Page object — page de connexion Sauce Demo (URL de base).
...               Localisateurs sondés live le 2026-07-24 (rf-mcp, Browser
...               chromium headless). Les URLs viennent de
...               variables/env_demo.yaml, importé par la suite.
Library           Browser


*** Variables ***
# Ancres stables : attribut data-test (present sur tous les champs du
# formulaire), jamais un id genere ni un XPath positionnel.
${SD_LOGIN_USERNAME}            css=[data-test="username"]
${SD_LOGIN_PASSWORD}            css=[data-test="password"]
${SD_LOGIN_BUTTON}              css=[data-test="login-button"]
# Le bandeau d'erreur est un h3 data-test=error, retire du DOM (detached)
# quand on le ferme ; son bouton de fermeture n'a AUCUN nom accessible,
# seul data-test=error-button est exploitable.
${SD_LOGIN_ERROR}               css=[data-test="error"]
${SD_LOGIN_ERROR_CLOSE}         css=[data-test="error-button"]
${SD_LOGIN_TIMEOUT}             10s
${SD_LOGIN_SHORT_TIMEOUT}       5s


*** Keywords ***
La Page De Connexion Doit Être Affichée
    [Documentation]    Formulaire de connexion visible et URL de base courante.
    Wait For Elements State    ${SD_LOGIN_USERNAME}    visible    timeout=${SD_LOGIN_TIMEOUT}
    Wait For Elements State    ${SD_LOGIN_PASSWORD}    visible    timeout=${SD_LOGIN_TIMEOUT}
    Wait For Elements State    ${SD_LOGIN_BUTTON}    visible    timeout=${SD_LOGIN_TIMEOUT}
    Get Url    ==    ${BASE_URL}

Saisir Les Identifiants
    [Documentation]    Saisit l'identifiant et le mot de passe ; le mot de passe
    ...    DOIT être une variable typée `Secret:` (Fill Secret refuse le texte
    ...    brut, ce qui garantit le non-log du secret).
    [Arguments]    ${identifiant}    ${mot_de_passe}
    Fill Text    ${SD_LOGIN_USERNAME}    ${identifiant}
    Fill Secret    ${SD_LOGIN_PASSWORD}    ${mot_de_passe}

Saisir Des Identifiants Volontairement Invalides
    [Documentation]    Variante pour les scénarios d'échec : la valeur passée
    ...    n'est pas un secret (mot de passe faux assumé), donc Fill Text.
    [Arguments]    ${identifiant}    ${mot_de_passe}
    Fill Text    ${SD_LOGIN_USERNAME}    ${identifiant}
    Fill Text    ${SD_LOGIN_PASSWORD}    ${mot_de_passe}

Valider La Connexion
    [Documentation]    Soumet le formulaire de connexion.
    Click    ${SD_LOGIN_BUTTON}

Un Message D'Erreur De Connexion Doit Être Affiché
    [Documentation]    Ancre data-test=error + message attendu : l'ancre seule ne
    ...    discrimine pas la cause de l'échec, le texte est donc nécessaire.
    [Arguments]    ${message_attendu}
    Wait For Elements State    ${SD_LOGIN_ERROR}    visible    timeout=${SD_LOGIN_SHORT_TIMEOUT}
    Get Text    ${SD_LOGIN_ERROR}    ==    ${message_attendu}

Aucun Message D'Erreur De Connexion Ne Doit Être Affiché
    [Documentation]    Le bandeau est absent du DOM (pas seulement masqué).
    Get Element Count    ${SD_LOGIN_ERROR}    ==    ${0}

Fermer Le Message D'Erreur De Connexion
    [Documentation]    Clic sur la croix ; le bandeau est détaché du DOM.
    Click    ${SD_LOGIN_ERROR_CLOSE}
    Wait For Elements State    ${SD_LOGIN_ERROR}    detached    timeout=${SD_LOGIN_SHORT_TIMEOUT}

L'Identifiant Saisi Doit Être Conservé
    [Documentation]    Après fermeture de l'erreur, le formulaire reste rempli.
    [Arguments]    ${identifiant_attendu}
    Get Property    ${SD_LOGIN_USERNAME}    value    ==    ${identifiant_attendu}

Les Champs De Connexion Doivent Être Vides
    [Documentation]    Après déconnexion, le formulaire est réinitialisé.
    Get Property    ${SD_LOGIN_USERNAME}    value    ==    ${EMPTY}
