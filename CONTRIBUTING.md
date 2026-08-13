# Contributing

Contributions should preserve the plugin's public-only boundary and fail-closed workflow.

1. Keep the repository limited to the manifest, MCP configuration, skills, public schemas, examples, tests, documentation, and static assets.
2. Do not add server code, private design documents, infrastructure details, internal routes, credentials, user data, or operational scripts.
3. Do not edit `contracts/public-tools.json` by hand. Update the service contract, regenerate it, and review the resulting public diff.
4. Keep source reads revision-pinned, edits path-scoped and lease-protected, previews revision-bound, and publication separately confirmed.
5. Before a release, export the runtime MCP contract and verify it against the public package:

   ```bash
   cd <runtime-mcp-checkout>
   uv run python scripts/export_public_contract.py --output /tmp/vibex-runtime-contract.json
   cd <public-plugin-checkout>
   python3 scripts/verify_runtime_contract.py --runtime-contract /tmp/vibex-runtime-contract.json
   ```
6. For every user-facing VibeX feature, audit the complete release diff—not only the plugin repository. Update the affected Skill when the change adds a user action, `next_action`, confirmation field, assistant entry point, capability, or safety boundary. A server-driven form must render and confirm newly returned fields instead of relying on a frozen client-side allowlist.
7. Record the cross-repository impact and validation result in the internal `doc/vibex-codex/新增功能自动同步与发布门禁.md` release log. Keep private topology and credentials out of this public repository.
8. Run `python3 scripts/validate_public_package.py` and `python3 -m pytest -q` before submitting a change.
9. Use the SemVer-safe `Y.M.D-tHHmm` release format, for example `26.8.7-t0930`; the `t` keeps zero-padded times valid as a prerelease identifier.

Public releases must be created from the validator-approved package contents in a fresh public history. Private development history must not be copied into a public repository.
