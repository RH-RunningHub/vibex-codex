---
name: vibex-publish
description: Prepare, confirm, execute, and verify publication of an owned VibeX project at an exact stable revision. Use only when the user explicitly asks to publish, deploy publicly, or release a project; never infer authorization from editing or preview completion.
---

# VibeX Publish

Publishing is a separate, explicit two-step confirmation flow.

## Prepare

1. Confirm the user explicitly requested publication. Phrases such as “改完了”, “预览通过”, or “继续” are not publication authorization.
2. Call `vibex_get_project` and identify the exact stable revision.
3. Call `vibex_prepare_publish` with that revision, target, visibility, and a fresh idempotency key. If the service reports an authentication or scope error, renew the complete VibeX OAuth connection, then retry the same request with the same idempotency key.
4. Show the returned project, revision, target, visibility, address options, and confirmation digest in a concise summary.
5. Ask the user to explicitly confirm that exact summary. Do not call the publish tool in the same step unless the user's current message already unambiguously confirms the displayed summary.

## Publish and verify

After explicit confirmation, call `vibex_publish_project` with the single-use intent ID, exact confirmation digest, and a fresh idempotency key. Poll `vibex_get_operation_status` until terminal.

When successful, report the public result and verify the returned address when the client can safely do so. If verification fails or state is uncertain, query operation status and report the recovery guidance; do not create a second release.

## Invalidation rules

If project owner, source revision, target, visibility, slug, domain, or options change, discard the old confirmation and prepare a new one. An expired or consumed intent cannot be reused.

Never publish from `$vibex-coding` or `$vibex-preview`, and never treat a successful preview as confirmation.
