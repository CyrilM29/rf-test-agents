---
name: agents-versionnes-alignes-a-la-release
description: >-
  2026-09-29, décision de méthode : chaque définition d'agent porte
  `version: X.Y.Z`, la version de release du dépôt qui la livre (ici
  `VERSION`, 1.0.0), exigée par le générateur, inscrite dans les cibles
  générées et épinglée par un test ; le handoff schéma 2 nomme son
  `producer` ; à chaque release, tout ce qui porte la version est aligné
type: projet
date: 2026-09-29
---

Jusqu'au 2026-09-29, les agents n'avaient aucun numéro : seuls le contrat
(« version 1 ») et le schéma des handoffs en portaient un. Un plan ne disait
donc pas quelle version de l'agent l'avait écrit, et les copies d'un même
agent dans les verticales ne se comparaient pas. L'utilisateur a demandé que
les agents soient versionnés et qu'à CHAQUE release on vérifie que tout ce
qui porte la version est aligné sur elle.

**Pourquoi un mécanisme et pas une consigne :** un bump de version oublié sur
une partie des fichiers est exactement ce qui est arrivé aux bibliothèques
SAPFX (0.2.x, 0.3.0, 0.4.0), et seul un garde l'a arrêté. Le générateur
refuse donc une version absente, mal formée ou divergente entre agents d'un
même dépôt, et l'écrit dans la bannière des cibles : une cible non
régénérée échoue `--check`. Un test épingle la version des agents à la
source du dépôt (`VERSION` ici, `pyproject.toml` dans une verticale qui
publie une bibliothèque). La version n'entre pas dans le frontmatter VS Code,
que Copilot ne reconnaîtrait pas.

**Handoff :** le schéma 2 ajoute `producer` (`agent`, `version`), toujours
dans un schéma FERMÉ. Le schéma 1 reste valide tel quel pour les sidecars
signés avant : les réécrire pour paraître récents serait une attestation
fabriquée.

**Comment appliquer :** à chaque release d'un dépôt de la famille, avant le
tag, aligner les paquets, les définitions d'agents, les cibles générées et
le changelog, puis laisser les gardes le confirmer. Propagé le même jour à
SAPFX (agents en 0.8.2, version des bibliothèques), ODOOFX (0.1.0, version
de sa bibliothèque) et RF_GenAI (fichier `VERSION`, 1.0.0, aucun paquet
publié), handoff schéma 2 partout.
