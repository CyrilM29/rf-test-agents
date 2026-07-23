---
description: Générer une suite Robot Framework depuis un plan specs/, chaque étape vérifiée live via rf-mcp (agent rf-generator)
---

Use the **rf-generator** agent to turn a plan from `specs/` into an executable
Robot Framework suite under `tests/robot/`, for: $ARGUMENTS

If the arguments do not name a spec file, list `specs/*.md` (excluding
README.md) and ask the user which plan to generate — or suggest running
`/rf-plan` first when `specs/` is empty. Pass the user's connection variables
(base URL, user…) through to the agent; never invent credentials.

Then launch the agent, wait for its result, and relay its report (suite path,
spec ↔ test mapping, keywords added to the resource layer, dry-run and
live-run results) to the user.
