---
description: Activer, désactiver ou consulter le mode autonome du hook de permissions (politique locale du poste)
argument-hint: on | off | status
disable-model-invocation: true
---

The workstation owner invoked this command to set the local policy of the
PreToolUse permission hook. Argument: `on`, `off` or `status` (no argument
means `status`): $ARGUMENTS

Run exactly `python scripts/agent_policy.py <argument>` from the repository
root, then relay its output to the user in French, in one or two lines.

For `on` and `off`, the permission hook asks the owner to confirm the run:
that is expected, approval rules change only by a human. Never retry, reword
or route around that confirmation.

This command is the owner's explicit request. Never run
`scripts/agent_policy.py on` on your own initiative, from another command or
to get past a confirmation: the contract forbids changing approval rules to
bypass a denial.
