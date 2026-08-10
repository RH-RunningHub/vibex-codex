#!/usr/bin/env python3
"""Validate the source tree and the exact public release allowlist."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TOP_LEVEL = {
    ".codex-plugin",
    ".github",
    ".gitignore",
    ".mcp.json",
    "assets",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "contracts",
    "examples",
    "LICENSE",
    "PRIVACY.md",
    "README.md",
    "README_CN.md",
    "scripts",
    "SECURITY.md",
    "skills",
    "tests",
}
IGNORED_TOP_LEVEL = {".git", ".pytest_cache", "__pycache__", "dist"}
EXPECTED_TOOLS = [
    "vibex_list_projects",
    "vibex_get_project",
    "vibex_create_project",
    "vibex_get_source_tree",
    "vibex_read_source_file",
    "vibex_begin_edit",
    "vibex_renew_edit",
    "vibex_apply_patch",
    "vibex_commit_edit",
    "vibex_cancel_edit",
    "vibex_prepare_preview",
    "vibex_prepare_publish",
    "vibex_publish_project",
    "vibex_get_operation_status",
]
EXPECTED_OAUTH_SCOPES = [
    "vibex.projects.read",
    "vibex.projects.preview",
    "vibex.projects.create",
    "vibex.projects.edit",
    "vibex.projects.publish",
]
EXPECTED_DISPLAY_NAME = "vibex-codex"
VERSION_PATTERN = re.compile(
    r"^(?:[1-9]\d*)\."
    r"(?:[1-9]|1[0-2])\."
    r"(?:[1-9]|[12]\d|3[01])"
    r"-t(?:[01]\d|2[0-3])[0-5]\d"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
EXPECTED_DEFAULT_PROMPTS = [
    "连接并查看我的 VibeX 项目；首次仅申请读取权限，后续预览、创建、编辑或发布时再按需追加对应权限；无法自动授权时，请到插件的 MCP服务器齿轮中选择“发起授权”。编辑后始终打开内置浏览器预览。",
    "使用 VibeX 编码安全地完成这项修改，然后准备预览。",
    "使用 VibeX 发布准备发布确认；得到我的明确确认后再发布。",
]
EXPECTED_SKILL_INTERFACE = {
    "vibex-coding": ("VibeX 编码", "使用 $vibex-coding 在我的 VibeX 项目中完成这项修改。"),
    "vibex-preview": ("VibeX 预览", "使用 $vibex-preview 验证我的最新 VibeX 项目版本。"),
    "vibex-projects": (
        "VibeX 项目",
        "使用 $vibex-projects 连接 VibeX；首次仅申请读取权限，后续预览、创建、编辑或发布时再按需追加对应权限；无法自动授权时，请到插件的 MCP服务器齿轮中选择“发起授权”。编辑后始终打开内置浏览器预览。",
    ),
    "vibex-publish": ("VibeX 发布", "使用 $vibex-publish 准备并确认发布我的 VibeX 项目。"),
}
TEXT_SUFFIXES = {"", ".json", ".md", ".py", ".svg", ".yaml", ".yml"}
FORBIDDEN_FRAGMENT_DIGESTS = {
    9: frozenset({"7e02aa1ca8aa6072d02f21bca42ac5fa54c589c74b94ce8f587e3a37852513ec"}),
    11: frozenset({"db1942d90aeadf636af286f6587f32f7f56845737269defb6ec2353394556da3"}),
    13: frozenset({"4995851f9cf6240d2a7cb614d9dec2f3b0cdb526f9b9e372d9e1d6fe78664f13"}),
    19: frozenset({"fb735f5719fd2e36a92dc7c117aaeb3a696fe79dc9bd198eda794b81d0400fbc"}),
    23: frozenset(
        {
            "709b7bc7f7547ec3a5f15c40a10e888718481e9f2b99aedac402b995528f35b8",
            "8bc8862f1126d231021c781ccb9ab2a1fa3594d93be52382c1ecb0eb69444efb",
        }
    ),
}


def _is_private_ip(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return address.is_private and not address.is_loopback


def _contains_forbidden_fragment(
    text: str,
    digests_by_length: dict[int, frozenset[str] | set[str]] = FORBIDDEN_FRAGMENT_DIGESTS,
) -> bool:
    encoded = text.encode("utf-8")
    for length, forbidden_digests in digests_by_length.items():
        if length > len(encoded):
            continue
        for start in range(len(encoded) - length + 1):
            candidate = encoded[start : start + length]
            if hashlib.sha256(candidate).hexdigest() in forbidden_digests:
                return True
    return False


def _expected_security_schemes(scope: object) -> list[dict[str, object]]:
    if scope in EXPECTED_OAUTH_SCOPES:
        return [{"type": "oauth2", "scopes": [scope]}]
    if scope == "any granted VibeX project scope":
        return [
            {"type": "oauth2", "scopes": [candidate]}
            for candidate in EXPECTED_OAUTH_SCOPES
        ]
    return []


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    top_level = {item.name for item in root.iterdir() if item.name not in IGNORED_TOP_LEVEL}
    unexpected = sorted(top_level - ALLOWED_TOP_LEVEL)
    if unexpected:
        errors.append(f"unexpected top-level paths: {', '.join(unexpected)}")

    manifest_path = root / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid plugin manifest: {exc}")
        manifest = {}
    version = manifest.get("version")
    if (
        not isinstance(version, str)
        or len(version) > 64
        or VERSION_PATTERN.fullmatch(version) is None
    ):
        errors.append(
            "plugin version must use SemVer-compatible Y.M.D-tHHmm format "
            "(for example 26.8.7-t1450)"
        )
    if manifest.get("license") != "Apache-2.0":
        errors.append("plugin license must be Apache-2.0")
    if manifest.get("skills") != "./skills/":
        errors.append("manifest must expose only the checked-in skills directory")
    if manifest.get("mcpServers") != "./.mcp.json":
        errors.append("manifest must use the checked-in MCP configuration")
    interface = manifest.get("interface", {})
    if interface.get("displayName") != EXPECTED_DISPLAY_NAME:
        errors.append(f"manifest display name must be {EXPECTED_DISPLAY_NAME}")
    prompts = interface.get("defaultPrompt", [])
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        errors.append("manifest must provide one to three default prompts")
    elif any(not isinstance(prompt, str) or len(prompt) > 128 for prompt in prompts):
        errors.append("manifest default prompts must be strings of at most 128 characters")
    elif prompts != EXPECTED_DEFAULT_PROMPTS:
        errors.append("manifest default prompts must use the approved Simplified Chinese copy")

    try:
        mcp_config = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
        server = mcp_config["mcpServers"]["vibex-codex"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid MCP configuration: {exc}")
    else:
        if server != {
            "type": "http",
            "url": "https://vibex.runninghub.cn/mcp/vibex",
            "auth": "oauth",
            "oauth_resource": "https://vibex.runninghub.cn/mcp/vibex",
        }:
            errors.append(
                "MCP configuration must use the production Streamable HTTP endpoint "
                "with explicit OAuth resource binding"
            )

    contract_path = root / "contracts" / "public-tools.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid public contract: {exc}")
        contract = {}
    names = [tool.get("name") for tool in contract.get("tools", [])]
    if names != EXPECTED_TOOLS:
        errors.append("public contract must contain the exact ordered 14-tool allowlist")
    else:
        for tool in contract["tools"]:
            expected_security_schemes = _expected_security_schemes(tool.get("scope"))
            if not expected_security_schemes:
                errors.append(f'{tool["name"]}: declares an unsupported OAuth scope')
            elif tool.get("securitySchemes") != expected_security_schemes:
                errors.append(
                    f'{tool["name"]}: must declare only the minimum operation scope'
                )

    secret_assignment = re.compile(
        r"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"][^<][^'\"]{7,}['\"]"
    )
    ipv4_pattern = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")

    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_TOP_LEVEL for part in path.parts):
            continue
        rel = path.relative_to(root)
        if path.is_symlink():
            errors.append(f"{rel}: symbolic links are not allowed in the public package")
            continue
        if not path.is_file():
            continue
        if path.suffix not in TEXT_SUFFIXES:
            errors.append(f"{rel}: unsupported public file type")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{rel}: public text file is not valid UTF-8")
            continue
        if _contains_forbidden_fragment(text):
            errors.append(f"{rel}: contains non-public implementation detail")
        if secret_assignment.search(text):
            errors.append(f"{rel}: contains a possible embedded secret")
        for candidate in ipv4_pattern.findall(text):
            if _is_private_ip(candidate):
                errors.append(f"{rel}: contains a private network address")

    required_skills = {"vibex-projects", "vibex-coding", "vibex-preview", "vibex-publish"}
    present_skills = {path.name for path in (root / "skills").iterdir() if path.is_dir()}
    if present_skills != required_skills:
        errors.append("skills directory must contain exactly the four documented VibeX skills")
    for skill_name in sorted(required_skills):
        skill_file = root / "skills" / skill_name / "SKILL.md"
        agent_file = root / "skills" / skill_name / "agents" / "openai.yaml"
        try:
            skill_text = skill_file.read_text(encoding="utf-8")
            agent_text = agent_file.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{skill_name}: missing required skill file: {exc}")
            continue
        if not skill_text.startswith("---\n") or f"\nname: {skill_name}\n" not in skill_text:
            errors.append(f"{skill_name}: invalid SKILL.md frontmatter")
        if "\ndescription: " not in skill_text.split("---", 2)[1]:
            errors.append(f"{skill_name}: missing skill description")
        display_name, default_prompt = EXPECTED_SKILL_INTERFACE[skill_name]
        required_agent_fragments = (
            f'display_name: "{display_name}"',
            f'default_prompt: "{default_prompt}"',
            f"${skill_name}",
            'value: "vibex-codex"',
            'transport: "streamable_http"',
            'url: "https://vibex.runninghub.cn/mcp/vibex"',
            "allow_implicit_invocation: true",
        )
        if any(fragment not in agent_text for fragment in required_agent_fragments):
            errors.append(f"{skill_name}: invalid MCP dependency or invocation policy")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("Public package validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Public package validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
