---
name: hook-copilot-cli-apply-patch-texte-brut
description: >-
  2026-10-03, le hook PreToolUse refusait toute écriture par patch sous la
  Copilot CLI (« Hook command failed with code 1 ») : l'hôte traduit l'appel
  au format Claude, renomme l'outil et passe le texte brut du patch en
  `tool_input` ; le patch se reconnaît à son enveloppe, pas à son nom ; et un
  hook en `.*` se modifie en une seule écriture
type: projet
date: 2026-10-03
---

Sous la Copilot CLI (VS Code, sessions `copilotcli:`), chaque écriture par
`apply_patch` était refusée : « Denied by preToolUse hook from "repo settings"
(hook errored) », cause affichée « Hook command failed with code 1 ». Mesuré
sur une session réelle : 12 refus, tous des `apply_patch` dont l'entrée est le
texte brut du patch (appel « custom ») ; tous les autres outils passaient.

**Cause, établie en trois mesures :**

1. Le hook exigeait un objet en `tool_input` ; il refusait (« Missing tool name
   or structured arguments ») et sortait en code 2. L'hôte lance la commande par
   un shell qui ramène tout code non nul à 1 et ignore le JSON de stdout (reproduit
   avec `powershell -Command`) : le refus se lisait comme une panne.
2. Une fois la raison écrite sur stderr, l'hôte l'a affichée (« Stderr: ... »).
3. Une fois la FORME reçue ajoutée à cette raison : `tool_name` chaîne,
   `tool_input` chaîne, clés `cwd`, `hook_event_name`, `session_id`,
   `timestamp`, `tool_input`, `tool_name`. L'hôte traduit donc l'appel au format
   Claude ET renomme l'outil : un test sur `tool_name == "apply_patch"` ne
   l'attrapait pas. Le nom exact n'a pas été lu (la raison le nomme désormais).

Deux hypothèses écartées par la mesure, pas par le raisonnement : le chemin du
script (`CLAUDE_PROJECT_DIR`, le wrapper de cwd y fonctionnait) et un texte de
patch absent (`null`).

**Correctif** (`scripts/hook_agent_permissions.py`) : une chaîne brute est lue
comme `{"input": <patch>}` quand l'outil est `apply_patch` OU quand elle commence
par l'enveloppe `*** Begin Patch`, quel que soit le nom donné par l'hôte. Elle
suit la voie des objets : cibles du patch contrôlées contre les règles
d'approbation, `ask` sous `confirm`, lecture seule refusée. Toute autre chaîne
brute reste refusée (échec fermé). Un refus structurel écrit sur stderr la forme
reçue (types, clés, nom d'outil s'il est un identifiant court), jamais le
contenu. Contre-épreuve jouée : sans l'enveloppe, les noms réécrits retombent
en refus. Reporté le même jour à SAPFX, ODOOFX et RF_GenAI (Playwright_GenAI n'a
pas ce hook).

**How to apply:**

- Diagnostiquer par les événements `hook.start`/`hook.end` de la session hôte,
  puis faire dire au hook ce qu'il reçoit (forme, jamais contenu) plutôt que de
  supposer une forme et la coder.
- Modifier ce hook en UNE seule écriture. Le 2026-10-03, une modification en
  deux éditions a laissé entre les deux une variable non définie : le hook,
  matcher `.*` et échec fermé, a refusé tout appel non lu, y compris l'édition
  qui l'aurait réparé ; seul l'humain a pu rétablir le fichier à la main.
