---
description: ISTQB, deux modes hors ligne : concevoir un plan de test + cas de test rejouables depuis un plan specs/ ou une sortie recorder, ou REVOIR une suite générée (rapport daté et verdict sous specs/istqb/revues/) (agent rf-istqb)
argument-hint: <conception | revue> <plan, sortie recorder, suite ou slug>
---

Use the **rf-istqb** agent for: $ARGUMENTS

Pick the mode from the arguments (first word `conception` or `revue`, or the
wording: a suite to judge means review, a plan or a recorder output to
formalize means design). If it is ambiguous, ask once, in French.

**Conception** : turn existing test material into an ISTQB test plan + test
cases under `specs/istqb/`. If the arguments do not name a source, list the
candidates (in French): `specs/*.md` plans (excluding README.md) and any
recorder output the workspace holds (rf-web-recorder exports: `*.robot`
suites, `*-plan.md` and `*-istqb.md` drafts) and ask which to use; suggest
`/rf-plan` or a recording session when nothing exists yet.

**Revue** : audit a generated suite against its plan and write the dated report
with a verdict under `specs/istqb/revues/<slug>.revue.md`. If the arguments do
not name a suite, list the suites under `tests/robot/` that carry a `Spec:`
marker and have no report in `specs/istqb/revues/`, and ask which to review.
The review comes AFTER `/rf-verify` (the verifier rules on the invariant and
the evidence, the ISTQB review on the test design); pass the verifier's verdict
and the run evidence when they exist. Give the agent the mission id
`istqb-revue-<slug>` for its handover trail.

Then launch the agent, wait for its result, and relay its French report to the
user: for a design, the document path, the test-case list with priorities,
traceability gaps and the « à compléter » items needing a human answer; for a
review, the report path, the verdict, the counts by severity, the main
findings and who acts on each.
