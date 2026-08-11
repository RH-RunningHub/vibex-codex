# Privacy

The plugin sends only the user-requested project operations to the VibeX MCP endpoint configured in [`.mcp.json`](./.mcp.json). Authentication credentials are managed by the MCP client and must not be stored in this repository.

Depending on the requested operation, the service may process project identifiers, safe project metadata, selected source paths and content, bounded patches, redacted diagnostics, aggregate usage counts, cover-generation inputs, preview state, and publication choices. The plugin does not request unrelated browser history, passwords, everyday browser profiles, arbitrary local files, or credentials.

Preview pages are treated as untrusted content. The separate Codex Desktop Browser capability, when available, uses its own profile and is not part of this plugin.

For account-level privacy, retention, or deletion questions, use RunningHub's official privacy and support channels.
