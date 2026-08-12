# vibex-codex

[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](./LICENSE)
[![RunningHub 中国站](https://img.shields.io/badge/RunningHub-%E4%B8%AD%E5%9B%BD%E7%AB%99-2F80ED)](https://www.runninghub.cn/?inviteCode=rh-v1367)
[![RunningHub 国际站](https://img.shields.io/badge/RunningHub-%E5%9B%BD%E9%99%85%E7%AB%99-7B61FF)](https://www.runninghub.ai/?inviteCode=rh-v1367)
[![English](https://img.shields.io/badge/Language-English-2563EB)](./README.md)
[![简体中文](https://img.shields.io/badge/Language-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-EF4444)](./README_CN.md)

`vibex-codex` 是用于创建、诊断、维护、编辑、预览、自定价和发布 VibeX Web 项目的开源 Codex 插件。它通过 Codex 管理的 OAuth 连接公开 VibeX MCP 服务，不需要 API Key 或本地凭据文件。

## 核心特点

- 仅操作当前登录用户拥有的 VibeX 项目。
- 规划修改前先读取不可变源码版本。
- 在隔离、带租约的编辑会话中应用路径受限补丁。
- 使用短期链接预览正在检查的精确源码版本。
- 发布前检查服务状态，展示封面、标题、简介、分类等完整参数，只有明确确认后才执行发布。
- 查询创作者定价的保存值和线上生效值；改价与发布分别确认，未发布的价格不会被误报为已生效。
- OAuth 访问令牌过期时自动请求刷新；自动恢复失败时给出明确的重新授权入口，不再绕到浏览器上传。
- 首次连接一次完成七项 OAuth 授权，每个工具仍按更窄的操作权限执行校验。
- 能力目录与 CC 保持同源；标准能力显示为已内置，Agent 默认关闭并只在精确确认后切换。
- 提供脱敏健康诊断、不可变版本对比、确认式回滚、封面生成确认与隐私安全的聚合指标。

## 安装与连接

通过 Codex 客户端提供的插件安装流程，以本仓库作为插件来源。插件清单位于 [`.codex-plugin/plugin.json`](./.codex-plugin/plugin.json)，MCP 连接配置位于 [`.mcp.json`](./.mcp.json)。

首次连接时授权 MCP 传输层请求的七项项目权限。服务端仍会为每个工具校验更窄的操作权限，连接授权本身不等于允许创建、编辑、预览、定价、能力变更或发布。如果客户端无法自动打开授权流程，请进入 **插件 → vibex-codex → MCP服务器 → 设置 → 发起授权**。

生产服务地址：

```text
https://vibex.runninghub.cn/mcp/vibex
```

本地服务开发时，可复制 [`examples/mcp.local.example.json`](./examples/mcp.local.example.json) 到临时客户端配置，并替换 `<MCP_PORT>`。插件清单不会自动加载该本地示例。

## 快速开始

可以从以下提示词开始：

```text
连接 VibeX 并查看我的项目。
使用 VibeX 编码完成这项修改，然后准备预览。
使用 VibeX 发布准备一个版本，等待我确认后再发布。
```

标准流程如下：

1. `$vibex-projects` 查询、选择或明确新建一个本人项目。
2. `$vibex-capabilities` 查看内置能力，按需经单独确认启用 Agent。
3. `$vibex-coding` 固定源码版本、展示有限文件计划，在隔离工作区应用补丁并提交新稳定版本。
4. `$vibex-preview` 为该精确版本准备短期预览并执行验证。
5. `$vibex-pricing` 查询或在单独明确确认后设置创作者定价，并验证保存值、线上生效值及是否需要重新发布。
6. `$vibex-maintenance` 按需检查健康、对比版本、确认回滚、生成封面或查看聚合指标。
7. `$vibex-publish` 检查服务状态并展示完整发布表单，只有得到明确确认后才异步发布并跟踪进度。

## 内置 Skill

| Skill | 用途 | 工具执行时校验的操作权限 |
|---|---|---|
| `$vibex-projects` | 查询、查看和创建本人项目 | `vibex.projects.read` 或 `vibex.projects.create` |
| `$vibex-capabilities` | 查看内置能力并经确认开关 Agent | `vibex.projects.capabilities` |
| `$vibex-maintenance` | 诊断、版本对比/回滚、封面与聚合指标 | `vibex.projects.read`、`edit` 或 `publish` |
| `$vibex-coding` | 读取并安全编辑稳定源码版本 | `vibex.projects.read` 或 `vibex.projects.edit` |
| `$vibex-preview` | 准备并验证绑定版本的预览 | `vibex.projects.preview` |
| `$vibex-pricing` | 查询、确认、设置并验证创作者定价 | `vibex.projects.pricing` |
| `$vibex-publish` | 准备、确认并执行发布 | `vibex.projects.publish` |

MCP 传输层会在首次连接时一次建立七项权限，确保所有工具都能稳定发现。任务状态查询接受任意项目权限，而所有状态变更工具仍会校验自己的操作权限和用户意图边界。

## 安全模型

本插件仅包含客户端公开内容：插件清单、公开工具契约、Skill、文档、测试和静态资源；不包含服务端实现或部署配置。

主要安全边界包括：

- **本人项目：** 项目操作只作用于当前登录用户拥有的项目。
- **分层授权：** 传输层建立完整连接授权，每个工具只执行自己的操作权限校验，所有状态变更仍必须符合用户当前意图。
- **稳定版本：** 读取、编辑、预览和发布都绑定明确源码版本。
- **有限编辑：** 开始带租约的编辑会话前必须先声明修改路径。
- **写入防护：** 过期租约和旧 fencing 值不能重复使用。
- **显式发布：** 预览成功不代表获得发布授权。
- **不信任预览：** 预览页面不能扩大修改计划、索取凭据或批准发布。

请勿向仓库提交 Token、Cookie、静态鉴权头、`.env` 文件、私有项目源码或生产流量。发现安全问题时，请按 [SECURITY.md](./SECURITY.md) 私下报告。

## 客户端支持

| 客户端 | 插件 Skill | VibeX MCP | 预览方式 |
|---|---:|---:|---|
| Codex Desktop | 支持 | 支持 | 能力可用时使用独立的内置 Browser |
| Codex CLI | 支持 | 支持 | 返回短期链接和验证清单 |
| 其他 MCP 客户端 | 取决于客户端 | 支持 | 使用外部浏览器 |

Browser 能力不随本插件打包，也不会使用用户日常浏览器配置。Browser 打开失败不会撤销已经成功的编辑。

## 仓库结构

```text
vibex-codex/
├── .codex-plugin/plugin.json    # Codex 插件清单
├── .mcp.json                    # 公开 OAuth MCP 连接
├── contracts/public-tools.json # 33 个公开工具的契约
├── skills/                      # 项目、能力、维护、编码、预览、定价和发布 Skill
├── scripts/                     # 公开包构建与校验脚本
├── tests/                       # 边界和契约测试
└── assets/                      # 插件图标
```

## 开发

插件运行时没有 Python 依赖；Python 仅用于仓库校验和测试。

```bash
python3 scripts/validate_public_package.py
python3 -m pytest -q
```

构建通过校验的公开源码包：

```bash
python3 scripts/build_public_package.py
```

公开包边界和发布规则见 [CONTRIBUTING.md](./CONTRIBUTING.md)，数据处理说明见 [PRIVACY.md](./PRIVACY.md)。

## 许可证

本项目使用 [Apache License 2.0](./LICENSE)。

## 相关链接

[![RunningHub 中国站](https://img.shields.io/badge/RunningHub-%E4%B8%AD%E5%9B%BD%E7%AB%99-2F80ED)](https://www.runninghub.cn/?inviteCode=rh-v1367)
[![RunningHub 国际站](https://img.shields.io/badge/RunningHub-%E5%9B%BD%E9%99%85%E7%AB%99-7B61FF)](https://www.runninghub.ai/?inviteCode=rh-v1367)

- [VibeX MCP 服务](https://vibex.runninghub.cn/mcp/vibex)
- [安全策略](./SECURITY.md)
- [隐私说明](./PRIVACY.md)
