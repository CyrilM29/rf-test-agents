---
name: rejeu-et-defaut-connu-jamais-sur-un-texte
description: >-
  2026-09-23, décision de méthode : un rejeu n'est admissible que DÉCLARÉ pour
  une classe transitoire mesurée, sur une étape de lecture, jamais une
  écriture ; un défaut connu se reconnaît à son identité technique, jamais à un
  motif de texte, et l'échec reste rouge
type: projet
date: 2026-09-23
---

Deux pratiques répandues dans les frameworks d'automatisation ont été étudiées
le 2026-09-23 : rejouer un test en échec selon des « politiques », et déclasser
en avertissement une erreur « connue ». Les deux se reconnaissaient à un motif
cherché dans le texte de l'exception. L'idée est retenue (lot 1 de
`comms/backlog-produit.md`, local), la forme est refusée.

**Pourquoi :** un motif de texte dépend de la langue et de la formulation du
message, il cesse de correspondre en silence ou correspond à un autre défaut ;
déclasser un échec sur un motif fait un rapport vert sur un système rouge ; et
rejouer une écriture peut la doubler, un timeout côté client n'étant pas une
non-écriture côté serveur (constaté dans une verticale : le rejeu a créé un
second enregistrement). Le contrat interdit déjà le rejeu jusqu'au vert : ce
qui est admis ici est une politique décidée AVANT le run, jamais par un agent
pendant une réparation.

**Comment appliquer :** une classe de rejeu = prédicat sur le type, le code ou
le statut, budget de deux rejeux, mesure qui la justifie ; étape idempotente
seulement ; un défaut connu = identité technique, cible, ticket, date
d'expiration, échec toujours rouge et classé à part. Le generator déclare, le
verifier refuse une classe sans preuve, une classe qui couvre une écriture, ou
un défaut connu sans expiration. Même règle pour le statut `pending` : déclaré
à la génération avec sa condition de levée, jamais ajouté pendant une
réparation.
