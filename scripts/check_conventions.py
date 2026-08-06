"""Garde mécanique des conventions #1 et #2 : celles qu'un linter peut prouver.

Les agents (rf-generator, rf-healer) promettent en prose que :

* **convention #1**, les tests ne contiennent aucun localisateur brut :
  CSS/XPath/stratégies (`css=`, `xpath=`, `//…`, `id=`, sélecteurs chaînés
  Browser `a >> b`) vivent dans ``resources/`` ou ``variables/locators.py``,
  jamais dans un fichier de ``tests/robot/`` ;
* **convention #2**, jamais de ``Sleep`` : synchronisation réelle uniquement,
  dans les tests COMME dans la couche resources.

Une règle en prose n'est pas un contrat : ce garde la rend mécanique. Il est
appelé par le rf-generator comme gate (entre le dry run et le run live), par le
hook post-édition du workspace et par la CI. Échec = un artefact viole une
convention → corriger la ventilation (déplacer le localisateur dans un page
object, remplacer le Sleep par une vraie synchronisation), jamais contourner
le garde.

Limites assumées : détection par motifs sur les cellules Robot Framework
(séparateur 2+ espaces ou tabulation) ; les blocs ``Documentation`` et les
commentaires sont ignorés (on peut y CITER un localisateur). Un localisateur
exotique peut passer : le garde attrape les violations franches, la revue
humaine garde le reste.

Usage::

    python scripts/check_conventions.py              # tout le workspace
    python scripts/check_conventions.py tests/robot/ui/web/x.robot   # ciblé
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Stratégies de localisation explicites (SeleniumLibrary, Browser) en tête de
# cellule. `timeout=`, `url=`… ne matchent pas : la liste est fermée.
_STRATEGY = re.compile(
    r"^(css|xpath|id|text|link|partial link|name|class|tag|dom|jquery)"
    r"\s*[:=]", re.IGNORECASE)
# XPath nu : la cellule commence par // ou (//
_BARE_XPATH = re.compile(r"^\(?//")
# Sélecteur chaîné Browser : `parent >> child`
_CHAINED = re.compile(r"\s>>\s")

_CELL_SPLIT = re.compile(r"\t|[ ]{2,}")


def _cells(line: str) -> list[str]:
    """Cellules RF de la ligne, commentaires (# …) tronqués."""
    cells = [c.strip() for c in _CELL_SPLIT.split(line.rstrip())]
    kept = []
    for cell in cells:
        if cell.startswith("#"):
            break
        if cell:
            kept.append(cell)
    return kept


def _is_sleep(cell: str) -> bool:
    # RF matche les keywords sans casse ; `BuiltIn.Sleep` est le nom qualifié.
    return cell.lower() in ("sleep", "builtin.sleep")


def _is_raw_locator(cell: str) -> bool:
    if cell.startswith(("http://", "https://")):
        return False
    return bool(_STRATEGY.match(cell) or _BARE_XPATH.match(cell)
                or _CHAINED.search(cell))


def scan_file(path: Path, forbid_locators: bool) -> list[tuple[int, str]]:
    """(ligne, message) pour chaque violation du fichier.

    ``forbid_locators=True`` pour les fichiers de tests (convention #1) ;
    le Sleep (convention #2) est interdit partout.
    """
    problems = []
    in_doc = False
    for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1):
        cells = _cells(line)
        if not cells:
            continue
        first = cells[0]
        # Blocs Documentation : on peut y citer un localisateur en prose.
        if first in ("Documentation", "[Documentation]"):
            in_doc = True
            continue
        if in_doc and first == "...":
            continue
        in_doc = False
        for cell in cells:
            if _is_sleep(cell):
                problems.append(
                    (lineno, "Sleep interdit (convention #2) : utiliser la "
                             "synchronisation réelle de la bibliothèque"))
                break
        if forbid_locators:
            for cell in cells[1:] if first != "..." else cells:
                if _is_raw_locator(cell):
                    problems.append(
                        (lineno, "localisateur brut dans un test "
                                 "(convention #1) : « %s », le déplacer dans "
                                 "resources/page_objects/ ou "
                                 "variables/locators.py" % cell))
    return problems


def check(repo_root: Path, targets: list[str] | None = None) -> int:
    """0 = conventions tenues, 1 = au moins une violation."""
    if targets:
        paths = [repo_root / t for t in targets]
    else:
        paths = [repo_root / "tests" / "robot", repo_root / "resources"]
    files = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.robot")))
            files.extend(sorted(path.rglob("*.resource")))
        elif path.exists():
            files.append(path)
    tests_root = (repo_root / "tests" / "robot").resolve()
    failed = False
    total = 0
    for file in files:
        forbid = tests_root in file.resolve().parents
        problems = scan_file(file, forbid_locators=forbid)
        for lineno, message in problems:
            print("  - %s:%d : %s"
                  % (file.relative_to(repo_root), lineno, message))
        failed = failed or bool(problems)
        total += 1
    if failed:
        print("[check_conventions] ÉCHEC (voir ci-dessus).")
        return 1
    print("[check_conventions] OK : %d fichier(s), aucune violation." % total)
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="*",
                        help="fichiers/répertoires à contrôler (défaut : "
                             "tests/robot/ et resources/)")
    parser.add_argument("--root", default=".",
                        help="racine du dépôt (défaut : répertoire courant)")
    args = parser.parse_args(argv)
    return check(Path(args.root).resolve(), args.targets or None)


if __name__ == "__main__":
    sys.exit(main())
