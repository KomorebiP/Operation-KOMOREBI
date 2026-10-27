#!/usr/bin/env python3
"""Replay the two supplied Lean projects with an existing offline runtime.

The wrapper uses the original project verifiers. It never downloads a runtime,
changes proof sources, or enables the optional Linux compatibility adapter
without --compat-shim. --dry-run does not start Lean or write any files.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile


PACKAGE = Path(__file__).resolve().parents[1]
QUANTUM = PACKAGE / "sources/quantum/Quantum_Arithmetic_Complete_Release/lean/checked_checkpoint"
CIRCUITS = PACKAGE / "sources/circuits/Komorebi_Circuit_Obstructions_Research_Edition_1.0/source/komorebi-circuit-obstructions-v1.2.0"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_plan(runtime: Path, output: Path) -> list[dict]:
    toolchain = runtime / "toolchain"
    return [
        {
            "name": "quantum",
            "cwd": str(QUANTUM),
            "argv": [sys.executable, str(QUANTUM / "scripts/verify_lean.py"),
                     "--toolchain", str(toolchain),
                     "--packages", str(runtime / "workspace/.lake/packages"),
                     "--out", str(output / "quantum")],
            "receipt": str(output / "quantum/REPORT.json"),
        },
        {
            "name": "circuits",
            "cwd": str(CIRCUITS),
            "argv": [sys.executable, str(CIRCUITS / "scripts/verify_lean.py"),
                     "--toolchain", str(toolchain),
                     "--out", str(output / "circuits")],
            "receipt": str(output / "circuits/verification.json"),
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", required=True, type=Path,
                        help="Root of the extracted Komorebi_Portable_Lean_4.34.0-rc2 kit")
    parser.add_argument("--out", required=True, type=Path,
                        help="New output directory; an existing directory is never overwritten")
    parser.add_argument("--compat-shim", action="store_true",
                        help="Explicitly preload the kit's Linux executable-path adapter")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands only; no runtime, compiler or output directory is needed")
    args = parser.parse_args()
    runtime, output = args.runtime.expanduser().resolve(), args.out.expanduser().resolve()
    plan = make_plan(runtime, output)
    if args.dry_run:
        print("DRY RUN: no commands executed and no proof claim made.")
        print("Compatibility adapter:", "explicitly requested" if args.compat_shim else "not enabled by wrapper")
        for step in plan:
            print(f"\n[{step['name']}] cwd: {step['cwd']}")
            print(shlex.join(step["argv"]))
            print("Expected receipt:", step["receipt"])
        return 0

    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
        parser.error("The stored offline kit requires Linux x86_64, including compatible WSL2.")
    if output.exists():
        parser.error(f"Output already exists; choose a new directory: {output}")
    required = [runtime / "toolchain/bin" / name for name in ("lean", "lake", "leanchecker")]
    required += [Path(step["argv"][1]) for step in plan]
    if args.compat_shim:
        required.append(runtime / "compat/app_path.so")
    missing = [str(path) for path in required if not path.is_file()]
    packages = runtime / "workspace/.lake/packages"
    if not packages.is_dir():
        missing.append(str(packages))
    if missing:
        parser.error("Required files or cache are missing:\n" + "\n".join(missing))
    if any(not os.access(path, os.X_OK) for path in required[:3]):
        parser.error("The supplied Lean, Lake and leanchecker binaries must be executable.")

    # Keep external Lean settings from substituting a different library root.
    env = os.environ.copy()
    for key in ("LEAN_PATH", "LEAN_SRC_PATH", "LEAN_SYSROOT", "LAKE_HOME"):
        env.pop(key, None)
    output.mkdir(parents=True, exist_ok=False)
    summary = {
        "status": "RUNNING", "started_at": datetime.now(timezone.utc).isoformat(),
        "runtime": str(runtime), "compat_shim_requested": args.compat_shim,
        "official_declaration_counts": {"quantum": 96, "circuits": 115},
        "scope": "The supplied formal subsets only; supplementary mode-one checks are separate.",
        "runs": [],
    }
    summary_path = output / "replay_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    adapter_directory = None
    try:
        if args.compat_shim:
            # The Linux loader cannot represent spaces inside LD_PRELOAD paths.
            adapter_directory = tempfile.TemporaryDirectory(prefix="komorebi-lean-", dir="/tmp")
            adapter = Path(adapter_directory.name) / "app_path.so"
            shutil.copy2(runtime / "compat/app_path.so", adapter)
            previous = env.get("LD_PRELOAD", "")
            env["LD_PRELOAD"] = str(adapter) + (":" + previous if previous else "")
            summary["compat_shim_sha256"] = digest(adapter)
        for step in plan:
            log = output / (step["name"] + ".console.log")
            record = {**step, "verifier_sha256": digest(Path(step["argv"][1])),
                      "console_log": log.name, "status": "FAIL"}
            print(f"Running {step['name']} verifier...", flush=True)
            try:
                with log.open("w", encoding="utf-8") as stream:
                    completed = subprocess.run(step["argv"], cwd=step["cwd"], env=env,
                                               stdout=stream, stderr=subprocess.STDOUT)
                record["exit_status"] = completed.returncode
                receipt = Path(step["receipt"])
                if receipt.is_file():
                    result = json.loads(receipt.read_text(encoding="utf-8"))
                    record["receipt_status"] = result.get("status")
                    record["receipt_sha256"] = digest(receipt)
                if completed.returncode == 0 and record.get("receipt_status") == "PASS":
                    record["status"] = "PASS"
            except (OSError, ValueError) as exc:
                record["failure"] = str(exc)
            if log.is_file():
                record["console_log_sha256"] = digest(log)
            summary["runs"].append(record)
            summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            print(f"{step['name']}: {record['status']} (see {log})", flush=True)
        summary["status"] = "PASS" if all(r["status"] == "PASS" for r in summary["runs"]) else "FAIL"
    except OSError as exc:
        summary["status"] = "FAIL"
        summary["failure"] = str(exc)
    finally:
        if adapter_directory is not None:
            adapter_directory.cleanup()
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"{summary['status']}: {summary_path}")
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
