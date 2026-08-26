---
name: vibex-capabilities
description: Inspect and safely configure the canonical CC capabilities of an owned VibeX project. Use when the user asks which capabilities are required or optional, whether a selectable capability is enabled, or asks to enable or disable an optional capability.
---

# VibeX Project Capabilities

Treat `vibex_list_capabilities` and `vibex_get_project_capabilities` as
authoritative. Capabilities are split by the project's locked flow into
required (always on, cannot be disabled) and optional (user-toggleable). Do
not hard-code a complete capability list. Names such as `rh-login`,
`design-open-design`, `local-auth`, or `rh-agent` are examples only; the
server-returned `required` and `optional` lists for this project are the
source of truth.

## Inspect

1. Resolve exactly one owned project with `$vibex-projects`.
2. Call `vibex_list_capabilities` to read the current catalog version and hash.
3. Call `vibex_get_project_capabilities` immediately before proposing a change.
4. Show required capabilities as locked. Show each returned optional
   capability with its current enabled state. Do not infer state from source
   files. Do not offer to change the project's flow; the flow is locked after
   creation.

## Prepare and confirm

Call `vibex_prepare_capability_change` with the exact `config_revision`, the
complete target list of optional enabled capabilities, and a fresh
idempotency key. Preparing does not change the project.

Never include a capability that the server did not return in `optional`.
Hidden required items are not user-toggleable and must not be switched by
the assistant. Never propose enabling two capabilities that conflict; treat
the returned `conflicts` field as authoritative. `local-auth` and
`rh-login` are one such mutually exclusive pair.

If the target list enables `local-auth`, state explicitly that live AI usage
for this published app will switch to the creator's owner billing, and
obtain confirmation of that billing change before applying.

Show the returned before/after summary and state explicitly that the change:

- does not edit or roll back source;
- does not publish;
- does not change the active published snapshot;
- does not change the project's flow;
- may remain pending while a coding task is active and will apply automatically.

Ask the user to explicitly confirm this exact summary, including any
owner-billing consequence. A previous edit, preview, pricing, rollback, or
publish confirmation does not authorize a capability change. Any changed
project, revision, target list, catalog hash, or digest invalidates the
intent.

## Apply and verify

After explicit confirmation, call `vibex_set_project_capabilities` once with
the intent ID, exact digest, and a fresh idempotency key. Retry an uncertain
transport result only with identical arguments and the same key. Then call
`vibex_get_project_capabilities` and report `applied` or `pending`
accurately. Report the returned `billing_mode` as-is; do not infer or omit
it.

Never toggle a capability by editing application files. Disabling a
capability must not delete capability-created source or data. Never publish
from this skill.
