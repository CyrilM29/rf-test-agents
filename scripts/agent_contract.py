"""Contrats de mission et verdicts, controles hors application testee."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = 2
# Schéma 1 : les sidecars signés avant que les agents portent une version
# (2026-09-29). Toujours valides, jamais réécrits pour paraître récents.
LEGACY_SCHEMA_VERSIONS = frozenset({1})
_BASE_FIELDS = frozenset({"schema_version", "mission_id", "target", "invariant",
                          "scope", "mode", "budgets", "evidence"})
_RELEASE_VERSION = re.compile(r"\d+\.\d+\.\d+")
HEAL_VERDICTS = frozenset({
    "repaired_verified", "application_defect", "blocked", "needs_human", "not_verified",
})


def identifier(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
        raise ValueError("Expected a non-sensitive identifier")
    return value


def confined_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("Expected a relative artifact path")
    path = (root / value).resolve()
    if Path(value).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError("Artifact path escapes the workspace")
    return path


def validate_producer(value: object) -> dict:
    """The agent that signed the handoff, and the version its definition carried.

    Schema 2 names it so a plan can be traced to the agent release that wrote
    it; the version is the definition's `version` front-matter field."""
    if not isinstance(value, dict) or set(value) != {"agent", "version"}:
        raise ValueError("Invalid producer fields")
    identifier(value["agent"])
    if not isinstance(value["version"], str) or not _RELEASE_VERSION.fullmatch(value["version"]):
        raise ValueError("Producer version must be X.Y.Z")
    return value


def validate_handoff(data: object, root: Path) -> dict:
    if not isinstance(data, dict) or "schema_version" not in data:
        raise ValueError("Invalid handoff fields")
    schema = data["schema_version"]
    if type(schema) is not int or schema not in LEGACY_SCHEMA_VERSIONS | {SCHEMA_VERSION}:
        raise ValueError("Unsupported handoff schema")
    required = _BASE_FIELDS | ({"producer"} if schema == SCHEMA_VERSION else set())
    if set(data) != required:
        raise ValueError("Invalid handoff fields")
    if schema == SCHEMA_VERSION:
        validate_producer(data["producer"])
    identifier(data["mission_id"])
    identifier(data["target"])
    if not isinstance(data["invariant"], str) or not data["invariant"].strip():
        raise ValueError("Missing business invariant")
    if data["mode"] not in {"read_only", "explore", "full"}:
        raise ValueError("Invalid mission mode")
    if not isinstance(data["scope"], list) or not data["scope"]:
        raise ValueError("Missing authorized scope")
    for item in data["scope"]:
        confined_path(root, item)
    budgets = data["budgets"]
    if not isinstance(budgets, dict) or set(budgets) != {"attempts", "tool_calls", "seconds"}:
        raise ValueError("Invalid budget fields")
    if any(type(value) is not int or value <= 0 for value in budgets.values()):
        raise ValueError("Budgets must be positive integers")
    evidence = data["evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("Missing evidence")
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise ValueError("Invalid evidence fields")
        path = confined_path(root, item["path"])
        if not path.is_file():
            raise ValueError("Evidence file is missing")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Evidence hash mismatch")
    return data


def heal_verdict(facts: dict) -> str:
    required = {"failure_class", "target_matches", "invariant_preserved",
                "replay_passed", "scope_complete", "new_skips", "new_baselines",
                "evidence_checked", "budget_exhausted", "unknown_write_outcome"}
    if not isinstance(facts, dict) or set(facts) != required:
        raise ValueError("Incomplete verdict facts")
    for key in required - {"failure_class", "new_skips", "new_baselines"}:
        if type(facts[key]) is not bool:
            raise ValueError("Verdict flags must be booleans")
    for key in ("new_skips", "new_baselines"):
        if type(facts[key]) is not int or facts[key] < 0:
            raise ValueError("Verdict counts must be non-negative integers")
    category = facts["failure_class"]
    if category not in {"locator_drift", "timing", "data_drift", "library_defect",
                        "functional_change", "application_defect", "unknown"}:
        raise ValueError("Unknown failure class")
    if not facts["target_matches"] or facts["unknown_write_outcome"]:
        return "needs_human"
    if not facts["evidence_checked"]:
        return "not_verified"
    if category == "application_defect":
        return "application_defect"
    if category in {"functional_change", "data_drift"}:
        return "needs_human"
    if facts["new_skips"] or facts["new_baselines"] or not facts["invariant_preserved"]:
        return "needs_human"
    if facts["budget_exhausted"]:
        return "blocked"
    if category == "unknown" or not facts["replay_passed"] or not facts["scope_complete"]:
        return "not_verified"
    return "repaired_verified"


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["handoff", "verdict"])
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.artifact.read_text(encoding="utf-8-sig"))
        if args.operation == "handoff":
            validate_handoff(data, args.root)
            print("Handoff structure and evidence hashes verified; business truth not inferred.")
            return 0
        result = heal_verdict(data)
        print(json.dumps({"verdict": result, "basis": "supplied facts, independent review required"}))
        return 0 if result == "repaired_verified" else 1
    except (ValueError, TypeError, OSError):
        print("Invalid or unreadable agent artifact.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
