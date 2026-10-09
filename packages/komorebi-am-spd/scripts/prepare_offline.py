"""Download a binary wheelhouse for an explicitly selected target interpreter."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("wheelhouse"))
    parser.add_argument("--platform")
    parser.add_argument("--python-version")
    parser.add_argument("--abi")
    parser.add_argument("--lock", type=Path)
    args = parser.parse_args()
    if not args.wheel.is_file():
        parser.error("--wheel must identify the built AM-SPD wheel")
    args.output.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "pip", "download", "--only-binary=:all:", "--dest", str(args.output)]
    for name in ("platform", "python_version", "abi"):
        value = getattr(args, name)
        if value:
            command.extend(["--" + name.replace("_", "-"), value])
    if args.platform or args.python_version or args.abi:
        command.extend(["--implementation", "cp"])
    if args.lock:
        command.extend(["--requirement", str(args.lock)])
    command.append(str(args.wheel.resolve()))
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
