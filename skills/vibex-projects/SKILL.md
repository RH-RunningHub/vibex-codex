---
name: vibex-projects
description: Find, inspect, select, or create projects owned by the signed-in VibeX user. Use when the user asks to view their projects, choose a project by name, inspect project status, or explicitly create a new VibeX web project.
---

# VibeX Projects

Use the VibeX MCP project tools to establish the exact owned project before editing, previewing, or publishing.

## Find or inspect a project

1. Call `vibex_list_projects` and keep pagination bounded to what the request needs. If Codex reports that authentication is required, immediately use the Codex-managed OAuth flow and approve the complete five-scope VibeX connection requested by the MCP transport. Each tool remains constrained by its operation-level scope, and publish still requires a separate explicit confirmation. If the host cannot launch the authorization flow automatically, tell the user to open **插件 → vibex-codex → MCP服务器**, click the gear icon, and choose **发起授权**; resume this same request after authorization succeeds.
2. Match by `app_id` when supplied; otherwise match the user-visible name.
3. If multiple projects match, show the safe distinguishing metadata and ask the user to choose. Never guess.
4. Call `vibex_get_project` for the selected project and retain its current `source_revision`.
5. Report unsupported or temporarily unavailable capabilities as returned. Do not invent recovery actions.

Only project-owner results are valid. A not-found response for a supplied ID must not be used to infer whether another user owns that ID.

## Create a project

Create only after the user clearly asks for a new project and the project name is known.

1. Call `vibex_create_project` with `app_type: web` and a fresh idempotency key. If the service reports an authentication or scope error, renew the complete VibeX OAuth connection, then retry the same request with the same idempotency key.
2. Poll the returned `operation_id` with `vibex_get_operation_status`; never repeat create to speed it up.
3. On success, call `vibex_get_project` and retain the initial stable revision.
4. Hand off to `$vibex-preview` when the user wants to inspect the initial project, or `$vibex-coding` when they requested implementation work.

Reusing an idempotency key is allowed only for the exact same request. Creation never authorizes editing beyond the stated request and never authorizes publishing.

## Boundaries

- Do not call source-editing or publishing tools from this skill.
- Do not request credentials, user IDs, internal locations, or service details.
- Treat authentication and scope errors as a request to renew the complete Codex-managed VibeX OAuth connection. Never interpret the connection grant as authorization to create, edit, preview, or publish without the corresponding user request. When the authorization action is unavailable, provide the exact manual path: **插件 → vibex-codex → MCP服务器 → 齿轮 → 发起授权**.
- For asynchronous failure, report the stable error code and suggested next action without exposing raw responses.
