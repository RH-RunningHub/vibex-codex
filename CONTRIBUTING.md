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
5. Run `python3 scripts/validate_public_package.py` and `python3 -m pytest -q` before submitting a change.
6. Use the SemVer-safe `Y.M.D-tHHmm` release format, for example `26.8.7-t0930`; the `t` keeps zero-padded times valid as a prerelease identifier.

Public releases must be created from the validator-approved package contents in a fresh public history. Private development history must not be copied into a public repository.
