#!/usr/bin/env python3
"""Build a clean public source archive after enforcing the allowlist."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

from validate_public_package import ALLOWED_TOP_LEVEL, ROOT, validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "vibex-codex")
    args = parser.parse_args()

    errors = validate(ROOT)
    if errors:
        raise SystemExit("refusing to build an invalid public package:\n- " + "\n- ".join(errors))

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vibex-codex-public-") as temp_dir:
        staging = Path(temp_dir) / "vibex-codex"
        staging.mkdir()
        for name in sorted(ALLOWED_TOP_LEVEL):
            source = ROOT / name
            if not source.exists():
                continue
            destination = staging / name
            if source.is_dir():
                shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(source, destination)
        archive = shutil.make_archive(str(output), "gztar", staging.parent, staging.name)
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
