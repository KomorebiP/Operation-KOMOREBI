#!/usr/bin/env python3
"""Reproduce the Komorebi IUT–KTG Block 03 Lean verification.

This verifier checks the finite implementation claim only: the recorded sources
build, every Lean source elaborates with warnings as errors, predecessor core
sources are unchanged, required Block 03 interfaces are present, and no
prohibited placeholders occur.  It does not authenticate the IUT papers or
prove/disprove IUT III Corollary 3.12.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "formalization" / "lean"
OUT = ROOT / "verification" / "block03_final"
BLOCK02_REPORT = ROOT / "verification" / "block02_final" / "verification.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def executable(env_name: str, fallback: str) -> str:
    candidate = os.environ.get(env_name)
    if candidate:
        p = Path(candidate)
        if not p.is_file():
            raise SystemExit(f"{env_name} does not name a file: {candidate}")
        return str(p)
    found = shutil.which(fallback)
    if not found:
        raise SystemExit(
            f"Missing {fallback}. Put it on PATH or set {env_name} to the executable."
        )
    return found


def run(
    argv: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout_seconds: int = 600,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout_seconds,
        )
        return {
            "argv": argv,
            "cwd": str(cwd),
            "returncode": proc.returncode,
            "timed_out": False,
            "timeout_seconds": timeout_seconds,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "output": proc.stdout,
        }
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return {
            "argv": argv,
            "cwd": str(cwd),
            "returncode": None,
            "timed_out": True,
            "timeout_seconds": timeout_seconds,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "output": output,
        }


def strip_lean_comments(text: str) -> str:
    """Remove nested block and line comments for a conservative token scan."""
    out: list[str] = []
    i = 0
    depth = 0
    in_string = False
    while i < len(text):
        if depth:
            if text.startswith("/-", i):
                depth += 1
                i += 2
            elif text.startswith("-/", i):
                depth -= 1
                i += 2
            else:
                if text[i] == "\n":
                    out.append("\n")
                i += 1
            continue
        if not in_string and text.startswith("/-", i):
            depth = 1
            i += 2
            continue
        if not in_string and text.startswith("--", i):
            j = text.find("\n", i)
            if j == -1:
                break
            out.append("\n")
            i = j + 1
            continue
        ch = text[i]
        out.append(ch)
        if ch == '"' and (i == 0 or text[i - 1] != "\\"):
            in_string = not in_string
        i += 1
    return "".join(out)


def contract_audit() -> dict[str, Any]:
    requirements: dict[str, list[str]] = {
        "formalization/lean/KTG/IUT312Types.lean": [
            "structure TypedData",
            "MultiradialOutputPackage",
            "FixedQPilot",
            "HolomorphicHullInput",
            "ComparableLineObject",
            "LogVolumeMeasurement",
            "def QPilotHullContainment",
            "qPilotHullContainment_iff_hullWitness",
        ],
        "formalization/lean/KTG/IUT312Certificates.lean": [
            "structure ObstructionSemantics",
            "Ind1State",
            "Ind2State",
            "Ind3State",
            "structure InputPrimeStripLink",
            "structure SimultaneousHolomorphicExpressibility",
            "structure AlgorithmicParallelTransport",
            "structure SourceRealizationCertificate",
            "def certification",
        ],
        "formalization/lean/KTG/IUT312Normalization.lean": [
            "structure OutputGrade",
            "structure DeterminantGrade",
            "structure ProcessionInputGrade",
            "structure QPilotGrade",
            "def normalizationGradeBridge",
            "def directNormalization",
            "structure IUTIVSquareWeightedGrade",
            "attachIUTIVSquareWeight_exponent",
        ],
        "formalization/lean/KTG/IUT312WitnessObligation.lean": [
            "def StepXiEWitnessPreservation",
            "structure SourceWitnessTheorem",
            "def witnessBridgeOfSourceTheorem",
            "theorem scalarBoundOfSourceWitness",
        ],
        "formalization/lean/KTG/IUT312SourceCountermodel.lean": [
            "theorem all_source_prewitness_fields_do_not_imply_containment",
            "theorem no_sourceWitnessTheorem",
        ],
        "formalization/lean/KTG/IUT312Cor312Bridge.lean": [
            "def cor312Interface",
            "theorem witness312_iff_qPilotHullContainment",
            "theorem cor312CertificateOfSourceWitness",
            "theorem cor312ScalarBoundOfSourceWitness",
        ],
        "formalization/lean/KTG/IUT312SourceExample.lean": [
            "namespace SourceExample",
            "theorem sourceWitnessTheorem",
            "theorem source_pipeline_scalar_bound",
        ],
        "notes/IUT_312_FIELD_TO_SOURCE_MAP.md": [
            "Step (xi-e)",
            "Step (xi-f)",
            "Remark 3.11.1",
            "Theorem 3.11",
            "IUT IV",
            "Open theorem",
        ],
        "notes/IUT_312_OPEN_OBLIGATIONS.md": [
            "O5 — Step (xi-e) witness preservation",
            "SourceWitnessTheorem D S N",
            "proof or disproof of Corollary 3.12",
        ],
    }
    missing_files: list[str] = []
    missing_markers: dict[str, list[str]] = {}
    for rel, markers in requirements.items():
        path = ROOT / rel
        if not path.is_file():
            missing_files.append(rel)
            continue
        text = path.read_text(encoding="utf-8")
        absent = [marker for marker in markers if marker not in text]
        if absent:
            missing_markers[rel] = absent

    witness_text = (ROOT / "formalization/lean/KTG/IUT312WitnessObligation.lean").read_text(
        encoding="utf-8"
    )
    example_text = (ROOT / "formalization/lean/KTG/IUT312SourceExample.lean").read_text(
        encoding="utf-8"
    )
    open_boundary = {
        "generic_open_proposition_declared": "def StepXiEWitnessPreservation" in witness_text,
        "iut_specific_global_instance_present": False,
        "finite_equality_example_instance_present": "theorem sourceWitnessTheorem" in example_text,
        "interpretation": (
            "The release declares the IUT-shaped witness proposition but supplies an "
            "instance only inside the finite SourceExample namespace."
        ),
    }
    return {
        "status": "PASS" if not missing_files and not missing_markers else "FAIL",
        "missing_files": missing_files,
        "missing_markers": missing_markers,
        "open_boundary": open_boundary,
    }


def predecessor_core_audit(current_hashes: dict[str, str]) -> dict[str, Any]:
    if not BLOCK02_REPORT.is_file():
        return {"status": "FAIL", "failure": "MISSING_BLOCK02_VERIFICATION_REPORT"}
    predecessor = json.loads(BLOCK02_REPORT.read_text(encoding="utf-8"))
    old_hashes: dict[str, str] = predecessor.get("source_sha256", {})
    checked: dict[str, dict[str, str]] = {}
    changed: dict[str, dict[str, str | None]] = {}
    for rel, old_digest in sorted(old_hashes.items()):
        # KTG.lean is the import aggregator and is expected to change in Block 03.
        if rel == "formalization/lean/KTG.lean":
            continue
        if not rel.startswith("formalization/lean/KTG/"):
            continue
        new_digest = current_hashes.get(rel)
        checked[rel] = {"block02": old_digest, "block03": new_digest or "MISSING"}
        if new_digest != old_digest:
            changed[rel] = {"block02": old_digest, "block03": new_digest}
    return {
        "status": "PASS" if not changed else "FAIL",
        "checked_count": len(checked),
        "expected_changed_file": "formalization/lean/KTG.lean",
        "unexpected_changes": changed,
        "checked": checked,
    }


def write_report(report: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "verification.json").write_text(
        json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="remove .lake/build first")
    args = parser.parse_args()

    lean = executable("LEAN_BIN", "lean")
    lake = executable("LAKE_BIN", "lake")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    lean_version = run([lean, "--version"], PROJECT, timeout_seconds=60)
    lake_version = run([lake, "--version"], PROJECT, timeout_seconds=60)
    records.extend([lean_version, lake_version])
    if lean_version["returncode"] != 0 or lake_version["returncode"] != 0:
        report = {
            "status": "FAIL_TOOLCHAIN",
            "records": records,
            "claim_boundary": {"iut_iii_corollary_3_12": "NOT_PROVED_OR_DISPROVED"},
        }
        write_report(report)
        return 1

    if args.clean:
        shutil.rmtree(PROJECT / ".lake" / "build", ignore_errors=True)

    build = run([lake, "build"], PROJECT, timeout_seconds=900)
    (OUT / "lake_build.log").write_text(build["output"], encoding="utf-8")
    records.append({k: v for k, v in build.items() if k != "output"} | {"log": "lake_build.log"})
    if build["returncode"] != 0 or build["timed_out"]:
        report = {
            "status": "INCONCLUSIVE_TIMEOUT" if build["timed_out"] else "FAIL_LAKE_BUILD",
            "project": str(PROJECT),
            "records": records,
            "claim_boundary": {"iut_iii_corollary_3_12": "NOT_PROVED_OR_DISPROVED"},
        }
        write_report(report)
        print(build["output"], end="")
        return 1

    lean_files = sorted((PROJECT / "KTG").glob("*.lean")) + [PROJECT / "KTG.lean"]
    source_hashes = {str(p.relative_to(ROOT)): sha256(p) for p in lean_files}

    forbidden: dict[str, list[str]] = {}
    token_re = re.compile(r"\b(?:sorry|admit|unsafe)\b|^\s*axiom\b", re.MULTILINE)
    for path in lean_files:
        stripped = strip_lean_comments(path.read_text(encoding="utf-8"))
        hits = sorted(set(m.group(0).strip() for m in token_re.finditer(stripped)))
        if hits:
            forbidden[str(path.relative_to(ROOT))] = hits

    per_file: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="ktg-block03-") as td:
        tmp = Path(td)
        env = os.environ.copy()
        built_lib = PROJECT / ".lake" / "build" / "lib" / "lean"
        old_path = env.get("LEAN_PATH", "")
        env["LEAN_PATH"] = str(built_lib) + (os.pathsep + old_path if old_path else "")
        log_dir = OUT / "per_file"
        log_dir.mkdir(parents=True, exist_ok=True)
        for index, source in enumerate(lean_files):
            slug = str(source.relative_to(PROJECT)).replace(os.sep, "__").replace(".lean", "")
            output = tmp / f"{index:02d}_{slug}.olean"
            rec = run(
                [lean, "-j1", "-DwarningAsError=true", "-o", str(output), str(source)],
                PROJECT,
                env,
                timeout_seconds=300,
            )
            log_name = f"per_file/{index:02d}_{slug}.log"
            (OUT / log_name).write_text(rec["output"], encoding="utf-8")
            per_file.append(
                {k: v for k, v in rec.items() if k != "output"}
                | {"source": str(source.relative_to(ROOT)), "log": log_name}
            )

    failed_files = [r["source"] for r in per_file if r["returncode"] != 0]
    timed_out_files = [r["source"] for r in per_file if r["timed_out"]]
    contract = contract_audit()
    predecessor_core = predecessor_core_audit(source_hashes)

    status = "PASS"
    if forbidden:
        status = "FAIL_PLACEHOLDER_AUDIT"
    elif timed_out_files:
        status = "INCONCLUSIVE_PER_FILE_TIMEOUT"
    elif failed_files:
        status = "FAIL_PER_FILE_WARNING_AS_ERROR"
    elif contract["status"] != "PASS":
        status = "FAIL_BLOCK03_CONTRACT_AUDIT"
    elif predecessor_core["status"] != "PASS":
        status = "FAIL_PREDECESSOR_CORE_AUDIT"

    report = {
        "status": status,
        "release": "Komorebi_IUT_KTG_Block03_Checked_v0.3.0_2026-09-17",
        "project": str(PROJECT),
        "declared_toolchain": (PROJECT / "lean-toolchain").read_text().strip(),
        "actual_lean_version": lean_version["output"].strip(),
        "actual_lake_version": lake_version["output"].strip(),
        "clean_build_requested": args.clean,
        "lean_source_count": len(lean_files),
        "source_sha256": source_hashes,
        "forbidden_token_hits": forbidden,
        "failed_per_file_checks": failed_files,
        "timed_out_per_file_checks": timed_out_files,
        "block03_contract_audit": contract,
        "predecessor_core_audit": predecessor_core,
        "records": records,
        "per_file": per_file,
        "verified_finite_assertion": (
            "The Block 03 Lean sources build and independently elaborate under the "
            "recorded compiler; the typed source-level interface, countermodel, and "
            "finite equality example are accepted by Lean."
        ),
        "claim_boundary": {
            "iut_iii_corollary_3_12": "NOT_PROVED_OR_DISPROVED",
            "source_instantiation": "OPEN",
            "open_theorem": "IUT312.StepXiEWitnessPreservation",
            "verified_claim": (
                "A source-faithful typed proof interface has been formalized, and the "
                "pre-witness fields are formally insufficient in a finite model."
            ),
            "nonclaims": [
                "The IUT papers have not been fully formalized.",
                "The actual IUT Step (xi-e) data have not been instantiated as Lean objects.",
                "No IUT-specific inhabitant of SourceWitnessTheorem is supplied.",
                "The finite countermodel is a logical independence model, not a counterexample to IUT.",
                "Compiler success does not authenticate the mathematical source interpretation.",
            ],
        },
    }
    write_report(report)
    print(
        json.dumps(
            {
                "status": status,
                "lean_source_count": len(lean_files),
                "failed_per_file_checks": failed_files,
                "timed_out_per_file_checks": timed_out_files,
                "forbidden_token_hits": forbidden,
                "block03_contract_audit": contract["status"],
                "predecessor_core_audit": predecessor_core["status"],
                "iut_iii_corollary_3_12": "NOT_PROVED_OR_DISPROVED",
            },
            indent=2,
        )
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
