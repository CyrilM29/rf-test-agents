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
    assert hook["command"] == "python scripts/hook_agent_permissions.py"
    result = subprocess.run(
        [sys.executable, "scripts/hook_agent_permissions.py"], cwd=ROOT,
        input=json.dumps(dict(tool_name=tool, tool_input=argument)),
        capture_output=True, text=True, check=False, env=CONFIRM_ENV,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "ask"
