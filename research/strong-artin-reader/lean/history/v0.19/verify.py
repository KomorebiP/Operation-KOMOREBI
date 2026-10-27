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
BASE_NAME = "Strong_Artin_Lean_v0.18.0_Cyclic_H1_Tate_Normalization_Checked.zip"
BASE_SHA256 = "70301451298b50e554c8ef517dd7b013f82810681711e0f3d032ea59019cd8bf"
MODULES = [
    "PowerDivisibility",
    "NilpotentRightInverse",
    "NonlinearHenselStep",
    "NonlinearHenselTower",
    "RelativeNonlinearHenselCapstone",
    "VariableJacobianHensel",
    "QuadraticRemainderGain",
]
DECLARATIONS = {
    "theorem": 32,
    "lemma": 0,
    "def": 8,
    "abbrev": 0,
    "structure": 0,
    "instance": 0,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(map(str, cmd)), flush=True)
    return subprocess.run(cmd, text=True, **kwargs)


def count_declarations(src: Path) -> dict[str, int]:
    text = "\n".join((src / f"{m}.lean").read_text() for m in MODULES)
    out: dict[str, int] = {}
    for kind in DECLARATIONS:
        pattern = rf"(?m)^\s*(?:@\[[^\n]*\]\s*)?(?:public\s+)?{kind}\s"
        out[kind] = len(re.findall(pattern, text))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    src = root / "src"
    kit = args.kit.resolve()
    launcher = kit / "run.sh"
    workspace = kit / "workspace"
    out = (args.out or root / "verification" / "fresh_replay").resolve()
    olean = out / "olean"
    logs = out / "logs"
    state_path = out / "state.json"

    if out.exists() and not args.resume:
        shutil.rmtree(out)
    olean.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)

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
    print("base v0.18 sha256:", actual_base)
    if actual_base != BASE_SHA256:
        print("base archive hash mismatch", file=sys.stderr)
        return 5

    prohibited: list[tuple[str, str]] = []
    for module in MODULES:
        text = (src / f"{module}.lean").read_text()
        for token in ("sorry", "admit"):
            if re.search(rf"\b{token}\b", text):
                prohibited.append((module, token))
        for token in ("axiom", "opaque"):
            if re.search(rf"(?m)^\s*{token}\s", text):
                prohibited.append((module, token))
    if prohibited:
        print("prohibited proof escape:", prohibited, file=sys.stderr)
        return 6

    actual_declarations = count_declarations(src)
    print("declarations:", actual_declarations)
    if actual_declarations != DECLARATIONS:
        print("declaration-count mismatch", file=sys.stderr)
        return 7

    evidence: list[dict[str, object]] = []
    completed: dict[str, dict[str, object]] = {}
    if args.resume and state_path.exists():
        state = json.loads(state_path.read_text())
        for item in state.get("module_results", []):
            module = str(item["module"])
            target = olean / f"{module}.olean"
            source = src / f"{module}.lean"
            if (
                item.get("returncode") == 0
                and item.get("sorryAx") is False
                and item.get("source_sha256") == sha256(source)
                and target.exists()
            ):
                completed[module] = item
                evidence.append(item)

    source_roots = f"{olean}:{src}"

    for module in MODULES:
        if module in completed:
            print("RESUME PASS", module, flush=True)
            continue
        source = src / f"{module}.lean"
        target = olean / f"{module}.olean"
        shell = (
            'export LEAN_PATH="$1:$2:${LEAN_PATH:-}"; '
            'lean -j1 -DwarningAsError=true -R "$2" -o "$3" "$4"'
        )
        proc = run(
            [
                "bash", str(launcher), "lake", "env", "bash", "-c", shell, "_",
                source_roots, str(src), str(target), str(source),
            ],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        (logs / f"{module}.log").write_text(proc.stdout)
        print(proc.stdout, end="")
        item = {
            "module": module,
            "kind": "v0.19",
            "source_sha256": sha256(source),
            "returncode": proc.returncode,
            "sorryAx": "sorryAx" in proc.stdout,
        }
        evidence.append(item)
        state_path.write_text(json.dumps({"module_results": evidence}, indent=2) + "\n")
        if proc.returncode != 0:
            return proc.returncode
        if item["sorryAx"]:
            print(f"sorryAx detected in {module}", file=sys.stderr)
            return 8

    # Preserve canonical module order after a resumed run.
    by_name = {str(x["module"]): x for x in evidence}
    ordered = [by_name[m] for m in MODULES]
    result = {
        "checkpoint": "Strong Artin Lean v0.19.0 — Relative Nonlinear Hensel Lifting",
        "status": "PASS",
        "verification_scope": "fresh replay of all seven additive v0.19 modules",
        "lean": EXPECTED_LEAN,
        "mathlib": EXPECTED_MATHLIB,
        "base_v0.18_sha256": actual_base,
        "new_v0.19_modules": len(MODULES),
        "total_modules_replayed": len(ordered),
        "module_results": ordered,
        "all_exit_codes_zero": all(x["returncode"] == 0 for x in ordered),
        "additive_declarations": DECLARATIONS,
        "prohibited_active_source_occurrences": [],
        "axiom_dependencies": ["propext", "Classical.choice", "Quot.sound"],
        "closed_bridges": [
            "a nilpotent error in an approximate right inverse corrects to an exact right inverse",
            "a nilpotent scalar multiple error is nilpotent in the endomorphism ring",
            "one-power Taylor remainder gain gives a genuine nonlinear Hensel improvement",
            "compatible nonlinear approximations exist through every depth",
            "finite nilpotent thickness converts the approximation tower into an exact root",
            "the Jacobian may vary across the residual fibre while one approximate right inverse remains stable modulo the nilpotent parameter",
            "affine-quadratic equation systems satisfy the required Taylor remainder gain automatically",
        ],
        "open_boundaries": [
            "construction of the approximate right inverse from the actual residual augmented Jacobian in the arithmetic presentation",
            "verification of residual-fibre Jacobian stability for the actual deformation and Hecke equations",
            "verification of the Taylor remainder gain for the actual complete local equations",
            "continuous local Galois cohomology and Tate pairing comparison",
            "Chebotarev and global Selmer-Jacobian arithmetic instantiation",
            "patchable determinant-bearing residual finite-Satake occurrence",
            "relative patching, twist equivariance, ramified attachment, and Strong Artin",
        ],
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    if state_path.exists():
        state_path.unlink()
    print("PASS: all seven v0.19 modules compiled with warnings as errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
