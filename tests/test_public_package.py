from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_public_package", ROOT / "scripts" / "validate_public_package.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)

RUNTIME_SPEC = importlib.util.spec_from_file_location(
    "verify_runtime_contract", ROOT / "scripts" / "verify_runtime_contract.py"
)
assert RUNTIME_SPEC and RUNTIME_SPEC.loader
RUNTIME_VERIFIER = importlib.util.module_from_spec(RUNTIME_SPEC)
RUNTIME_SPEC.loader.exec_module(RUNTIME_VERIFIER)


def test_public_package_boundary() -> None:
    assert VALIDATOR.validate(ROOT) == []


def test_plugin_listing_uses_vibex_codex_name_and_chinese_prompts() -> None:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
    interface = manifest["interface"]
    assert VALIDATOR.VERSION_PATTERN.fullmatch(manifest["version"])
    assert interface["displayName"] == "vibex-codex"
    assert interface["defaultPrompt"] == VALIDATOR.EXPECTED_DEFAULT_PROMPTS
    assert interface["defaultPrompt"][0] == (
        "连接并查看我的 VibeX 项目；首次连接一次授权读取、创建、编辑、预览和发布五项权限；"
        "各工具仍按操作权限校验，发布必须另行明确确认。无法自动授权时，请到插件的 MCP服务"
        "器齿轮中选择“发起授权”。"
    )


def test_mcp_configuration_declares_oauth_resource_explicitly() -> None:
    config = json.loads((ROOT / ".mcp.json").read_text())
    server = config["mcpServers"]["vibex-codex"]
    assert server["url"] == "https://vibex.runninghub.cn/mcp/vibex"
    assert server["auth"] == "oauth"
    assert server["oauth_resource"] == server["url"]


def test_plugin_version_is_semver_safe_for_zero_padded_times() -> None:
    valid = [
        "26.8.7-t0005",
        "26.8.7-t0930",
        "26.8.7-t1450",
        "26.8.7-t2359+codex.a36d953",
    ]
    invalid = [
        "26.08.07.1450",
        "26.8.7-0930",
        "26.8.7-t2360",
        "26.8.7-t2400",
        "26.8.7+1450",
        f"26.8.7-t1450+{'a' * 64}",
    ]
    assert all(VALIDATOR.VERSION_PATTERN.fullmatch(version) for version in valid)
    assert all(
        len(version) > 64 or VALIDATOR.VERSION_PATTERN.fullmatch(version) is None
        for version in invalid
    )


def test_contract_has_exact_tool_allowlist() -> None:
    contract = json.loads((ROOT / "contracts" / "public-tools.json").read_text())
    assert [tool["name"] for tool in contract["tools"]] == VALIDATOR.EXPECTED_TOOLS
    assert len(contract["tools"]) == 15
    for tool in contract["tools"]:
        expected = [
            {"type": "oauth2", "scopes": VALIDATOR.EXPECTED_OAUTH_SCOPES}
        ]
        assert tool["securitySchemes"] == expected


def test_runtime_contract_verifier_detects_cross_repository_drift(
    tmp_path: Path,
) -> None:
    public = ROOT / "contracts" / "public-tools.json"
    runtime = tmp_path / "runtime.json"
    runtime.write_text(public.read_text(encoding="utf-8"), encoding="utf-8")
    assert RUNTIME_VERIFIER.verify(runtime, public) == []

    payload = json.loads(runtime.read_text(encoding="utf-8"))
    payload["tools"] = payload["tools"][:-1]
    runtime.write_text(json.dumps(payload), encoding="utf-8")
    assert any(
        "differs" in error for error in RUNTIME_VERIFIER.verify(runtime, public)
    )


def test_validator_uses_non_reversible_private_denylist() -> None:
    source = (ROOT / "scripts" / "validate_public_package.py").read_text()
    assert "forbidden_fragments = [" not in source
    assert "FORBIDDEN_FRAGMENT_DIGESTS" in source


def test_hashed_denylist_scanner_detects_a_synthetic_marker() -> None:
    marker = "synthetic-private-marker"
    digest = hashlib.sha256(marker.encode()).hexdigest()
    denylist = {len(marker): {digest}}
    assert VALIDATOR._contains_forbidden_fragment(
        f"safe-prefix-{marker}-safe-suffix", denylist
    )
    assert not VALIDATOR._contains_forbidden_fragment("public-only-content", denylist)


def test_validator_rejects_unknown_binary_files(tmp_path: Path) -> None:
    checkout = tmp_path / "vibex-codex"
    shutil.copytree(
        ROOT,
        checkout,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "dist"),
    )
    (checkout / "skills" / "vibex-coding" / "private.pem").write_bytes(b"placeholder")
    assert any("unsupported public file type" in error for error in VALIDATOR.validate(checkout))


def test_validator_rejects_symlinks(tmp_path: Path) -> None:
    checkout = tmp_path / "vibex-codex"
    shutil.copytree(
        ROOT,
        checkout,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "dist"),
    )
    outside = tmp_path / "outside.txt"
    outside.write_text("outside content")
    (checkout / "skills" / "vibex-coding" / "outside.txt").symlink_to(outside)
    assert any("symbolic links are not allowed" in error for error in VALIDATOR.validate(checkout))


def test_publish_annotations_remain_explicit_and_destructive() -> None:
    contract = json.loads((ROOT / "contracts" / "public-tools.json").read_text())
    tools = {tool["name"]: tool for tool in contract["tools"]}
    publish = tools["vibex_publish_project"]
    assert publish["annotations"]["destructiveHint"] is True
    assert publish["annotations"]["readOnlyHint"] is False


def test_preview_and_publish_are_separate_scopes() -> None:
    contract = json.loads((ROOT / "contracts" / "public-tools.json").read_text())
    tools = {tool["name"]: tool for tool in contract["tools"]}
    assert tools["vibex_prepare_preview"]["scope"] == "vibex.projects.preview"
    assert tools["vibex_prepare_publish"]["scope"] == "vibex.projects.publish"
