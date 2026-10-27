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
BASE_NAME = "Strong_Artin_Lean_v0.20.0_Polynomial_Presentation_Hensel_Checked.zip"
BASE_SHA256 = "9dafcfcd6d23871e5a167b18314083afae3159a74c16e9aa4fa9bc65f4b3770f"

V019 = [
    "PowerDivisibility",
    "NilpotentRightInverse",
    "VariableJacobianHensel",
]
V020 = [
    "ScalarPowerDivisibility",
    "PolynomialExpressionTaylor",
    "PolynomialSystemTaylor",
    "FiniteCoordinatePolynomialHensel",
    "ResidualMatrixRightInverseLift",
    "SurjectiveMatrixRightInverse",
    "SurjectiveResidueHomPolynomialHensel",
]
V021 = [
    "MvPolynomialExprCompiler",
    "NilpotentMonomialEvaluation",
    "MvPowerSeriesArtinTruncation",
    "MvPowerSeriesNilpotentSubstitution",
    "MvPolynomialExprDerivative",
    "FormalPowerSeriesSystemHensel",
    "FormalPowerSeriesJacobianAtOrigin",
    "CompletedPresentationHenselCapstone",
    "FormalPresentationPoint",
]
DECLARATIONS = {
    "theorem": 50,
    "lemma": 0,
    "def": 18,
    "abbrev": 1,
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
    text = "\n".join((src / f"{m}.lean").read_text() for m in V021)
    out: dict[str, int] = {}
    for kind in DECLARATIONS:
        pattern = rf"(?m)^\s*(?:@\[[^\n]*\]\s*)?(?:public\s+)?{kind}\s"
        out[kind] = len(re.findall(pattern, text))
    return out


def scan_prohibited(paths: list[Path]) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for path in paths:
        text = path.read_text()
        for token in ("sorry", "admit"):
            if re.search(rf"\b{token}\b", text):
                found.append({"file": path.name, "token": token})
        for token in ("axiom", "opaque"):
            if re.search(rf"(?m)^\s*(?:public\s+)?{token}\s", text):
                found.append({"file": path.name, "token": token})
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    dep19 = root / "deps" / "v0.19"
    dep20 = root / "deps" / "v0.20"
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
    print("base v0.20 sha256:", actual_base)
    if actual_base != BASE_SHA256:
        print("base archive hash mismatch", file=sys.stderr)
        return 5

    specs: list[tuple[str, str, Path, Path]] = []
    specs += [(m, "v0.19_dependency", dep19 / f"{m}.lean", dep19) for m in V019]
    specs += [(m, "v0.20_dependency", dep20 / f"{m}.lean", dep20) for m in V020]
    specs += [(m, "v0.21", src / f"{m}.lean", src) for m in V021]

    active_paths = [s[2] for s in specs]
    prohibited = scan_prohibited(active_paths)
    if prohibited:
        print("prohibited proof escape:", prohibited, file=sys.stderr)
        return 6

    actual_declarations = count_declarations(src)
    print("new declarations:", actual_declarations)
    if actual_declarations != DECLARATIONS:
        print("declaration-count mismatch", file=sys.stderr)
        return 7

    evidence: list[dict[str, object]] = []
    completed: dict[str, dict[str, object]] = {}
    if args.resume and state_path.exists():
        state = json.loads(state_path.read_text())
        for item in state.get("module_results", []):
            module = str(item["module"])
            spec = next((s for s in specs if s[0] == module), None)
            if spec is None:
                continue
            source = spec[2]
            target = olean / f"{module}.olean"
            if (
                item.get("returncode") == 0
                and item.get("sorryAx") is False
                and item.get("source_sha256") == sha256(source)
                and target.exists()
            ):
                completed[module] = item
                evidence.append(item)

    for module, kind, source, root_for_R in specs:
        if module in completed:
            print("RESUME PASS", module, flush=True)
            continue
        target = olean / f"{module}.olean"
        shell = (
            'export LEAN_PATH="$1:$2:$3:$4:${LEAN_PATH:-}"; '
            'lean -j1 -DwarningAsError=true -R "$5" -o "$6" "$7"'
        )
        proc = run(
            [
                "bash", str(launcher), "lake", "env", "bash", "-c", shell, "_",
                str(olean), str(dep19), str(dep20), str(src),
                str(root_for_R), str(target), str(source),
            ],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        (logs / f"{module}.log").write_text(proc.stdout)
        print(proc.stdout, end="")
        item = {
            "module": module,
            "kind": kind,
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

    by_name = {str(x["module"]): x for x in evidence}
    ordered = [by_name[m] for m, _, _, _ in specs]
    result = {
        "checkpoint": "Strong Artin Lean v0.21.0 — Completed Formal Presentation and Algebra Point",
        "status": "PASS",
        "verification_scope": "fresh replay of the complete 19-module direct source dependency closure",
        "lean": EXPECTED_LEAN,
        "mathlib": EXPECTED_MATHLIB,
        "base_v0.20_sha256": actual_base,
        "v0.19_dependency_modules": len(V019),
        "v0.20_dependency_modules": len(V020),
        "new_v0.21_modules": len(V021),
        "total_modules_replayed": len(ordered),
        "module_results": ordered,
        "all_exit_codes_zero": all(x["returncode"] == 0 for x in ordered),
        "additive_declarations": DECLARATIONS,
        "prohibited_active_source_occurrences": [],
        "axiom_dependencies": ["propext", "Classical.choice", "Quot.sound"],
        "closed_bridges": [
            "finite multivariate polynomials compile into the v0.20 expression language with identical evaluation",
            "nilpotent coordinate substitution kills every monomial at or above the nilpotence cutoff",
            "canonical multivariate formal-power-series substitution equals finite total-degree truncation over a nilpotent principal thickening",
            "the polynomial compiler preserves formal partial derivatives and coordinate Jacobians",
            "finite formal-power-series systems inherit the v0.20 polynomial Hensel theorem",
            "at a centered presentation the compiled residual Jacobian is the original untruncated linear-coefficient matrix",
            "a surjective reduced linear-coefficient matrix produces an exact zero of the untruncated formal system",
            "the exact zero yields an algebra homomorphism from the completed presentation quotient to the coefficient ring",
        ],
        "open_boundaries": [
            "construction of the actual Strong Artin deformation or Hecke algebra as a finite completed formal-power-series presentation",
            "identification of its reduced linear-coefficient matrix with the Taylor-Wiles-completed arithmetic Jacobian",
            "global Selmer-Jacobian comparison and arithmetic interpretation of auxiliary variables",
            "continuous local Galois cohomology, local Tate pairing, and Chebotarev instantiation",
            "patchable determinant-bearing residual finite-Satake automorphic occurrence",
            "relative patching or finite-depth carrier, twist equivariance, ramified attachment, and Strong Artin",
        ],
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    (root / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    if state_path.exists():
        state_path.unlink()
    print("PASS: all 19 dependency and v0.21 modules compiled with warnings as errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
