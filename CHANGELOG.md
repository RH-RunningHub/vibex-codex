# Changelog

## 26.8.12-t2223

- Add the canonical CC capability catalog and versioned project capability inspection.
- Add confirmation-gated Agent enable/disable tools without changing source or the active published snapshot.
- Expand the public MCP contract from 29 to 33 tools and add the dedicated capability OAuth scope.

## 26.8.11-t2221

- Add redacted project diagnostics and privacy-safe aggregate project metrics.
- Add immutable revision history and manifest comparison, plus a single-use confirmed rollback flow.
- Add cover status, preview, and separately confirmed cover generation without granting publication.
- Expand the public MCP contract from 20 to 29 tools without adding OAuth scopes.

## 26.8.11-t2053

- Add creator-pricing inspection, confirmation, application, and verification tools with a dedicated six-scope OAuth permission.
- Keep pricing and publication as separate explicit confirmations, and report saved versus effective pricing without claiming an unpublished value is live.
- Teach Codex to upgrade only eligible standard-model hooks and to avoid AI-application revenue flows.

## 26.8.11-t1945

- Wait for the server to reap an expired edit lease before starting a replacement session, and report a stuck edit instead of repeatedly acquiring new locks.

## 26.8.11-t1915

- Add publish readiness and complete publish-form tools, including cover preview, title, summary, gallery categories, remix, URL mode, and data-reset confirmation.
- Make project publishing asynchronous and require clients to poll structured operation phases instead of holding a long request open.
- Recover automatically from expired OAuth access tokens through safe refresh retries, with explicit reauthorization guidance only when recovery fails.

## 26.8.10-t1958

- Align every public tool's OAuth connection metadata with the MCP transport's five-scope handshake while retaining operation-level scope checks.
- Add `vibex_initialize_source` so eligible legacy Web projects can create their first immutable source revision before editing.
- Update all skills, starter prompts, documentation, validators, and contracts to match the runtime service.

## 26.8.10-t1615

- Apply least-privilege OAuth scopes per public tool and request additional capabilities incrementally.
- Replace public internal-identifier literals with digest-based release validation.
- Reject symbolic links, unknown binary types, and invalid UTF-8 from the public package boundary.
- Expand the English and Simplified Chinese documentation for installation, security, usage, and development.

## 26.8.10-t1438

- Request all five VibeX project OAuth scopes during the initial connection so the token matches the MCP server's transport requirements.
- Update the first project starter prompt to explain the complete authorization request and keep previews in the built-in browser.

## 26.8.7-t1802+codex.20260808184141

- Kept release validation compatible with Codex cachebuster versions.
- Added an explicit regression assertion for the public VibeX MCP endpoint.

## 26.8.7-t1802

- Standardized the user-facing plugin name as `vibex-codex`.
- Localized plugin listing copy and starter prompts for Simplified Chinese.
- Switched date-based releases to strict SemVer-safe `Y.M.D-tHHmm` versions.
- Declared the OAuth resource explicitly and made the first starter prompt request immediate authorization.

## 1.0.0

- Added four focused skills for projects, coding, preview, and publication.
- Published a generated 14-tool public MCP contract.
- Added Codex Desktop Browser preview guidance with CLI and external-browser fallbacks.
- Added explicit open-source, privacy, security, and package-boundary checks.
