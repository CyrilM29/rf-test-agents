---
description: Activer, désactiver ou consulter le mode autonome du hook de permissions (politique locale du poste)
---

Le propriétaire du poste demande de régler la politique locale du hook
`PreToolUse` de ce dépôt. Argument attendu : `on`, `off` ou `status` (sans
argument : `status`), tapé après `/autonomie` : ${input:action:status}

Lance exactement `python scripts/agent_policy.py <argument>` dans le terminal,
à la racine du dépôt, puis rapporte sa sortie en une ou deux lignes, en
français.

Pour `on` et `off`, le hook de permissions demande au propriétaire de
confirmer le lancement : c'est voulu, seul un humain change les règles
d'approbation. Ne jamais relancer, reformuler ni contourner cette
confirmation.

Cette commande est la demande explicite du propriétaire. Ne lance jamais
`scripts/agent_policy.py on` de ta propre initiative, depuis une autre
commande ou pour passer une confirmation : le contrat d'agent
(`.claude/agent-contract.md`) interdit de changer les règles d'approbation pour
contourner un refus.
