#!/usr/bin/env python3
"""Run an archived research suite in a new evidence directory."""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=("foundation", "coupled"))
    parser.add_argument("--output-dir", required=True, help="New relative path under research/")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent / "research"
    relative = Path(args.output_dir)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        parser.error("output-dir must be a nonempty relative path without '..'")
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()):
        parser.error("output-dir resolves outside the research directory")
    if sys.flags.optimize:
        parser.error("Run without -O so that mathematical assertions remain enabled")
    if target.exists():
        parser.error(f"Refusing an existing output directory: {target}")
    dependencies = ("mpmath",) if args.suite == "foundation" else ("numpy", "matplotlib", "mpmath", "PIL")
    missing = [name for name in dependencies if importlib.util.find_spec(name) is None]
    if missing:
        parser.error("Missing Python dependencies: " + ", ".join(missing))
    script = "run_release.py" if args.suite == "foundation" else "run_v11.py"
    command = [sys.executable, str(root / "checks" / script), "--output-dir", relative.as_posix()]
    if args.suite == "foundation":
        target.mkdir(parents=True, exist_ok=False)
        import mpmath
        command += ["--dependencies", str(Path(mpmath.__file__).resolve().parent.parent)]
    try:
        return subprocess.run(command, cwd=root, check=False).returncode
    except OSError as error:
        print(f"Unable to start the research suite: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
