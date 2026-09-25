---
name: stdd-lu-a-l-aune-de-tdd
description: >-
  2026-09-25, cadrage du STDD formulé par l'utilisateur : la même logique que
  TDD, une brique plus tôt ; la spec est « verte par défaut, en théorie »
  (personne ne l'exécute), et le STDD la met à l'épreuve du système réel avant
  le moindre test ; à dire « même logique », jamais « contre TDD »
type: projet
date: 2026-09-25
---

Le 2026-09-25, en relisant le film pédagogique du STDD, l'utilisateur a
formulé le cadrage qui manquait pour un public de développeurs : le STDD se
lit à l'aune de TDD.

TDD, c'est rouge, vert, refactor : le test d'abord, il échoue, puis le code le
fait passer. Le STDD garde cette logique et la déplace d'une brique : la
première brique est la spec. Or une spec est **verte par défaut, en théorie** :
on l'écrit, on la croit, personne ne l'exécute, donc rien ne peut la faire
échouer. Le STDD met cette brique à l'épreuve du système réel. La confrontation
menée par le planner est sa phase rouge (les hypothèses que le système
réfute), la spec observée sa phase verte, et seulement ensuite viennent le
test et le code. Une spec que personne n'a confrontée est verte comme un test
qu'on n'a jamais lancé : par défaut, pas par preuve.

**Pourquoi :** les trois maillons (spec, test, développement) décrivent l'ordre
des opérations, mais pas pourquoi la spec doit passer par le système réel. Le
parallèle TDD le dit en une phrase à quiconque connaît déjà le cycle rouge,
vert, refactor, et il donne un nom à ce que la confrontation produit (la
phase rouge de la spec).

**Comment appliquer :** le cadrage vit dans la section STDD de `CLAUDE.md`
(définition canonique) et dans les deux README ; les verticales (SAPFX, ODOOFX)
et le site AI Cabra le reprennent. Toujours « la même logique, une brique plus
tôt », jamais le STDD contre TDD, et toujours sans opposer le STDD au BDD, qui
reste l'une des formes d'entrée de la spec.
