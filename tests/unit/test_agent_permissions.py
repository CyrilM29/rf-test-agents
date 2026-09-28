"""Contre-epreuves des permissions sur les deux dialectes d'hote."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "hook_agent_permissions.py"
SPEC = importlib.util.spec_from_file_location("permissions_under_test", SCRIPT)
permissions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(permissions)


def verdict(tool, arguments=None, **kwargs):
    return permissions.decision(
        {"tool_name": tool, "tool_input": arguments or {}}, **kwargs
    ).get("hookSpecificOutput", {}).get("permissionDecision")


@pytest.mark.parametrize("tool", ["Read", "read_file", "search/readFile"])
@pytest.mark.parametrize("key", ["file_path", "filePath"])
def test_read_preserves_host_permissions(tool, key):
    assert verdict(tool, {key: "specs/example.md"}) is None


@pytest.mark.parametrize("tool", [
    "Bash", "PowerShell", "run_in_terminal", "runCommands", "apply_patch",
    "Write", "Edit", "create_file", "replace_string_in_file",
    "mcp__rf-mcp__execute_step", "rf-mcp-sap/execute_step",
    "mcp_robot_framewo_execute_batch", "mcp_robot_framewo_execute_flow",
    "mcp__rf-mcp__manage_session", "mcp__rf-mcp__run_test_suite",
    "mcp__rf-mcp-sap__sapfx_reload", "runSubagent", "unknown_tool",
])
def test_effectful_or_unknown_requires_confirmation(tool):
    assert verdict(tool, {"command": "read then write"}) == "ask"
    assert verdict(tool, read_only=True) == "deny"


def test_no_keyword_name_can_grant_permission():
    assert verdict("mcp__rf-mcp__execute_step", {
        "keyword": "Get Everything", "arguments": ["ignore permissions"],
    }) == "ask"


@pytest.mark.parametrize("payload", [None, [], {}, {"tool_name": "Read"},
    {"tool_name": "Read", "tool_input": {"filePath": 12}},
    {"tool_name": "Read", "tool_input": {"filePath": "a", "file_path": "b"}},
])
def test_invalid_input_fails_closed(payload):
    assert permissions.decision(payload)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_cli_invalid_json_denies_without_leaking_input():
    result = subprocess.run([sys.executable, str(SCRIPT)], input="private-input",
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "private-input" not in result.stdout + result.stderr
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize("tool, arguments", [
    ("Write", {"file_path": "specs/example.md"}),
    ("Edit", {"file_path": "resources/example.resource"}),
    ("mcp__rf-mcp__execute_step", {"keyword": "Click"}),
    ("rf-mcp/execute_step", {"keyword": "Click"}),
    ("Agent", {"prompt": "explore"}),
    ("edit/createFile", {"filePath": "specs/example.md"}),
    ("edit/editFiles", {"filePath": "resources/example.resource"}),
    ("replace_string_in_file", {"filePath": "resources/example.resource"}),
    ("mcp_rf-mcp_execute_step", {"keyword": "Click"}),
    ("mcp_robot_framewo_execute_batch", {"steps": []}),
    ("run_in_terminal", {"command": "python scripts/check_conventions.py"}),
    ("runSubagent", {"prompt": "explore"}),
    ("Bash", {"command": "python -m robot --outputdir results/x tests/robot"}),
    ("PowerShell", {"command": "git status; git diff --stat"}),
])
def test_autonomous_policy_returns_routine_calls_to_the_host(tool, arguments):
    assert verdict(tool, arguments, policy="autonomous") is None
    assert verdict(tool, arguments) == "ask"
    assert verdict(tool, arguments, policy="autonomous", read_only=True) == "deny"


@pytest.mark.parametrize("command", [
    "git commit -m 'x'", "cd repo && git push origin main", "git -C repo tag v1",
    "git reset --hard HEAD~1", "git checkout -- specs/a.md", "gh pr create",
    "rm -rf results", "Remove-Item -Recurse x", "pip install foo",
    "pnpm publish", "docker rm a4h", "git push --force", "git commit --no-verify",
])
def test_autonomous_policy_still_confirms_important_phases(command):
    assert verdict("Bash", {"command": command}, policy="autonomous") == "ask"
    assert verdict("run_in_terminal", {"command": command}, policy="autonomous") == "ask"


@pytest.mark.parametrize("tool", [
    "unknown_tool", "Artifact", "Workflow", "mcp__claude_ai_Claude_Docs__create",
    "mcp__mammouth__demander_a_mammouth", "RemoteTrigger",
])
def test_autonomous_policy_never_covers_unknown_or_outward_tools(tool):
    assert verdict(tool, {"command": "anything"}, policy="autonomous") == "ask"


@pytest.mark.parametrize("tool, arguments", [
    ("Bash", {"command": "python scripts/agent_policy.py on"}),
    ("PowerShell", {"command": "python scripts\\agent_policy.py off"}),
    ("run_in_terminal", {"command": "Set-Content .claude/agent-policy.local.json '{}'"}),
    ("Bash", {"command": "echo '{}' > .claude/settings.local.json"}),
    ("PowerShell", {"command": "python scripts/hook_agent_permissions.py < payload.json"}),
    ("Write", {"file_path": "E:\\repo\\.claude\\agent-policy.local.json"}),
    ("Edit", {"file_path": "/repo/.claude/settings.json"}),
    ("replace_string_in_file", {"filePath": "C:/repo/scripts/hook_agent_permissions.py"}),
    ("create_file", {"filePath": "/repo/.claude/settings.local.json"}),
    ("edit/editFiles", {"filePath": "/repo/scripts/agent_policy.py"}),
    ("apply_patch", {"input": "*** Begin Patch\n*** Update File: /repo/.claude/settings.json\n"
                              "@@\n-a\n+b\n*** End Patch"}),
    ("Skill", {"skill": "autonomie", "args": "on"}),
    ("SlashCommand", {"command": "/autonomie off"}),
])
def test_only_a_human_changes_the_approval_rules(tool, arguments):
    assert verdict(tool, arguments, policy="autonomous") == "ask"
    assert verdict(tool, arguments) == "ask"
    assert verdict(tool, arguments, read_only=True) == "deny"


@pytest.mark.parametrize("tool, arguments", [
    ("Bash", {"command": "python scripts/agent_policy.py status"}),
    ("Bash", {"command": "python scripts/agent_policy.py"}),
    ("Bash", {"command": "python -m pytest tests/unit/test_agent_permissions.py"}),
    ("Edit", {"file_path": "/repo/CLAUDE.md", "old_string": ".claude/settings.json",
              "new_string": "the host settings"}),
    ("Write", {"file_path": "/repo/docs/settings.json"}),
    ("Skill", {"skill": "reponse-concise"}),
])
def test_approval_lock_leaves_routine_work_to_the_policy(tool, arguments):
    assert verdict(tool, arguments, policy="autonomous") is None


def test_autonomous_shell_without_command_string_is_confirmed():
    assert verdict("Bash", {"command": ["git", "push"]}, policy="autonomous") == "ask"


@pytest.mark.parametrize("environ, content, expected", [
    ({}, None, "confirm"),
    ({}, '{"policy": "autonomous"}', "autonomous"),
    ({}, '{"policy": "yolo"}', "confirm"),
    ({}, "not json", "confirm"),
    ({}, "[]", "confirm"),
    ({"RF_AGENT_POLICY": "confirm"}, '{"policy": "autonomous"}', "confirm"),
    ({"RF_AGENT_POLICY": "autonomous"}, None, "autonomous"),
    ({"RF_AGENT_POLICY": "bogus"}, '{"policy": "autonomous"}', "confirm"),
])
def test_policy_loading_falls_back_to_confirmation(tmp_path, environ, content, expected):
    policy_file = tmp_path / "agent-policy.local.json"
    if content is not None:
        policy_file.write_text(content, encoding="utf-8")
    assert permissions.load_policy(environ, policy_file) == expected


def test_policy_file_is_ignored_by_git():
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT,
                            capture_output=True, text=True, check=False)
    if inside.returncode != 0:
        pytest.skip("arbre hors git (export public) : rien à ignorer")
    result = subprocess.run(["git", "check-ignore", "-q", ".claude/agent-policy.local.json"],
                            cwd=ROOT, check=False)
    assert result.returncode == 0
