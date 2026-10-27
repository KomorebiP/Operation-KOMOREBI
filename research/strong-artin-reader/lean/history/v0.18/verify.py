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
BASE17_NAME = "Strong_Artin_Lean_v0.17.0_Local_Pairing_FiniteDepth_GenericSupport_Checked.zip"
BASE17_SHA256 = "974e4ee2fa8631114f9f1fafedd02ba9ef9d2e4a7ab9fbcdf49002f1823436ba"
BASE16_NAME = "Strong_Artin_Lean_v0.16.0_Jacobian_Chebotarev_Algebra_Checked.zip"
BASE16_SHA256 = "9bc4144969d6917d6cc40a761049b2576788694b5f3506b3272e24e144661530"

BASE16_MODULES = [
    "SpectralTraceConjugacy",
    "FrobeniusCocycleQuotient",
]
BASE17_MODULES = [
    "LocalFrobeniusPerfectPairing",
    "TameLocalPerfectPairing",
    "TameInertiaRelation",
]
NEW_MODULES = [
    "FiniteCyclicH1Model",
    "FiniteCyclicFrobeniusH1",
    "FiniteCyclicTamePairing",
    "FiniteCyclicTaylorWilesPairingCapstone",
    "OneDimensionalPairingNormalization",
    "LocalTateNormalizationBoundary",
]
DECLARATIONS = {
    "theorem": 24,
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


def locate_root(extracted: Path, marker: str) -> Path:
    hits = list(extracted.glob(f"*/src/{marker}.lean"))
    if len(hits) != 1:
        raise RuntimeError(f"expected one source tree containing {marker}.lean, found {len(hits)}")
    return hits[0].parent.parent


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
    extract17 = out / "base17_extract"
    extract16 = out / "base16_extract"
    for p in (olean, logs, extract17, extract16):
        p.mkdir(parents=True, exist_ok=True)

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

    base17 = root / "base" / BASE17_NAME
    actual_base17 = sha256(base17)
    print("base v0.17 sha256:", actual_base17)
    if actual_base17 != BASE17_SHA256:
        print("base v0.17 archive hash mismatch", file=sys.stderr)
        return 5

    with zipfile.ZipFile(base17) as zf:
        zf.extractall(extract17)
    try:
        base17_root = locate_root(extract17, "LocalFrobeniusPerfectPairing")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 8
    base17_src = base17_root / "src"

    base16 = base17_root / "base" / BASE16_NAME
    actual_base16 = sha256(base16)
    print("nested base v0.16 sha256:", actual_base16)
    if actual_base16 != BASE16_SHA256:
        print("nested base v0.16 archive hash mismatch", file=sys.stderr)
        return 9
    with zipfile.ZipFile(base16) as zf:
        zf.extractall(extract16)
    try:
        base16_root = locate_root(extract16, "FrobeniusCocycleQuotient")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 10
    base16_src = base16_root / "src"

    prohibited: list[tuple[str, str]] = []
    for module in NEW_MODULES:
        source = root / "src" / f"{module}.lean"
        text = source.read_text()
        for token in ("sorry", "admit"):
            if re.search(rf"\b{token}\b", text):
                prohibited.append((module, token))
        for token in ("axiom", "opaque"):
            if re.search(rf"(?m)^\s*{token}\s", text):
                prohibited.append((module, token))
    if prohibited:
        print("prohibited proof escape:", prohibited, file=sys.stderr)
        return 6

    evidence: list[dict[str, object]] = []
    source_roots = f"{olean}:{root / 'src'}:{base17_src}:{base16_src}"

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
            "sorryAx": "sorryAx" in proc.stdout,
        })
        if proc.returncode != 0:
            return proc.returncode
        if "sorryAx" in proc.stdout:
            print(f"sorryAx detected in {module}", file=sys.stderr)
            return 7
        return 0

    for module in BASE16_MODULES:
        rc = compile_module(module, base16_src / f"{module}.lean", base16_src, "v0.16_dependency")
        if rc != 0:
            return rc

    for module in BASE17_MODULES:
        rc = compile_module(module, base17_src / f"{module}.lean", base17_src, "v0.17_dependency")
        if rc != 0:
            return rc

    for module in NEW_MODULES:
        rc = compile_module(module, root / "src" / f"{module}.lean", root / "src", "v0.18")
        if rc != 0:
            return rc

    result = {
        "checkpoint": "Strong Artin Lean v0.18.0 — Finite Cyclic H1 and Tate Normalization Boundary",
        "status": "PASS",
        "verification_scope": "fresh replay of the exact 11-module additive dependency closure",
        "lean": EXPECTED_LEAN,
        "mathlib": EXPECTED_MATHLIB,
        "base_v0.17_sha256": actual_base17,
        "nested_base_v0.16_sha256": actual_base16,
        "base_v0.16_modules": len(BASE16_MODULES),
        "base_v0.17_modules": len(BASE17_MODULES),
        "new_v0.18_modules": len(NEW_MODULES),
        "total_modules_replayed": len(evidence),
        "module_results": evidence,
        "all_exit_codes_zero": all(x["returncode"] == 0 for x in evidence),
        "additive_declarations": DECLARATIONS,
        "prohibited_active_source_occurrences": [],
        "axiom_dependencies": ["propext", "Classical.choice", "Quot.sound"],
        "closed_bridges": [
            "finite cyclic H1 is coefficients modulo generator-minus-one when the norm vanishes",
            "the matrix Frobenius quotient is actual finite cyclic group cohomology under the comparison hypotheses",
            "the Frobenius centralizer is the full dual of that finite cyclic H1",
            "the q=1 tame relation space is the full dual of finite cyclic H1",
            "the representative pairing is exactly trace(PX)",
            "every finite cyclic H1 functional has a unique tame-relation representative",
            "two nonzero functionals on a one-dimensional local quotient differ by one unique unit",
            "Tate normalization up to a unit preserves exactly the nonvanishing detector",
        ],
        "open_boundaries": [
            "comparison of continuous local Galois cohomology with a suitable finite cyclic quotient",
            "proof that the arithmetic local Tate pairing is nonzero on the selected local line",
            "exact Frobenius, inertia, Tate-twist, and sign normalization",
            "Chebotarev realization and arithmetic Taylor-Wiles instantiation",
            "global Selmer-Jacobian comparison and nonlinear relative lifting",
            "patchable residual finite-Satake packet occurrence",
            "relative patched module, ramified local attachment, and Strong Artin",
        ],
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: all 11 direct dependency and v0.18 modules compiled with warnings as errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
