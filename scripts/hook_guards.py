"""Hook PostToolUse (Write|Edit) — lance les gardes après toute édition des
artefacts du cycle (specs/, tests/robot/, resources/, variables/).

Deux sévérités, calées sur la nature de chaque garde :

* ``check_conventions.py`` (localisateur brut dans un test, Sleep) : une
  violation est TOUJOURS un bug de l'artefact → exit 2, le message remonte à
  l'assistant qui doit corriger immédiatement ;
* ``check_spec_sync.py`` (suite périmée, spec PÉRIMÉE) : un échec peut être
  transitoire au milieu d'un cycle légitime (spec annotée puis re-stampée par
  rf-generator) → non bloquant, remonté en information (systemMessage +
  additionalContext).

Entrée : le JSON du hook sur stdin. Sortie : JSON Claude Code le cas échéant.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WATCHED = ("/specs/", "/tests/robot/", "/resources/", "/variables/")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    file_path = str((payload.get("tool_input") or {}).get("file_path") or "")
    normalized = file_path.replace("\\", "/")
    if not any(segment in normalized for segment in WATCHED):
        return 0
    root = Path(__file__).resolve().parents[1]

    def run(script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(root / "scripts" / script)],
            cwd=root, capture_output=True, text=True,
            encoding="utf-8", errors="replace")

    conventions = run("check_conventions.py")
    if conventions.returncode != 0:
        sys.stderr.write(conventions.stdout + conventions.stderr)
        return 2  # bloquant : l'assistant doit corriger la ventilation

    sync = run("check_spec_sync.py")
    if sync.returncode != 0:
        report = (sync.stdout + sync.stderr).strip()
        print(json.dumps({
            "systemMessage": "check_spec_sync : dérive spec ↔ suite détectée "
                             "(voir détail) — re-stamper ou régénérer.",
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": report,
            },
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
