# Changelog

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
