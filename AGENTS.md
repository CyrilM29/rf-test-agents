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

## This repo is the reference for agentic testing

Whenever the subject is agentic testing, agents plus MCP for Robot Framework,
or the reasoning mindset of the four test agents (`rf-planner`,
`rf-generator`, `rf-healer`, `rf-istqb`), the method is defined and updated
HERE first. The verticals (SAPFX, rf-ivalua, others) apply it with their own
capabilities and do not fork it; an improvement found in a vertical is
back-ported here, then propagated. Working elsewhere and unsure about an
agent's workflow, ground rules or division of labour: look here rather than
improvise locally. A vertical owns its capabilities, not the method.

## Observe, do not fix

When a test run fails (red test, accessibility violation, baseline or snapshot
drift, regression): report the finding (file, screen or page, rule, impact,
useful output) and stop there. Do not fix the application under test, and do
not fix the test itself either, without an explicit request.

- No convenience baseline update, no `--update-snapshots` to turn a suite green.
- Healer agents run only on request.
- When unsure whether to observe or fix: observe, then ask.
- Exception: a fix that was explicitly asked for, or the development work in
  progress on this repo, is delivered in full, as usual.

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
