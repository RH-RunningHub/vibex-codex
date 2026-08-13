---
name: vibex-maintenance
description: Diagnose and maintain an owned VibeX project using redacted health checks, immutable revision history and comparison, explicitly confirmed rollback, explicitly confirmed cover generation, user-uploaded 16:9 covers, and privacy-safe aggregate metrics. Use when the user asks about project health, errors, versions, rollback, covers, uploading a cover image, traffic, visitors, or task success.
---

# VibeX maintenance

Operate on one owned project and begin with `vibex_get_project` to capture its current stable `source_revision`.

## Read-only checks

- Use `vibex_get_diagnostics` for health. Report returned checks and safe error codes only; do not infer or request internal hosts, logs, paths, or credentials.
- Use `vibex_list_revisions` before history work. Use `vibex_compare_revisions` for the exact two immutable revisions and note when the bounded path list is truncated.
- Use `vibex_get_cover` to show the saved HTTPS CDN cover and current generation-job state. Never claim that a generated preview is saved or published unless the returned state says so.
- Use `vibex_get_project_metrics` for a 1–90 day window. Report only aggregate views, visitors, and task outcomes; never ask for visitor or task identifiers.

## Confirmed rollback

1. Verify there is no active edit and refresh the current project revision.
2. Show the target revision, revision comparison, and the fact that current source will be replaced.
3. Call `vibex_prepare_rollback` with the current and target revisions and a fresh idempotency key.
4. Display the complete returned confirmation card. Ask for explicit confirmation of that exact card.
5. Only after confirmation, call `vibex_rollback_project` once with the single-use intent, exact digest, and a fresh idempotency key.
6. Call `vibex_get_project` and `vibex_list_revisions` again. Never publish automatically.

If the source revision changes, the intent expires, the result is uncertain, or recovery is required, stop and report the actual state. Do not submit another rollback to guess.

## Confirmed cover generation

1. Call `vibex_get_cover` and show the current cover.
2. Collect and display the exact title and summary that will guide generation.
3. Call `vibex_prepare_cover_generation` with the stable revision and a fresh idempotency key.
4. Display its complete confirmation card and wait for explicit confirmation.
5. Call `vibex_generate_cover` once, then poll `vibex_get_cover` with bounded backoff until success, failure, or a clear timeout. When generation succeeds, report the returned CDN cover URL.

Cover confirmation is not publish confirmation. Never call `vibex_publish_project` from this skill.

## Cover upload

1. Call `vibex_get_cover` and show the current saved cover.
2. Only after the user explicitly asks to use their image as the cover, call `vibex_upload_cover` with a `data:image/png|jpeg|webp;base64,...` payload and a fresh idempotency key.
3. Report the returned public CDN HTTPS cover URL, 16:9 output size, and whether the image was center-cropped. Never stretch the source image, never treat a page-asset CDN URL from `vibex_upload_project_image` as a saved cover, and never publish.

Cover upload replaces the saved cover immediately with a content-addressed CDN object. It does not publish the project.

On authentication or scope errors, use the Codex-managed OAuth renewal flow and resume the same bounded request. The existing seven scopes cover these tools; do not request an extra scope.
