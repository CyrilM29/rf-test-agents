"""Active, désactive ou affiche la politique locale du hook de permissions.

Usage (depuis la racine du dépôt) :

    python scripts/agent_policy.py            # état (même chose que « status »)
    python scripts/agent_policy.py on         # mode autonome
    python scripts/agent_policy.py off        # retour au défaut : confirmation
    python scripts/agent_policy.py status     # état

``on`` écrit ``.claude/agent-policy.local.json`` (UTF-8 sans BOM, ignoré par
git) ; ``off`` le supprime. Le hook relit ce fichier à chaque appel d'outil :
le changement prend effet tout de suite, sans redémarrage. La variable
d'environnement ``RF_AGENT_POLICY`` l'emporte sur le fichier, et
``RF_AGENT_READ_ONLY=1`` sur les deux : l'état le signale.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_agent_permissions import POLICY_FILE, load_policy  # noqa: E402

EXPLICATIONS = {
    "autonomous": "le travail courant passe sans question ; commit, push, "
                  "suppression, installation et publication demandent toujours confirmation",
    "confirm": "tout ce qui n'est pas une lecture demande confirmation (défaut)",
}


def activer(fichier: Path = POLICY_FILE) -> None:
    fichier.parent.mkdir(parents=True, exist_ok=True)
    fichier.write_bytes(b'{"policy": "autonomous"}\n')


def desactiver(fichier: Path = POLICY_FILE) -> None:
    fichier.unlink(missing_ok=True)


def etat(environ: Mapping[str, str] | None = None, fichier: Path = POLICY_FILE) -> str:
    environ = os.environ if environ is None else environ
    politique = load_policy(environ, fichier)
    lignes = []
    if environ.get("RF_AGENT_READ_ONLY") == "1":
        lignes.append("Mode LECTURE SEULE (RF_AGENT_READ_ONLY=1) : tout ce qui n'est pas "
                      "une lecture est refusé, quelle que soit la politique ci-dessous.")
    if "RF_AGENT_POLICY" in environ:
        source = f"variable RF_AGENT_POLICY={environ['RF_AGENT_POLICY']!r}, prioritaire sur le fichier"
    elif fichier.exists():
        source = f"fichier {fichier.name}"
    else:
        source = "aucun réglage local"
    lignes.append(f"Politique : {politique} ({source}) : {EXPLICATIONS[politique]}.")
    if "RF_AGENT_POLICY" not in environ and fichier.exists() and politique == "confirm":
        try:
            lu = json.loads(fichier.read_text(encoding="utf-8")).get("policy")
        except (OSError, ValueError, AttributeError):
            lu = None
        if lu != "confirm":
            lignes.append(f"Attention : {fichier.name} est illisible ou inconnu, d'où le repli "
                          "sur la confirmation. « on » le réécrit proprement.")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    for flux in (sys.stdout, sys.stderr):
        # Un flux capturé (pytest, redirection) n'est pas toujours un
        # TextIOWrapper : ne jamais échouer pour l'encodage de la console.
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Mode autonome du hook de permissions.")
    parser.add_argument("action", nargs="?", default="status", choices=["on", "off", "status"])
    action = parser.parse_args(argv).action
    if action == "on":
        activer()
    elif action == "off":
        desactiver()
    print(etat())
    if action != "status" and "RF_AGENT_POLICY" in os.environ:
        print("Note : la variable RF_AGENT_POLICY de ce terminal masque le fichier ; "
              "une session lancée ailleurs suivra le fichier.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
