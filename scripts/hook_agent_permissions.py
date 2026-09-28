"""Garde pre-execution commun Claude Code/Copilot, sans decision LLM.

Trois politiques, de la plus stricte a la plus souple :

- ``RF_AGENT_READ_ONLY=1`` (environnement de l'hote) : tout ce qui n'est pas
  une lecture est refuse ;
- ``confirm`` (defaut) : tout ce qui n'est pas une lecture demande confirmation ;
- ``autonomous`` (choix explicite du proprietaire du poste, jamais committe) :
  les familles d'outils locales connues (editions, shell ordinaire, rf-mcp,
  delegation a un sous-agent) gardent les permissions de base de l'hote, et
  seules les PHASES IMPORTANTES demandent confirmation (commit, push, tag,
  reecriture d'historique, suppression, installation, publication, outil
  inconnu).

La politique se choisit par ``RF_AGENT_POLICY`` dans l'environnement de
l'hote, a defaut par le fichier local ``.claude/agent-policy.local.json``
(``{"policy": "autonomous"}``), ignore par git. Une valeur illisible retombe
sur ``confirm`` : le repli est la confirmation, jamais l'autonomie.

Seul un humain change les regles d'approbation : toucher le fichier de
politique, les reglages des hotes ou les deux scripts qui les appliquent, ou
invoquer ``/autonomie``, demande confirmation sous TOUTE politique.
"""
from __future__ import annotations

import json
import os
from collections.abc import Mapping
import re
import sys
from pathlib import Path

POLICY_FILE = Path(__file__).resolve().parent.parent / ".claude" / "agent-policy.local.json"
POLICIES = frozenset({"confirm", "autonomous"})

READ_TOOLS = frozenset({
    "Read", "Glob", "Grep", "read_file", "file_search", "grep_search",
    "list_dir", "semantic_search", "get_errors", "view_image",
    "search/readFile", "search/fileSearch", "search/textSearch",
    "search/listDirectory",
})
READ_MCP = frozenset({
    "mcp__qa-brain__qa_search", "mcp__qa-brain__qa_ask",
    "mcp__qa-brain__qa_status", "qa-brain/qa_search", "qa-brain/qa_ask",
    "qa-brain/qa_status", "mcp_qa-brain_qa_search", "mcp_qa-brain_qa_ask",
    "mcp_qa-brain_qa_status",
})

# Politique autonome : familles d'outils locales rendues aux permissions de
# l'hote. Tout le reste (outil inconnu, publication, MCP tiers) demande encore.
SHELL_TOOLS = frozenset({"Bash", "PowerShell", "run_in_terminal", "runCommands"})
EDIT_TOOLS = frozenset({
    "Write", "Edit", "NotebookEdit", "create_file", "replace_string_in_file",
    "apply_patch", "insert_edit_into_file",
    # Noms qualifiés de Copilot (dialecte des chatmodes générés).
    "edit/createFile", "edit/createDirectory", "edit/editFiles",
})
DELEGATION_TOOLS = frozenset({"Agent", "Task", "runSubagent", "SendMessage"})
HARNESS_TOOLS = frozenset({
    "ToolSearch", "Skill", "TodoWrite", "ReadNotifications", "ListAgents",
    "Monitor", "TaskStop",
})
# Trois dialectes de nommage des outils rf-mcp : Claude Code, référence
# qualifiée de Copilot, identifiant interne de Copilot (même forme que
# `mcp_qa-brain_*` ci-dessus, et forme tronquée du nom annoncé par le serveur).
AUTONOMOUS_MCP_PREFIXES = ("mcp__rf-mcp__", "rf-mcp/", "mcp_rf-mcp_", "mcp_robot_framewo_")

# Phases importantes : une commande shell qui en porte une demande toujours
# confirmation, quelle que soit la politique. Filet par motifs, pas une preuve.
IMPORTANT_COMMAND = re.compile(
    r"""\bgit\s+(?:-C\s+\S+\s+)?(?:commit|push|tag|reset|rebase|merge|cherry-pick|revert|clean
        |am|filter-branch|filter-repo|stash\s+(?:drop|clear)|branch\s+-[dD]|restore)\b
      | \bgit\s+(?:-C\s+\S+\s+)?checkout\s+--(?:\s|$)
      | \bgh\s+(?:pr|release|repo|issue|api|workflow|secret)\b
      | \brm\s+-\w*[rRf]
      | \b(?:Remove-Item|rmdir|Clear-Content|Stop-Process|shutdown|Restart-Computer)\b
      | \b(?:pip|pip3|uv\s+pip|npm|pnpm|yarn)\s+(?:install|uninstall|add|remove|publish)\b
      | \b(?:twine|wrangler|docker|netsh|schtasks|setx)\b
      | --force\b | --no-verify\b
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Regles d'approbation : ce qu'un agent ne change jamais de lui-meme, quelle
# que soit la politique (le contrat interdit de les changer pour passer un
# refus). Chemins relatifs au depot, compares en fin de chemin.
APPROVAL_FILES = (
    ".claude/agent-policy.local.json", ".claude/settings.json",
    ".claude/settings.local.json", "scripts/hook_agent_permissions.py",
    "scripts/agent_policy.py",
)
APPROVAL_COMMAND = re.compile(
    r"agent_policy\.py\s+(?:on|off)\b | agent-policy\.local\.json"
    r" | hook_agent_permissions\.py | \.claude[\\/]+settings(?:\.local)?\.json",
    re.IGNORECASE | re.VERBOSE,
)
PATCH_TARGET = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)


def decision(payload: object, *, read_only: bool = False, policy: str = "confirm") -> dict:
    """Ne jamais emettre allow : conserver les permissions de base de l'hote."""
    if not isinstance(payload, dict):
        return response("deny", "Invalid hook input.")
    tool = payload.get("tool_name")
    arguments = payload.get("tool_input")
    if not isinstance(tool, str) or not isinstance(arguments, dict):
        return response("deny", "Missing tool name or structured arguments.")
    paths = [arguments[key] for key in ("file_path", "filePath") if key in arguments]
    if any(not isinstance(path, str) for path in paths):
        return response("deny", "Invalid file path.")
    if len(paths) == 2 and paths[0] != paths[1]:
        return response("deny", "Conflicting host file paths.")
    if tool in READ_TOOLS or tool in READ_MCP:
        return {}
    if read_only:
        return response("deny", "Read-only policy: execution, edits and unknown tools are denied.")
    if touches_approval_rules(tool, arguments):
        return response(
            "ask",
            "Approval rules (local policy, host settings, permission hook) change only by a "
            "human: confirm this exact change yourself, never to get past a refusal.",
        )
    if policy == "autonomous" and autonomous_passes(tool, arguments):
        return {}
    return response(
        "ask",
        "Confirm this exact tool call, target and arguments. Unknown effects require review; "
        "previous approval does not authorize changed arguments or replay after an unknown outcome.",
    )


def autonomous_passes(tool: str, arguments: dict) -> bool:
    """Vrai pour un appel local courant, faux pour une phase importante."""
    if tool in SHELL_TOOLS:
        command = arguments.get("command")
        return isinstance(command, str) and not IMPORTANT_COMMAND.search(command)
    return (tool in EDIT_TOOLS or tool in DELEGATION_TOOLS or tool in HARNESS_TOOLS
            or tool.startswith(AUTONOMOUS_MCP_PREFIXES))


def touches_approval_rules(tool: str, arguments: dict) -> bool:
    """Vrai si l'appel change une regle d'approbation, dans les deux dialectes."""
    if tool in SHELL_TOOLS:
        command = arguments.get("command")
        return isinstance(command, str) and bool(APPROVAL_COMMAND.search(command))
    if tool in {"Skill", "SlashCommand"}:
        name = arguments.get("skill") or arguments.get("command") or ""
        return isinstance(name, str) and "autonomie" in name.lower()
    targets = [arguments.get(key) for key in ("file_path", "filePath", "path", "notebook_path")]
    patch = arguments.get("input")
    if isinstance(patch, str):
        targets.extend(PATCH_TARGET.findall(patch))
    for target in targets:
        if isinstance(target, str):
            normalized = "/" + target.strip().replace("\\", "/").lower()
            if normalized.endswith(tuple("/" + name for name in APPROVAL_FILES)):
                return True
    return False


def load_policy(environ: Mapping[str, str] | None = None, policy_file: Path = POLICY_FILE) -> str:
    """Politique choisie par l'hote ; tout doute retombe sur ``confirm``."""
    environ = os.environ if environ is None else environ
    value = environ.get("RF_AGENT_POLICY")
    if value is None:
        try:
            value = json.loads(policy_file.read_text(encoding="utf-8")).get("policy")
        except (OSError, ValueError, AttributeError):
            value = None
    return value if value in POLICIES else "confirm"


def response(verdict: str, reason: str) -> dict:
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": verdict,
        "permissionDecisionReason": reason,
    }}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        mode = os.environ.get("RF_AGENT_READ_ONLY", "0")
        if mode not in {"0", "1"}:
            raise ValueError("Invalid policy mode")
        result = decision(payload, read_only=mode == "1", policy=load_policy())
    except Exception:
        result = response("deny", "Permission hook failed; execution is denied.")
    print(json.dumps(result))
    return 2 if result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny" else 0


if __name__ == "__main__":
    sys.exit(main())
