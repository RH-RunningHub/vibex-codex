#!/usr/bin/env python3
"""Verify that the checked-in public contract exactly matches a runtime export."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def verify(runtime_path: Path, public_path: Path | None = None) -> list[str]:
    public_path = public_path or ROOT / "contracts" / "public-tools.json"
    try:
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid runtime contract: {exc}"]
    try:
        public = json.loads(public_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid public contract: {exc}"]
    if public != runtime:
        return [
            "public contract differs from the VibeX MCP runtime export; "
            "regenerate contracts/public-tools.json before release"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-contract", type=Path, required=True)
    parser.add_argument("--public-contract", type=Path)
    args = parser.parse_args()
    errors = verify(args.runtime_contract.resolve(), args.public_contract)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Runtime and public VibeX MCP contracts match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
