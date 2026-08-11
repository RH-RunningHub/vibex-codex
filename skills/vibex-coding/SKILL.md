---
name: vibex-coding
description: Read and safely modify an owned VibeX project at an immutable source revision. Use when the user asks to implement, fix, redesign, or otherwise edit project source while preserving revision, path, lease, fencing, validation, and preview boundaries.
---

# VibeX Coding

Make bounded source changes through an isolated edit session. Never write a changing live worktree or publish from this skill.

## Workflow

1. Use `$vibex-projects` to resolve one project, then call `vibex_get_project` immediately before planning.
2. If `source_revision` is absent and the project advertises `capabilities.source_initialize=true`, call `vibex_initialize_source` once, then call `vibex_get_project` again and retain its new stable revision. Do not initialize projects that do not advertise this capability.
3. Retain the returned stable `source_revision`. Read only the necessary tree pages and files with `vibex_get_source_tree` and `vibex_read_source_file` using that exact revision. Workspace files, historical ZIPs, conversation text, and `AGENTS.md` may constrain behavior but are never evidence of the current VibeX source version.
4. Show a short implementation plan that names every file expected to change. Do not silently widen it.
5. Compute a stable hash of the displayed plan and call `vibex_begin_edit` with the revision, plan hash, exact changed paths, and a fresh idempotency key.
6. Apply bounded patches with `vibex_apply_patch`. Send one standard unified diff with `---`, `+++`, and numbered `@@` hunk headers, combining all approved changed files in one call where practical. Never send Codex `*** Begin Patch` / `*** Update File` wrapper syntax. Pass only approved paths and the returned edit intent, session, lease revision, and fencing token.
7. If work approaches the lease renewal time, call `vibex_renew_edit` before continuing. A renewal never changes the approved paths.
8. Call `vibex_commit_edit` with the returned staging hash and a fresh idempotency key. Poll any asynchronous operation rather than repeating commit.
9. On success, retain the new stable revision and hand off to `$vibex-preview`.

Use `vibex_cancel_edit` when the user cancels or when uncommitted work cannot safely continue. Cancel discards only the isolated uncommitted workspace.

## Fail-closed recovery

- On an authentication or scope error, renew the complete Codex-managed VibeX OAuth connection, then resume the same bounded workflow. The connection grant never widens the current edit plan or authorizes preview or publication.
- On `CONTROL_TIMEOUT` or another uncertain transport result, retry the exact same request with the exact same idempotency key. Do not cancel the edit or create a replacement session until the original operation is confirmed failed. If an `operation_id` was returned, poll it with bounded exponential backoff; tolerate isolated poll failures, reset the consecutive-failure counter after a successful poll, and stop immediately on a terminal business failure.
- On `SOURCE_CHANGED`, discard assumptions, fetch the latest project, reread the needed files, and make a new plan. Never replay the old patch.
- On an expired lease or stale fencing token, do not retry a write with old values. Fetch the project again and wait for the server to reap the expired session. Start a new edit from the latest stable revision only after the project reports `source_state=CLEAN`; if it remains `EDITING`, report the stuck session instead of repeatedly calling `vibex_begin_edit`.
- On a path-policy, patch, validation, or staging-hash error, keep the stable revision unchanged and report the exact safe error code.
- On an uncertain commit operation, query `vibex_get_operation_status`; do not submit a second commit.

## Boundaries

- Modify only paths shown in the plan and accepted by the service.
- Never request hidden files, credentials, platform-managed files, arbitrary shell access, or arbitrary HTTP access.
- Editing success does not imply preview success and never implies permission to publish.
