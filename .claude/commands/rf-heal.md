---
description: Réparer un test Robot Framework en échec, diagnostic, vérification live via rf-mcp, patch de la couche resources (agent rf-healer)
---

Use the **rf-healer** agent to repair the failing Robot Framework test(s):
$ARGUMENTS

If the arguments do not identify the failure, ask the user for the failing
suite/test name (or the `robot` output / `output.xml` path), plus the
variables needed to reproduce; never invent credentials.

Then launch the agent, wait for its result, and relay its report (root causes,
each repair as before → after with its live evidence, final robot run status,
tests skipped with reasons) to the user.
