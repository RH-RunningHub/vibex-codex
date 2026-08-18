---
name: vibex-publish
description: Prepare, confirm, execute, and verify publication of an owned VibeX project at an exact stable revision. Use only when the user explicitly asks to publish, deploy publicly, or release a project; never infer authorization from editing or preview completion.
---

# VibeX Publish

Publishing is a separate, explicit confirmation flow. Never use a browser upload path as a fallback for an MCP failure.

## Authentication recovery

For every VibeX MCP call, if the transport reports an expired token, `AUTH_REQUIRED`, `invalid_token`, or an OAuth refresh failure:

1. Retry the same tool call once with exactly the same arguments and idempotency key. This retry asks the MCP host to refresh or reopen the VibeX OAuth connection automatically.
2. If authorization still fails, stop. Ask the user to reconnect **vibex-codex** using **MCP server settings → Initiate authorization**, then resume the same step after authorization. Do not switch to Browser, local files, or another upload channel.

## Readiness and form

1. Confirm that the user explicitly requested publication. “改完了”, “预览通过”, and “继续” are not publication authorization.
2. Call `vibex_get_project` and pin its exact stable `source_revision`.
3. Call `vibex_get_publish_readiness` for that revision before presenting publish choices.
   - If `ready` is false, show the returned blocker or server-unavailable message and stop.
   - Do not prepare or execute a publish while readiness is blocked or unknown.
4. Call `vibex_get_publish_form` and display every returned user-visible value, default, option, and constraint. The server response is authoritative; the known fields include:
   - Render `cover.url` as a Markdown image when present. State clearly when no cover exists.
   - Title and summary.
   - Test or production environment.
   - Private or public visibility.
   - Whether to submit to the Inspiration Gallery. This is separate from public visibility.
   - Gallery category, subcategory, and industry when gallery submission is enabled.
   - Whether remixing is allowed.
   - URL mode and slug when applicable.
   - Whether development backend data will be reset.
   - Creator pricing: configured and effective percentages, synchronization state, whether this release activates pricing, and whether the pricing revision is still current.
5. Also surface any newly returned field that is not in the known list. Preserve its server-provided name, value, choices, dependency, and constraint instead of silently dropping it. If its effect is unclear or the server does not provide a safe selectable/default value, stop before preparation and explain which field needs an updated contract or product decision.
6. Ask the user to confirm or change every value. Never silently reuse defaults for a destructive or public-facing option.

## Prepare and explicit confirmation

Call `vibex_prepare_publish` with all selected values accepted by the current tool schema and a fresh idempotency key. Build the human-readable confirmation card from the returned `confirmation` object, not from a hard-coded client field list. Show every returned confirmation field, including the cover, title, summary, revision, environment, visibility, gallery settings, category, remix setting, URL choice, data-reset setting, creator pricing, and any field added by a newer server contract.

Put `confirmation_digest` under a short “technical details” section; the digest is not the confirmation UI. Ask the user to explicitly confirm that exact card. If pricing configuration changed after preparation, discard the intent and prepare again. Do not call `vibex_publish_project` in the same step unless the current user message already unambiguously confirms the complete displayed card.

Any change to the project owner, source revision, cover, title, summary, target, visibility, gallery settings, categories, remix setting, URL/slug, domain, or reset setting invalidates the old intent. Prepare a new one.

If the server adds another confirmation-bound field, treat changing that field as invalidating the old intent too. Never reconstruct, omit, rename, or normalize an unfamiliar confirmation value on the client; display the returned value and require the user to confirm the complete card.

## Publish and poll

After explicit confirmation, call `vibex_publish_project` once with the single-use intent ID, exact digest, and a fresh idempotency key. A normal response is `QUEUED` or `RUNNING`; do not wait on the original publish request and do not submit a duplicate publish.

Poll `vibex_get_operation_status` until a terminal state:

- Poll after 2, 4, 8, then 10 seconds, capped at 10 seconds.
- Parse only structured `state`, `phase`, `error_code`, `retryable`, `next_action`, and `error_detail` fields.
- Reset the consecutive transport-failure count after any successful response.
- After five consecutive transport failures, stop polling and report that the result is unknown. Keep the operation ID for later recovery; never create another release automatically.
- `FAILED`, `CANCELED`, and `TIMED_OUT` are terminal. Show the server error and guidance; do not automatically retry a business failure. When `error_detail` is present (for example an audit verdict with a bounded findings summary), show its rule IDs, messages, and affected files so the user knows exactly why the publish was rejected and what to fix.
- `UNKNOWN` means recovery is required. Report it and do not republish.
- For a long-running operation, give a concise phase update at least every 30 seconds.

On `SUCCEEDED`, show the publish URL and verify it when the client can safely do so. A verification failure does not authorize a second publish; query the same operation instead.

Never publish from `$vibex-coding` or `$vibex-preview`, and never treat a successful preview as confirmation.
