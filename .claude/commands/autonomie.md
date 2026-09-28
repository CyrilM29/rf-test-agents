---
description: Activer, désactiver ou consulter le mode autonome du hook de permissions (politique locale du poste)
---

The workstation owner invoked this command to set the local policy of the
PreToolUse permission hook. Argument: `on`, `off` or `status` (no argument
means `status`): $ARGUMENTS

Run exactly `python scripts/agent_policy.py <argument>` from the repository
root, then relay its output to the user in French, in one or two lines.

This command is the owner's explicit request. Never run
`scripts/agent_policy.py on` on your own initiative, from another command or
to get past a confirmation: the contract forbids changing approval rules to
bypass a denial.
