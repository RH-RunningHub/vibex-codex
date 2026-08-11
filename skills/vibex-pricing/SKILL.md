---
name: vibex-pricing
description: Safely inspect, enable, prepare, confirm, apply, and verify VibeX creator pricing for an owned project. Use when the user asks about creator pricing, markup, custom pricing, visitor model-call prices, pricing eligibility, a pricing upgrade, changing a markup percentage, disabling markup, or whether a configured price is live.
---

# VibeX Creator Pricing

Treat creator pricing as a financial operation. Reading is safe; changing a
percentage requires a separate exact confirmation and never authorizes source
publication.

## Authentication recovery

For every VibeX MCP call, retry the same call once with identical arguments and
idempotency key after `AUTH_REQUIRED`, `invalid_token`, an expired token, or an
OAuth refresh failure. This asks the host to refresh or reopen the complete
six-scope VibeX connection. If it still fails, stop and ask the user to open
**Plugins → vibex-codex → MCP server → Settings → Initiate authorization**.
Never switch to browser upload, local files, or another channel.

## Inspect exact state

1. Use `$vibex-projects` to resolve exactly one owned project.
2. Call `vibex_get_project` immediately before acting and retain its stable
   `source_revision`.
3. Call `vibex_get_pricing` with that exact revision.
4. Show the configured percentage, effective percentage, maximum, synchronization
   state, and whether publication is still required. Do not claim that a saved
   percentage is live when `effective_markup_bps` is zero or
   `requires_republish=true`.

Follow the server result:

- `pricing_not_available_for_account`: explain that creator pricing is not
  enabled for this account. Do not attempt a write.
- `explain_ai_app_revenue_model_and_do_not_upgrade`: explain that this project
  uses a platform AI application whose revenue follows the AI-application author
  model. Do not edit source to add pricing markers. Offer migration to direct
  model APIs only if the user explicitly asks for that product change.
- `upgrade_pricing_capability`: explain that the source needs a bounded upgrade.
  Do not begin editing until the user approves that source change.
- `publish_supported_source_before_claiming_pricing_is_live`: state that the
  development source supports pricing but the active public release does not.
- `wait_for_pricing_sync` or `show_pricing_sync_failure`: report the actual RH
  synchronization state instead of preparing another write.

Setting `0%` disables markup and must not require a source upgrade.

## Upgrade an eligible old project

Use `$vibex-coding` and its revision, path, lease, fencing, commit, and preview
boundaries. Keep the change limited to the hook that actually performs the
RunningHub standard-model request.

1. Search the revision-pinned `pb_hooks/*.pb.js` files for the real outbound
   `/openapi/v2/` request. Do not assume the filename is `aigc.pb.js` and do not
   create an unused empty hook.
2. If the only outbound endpoint contains `/run/ai-app/`, stop; that channel is
   not eligible for creator markup.
3. For a standard-model hook, make the smallest change that supplies all three
   runtime signals in the called code path:
   `@vibex-protocol: markup/1`, the `X-RH-Vibex-Ticket` request header, and the
   shared `ForwardRhHeaders(` helper (a local equivalent is acceptable).
4. Forward the ticket only on billable submit, price-preview, and upload calls;
   do not add it to read-only query calls. Preserve model parameters, business
   fields, routes, and defaults.
5. Commit the bounded edit, preview it, then call `vibex_get_project` and
   `vibex_get_pricing` again with the new stable revision. Never infer support
   from the patch itself.

An upgrade or preview does not authorize publishing.

## Prepare and confirm a percentage

Convert a user percentage to integer basis points exactly: `1% = 100 bps`.
Reject guesses and ask for the percentage when it is missing.

Call `vibex_prepare_pricing` with the exact stable revision, target basis points,
and a fresh idempotency key. This call does not change pricing. Display a
confirmation card containing:

- current and target percentages;
- visitor price per ¥1.00 base price;
- creator markup per ¥1.00 base price;
- whether the change affects visitor model-call prices;
- whether a new public release is required;
- source revision and expiration time.

Place `confirmation_digest` under a short technical-details section. Ask the
user to explicitly confirm that exact card. A generic “继续” from before the
card, an edit approval, a preview approval, or a publish approval is not pricing
confirmation. Any change to project, revision, current pricing revision, target
percentage, or confirmation card invalidates the intent.

## Apply and verify

After explicit confirmation, call `vibex_set_pricing` once with the intent ID,
exact digest, and a fresh idempotency key. On an uncertain transport result,
retry only the identical request with the same key.

Poll `vibex_get_pricing` after 2, 4, 8, then 10 seconds while synchronization is
pending. Reset the consecutive transport-failure count after a successful poll;
after five consecutive failures, report the result as unknown and stop. Do not
submit another pricing intent to repair an uncertain result.

- `effective`: show configured and effective percentages.
- `syncing`: say the value is saved but RH synchronization is still running.
- `failed`: show the bounded server error and say the server will reconcile;
  do not repeatedly set the same value.
- `requires_republish=true`: say the value is saved but not active for public
  visitors. Offer `$vibex-publish` as a separate flow and wait for explicit
  publication authorization.

Never call `vibex_publish_project` from this skill. Never treat pricing success
as publication confirmation or publication success as pricing confirmation.
