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
BASE_ZIP = "Strong_Artin_Lean_v0.13.0_Relative_Projector_Detection_Checked.zip"
BASE_ZIP_SHA256 = "a1bb7aa1b591fbe6e8bb15261d3b26cf3dfc5e033b328ffd6df3c4a525c20057"
BASE12_ZIP = "Strong_Artin_Lean_v0.12.0_Transverse_Obstruction_Checked.zip"

BASE12_MODULES = [
    "CyclicDefectAlgebra",
    "CyclicTransverseObstruction",
    "ProjectorProbeSurjectivity",
    "CyclicRelativeProbeObstruction",
]
BASE13_MODULES = [
    "CenteredProbeTransverse",
    "ProjectorTraceTransverse",
    "ActualProjectorCyclicObstruction",
    "AdequateProbeDetection",
    "ConjugationProjectorProbes",
    "AdequateProjectorCyclicObstruction",
    "FiniteProbeExtraction",
    "FiniteProjectorProbeExtraction",
    "RelativeSpectralDetection",
    "RelativeAdequacyProjectorCapstone",
]
NEW_MODULES = [
    "PreChebotarevSelector",
    "ProjectorPreChebotarevSelector",
    "RelativePreChebotarevSelector",
    "FiniteGroupH1Averaging",
    "H1RestrictionInjective",
    "CohomologicalRelativePreChebotarev",
    "TransverseAdjointRepresentation",
    "TransverseQuotientProjectorProbes",
    "TransverseCohomologicalPreChebotarev",
    "CyclotomicDepthSurvival",
    "QuotientFixedVectorAveraging",
    "TransverseAdjointNoFixed",
    "TransverseAdjointPullbackNoFixed",
    "RelativeCyclotomicDepthSurvival",
    "RelativeTaylorWilesPreChebotarev",
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


def unique_src_root(root: Path, module: str) -> Path:
    hits = list(root.rglob(f"src/{module}.lean"))
    if len(hits) != 1:
        raise RuntimeError(
            f"expected exactly one source root for {module}, found {len(hits)}: {hits}"
        )
    return hits[0].parent


def extract_once(archive: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--max-checks",
        type=int,
        default=0,
        help="compile at most this many not-yet-verified modules; 0 means all",
    )
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    kit = args.kit.resolve()
    launcher = kit / "run.sh"
    workspace = kit / "workspace"
    out = (args.out or root / "verification" / "fresh_replay").resolve()
    olean = out / "olean"
    logs = out / "logs"
    extracted = out / "base_extract"
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

    base_zip = root / "base" / BASE_ZIP
    actual_base_hash = sha256(base_zip)
    print("base v0.13 sha256:", actual_base_hash)
    if actual_base_hash != BASE_ZIP_SHA256:
        print("base archive hash mismatch", file=sys.stderr)
        return 5

    prohibited: list[tuple[str, str]] = []
    for module in NEW_MODULES:
        text = (root / "src" / f"{module}.lean").read_text()
        for token in ("sorry", "admit"):
            if re.search(rf"\b{token}\b", text):
                prohibited.append((module, token))
        if re.search(r"(?m)^\s*axiom\s", text):
            prohibited.append((module, "axiom"))
    if prohibited:
        print("prohibited proof escape:", prohibited, file=sys.stderr)
        return 6

    v013_extract = extracted / "v013"
    v012_extract = extracted / "v012"
    if not args.resume or not v013_extract.exists():
        extract_once(base_zip, v013_extract)
    base13_src = unique_src_root(v013_extract, "RelativeAdequacyProjectorCapstone")
    nested_v012 = list(v013_extract.rglob(BASE12_ZIP))
    if len(nested_v012) != 1:
        raise RuntimeError(f"expected one nested v0.12 archive, found {len(nested_v012)}")
    if not args.resume or not v012_extract.exists():
        extract_once(nested_v012[0], v012_extract)
    base12_src = unique_src_root(v012_extract, "ProjectorProbeSurjectivity")
    new_src = root / "src"

    original_jobs: list[tuple[str, str, Path]] = []
    original_jobs += [("base-v0.12", m, base12_src / f"{m}.lean") for m in BASE12_MODULES]
    original_jobs += [("base-v0.13", m, base13_src / f"{m}.lean") for m in BASE13_MODULES]
    original_jobs += [("new-v0.14", m, new_src / f"{m}.lean") for m in NEW_MODULES]

    # Lean's `-R` option requires every compiled source to be contained in one
    # root. Stage the exact dependency closure into a flat module directory.
    staged_src = out / "staged_src"
    staged_src.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, str, Path]] = []
    for kind, module, source in original_jobs:
        if not source.exists():
            print(f"missing source: {source}", file=sys.stderr)
            return 7
        staged = staged_src / f"{module}.lean"
        shutil.copy2(source, staged)
        jobs.append((kind, module, staged))

    compiled_this_run = 0
    evidence: list[dict[str, object]] = []
    for kind, module, source in jobs:
        if not source.exists():
            print(f"missing source: {source}", file=sys.stderr)
            return 7
        digest = sha256(source)
        stamp = logs / f"{module}.json"
        object_file = olean / f"{module}.olean"
        if args.resume and stamp.exists() and object_file.exists():
            try:
                old = json.loads(stamp.read_text())
                if old.get("returncode") == 0 and old.get("source_sha256") == digest:
                    print("REUSE", module, digest)
                    evidence.append(old)
                    continue
            except Exception:
                pass

        if args.max_checks and compiled_this_run >= args.max_checks:
            print("PARTIAL: max-checks reached; rerun with --resume")
            return 2

        shell = (
            'export LEAN_PATH="$1:$2:${LEAN_PATH:-}"; '
            'lean -j1 -DwarningAsError=true -R "$2" -o "$3" "$4"'
        )
        proc = run(
            [
                "bash",
                str(launcher),
                "lake",
                "env",
                "bash",
                "-c",
                shell,
                "_",
                str(olean),
                str(staged_src),
                str(object_file),
                str(source),
            ],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        (logs / f"{module}.log").write_text(proc.stdout)
        print(proc.stdout, end="")
        record = {
            "kind": kind,
            "module": module,
            "source_sha256": digest,
            "returncode": proc.returncode,
        }
        stamp.write_text(json.dumps(record, indent=2) + "\n")
        evidence.append(record)
        compiled_this_run += 1
        if proc.returncode != 0:
            return proc.returncode

    result = {
        "pass": True,
        "lean": EXPECTED_LEAN,
        "mathlib": EXPECTED_MATHLIB,
        "base_v0.13_sha256": actual_base_hash,
        "base_modules": len(BASE12_MODULES) + len(BASE13_MODULES),
        "new_modules": len(NEW_MODULES),
        "modules": evidence,
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        "PASS: v0.12/v0.13 dependency closure and all fifteen v0.14 modules "
        "compiled with warnings as errors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
