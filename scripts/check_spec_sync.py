"""Garde de synchronisation specs/ ↔ tests/robot/ : le plan est la source de vérité.

Le plan métier Markdown (``specs/``, écrit/relu par le métier) est l'artefact
canonique ; la suite ``.robot`` n'en est qu'une **dérivation** produite par
rf-generator. Pour que cette promesse tienne, il faut détecter la dérive dans
les deux sens :

* une suite générée porte un **marqueur de provenance** dans sa
  ``Documentation`` : ``Spec: specs/<plan>.md (sha256:<12 hex du contenu>)`` ;
* si le plan a changé depuis la génération (hash différent), la suite est
  **périmée** → exit 1 : il faut repasser par ``/rf-generate`` (ou assumer le
  changement en re-stampant), jamais éditer la suite à la main en silence ;
* un marqueur pointant vers un plan disparu est cassé → exit 1 ;
* les plans sans suite sont listés à titre informatif (le generator n'est
  peut-être pas encore passé) — jamais bloquant.

Garde de cohérence, pas générateur — la génération reste le travail de
rf-generator, qui exécute chaque étape live avant d'écrire. Seul ``--stamp``
écrit : il appose/rafraîchit le marqueur d'une suite APRÈS une (re)génération
assumée.

Adapté du garde homonyme du projet SAPFX (même auteur, Apache-2.0) ; la seule
différence : les suites sont cherchées récursivement (layout ventilé
``tests/robot/{api, ui/web, ui/mobile, cross}``).

Usage::

    python scripts/check_spec_sync.py                # le garde (CI-compatible)
    python scripts/check_spec_sync.py --stamp tests/robot/ui/web/x.robot specs/x.md
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

MARKER = re.compile(
    r"Spec:\s*(?P<spec>specs/[^\s]+\.md)\s*\(sha256:(?P<digest>[0-9a-f]{12})\)")

# Plans sans suite par nature : le contrat du répertoire et les feuilles de
# route produites par le mode discovery du planner.
_UNLINKED_OK = ("README.md", "couverture-proposee.md")


def spec_digest(spec_path: Path) -> str:
    """Empreinte (12 hex) du plan, fins de ligne normalisées — stable à
    travers les checkouts CRLF/LF de git sous Windows."""
    text = spec_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def find_markers(robot_dir: Path) -> list[tuple[Path, str, str]]:
    """(suite, chemin de spec, digest annoncé) pour chaque suite marquée."""
    found = []
    for suite in sorted(robot_dir.rglob("*.robot")):
        match = MARKER.search(suite.read_text(encoding="utf-8"))
        if match:
            found.append((suite, match.group("spec"), match.group("digest")))
    return found


def check(repo_root: Path) -> int:
    """Le garde : 0 = tout est en phase, 1 = suite périmée ou marqueur cassé."""
    robot_dir = repo_root / "tests" / "robot"
    specs_dir = repo_root / "specs"
    markers = find_markers(robot_dir) if robot_dir.exists() else []
    problems = []
    linked_specs = set()
    for suite, spec_rel, digest in markers:
        spec_path = repo_root / spec_rel
        if not spec_path.exists():
            problems.append("%s : marqueur cassé — %s n'existe plus"
                            % (suite.name, spec_rel))
            continue
        linked_specs.add(spec_path.name)
        actual = spec_digest(spec_path)
        if actual != digest:
            problems.append(
                "%s : PÉRIMÉE — %s a changé depuis la génération "
                "(sha256 %s ≠ %s) : repasser par /rf-generate, ou re-stamper "
                "si le changement n'impacte pas la suite"
                % (suite.name, spec_rel, actual, digest))
    if problems:
        print("[check_spec_sync] ÉCHEC :")
        for problem in problems:
            print("  - %s" % problem)
        return 1
    unlinked = [p.name for p in sorted(specs_dir.glob("*.md"))
                if p.name not in linked_specs and p.name not in _UNLINKED_OK] \
        if specs_dir.exists() else []
    print("[check_spec_sync] OK — %d suite(s) en phase avec leur spec."
          % len(markers))
    if unlinked:
        print("  (info : specs sans suite générée : %s)" % ", ".join(unlinked))
    return 0


def stamp(repo_root: Path, suite_rel: str, spec_rel: str) -> int:
    """Appose (ou rafraîchit) le marqueur de provenance d'une suite — à appeler
    APRÈS une (re)génération assumée, jamais pour masquer une dérive."""
    suite_path = repo_root / suite_rel
    spec_path = repo_root / spec_rel
    if not suite_path.exists() or not spec_path.exists():
        print("[check_spec_sync] introuvable : %s ou %s" % (suite_rel, spec_rel))
        return 1
    digest = spec_digest(spec_path)
    marker = "Spec: %s (sha256:%s)" % (spec_rel.replace("\\", "/"), digest)
    text = suite_path.read_text(encoding="utf-8")
    if MARKER.search(text):
        text = MARKER.sub(marker, text, count=1)
    else:
        # Ancrage : première ligne de la Documentation de la suite — le
        # marqueur devient une ligne de continuation juste en dessous.
        lines = text.splitlines(keepends=True)
        for index, line in enumerate(lines):
            if line.startswith("Documentation"):
                newline = "\r\n" if line.endswith("\r\n") else "\n"
                lines.insert(index + 1, "...                 %s%s"
                             % (marker, newline))
                break
        else:
            print("[check_spec_sync] pas de ligne Documentation dans %s — "
                  "ajouter le marqueur à la main" % suite_rel)
            return 1
        text = "".join(lines)
    suite_path.write_text(text, encoding="utf-8")
    print("[check_spec_sync] stampé : %s ← %s" % (suite_rel, marker))
    return 0


def main(argv: list[str] | None = None) -> int:
    # Console Windows en cp1252 : le rapport contient des caractères hors page
    # de code — UTF-8 best-effort plutôt qu'un plantage à l'affichage.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".",
                        help="racine du dépôt (défaut : répertoire courant)")
    parser.add_argument("--stamp", nargs=2, metavar=("SUITE", "SPEC"),
                        help="appose/rafraîchit le marqueur de SUITE depuis SPEC")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.stamp:
        return stamp(root, args.stamp[0], args.stamp[1])
    return check(root)


if __name__ == "__main__":
    sys.exit(main())
