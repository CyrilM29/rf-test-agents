*** Settings ***
Documentation     Sauce Demo : connexion et ajout au panier (canal web).
...                 Spec: specs/saucedemo-connexion-panier.md (sha256:e81fe483f892, 2026-08-04)
...               Browser / Playwright, chromium headless.
...               Generated from specs/saucedemo-connexion-panier.md by
...               rf-generator : re-run the generator rather than hand-editing
...               locators here.
...               Exécution (mot de passe typé Secret: sur la ligne de
...               commande, jamais dans un fichier : convention #6 ; noter
...               l'espace après « SAUCE_PASSWORD: », exigé par la syntaxe de
...               typage des variables -v de Robot Framework 7.4) :
...               robot --outputdir results -v "SAUCE_USER:standard_user"
...               -v "SAUCE_PASSWORD: secret:<mot-de-passe>"
...               tests/robot/ui/web/saucedemo_connexion_panier.robot
Resource          ../../../../resources/common.resource
Resource          ../../../../resources/page_objects/saucedemo_login_page.resource
Resource          ../../../../resources/page_objects/saucedemo_inventory_page.resource
Resource          ../../../../resources/page_objects/saucedemo_cart_page.resource
Variables         ../../../../variables/env_demo.yaml
Suite Setup       Ouvrir Le Navigateur Sauce Demo
Suite Teardown    Fermer Le Navigateur Sauce Demo
Test Setup        Ouvrir La Boutique Sauce Demo
Test Teardown     Fermer La Session Navigateur
Test Tags         saucedemo    web


*** Variables ***
# Mot de passe volontairement faux : donnée de scénario, pas un credential.
${MOT_DE_PASSE_INVALIDE}        mot-de-passe-invalide
# Le libellé est ici discriminant : l'ancre data-test=error est partagée par
# tous les cas d'échec (identifiants faux, champ obligatoire, accès sans
# session). Surface la plus fragile de la suite (cf. § Points de vigilance).
${MESSAGE_ERREUR_IDENTIFIANTS}
...    Epic sadface: Username and password do not match any user in this service


*** Test Cases ***
Connexion Réussie Avec Des Identifiants Valides
    [Documentation]    Scénario 1 du plan : connexion avec les identifiants
    ...    valides ${SAUCE_USER} / ${SAUCE_PASSWORD} (variables de ligne de
    ...    commande, mot de passe typé Secret:).
    [Tags]    connexion
    La Page De Connexion Doit Être Affichée
    Se Connecter Avec    ${SAUCE_USER}    ${SAUCE_PASSWORD}
    La Page Inventaire Doit Être Affichée
    Le Nombre De Produits Affichés Doit Être    ${NOMBRE_PRODUITS_ATTENDU}
    Aucun Message D'Erreur De Connexion Ne Doit Être Affiché
    Le Panier Doit Être Vide

Connexion Refusée Avec Un Mot De Passe Erroné
    [Documentation]    Scénario 2 du plan : identifiant valide + mot de passe
    ...    erroné : aucune navigation, message d'erreur discriminant, puis
    ...    fermeture du bandeau sans perte de la saisie.
    [Tags]    connexion    negatif
    La Page De Connexion Doit Être Affichée
    Tenter Une Connexion Avec    ${SAUCE_USER}    ${MOT_DE_PASSE_INVALIDE}
    Un Message D'Erreur De Connexion Doit Être Affiché    ${MESSAGE_ERREUR_IDENTIFIANTS}
    La Page De Connexion Doit Être Affichée
    Fermer Le Message D'Erreur De Connexion
    Aucun Message D'Erreur De Connexion Ne Doit Être Affiché
    L'Identifiant Saisi Doit Être Conservé    ${SAUCE_USER}

Ajout D'Un Article Au Panier Et Vérification Du Badge Et Du Contenu
    [Documentation]    Scénario 3 du plan : ajout de ${ARTICLE_TESTE}, contrôle
    ...    du badge et du contenu du panier, réversibilité (retrait) puis
    ...    déconnexion par le menu latéral.
    [Tags]    panier
    Se Connecter Avec    ${SAUCE_USER}    ${SAUCE_PASSWORD}
    La Page Inventaire Doit Être Affichée
    Le Panier Doit Être Vide
    Ajouter L'Article Au Panier    ${ARTICLE_TESTE}
    Le Badge Du Panier Doit Indiquer    1
    L'Article Doit Être Retirable Depuis La Liste Produits    ${ARTICLE_TESTE}
    Ouvrir Le Panier
    La Page Panier Doit Être Affichée
    Le Nombre De Lignes Du Panier Doit Être    1
    Le Panier Doit Contenir L'Article    ${ARTICLE_TESTE}    1    ${PRIX_ARTICLE_TESTE}
    Retirer L'Article Du Panier    ${ARTICLE_TESTE}
    Le Panier Doit Être Vide
    Le Nombre De Lignes Du Panier Doit Être    0
    Se Déconnecter
    La Page De Connexion Doit Être Affichée
    Les Champs De Connexion Doivent Être Vides
