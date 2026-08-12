---
name: vibex-capabilities
description: Inspect and safely configure the canonical CC capabilities of an owned VibeX project. Use when the user asks which capabilities are built in, whether Agent is enabled, or asks to enable or disable a selectable capability.
---

# VibeX Project Capabilities

Use the CC catalog as authoritative. Standard business capabilities are built in
and cannot be disabled. `rh-agent` is selectable and defaults to off.

## Inspect

1. Resolve exactly one owned project with `$vibex-projects`.
2. Call `vibex_list_capabilities` to read the current catalog version and hash.
3. Call `vibex_get_project_capabilities` immediately before proposing a change.
4. Show built-in capabilities as locked and show the current Agent state. Do not
   infer state from source files.

## Prepare and confirm

Call `vibex_prepare_capability_change` with the exact `config_revision`, the
complete target list of selectable enabled capabilities, and a fresh idempotency
key. Preparing does not change the project.

Show the returned before/after summary and state explicitly that the change:

- does not edit or roll back source;
- does not publish;
- does not change the active published snapshot;
- may remain pending while a coding task is active and will apply automatically.

Ask the user to explicitly confirm this exact summary. A previous edit, preview,
pricing, rollback, or publish confirmation does not authorize a capability
change. Any changed project, revision, target list, catalog hash, or digest
invalidates the intent.

## Apply and verify

After explicit confirmation, call `vibex_set_project_capabilities` once with the
intent ID, exact digest, and a fresh idempotency key. Retry an uncertain transport
result only with identical arguments and the same key. Then call
`vibex_get_project_capabilities` and report `applied` or `pending` accurately.

Never toggle a capability by editing application files. Disabling Agent must not
delete Agent-created source or data. Never publish from this skill.
