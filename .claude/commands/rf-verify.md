---
description: Independent read-only review of generated or healed tests and evidence
argument-hint: <spec, handoff, original/final artifacts and replay evidence>
---

Use the `rf-verifier` agent to review $ARGUMENTS against the original business
invariant. Read `.claude/agent-contract.md`. Do not repair, run tests or write
a report file. Missing inputs produce `not_verified`. Report findings and
evidence references in the conversation, with a separate verifier verdict.