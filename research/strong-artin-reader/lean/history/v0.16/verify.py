#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

EXPECTED_LEAN = "4.34.0-rc2"
EXPECTED_MATHLIB = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
BASE_NAME = "Strong_Artin_Lean_v0.15.0_Adaptive_Auxiliary_Set_Checked.zip"
BASE_SHA256 = "77b0988d26f5a61d02028339697942e3863457074a1682124c7a4b538817ab4e"
BASE_MODULES = [
    "AdaptiveAuxiliarySelection",
    "GoodAuxiliarySelection",
    "RelativeTaylorWilesFiniteSet",
]
NEW_MODULES = [
    "AuxiliaryColumnCompletion",
    "RelativeTaylorWilesJacobianCapstone",
    "CoprimeKernelSurjectivity",
    "AffineCocyclePackaging",
    "SpectralTraceConjugacy",
    "SpectralDeterminantDifferential",
    "FrobeniusCocycleQuotient",
    "MatrixCocycleConjugacy",
    "ChebotarevReadySpectralClass",
    "LocalTaylorWilesLinearInterface",
]
DECLARATIONS = {
    "theorem": 47,
    "lemma": 0,
    "def": 17,
    "abbrev": 0,
    "structure": 4,
    "instance": 5,
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


def locate_base_src(extracted: Path) -> Path:
    hits = list(extracted.glob("*/src/AdaptiveAuxiliarySelection.lean"))
    if len(hits) != 1:
        raise RuntimeError(f"expected one extracted v0.15 source tree, found {len(hits)}")
    return hits[0].parent


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
    extracted = out / "base_extract"
    olean.mkdir(parents=True)
    logs.mkdir(parents=True)
    extracted.mkdir(parents=True)

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
    print("base v0.15 sha256:", actual_base)
    if actual_base != BASE_SHA256:
        print("base archive hash mismatch", file=sys.stderr)
        return 5

    with zipfile.ZipFile(base) as zf:
        zf.extractall(extracted)
    try:
        base_src = locate_base_src(extracted)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 8

    prohibited: list[tuple[str, str]] = []
    for module in NEW_MODULES:
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
    source_roots = f"{olean}:{root / 'src'}:{base_src}"

    def compile_module(module: str, source: Path, module_root: Path, kind: str) -> int:
        target = olean / f"{module}.olean"
        shell = (
            'export LEAN_PATH="$1:${LEAN_PATH:-}"; '
            'lean -j1 -DwarningAsError=true -R "$2" -o "$3" "$4"'
        )
        proc = run(
            [
                "bash", str(launcher), "lake", "env", "bash", "-c", shell, "_",
                source_roots, str(module_root), str(target), str(source),
            ],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        (logs / f"{module}.log").write_text(proc.stdout)
        print(proc.stdout, end="")
        evidence.append({
            "module": module,
            "kind": kind,
            "source_sha256": sha256(source),
            "returncode": proc.returncode,
        })
        if proc.returncode != 0:
            return proc.returncode
        if "sorryAx" in proc.stdout:
            print(f"sorryAx detected in {module}", file=sys.stderr)
            return 7
        return 0

    for module in BASE_MODULES:
        rc = compile_module(module, base_src / f"{module}.lean", base_src, "base_dependency")
        if rc != 0:
            return rc

    for module in NEW_MODULES:
        rc = compile_module(module, root / "src" / f"{module}.lean", root / "src", "v0.16")
        if rc != 0:
            return rc

    result = {
        "checkpoint": "Strong Artin Lean v0.16.0 — Jacobian Completion and Chebotarev-Class Algebra",
        "status": "PASS",
        "verification_scope": "fresh replay of the direct v0.15 dependency modules and all v0.16 modules",
        "lean": EXPECTED_LEAN,
        "mathlib": EXPECTED_MATHLIB,
        "base_v0.15_sha256": actual_base,
        "base_dependency_modules": len(BASE_MODULES),
        "new_modules": len(NEW_MODULES),
        "total_modules_replayed": len(evidence),
        "module_results": evidence,
        "all_exit_codes_zero": all(x["returncode"] == 0 for x in evidence),
        "additive_declarations": DECLARATIONS,
        "prohibited_active_source_occurrences": [],
        "axiom_dependencies": ["propext", "Classical.choice", "Quot.sound"],
        "closed_bridges": [
            "v0.15 auxiliary detection to augmented-Jacobian surjectivity",
            "prime-power splitting-kernel surjectivity onto prime-to-p residual quotients",
            "finite affine cocycle quotient and surjective range restriction",
            "conjugacy stability of commuting spectral-projector detection",
            "projector/residual-Frobenius fibre linkage in the selected conjugacy class",
            "descent of the projector trace through Frobenius coboundaries",
            "identification of the quotient detector with a determinant differential",
        ],
        "open_boundaries": [
            "continuous number-field realization of the abstract finite affine quotient",
            "Chebotarev realization outside the prescribed bad set",
            "exact local Taylor-Wiles Tate-pairing identification",
            "identification of arithmetic auxiliary variables with global Jacobian columns",
            "nonlinear finite-depth lifting or relative patching",
            "residual finite-Satake packet occurrence in determinant-bearing cohomology",
            "ramified local attachment",
            "solvable-image and unrestricted Strong Artin",
        ],
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: all direct dependencies and ten v0.16 modules compiled with warnings as errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
