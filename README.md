# vibex-codex

[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](./LICENSE)
[![RunningHub China](https://img.shields.io/badge/RunningHub-China-2F80ED)](https://www.runninghub.cn/?inviteCode=rh-v1367)
[![RunningHub International](https://img.shields.io/badge/RunningHub-International-7B61FF)](https://www.runninghub.ai/?inviteCode=rh-v1367)
[![English](https://img.shields.io/badge/Language-English-2563EB)](./README.md)
[![简体中文](https://img.shields.io/badge/Language-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-EF4444)](./README_CN.md)

`vibex-codex` is the open-source Codex plugin for creating, inspecting, editing, previewing, pricing, and publishing VibeX web projects. It connects Codex to the public VibeX MCP endpoint through Codex-managed OAuth; no API key or local credential file is required.

## Highlights

- Work only with projects owned by the signed-in VibeX user.
- Read immutable source revisions before planning a change.
- Apply path-scoped patches inside isolated, lease-protected edit sessions.
- Preview the exact revision being reviewed with a short-lived launch URL.
- Publish only after an explicit confirmation bound to the revision and target.
- Inspect saved and effective creator pricing, with separate confirmations for pricing and publication.
- Establish one complete six-scope OAuth connection while enforcing each tool's narrower operation scope.

## Install and connect

Install the plugin through the plugin flow provided by your Codex client, using this repository as the source. The checked-in manifest is [`.codex-plugin/plugin.json`](./.codex-plugin/plugin.json), and the MCP connection is declared in [`.mcp.json`](./.mcp.json).

When Codex first connects, authorize the six project scopes requested by the MCP transport. The service still checks the narrower operation scope for every tool, and the connection grant never replaces an explicit request to create, edit, preview, price, or publish. If the client cannot open the authorization flow automatically, open **Plugins → vibex-codex → MCP server → Settings → Start authorization**.

The production endpoint is:

```text
https://vibex.runninghub.cn/mcp/vibex
```

For local service development, copy [`examples/mcp.local.example.json`](./examples/mcp.local.example.json) into a temporary client configuration and replace `<MCP_PORT>`. The local example is not loaded by the plugin manifest.

## Quick start

Try one of the plugin's starter prompts:

```text
Connect to VibeX and show my projects.
Use VibeX Coding to implement this change, then prepare a preview.
Use VibeX Publish to prepare a release for my confirmation.
```

The normal workflow is:

1. `$vibex-projects` resolves or explicitly creates one owned project.
2. `$vibex-coding` pins a source revision, displays a bounded file plan, applies patches in an isolated workspace, and commits a new stable revision.
3. `$vibex-preview` prepares and verifies a short-lived preview for that exact revision.
4. `$vibex-pricing` inspects or explicitly changes creator pricing, then verifies saved and effective state.
5. `$vibex-publish` prepares a confirmation summary and publishes only after explicit approval.

## Included skills

| Skill | Purpose | Operation scope enforced by the tool |
|---|---|---|
| `$vibex-projects` | Find, inspect, and create owned projects | `vibex.projects.read` or `vibex.projects.create` |
| `$vibex-coding` | Read and safely edit a stable source revision | `vibex.projects.read` or `vibex.projects.edit` |
| `$vibex-preview` | Prepare and verify a revision-pinned preview | `vibex.projects.preview` |
| `$vibex-pricing` | Inspect, confirm, set, and verify creator pricing | `vibex.projects.pricing` |
| `$vibex-publish` | Prepare, confirm, and execute publication | `vibex.projects.publish` |

The MCP transport establishes all six scopes in one connection so every tool can be discovered reliably. Operation-status polling accepts any project scope, while each state-changing tool still enforces its own scope and user-intent boundary.

## Security model

The plugin is intentionally client-only: this repository contains the manifest, public tool contract, skills, documentation, tests, and static assets, but no server implementation or deployment configuration.

Its main safety boundaries are:

- **Owner scope:** project operations apply only to the signed-in user's projects.
- **Layered authorization:** the transport establishes the complete connection grant, while each tool enforces only its operation scope and all state changes still require matching user intent.
- **Stable revisions:** reads, edits, previews, and publication target explicit source revisions.
- **Bounded editing:** changed paths are declared before a lease-protected edit session begins.
- **Fenced writes:** stale leases and fencing values cannot be reused.
- **Explicit publication:** preview success never authorizes publication.
- **Untrusted previews:** preview-page content cannot widen an edit plan, request credentials, or approve a release.

Never commit tokens, cookies, static authorization headers, `.env` files, private project source, or production traffic to this repository. Report suspected vulnerabilities privately as described in [SECURITY.md](./SECURITY.md).

## Client support

| Client | Plugin skills | VibeX MCP | Preview behavior |
|---|---:|---:|---|
| Codex Desktop | Yes | Yes | Uses the separate built-in Browser capability when available |
| Codex CLI | Yes | Yes | Returns a short-lived URL and verification checklist |
| Other MCP clients | Client-dependent | Yes | Uses an external browser |

The Browser capability is not bundled with this plugin and does not use the user's everyday browser profile. A Browser failure does not undo a successful edit.

## Repository layout

```text
vibex-codex/
├── .codex-plugin/plugin.json    # Codex plugin manifest
├── .mcp.json                    # Public OAuth MCP connection
├── contracts/public-tools.json # Public 20-tool contract
├── skills/                      # Projects, coding, preview, pricing, and publish skills
├── scripts/                     # Public-package build and validation
├── tests/                       # Boundary and contract tests
└── assets/                      # Plugin artwork
```

## Development

The plugin has no Python runtime dependency. Python is used only for repository validation and tests.

```bash
python3 scripts/validate_public_package.py
python3 -m pytest -q
```

Build a validator-approved public source archive with:

```bash
python3 scripts/build_public_package.py
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the public-package boundary and release rules. Data handling is summarized in [PRIVACY.md](./PRIVACY.md).

## License

Licensed under the [Apache License 2.0](./LICENSE).

## Links

[![RunningHub China](https://img.shields.io/badge/RunningHub-China-2F80ED)](https://www.runninghub.cn/?inviteCode=rh-v1367)
[![RunningHub International](https://img.shields.io/badge/RunningHub-International-7B61FF)](https://www.runninghub.ai/?inviteCode=rh-v1367)

- [VibeX MCP endpoint](https://vibex.runninghub.cn/mcp/vibex)
- [Security policy](./SECURITY.md)
- [Privacy summary](./PRIVACY.md)
