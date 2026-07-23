---
description: Explorer une application live (via rf-mcp) et produire un plan de test dans specs/ (agent rf-planner)
---

Use the **rf-planner** agent to explore the target application and produce a
test plan under `specs/` for: $ARGUMENTS

If the arguments do not say so, first ask the user for:
- the channel — web (URL), API (base URL), mobile (app under test)…;
- the business goal to cover;
- the access (URL/endpoint + user) — never invent credentials.

Then launch the agent, wait for its result, and relay its report (spec path,
scenarios, observed data, missing business keywords) to the user.
