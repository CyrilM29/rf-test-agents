# memory/: AI assistants' project memory

Persistent working notes for AI assistants (Claude Code, GitHub Copilot,
Codex…) working on this repo. **Committed and public-safe**: non-negotiable
rules:

1. **Anonymized**: no personal data (name, e-mail, account), no machine
   paths, no private URLs, no secrets. Anything personal, machine-bound or
   cross-project belongs in the user's private memory base, never here.
2. **One entry = one durable project fact**: a costly debugging lesson, a
   decision with its context, a generic environment procedure. No session
   journals, no duplication of the repo docs (CLAUDE.md stays canonical).
3. **Absolute dates**; an entry is a dated observation, not live state:
   verify before asserting.
4. **`MEMORY.md` is the index**: one line per entry, updated in the same
   operation as any create/delete. Update rather than duplicate; delete what
   has become wrong.

Entry format:

```markdown
---
name: slug-kebab-case
description: one-line summary, decides whether the entry gets opened
type: projet | reference | recherche
date: YYYY-MM-DD
---

The fact. **Why:** the context. **How to apply:** the concrete move.
```
