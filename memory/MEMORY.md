# Project memory index

One line per entry; open an entry only if its description is relevant.
Rules: [README.md](README.md).

- [Agents versionnes, alignes a la release](agents-versionnes-alignes-a-la-release.md) : 2026-09-29, chaque definition porte `version: X.Y.Z` (version de release du depot, ici `VERSION`), exigee par le generateur, inscrite dans les cibles, epinglee par un test ; handoff schema 2 avec `producer`, schema 1 toujours valide ; a chaque release tout est aligne avant le tag ; propage a SAPFX, ODOOFX et RF_GenAI a faire
- [Fil de reprise a cote du journal](fil-de-reprise-a-cote-du-journal.md) : 2026-09-26, la regle « consigner au fil de l'eau pour qu'un autre agent reprenne » tenue par des entrees immuables (une par fichier, ecrivables avec Write seul) a cote du journal ; `resume` fusionne les verdicts du journal, jamais de rejeu, de session restauree ni de permission heritee
- [STDD lu a l'aune de TDD](stdd-lu-a-l-aune-de-tdd.md) : 2026-09-25, la meme logique que TDD une brique plus tot ; la spec est verte par defaut en theorie (personne ne l'execute), le STDD la confronte au systeme reel avant le moindre test ; jamais « contre TDD »
- [Rejeu et defaut connu, jamais sur un texte](rejeu-et-defaut-connu-jamais-sur-un-texte.md) : 2026-09-23, un rejeu n'est admis que DECLARE avant le run pour une classe transitoire mesuree, sur une etape de lecture, jamais une ecriture ; un defaut connu se reconnait a son identite technique avec ticket et expiration, jamais a un motif de texte ; l'echec reste rouge ; meme regle pour `pending`, declare a la generation
- [Oracles et jugement du modele](oracles-negatifs-ne-mesurent-pas-agent.md) : 2026-09-06, des faits fournis au calculateur valident son verdict, pas la capacite du modele a etablir ces faits
