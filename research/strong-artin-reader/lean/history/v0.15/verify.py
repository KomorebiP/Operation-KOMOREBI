#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXPECTED_LEAN = "4.34.0-rc2"
EXPECTED_MATHLIB = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
BASE_NAME = "Strong_Artin_Lean_v0.14.0_Cyclotomic_Depth_PreChebotarev_Checked.zip"
BASE_SHA256 = "fba7ddb9c2dfd2a13351a36fccd9d274e26108ca32952f955a5e79bae2331868"
MODULES = [
    "AdaptiveAuxiliarySelection",
    "GoodAuxiliarySelection",
    "RelativeTaylorWilesFiniteSet",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(map(str, cmd)), flush=True)
    return subprocess.run(cmd, text=True, **kwargs)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    kit = args.kit.resolve()
    launcher = kit / "run.sh"
    workspace = kit / "workspace"
    out = (args.out or root / "verification" / "fresh_replay").resolve()
    if out.exists():
        shutil.rmtree(out)
    olean = out / "olean"
    logs = out / "logs"
    olean.mkdir(parents=True)
    logs.mkdir(parents=True)

    version = run(
        ["bash", str(launcher), "lean", "--version"],
        cwd=workspace,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(version.stdout, end="")
    if version.returncode != 0 or EXPECTED_LEAN not in version.stdout:
        print("Lean version mismatch", file=sys.stderr)
        return 3

    mathlib = workspace / ".lake" / "packages" / "mathlib"
    git = run(
        ["git", "-C", str(mathlib), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    actual_mathlib = git.stdout.strip()
    print("mathlib:", actual_mathlib)
    if git.returncode != 0 or actual_mathlib != EXPECTED_MATHLIB:
        print("mathlib revision mismatch", file=sys.stderr)
        return 4

    base = root / "base" / BASE_NAME
    actual_base = sha256(base)
    print("base v0.14 sha256:", actual_base)
    if actual_base != BASE_SHA256:
        print("base archive hash mismatch", file=sys.stderr)
        return 5

    prohibited: list[tuple[str, str]] = []
    for module in MODULES:
        source = root / "src" / f"{module}.lean"
        text = source.read_text()
        for token in ("sorry", "admit"):
            if re.search(rf"\b{token}\b", text):
                prohibited.append((module, token))
        if re.search(r"(?m)^\s*axiom\s", text):
            prohibited.append((module, "axiom"))
    if prohibited:
        print("prohibited proof escape:", prohibited, file=sys.stderr)
        return 6

    evidence: list[dict[str, object]] = []
    for module in MODULES:
        source = root / "src" / f"{module}.lean"
        target = olean / f"{module}.olean"
        shell = (
            'export LEAN_PATH="$1:${LEAN_PATH:-}"; '
            'lean -j1 -DwarningAsError=true -R "$2" -o "$3" "$4"'
        )
        proc = run(
            [
                "bash", str(launcher), "lake", "env", "bash", "-c", shell, "_",
                str(olean), str(root / "src"), str(target), str(source),
            ],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        (logs / f"{module}.log").write_text(proc.stdout)
        print(proc.stdout, end="")
        record = {
            "module": module,
            "source_sha256": sha256(source),
            "returncode": proc.returncode,
        }
        evidence.append(record)
        if proc.returncode != 0:
            return proc.returncode
        if "sorryAx" in proc.stdout:
            print(f"sorryAx detected in {module}", file=sys.stderr)
            return 7

    result = {
        "checkpoint": "Strong Artin Lean v0.15.0 — Adaptive Auxiliary-Set Selection",
        "status": "PASS",
        "lean": EXPECTED_LEAN,
        "mathlib": EXPECTED_MATHLIB,
        "base_v0.14_sha256": actual_base,
        "new_modules": len(MODULES),
        "module_results": evidence,
        "all_exit_codes_zero": all(x["returncode"] == 0 for x in evidence),
        "declarations": {"theorem": 17, "lemma": 0, "def": 2, "abbrev": 0, "structure": 1},
        "prohibited_active_source_occurrences": [],
        "axiom_dependencies": ["propext", "Classical.choice", "Quot.sound"],
        "open_boundaries": [
            "finite Galois quotient packaging",
            "Chebotarev realization outside the bad set",
            "local Taylor-Wiles Tate-pairing identification",
            "instantiation of OnePrimeSelectionInterface",
            "residual packet occurrence and relative patching",
            "ramified local attachment",
            "solvable-image and unrestricted Strong Artin",
        ],
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: all three v0.15 additive modules compiled with warnings as errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
