#!/usr/bin/env python3
"""Recheck the Paper VII first block using the pinned portable Linux Lean kit.

Author: Komorebi P.
This checks the four active modules, their axiom inventories, and two expected
failure controls. It neither rebuilds Mathlib nor verifies the whole PRSC series.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

MATHLIB_REV = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
LEAN_VERSION = "4.34.0-rc2"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
MODULES = ("QuantumPacketCore", "SchurFeshbach", "LowModeConvergence", "ConstraintAudit")


def without_comments(text: str) -> str:
    """Discard Lean comments (including nested block comments) and string contents."""
    result: list[str] = []
    i, depth = 0, 0
    while i < len(text):
        if text.startswith("/-", i):
            depth += 1
            i += 2
        elif depth and text.startswith("-/", i):
            depth -= 1
            i += 2
            result.append(" ")
        elif depth:
            i += 1
        elif text.startswith("--", i):
            j = text.find("\n", i)
            i = len(text) if j < 0 else j
        elif text[i] == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
            i += 1
            result.append(" ")
        else:
            result.append(text[i])
            i += 1
    if depth:
        raise ValueError("Unterminated block comment")
    return "".join(result)


def run(command: list[str], timeout: int, cwd: Path | None = None) -> tuple[int, str, float]:
    started = time.monotonic()
    try:
        proc = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, round(time.monotonic() - started, 3)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        return 124, output + "\nVERIFIER TIMEOUT\n", round(time.monotonic() - started, 3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=180, help="Per-file compiler time limit")
    parser.add_argument("--out", type=Path, help="Output evidence directory, separate from archived evidence")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("Timeout must be positive")
    base = Path(__file__).resolve().parents[1]
    kit = args.kit.expanduser().resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = args.out or (base / "verification" / ("rerun_" + stamp))
    out.mkdir(parents=True, exist_ok=True)
    for needed in [kit / "run.sh", kit / "toolchain/bin/lean", kit / "workspace/lake-manifest.json"]:
        if not needed.is_file():
            parser.error(f"Missing kit file: {needed}")
    inventory = json.loads((base / "verification/theorem_inventory.json").read_text())
    report: dict = {
        "release": "PRSC_VII_v0.1.0_Checked_First_Block", "started_utc": stamp,
        "expected_lean_version": LEAN_VERSION, "expected_mathlib_revision": MATHLIB_REV,
        "allowed_axioms": sorted(ALLOWED_AXIOMS), "modules": [], "negative_controls": [],
        "scope": {"manuscript_items_checked": 6, "manuscript_finite_items": 19,
                  "manuscript_finite_items_not_checked": 13, "continuum_conjectures_not_proved": 5,
                  "prior_papers_rerun": False, "original_numerical_suite_rerun": False,
                  "mathlib_rebuilt_or_independently_rechecked": False},
    }
    version_cmd = ["bash", str(kit / "run.sh"), "lean", "--version"]
    code, version, elapsed = run(version_cmd, 60, kit / "workspace")
    (out / "lean_version.log").write_text(version)
    manifest = json.loads((kit / "workspace/lake-manifest.json").read_text())
    mathlib = next((x for x in manifest["packages"] if x["name"] == "mathlib"), {})
    gitcode, gitrev, _ = run(["git", "-C", str(kit / "workspace/.lake/packages/mathlib"),
                             "rev-parse", "HEAD"], 30)
    report["runtime"] = {"version": version.strip(), "version_exit_code": code,
                         "version_seconds": elapsed, "manifest_mathlib_revision": mathlib.get("rev"),
                         "actual_mathlib_revision": gitrev.strip(), "git_exit_code": gitcode}
    report["runtime"]["pass"] = (code == 0 and LEAN_VERSION in version and gitcode == 0
        and gitrev.strip() == MATHLIB_REV and mathlib.get("rev") == MATHLIB_REV)
    if not report["runtime"]["pass"]:
        report["pass"] = False
        (out / "SUMMARY.json").write_text(json.dumps(report, indent=2) + "\n")
        print("Runtime version or dependency pin mismatch. No theorem check claimed.")
        return 1

    runner = base / "scripts/check_low_memory.py"
    total_declarations = 0
    for name in MODULES:
        source = base / "formalization" / (name + ".lean")
        text = source.read_text()
        stripped = without_comments(text)
        forbidden = sorted(set(re.findall(r"\b(?:sorry|admit|axiom|unsafe|native_decide)\b", stripped)))
        declaration_count = len(re.findall(r"\btheorem\s+\w+", stripped))
        cmd = [sys.executable, str(runner), "--kit", str(kit), "--threads", "1",
               "--timeout", str(args.timeout), str(source)]
        rc, log, seconds = run(cmd, args.timeout + 120)
        (out / (name + ".log")).write_text(log)
        audits = {n: [a.strip() for a in ax.split(",") if a.strip()] for n, ax in
                  re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", log)}
        expected = set(inventory[name])
        unexpected_axioms = sorted({a for ax in audits.values() for a in ax} - ALLOWED_AXIOMS)
        good = (rc == 0 and not forbidden and not unexpected_axioms and
                set(audits) == expected and declaration_count == len(expected) and
                not re.search(r"\b(?:warning|error):", log, flags=re.I))
        row = {"module": name, "source": str(source.relative_to(base)),
               "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "command": cmd,
               "exit_code": rc, "seconds": seconds, "theorem_declarations": declaration_count,
               "forbidden_tokens": forbidden, "axiom_audits": audits,
               "unexpected_axioms": unexpected_axioms, "pass": good}
        report["modules"].append(row)
        total_declarations += declaration_count
        print(f"{name}: {'PASS' if good else 'FAIL'} ({declaration_count} declarations, {seconds}s)")

    controls = [("FalseEquality", "decide"), ("SorryPlaceholder", "sorry")]
    for name, marker in controls:
        source = base / "verification/negative_controls" / (name + ".lean")
        cmd = [sys.executable, str(runner), "--kit", str(kit), "--threads", "1",
               "--timeout", str(args.timeout), str(source)]
        rc, log, seconds = run(cmd, args.timeout + 120)
        (out / (name + ".log")).write_text(log)
        good = rc == 1 and "error:" in log and marker in log
        report["negative_controls"].append({"name": name, "expected_exit_code": 1,
            "exit_code": rc, "seconds": seconds, "source": str(source.relative_to(base)),
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "pass": good})
        print(f"{name}: {'PASS (expected rejection)' if good else 'FAIL'}")

    report["theorem_declarations"] = total_declarations
    report["pass"] = (report["runtime"]["pass"] and all(x["pass"] for x in report["modules"])
                       and all(x["pass"] for x in report["negative_controls"]))
    report["total_module_seconds"] = round(sum(x["seconds"] for x in report["modules"]), 3)
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (out / "SUMMARY.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Summary: {out / 'SUMMARY.json'}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
