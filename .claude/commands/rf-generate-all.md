---
description: Générer/régénérer en lot toutes les suites depuis les plans specs/ (agents rf-generator successifs)
---

Generate (or regenerate) Robot Framework suites for EVERY eligible plan under
`specs/`, using the **rf-generator** agent one spec at a time: $ARGUMENTS

1. Build the work list: `specs/*.md` minus `README.md`,
   `couverture-proposee.md`, and any spec carrying the
   `> **Statut : PÉRIMÉE (…)**` marker (those must go back through `/rf-plan`
   first: list them to the user instead of generating). If
   `python scripts/check_spec_sync.py` reports suites already in phase with
   their spec, skip those specs unless the user asked for a full regeneration.
2. Confirm the work list with the user (specs kept, specs skipped and why),
   and collect once the connection variables shared by the runs (base URL,
   user…), never invent credentials.
3. Launch the rf-generator agent **sequentially, one spec per agent run**:
   never several in parallel: they would collide on `resources/` page objects
   and on the live application session.
4. After each run, relay the agent's report (suite path, gates, keywords
   added), then move to the next spec. Stop and ask the user if a generation
   fails its gates twice on the same spec.
5. Finish with `python scripts/check_spec_sync.py` and
   `python scripts/check_conventions.py`, and summarize: suites generated,
   suites skipped, specs left for `/rf-plan`.
