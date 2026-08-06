# AGENTS.md

Condensed guide for AI coding assistants. **`CLAUDE.md` is the canonical
guide** (layout, agent definitions, conventions, rf-mcp compatibility notes):
read it first. Respond to the user in French; keywords/identifiers stay in
English.

Never use the em dash (« — ») anywhere in this repo (docs, READMEs, specs,
docstrings, comments, emitted strings, workflows, config): use a colon, a
comma, parentheses, or split the sentence (French puts a space before the
colon, English does not). Enforced by `scripts/check_no_em_dash.py` (CI +
`PostToolUse` hook + unit test).

## Memory (three coexisting layers)

1. **Project memory (this repo, public-safe)**: `memory/` at the repo root,
   anonymized durable project facts (no personal data, no machine paths, no
   private URLs); index `memory/MEMORY.md`, rules in `memory/README.md`.
2. **Private cross-project base**: `E:\QA_GenAI\agent-memory\`, user
   profile/preferences, machine specifics, cross-project facts, research
   notes; contract in its `PROTOCOLE.md`. Never published.
3. **Claude Code auto-memory** (Claude only): internal pointers, no
   duplication of the other layers.

Read both indexes at session start. New fact: publishable + project-specific
→ layer 1; personal/machine/cross-project → layer 2. One fact per file,
update the index in the same operation, never secrets anywhere.
