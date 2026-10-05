"""Un hook commun aux deux hotes, sans approbation implicite."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
# La politique locale du poste (fichier ignoré par git) ne doit pas changer
# ce que ces tests prouvent : la configuration committée demande confirmation.
CONFIRM_ENV = {**os.environ, "RF_AGENT_POLICY": "confirm"}


@pytest.mark.parametrize("tool, argument", [
    ("Edit", {"file_path": "resources/example.resource"}),
    ("replace_string_in_file", {"filePath": "resources/example.resource"}),
])
def test_real_config_executes_confirmation_gate(tool, argument):
    config = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    hooks = config["hooks"]["PreToolUse"]
    assert len(hooks) == 1 and hooks[0]["matcher"] == ".*"
    hook = hooks[0]["hooks"][0]
    assert "hook_agent_permissions.py" in hook["command"]
    result = subprocess.run(
        [sys.executable, "scripts/hook_agent_permissions.py"], cwd=ROOT,
        input=json.dumps(dict(tool_name=tool, tool_input=argument)),
        capture_output=True, text=True, check=False, env=CONFIRM_ENV,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "ask"


def configured_commands() -> dict[str, str]:
    config = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    return {event: groups[0]["hooks"][0]["command"] for event, groups in config["hooks"].items()}


def run_configured(event: str, cwd: Path, payload: dict, *, project_dir: bool):
    """Joue la commande telle que declaree, par un shell, comme le fait l'hote."""
    env = {k: v for k, v in CONFIRM_ENV.items() if k != "CLAUDE_PROJECT_DIR"}
    if project_dir:
        env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    return subprocess.run(
        configured_commands()[event], shell=True, cwd=cwd, input=json.dumps(payload),
        capture_output=True, text=True, check=False, env=env,
    )


@pytest.mark.parametrize("event", ["PreToolUse", "PostToolUse"])
def test_configured_command_survives_a_drifted_working_directory(event, tmp_path):
    # Un `cd` de l'agent deplace le cwd de la session : le hook, fail closed sur
    # TOUS les outils, ne doit pas dependre du dossier courant (CLAUDE_PROJECT_DIR).
    result = run_configured(
        event, tmp_path, {"tool_name": "Edit", "tool_input": {"file_path": "resources/example.resource"}},
        project_dir=True,
    )
    assert "can't open file" not in result.stderr and "No such file" not in result.stderr
    assert result.returncode == 0
    if event == "PreToolUse":
        assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "ask"


@pytest.mark.parametrize("event", ["PreToolUse", "PostToolUse"])
def test_configured_command_fails_closed_when_the_script_cannot_be_found(event, tmp_path):
    # Ni variable ni racine : un script introuvable doit BLOQUER (code 2). Tout
    # autre code est un simple avertissement chez l'hote, donc la porte de
    # permission s'ouvrirait en silence au lieu de rester fermee.
    result = run_configured(
        event, tmp_path, {"tool_name": "Edit", "tool_input": {"file_path": "resources/example.resource"}},
        project_dir=False,
    )
    assert result.returncode == 2
    assert "hook script not found" in result.stderr


def test_configured_command_still_runs_from_the_root_without_the_variable():
    # Hote qui ne fournit pas CLAUDE_PROJECT_DIR (Copilot) : repli sur le cwd.
    result = run_configured(
        "PreToolUse", ROOT, {"tool_name": "Edit", "tool_input": {"file_path": "resources/example.resource"}},
        project_dir=False,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "ask"
