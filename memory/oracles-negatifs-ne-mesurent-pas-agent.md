---
name: oracles-negatifs-ne-mesurent-pas-agent
description: Un verdict calcule sur des faits fournis ne prouve pas le jugement du modele
type: projet
date: 2026-09-06
---

Un catalogue negatif execute contre une fonction de verdict valide l'oracle,
pas la capacite du modele a reconnaitre le cas dans des preuves.

**Pourquoi :** en passant directement `target_matches=false`, le test fournit
deja le diagnostic que l'agent est cense etablir. Annoncer un taux de refus
corrects du modele depuis ces tests serait une evaluation circulaire.

**Comment appliquer :** garder les deux mesures distinctes. Pour evaluer l'agent,
donner la fixture et l'invariant sans son verdict attendu, conserver toutes les
tentatives et faire verifier les preuves independamment. Les tests hors ligne
restent utiles pour empecher un oracle d'accepter un skip comme reparation.