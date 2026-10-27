#!/usr/bin/env python3
"""Check a Lean file using the portable kit without retaining Lake in memory.

Author: Komorebi P.
Example:
    python check_low_memory.py --kit /path/to/kit MyProof.lean
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof", type=Path, help="Lean source file to check")
    parser.add_argument("--kit", type=Path, required=True, help="Extracted kit root")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--import-dir", type=Path, help="Local compiled module directory")
    parser.add_argument("--output", type=Path, help="Write checked compiled module to this path")
    parser.add_argument("--timeout", type=int, default=240, help="Compiler wall-clock limit in seconds")
    args = parser.parse_args()
    root = args.kit.expanduser().resolve()
    proof = args.proof.expanduser().resolve()
    workspace = root / "workspace"
    lean = root / "toolchain/bin/lean"
    for path in [root / "run.sh", lean, proof]:
        if not path.is_file():
            parser.error(f"Required file not found: {path}")
    if args.threads < 1 or args.timeout < 1:
        parser.error("Threads and timeout must be positive integers")

    # Read the environment into memory only. Do not persist inherited secrets.
    captured = subprocess.run(
        ["bash", str(root / "run.sh"), "lake", "env", "/usr/bin/env", "-0"],
        cwd=workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90,
    )
    if captured.returncode:
        sys.stderr.buffer.write(captured.stderr)
        return captured.returncode
    environment: dict[str, str] = {}
    for entry in captured.stdout.split(b"\0"):
        if b"=" in entry:
            key, value = entry.split(b"=", 1)
            environment[os.fsdecode(key)] = os.fsdecode(value)

    # The kit cleans its temporary adapter when Lake exits. Restore the inherited
    # preload setting, probe startup, and copy the same shipped adapter if needed.
    inherited_preload = os.environ.get("LD_PRELOAD", "")
    environment.pop("LD_PRELOAD", None)
    if inherited_preload:
        environment["LD_PRELOAD"] = inherited_preload
    with tempfile.TemporaryDirectory(prefix="komorebi-lean-lowmem-") as temporary:
        probe = subprocess.run(
            [str(lean), "--version"], cwd=workspace, env=environment,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15,
        )
        if probe.returncode:
            if b"failed to locate application" not in probe.stdout:
                sys.stderr.buffer.write(probe.stdout)
                return probe.returncode
            adapter = Path(temporary) / "app_path.so"
            shutil.copyfile(root / "compat/app_path.so", adapter)
            environment["LD_PRELOAD"] = str(adapter) + (
                ":" + inherited_preload if inherited_preload else ""
            )
        if args.import_dir:
            import_dir = args.import_dir.expanduser().resolve()
            if not import_dir.is_dir():
                parser.error(f"Import directory not found: {import_dir}")
            environment["LEAN_PATH"] = str(import_dir) + os.pathsep + environment.get("LEAN_PATH", "")
        command = [str(lean), f"-j{args.threads}", "-DwarningAsError=true"]
        if args.output:
            output = args.output.expanduser().resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            command += ["-R", str(proof.parent), "-o", str(output)]
        result = subprocess.run(
            command + [str(proof)],
            cwd=workspace, env=environment, timeout=args.timeout,
        )
        return result.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired as error:
        print(f"Lean check timed out after {error.timeout} seconds", file=sys.stderr)
        raise SystemExit(124)
    except (OSError, ValueError) as error:
        print(f"Lean check failed: {error}", file=sys.stderr)
        raise SystemExit(1)
