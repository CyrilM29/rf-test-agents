# GitHub Copilot instructions

**`CLAUDE.md` at the repo root is the canonical guide** for this project
(universal Robot Framework test agents — plan → generate → heal over rf-mcp):
read and apply it whatever assistant is in use. Respond to the user in French.

## Memory (three coexisting layers)

1. **Project memory (this repo, public-safe)**: `memory/` at the repo root —
   anonymized durable project facts (no personal data, no machine paths, no
   private URLs); index `memory/MEMORY.md`, rules in `memory/README.md`.
2. **Private cross-project base**: `E:\QA_GenAI\agent-memory\` (add it to the
   VS Code workspace to read/write it natively) — user profile/preferences,
   machine specifics, cross-project facts, research notes; contract in its
   `PROTOCOLE.md`. Never published.
3. **Claude Code auto-memory** (Claude only) — do not duplicate it.

Read both indexes at the start of a task. New fact: publishable +
project-specific → layer 1; personal/machine/cross-project → layer 2. One
fact per file, update the index in the same operation, never secrets anywhere.
