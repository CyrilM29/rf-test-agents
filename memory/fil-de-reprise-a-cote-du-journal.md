---
name: fil-de-reprise-a-cote-du-journal
description: >-
  2026-09-26, décision de méthode : la règle « consigner au fil de l'eau pour
  qu'un autre agent reprenne » est tenue par un fil d'entrées immuables À CÔTÉ
  du journal de reprise, et la reprise fusionne les verdicts du journal : un
  fil ne rejoue rien, ne restaure aucune session, n'accorde aucune permission
type: projet
date: 2026-09-26
---

L'utilisateur a posé le 2026-09-26 une règle pour toute la famille (SAPFX,
ODOOFX, les agents universels, l'écosystème Playwright) : un agent consigne ses
relevés, découvertes et avancement au fur et à mesure, pour qu'un autre agent
reprenne après un redémarrage de serveur, un timeout ou un crash, sans perte.
Écrite telle quelle (« reprendre exactement là où il s'est arrêté »), elle
contredisait la section Recovery du contrat, qui interdit le rejeu automatique
et la restauration d'une session depuis un point de reprise.

Décision : un **fil de reprise** (`scripts/agent_handover.py`) qui complète le
journal au lieu de le doubler. Le journal trace les écritures métier (jalons
planned, sent, confirmed) ; le fil trace le reste (vu, fait, décidé, demandé,
prochain geste). `resume` lit les deux, et une écriture `sent` sans
confirmation force toujours la réconciliation en lecture seule.

**Pourquoi une entrée par fichier et pas un fichier d'état unique :** le
planner, l'agent des missions les plus longues (une exploration a coûté 389
appels en une heure vingt dans une verticale), n'a pas de shell. Avec un seul
fichier, il devrait le relire puis le réécrire en entier à chaque ajout, et une
réécriture ratée efface tout le passé en silence. Créer le fichier suivant avec
Write ne touche jamais une entrée existante, et l'hôte refuse d'écraser un
fichier non lu. Un fichier d'état à la racine (`.agent_state.md`) aurait en
plus été vu par `git status` et aurait bloqué l'export public d'une verticale ;
le fil vit sous `results/`, ignoré partout.

**Comment appliquer :** première entrée `mission` (cible, mode, invariant),
puis une entrée par relevé, décision ou étape, au plus tard toutes les dix
actions, et une entrée `next` AVANT un geste long ou risqué. Reprendre, c'est
lire `resume`, rouvrir les sessions (identifiants en ligne de commande, jamais
depuis le fil), prouver la cible, re-percevoir, puis continuer dans
l'autorisation et le budget d'origine. Un fil incohérent (trou, entrée
modifiée, fichier étranger, verrou restant) arrête la reprise : on ne le
renumérote, ne le répare et ne le déverrouille jamais automatiquement. Le
filtre de secrets est un filet, pas une preuve. Ce qui n'a pas été écrit est
perdu : le « zéro perte » se tient en écrivant souvent.
