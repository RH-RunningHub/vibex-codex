---
name: vibex-coding
description: Read and safely modify an owned VibeX project at an immutable source revision. Use when the user asks to implement, fix, redesign, or otherwise edit project source while preserving revision, path, lease, fencing, validation, and preview boundaries.
---

# VibeX Coding

Make bounded source changes through an isolated edit session. Never write a changing live worktree or publish from this skill.

## Workflow

1. Use `$vibex-projects` to resolve one project, then call `vibex_get_project` immediately before planning.
2. Retain the returned stable `source_revision`. Read only the necessary tree pages and files with `vibex_get_source_tree` and `vibex_read_source_file` using that exact revision.
3. Show a short implementation plan that names every file expected to change. Do not silently widen it.
4. Compute a stable hash of the displayed plan and call `vibex_begin_edit` with the revision, plan hash, exact changed paths, and a fresh idempotency key.
5. Apply bounded patches with `vibex_apply_patch`. Pass only approved paths and the returned edit intent, session, lease revision, and fencing token.
6. If work approaches the lease renewal time, call `vibex_renew_edit` before continuing. A renewal never changes the approved paths.
7. Call `vibex_commit_edit` with the returned staging hash and a fresh idempotency key. Poll any asynchronous operation rather than repeating commit.
8. On success, retain the new stable revision and hand off to `$vibex-preview`.

Use `vibex_cancel_edit` when the user cancels or when uncommitted work cannot safely continue. Cancel discards only the isolated uncommitted workspace.

## Fail-closed recovery

- On an authentication or scope error, use the Codex-managed OAuth flow to request only `vibex.projects.read` for source reads or `vibex.projects.edit` for edit-session operations, then resume the same bounded workflow. Never request preview or publish access from this skill.
- On `SOURCE_CHANGED`, discard assumptions, fetch the latest project, reread the needed files, and make a new plan. Never replay the old patch.
- On an expired lease or stale fencing token, do not retry a write with old values. Start a new edit from the latest stable revision.
- On a path-policy, patch, validation, or staging-hash error, keep the stable revision unchanged and report the exact safe error code.
- On an uncertain commit operation, query `vibex_get_operation_status`; do not submit a second commit.

## Boundaries

- Modify only paths shown in the plan and accepted by the service.
- Never request hidden files, credentials, platform-managed files, arbitrary shell access, or arbitrary HTTP access.
- Editing success does not imply preview success and never implies permission to publish.
