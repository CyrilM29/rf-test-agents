"""Vérifie que les conventions numérotées de CLAUDE.md restent **portées** par
les définitions d'agents (``.claude/agents/rf-*.md``).

Ce dépôt assume une duplication : les conventions et le rituel de session
rf-mcp vivent à la fois dans CLAUDE.md et dans les trois définitions d'agents
(convention #8, « quadruplicated by design » — un agent ne lit pas CLAUDE.md
au moment où il travaille, il lit sa propre définition). Le prix de cette
duplication, c'est la dérive : une convention reformulée ici et oubliée là.

Ce garde-fou la rend visible. Pour chaque convention suivie, il vérifie :

1. que le passage attendu est encore présent **tel quel** dans CLAUDE.md
   (sinon la convention a été reformulée/déplacée : c'est ce script qu'il faut
   mettre à jour, pas rester silencieux sur une correspondance qu'il ne peut
   plus établir) ;
2. que chaque définition d'agent porte encore le marqueur correspondant.

Ce n'est **pas** un générateur : CLAUDE.md est de la prose libre destinée à des
lecteurs humains/IA, pas une donnée structurée — en extraire mécaniquement du
texte produirait des définitions d'agents de piètre qualité. C'est un garde de
COHÉRENCE, dans le même esprit que ``check_spec_sync.py`` (provenance) et
``check_conventions.py`` (artefacts). Porté depuis le projet SAPFX (même
auteur), où il couvre en plus les hints du serveur MCP et les cartes de
keywords des plugins — hors sujet ici, ce dépôt n'ayant pas de plugin.

Usage : python scripts/check_guidance_sync.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_CLAUDE_MD = _ROOT / "CLAUDE.md"
_AGENTS_DIR = _ROOT / ".claude" / "agents"

# (n° de convention, passage attendu tel quel dans CLAUDE.md).
_TRACKED = [
    (1, "Tests contain no raw locators"),
    (2, "Never `time.sleep`/`Sleep`"),
    (3, "Robust assertions"),
    (4, "Never fabricate locators"),
    (5, "The spec is the source of truth"),
    (6, "Credentials never in files"),
]

# Marqueurs (en minuscules) que CHAQUE définition d'agent doit encore porter :
# la traduction, pour l'agent qui la lit au travail, des conventions #1
# (localisateurs dans la couche resources), #2 (jamais d'attente fixe) et #6
# (identifiants hors des fichiers).
_AGENT_MARKERS = [
    (1, "resources/"),
    (2, "time.sleep"),
    (6, "secret:"),
]


def check() -> list[str]:
    """Retourne la liste des messages de problème (vide si tout est aligné)."""
    problems: list[str] = []
    claude_md = _CLAUDE_MD.read_text(encoding="utf-8")
    for num, anchor in _TRACKED:
        if anchor not in claude_md:
            problems.append(
                "CLAUDE.md convention #%d : passage attendu introuvable (%r) — "
                "reformulée/déplacée ? Mettre à jour "
                "scripts/check_guidance_sync.py." % (num, anchor))

    agent_files = sorted(_AGENTS_DIR.glob("rf-*.md")) \
        if _AGENTS_DIR.is_dir() else []
    if not agent_files:
        problems.append(
            "aucune définition d'agent rf-*.md sous %s — déplacées/renommées ? "
            "Mettre à jour scripts/check_guidance_sync.py." % _AGENTS_DIR)
    for path in agent_files:
        text = path.read_text(encoding="utf-8").lower()
        for num, marker in _AGENT_MARKERS:
            if marker not in text:
                problems.append(
                    "convention #%d : la définition d'agent %s ne mentionne "
                    "plus %r — a-t-elle dérivé ?" % (num, path.name, marker))
        # Convention #8 : chaque agent porte la note de synchronisation qui
        # rappelle que ces règles existent en quatre exemplaires.
        if "sync note" not in text:
            problems.append(
                "convention #8 : %s a perdu sa « Sync note » — le rappel que "
                "les ground rules doivent être modifiées dans les quatre "
                "fichiers à la fois." % path.name)
    return problems


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    problems = check()
    if not problems:
        print("[check_guidance_sync] OK — conventions portées par les %d "
              "définitions d'agents." % len(list(_AGENTS_DIR.glob("rf-*.md"))))
        return 0
    print("[check_guidance_sync] ÉCHEC :")
    for problem in problems:
        print("  - %s" % problem)
    return 1


if __name__ == "__main__":
    sys.exit(main())
