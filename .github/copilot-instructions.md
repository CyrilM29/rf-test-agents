# GitHub Copilot instructions

**`CLAUDE.md` at the repo root is the canonical guide** for this project
(universal Robot Framework test agents: plan → generate → heal over rf-mcp, plus the offline rf-istqb ISTQB designer):
read and apply it whatever assistant is in use. Respond to the user in French.

Never use the em dash (« — ») anywhere in this repo (docs, READMEs, specs,
docstrings, comments, emitted strings, workflows, config): use a colon, a
comma, parentheses, or split the sentence (French puts a space before the
colon, English does not). Enforced by `scripts/check_no_em_dash.py` (CI +
`PostToolUse` hook + unit test).

## Memory (three coexisting layers)

1. **Project memory (this repo, public-safe)**: `memory/` at the repo root,
   anonymized durable project facts (no personal data, no machine paths, no
   private URLs); index `memory/MEMORY.md`, rules in `memory/README.md`.
2. **Private cross-project base**: `E:\QA_GenAI\agent-memory\` (add it to the
   VS Code workspace to read/write it natively): user profile/preferences,
   machine specifics, cross-project facts, research notes; contract in its
   `PROTOCOLE.md`. Never published.
3. **Claude Code auto-memory** (Claude only): do not duplicate it.

Read both indexes at the start of a task. New fact: publishable +
project-specific → layer 1; personal/machine/cross-project → layer 2. One
fact per file, update the index in the same operation, never secrets anywhere.
