#!/usr/bin/env python3
"""Package Block 14 only after both actual completed gates pass.

This project-authored packaging procedure does not execute another Lean gate.
It writes evidence, the payload checksum inventory and external delivery files.
It must not alter any input bound by either proof-run receipt.
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FRESH = ROOT.with_name(ROOT.name + "_fresh")
OUTPUT = ROOT.parents[1] / "output"
PREFIX = "Komorebi_Machine_Theory_Lean_Block14_v0.14.0"
FONT_SUFFIXES = {".ttf", ".otf", ".woff", ".woff2", ".ttc", ".pfb", ".pfa", ".pfm", ".fon", ".afm"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_checked(name: str, argv: list[str], *, cwd: Path = ROOT, timeout: int = 90) -> str:
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    text = proc.stdout + proc.stderr
    (ROOT / "evidence" / (name + ".log")).write_text(text, encoding="utf-8")
    print(text, end="", flush=True)
    require(proc.returncode == 0, f"{name} failed with exit code {proc.returncode}; see evidence/{name}.log")
    return text


def validate_receipt(root: Path, name: str):
    receipt = load(root / "evidence" / name / "report.json")
    supervisor = load(root / "evidence" / (name + "_supervisor.json"))
    require(receipt["status"] == "PASS", f"{name} is not PASS")
    require(supervisor["status"] == "completed" and supervisor["exit_code"] == 0,
            f"{name} supervisor did not complete successfully")
    require(all(step["passed"] and not step["timed_out"] for step in receipt["steps"]),
            f"{name} contains a failed or timed-out required command")
    require(receipt["input_sha256_before"] == receipt["input_sha256_after"],
            f"{name} input hashes changed during the gate")
    for rel, expected in receipt["input_sha256_after"].items():
        require(sha(root / rel) == expected, f"{name} input changed after the gate: {rel}")
    require(receipt["source_results_formalized"] == 22 and receipt["source_results_not_formalized"] == 5,
            f"{name} has an unexpected source-coverage count")
    require(receipt["lean_internal_memory_limit_MiB"] == 4096, f"Unexpected memory limit in {name}")
    require(bool(receipt.get("runtime_adapter")), f"Missing adapter disclosure in {name}")
    return receipt


def file_inventory(root: Path):
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def copy_fresh_evidence() -> None:
    source = FRESH / "evidence/fresh14"
    target = ROOT / "evidence/fresh14"
    if target.exists():
        require(file_inventory(source) == file_inventory(target),
                "An existing fresh14 evidence directory differs; refusing to merge or overwrite it")
    else:
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
    for suffix in ("_supervisor.json", "_supervisor.log", "_launch.log"):
        src = FRESH / "evidence" / ("fresh14" + suffix)
        dst = ROOT / "evidence" / src.name
        if not src.is_file():
            require(suffix == "_launch.log", f"Missing required fresh gate file: {src}")
            continue
        if dst.exists():
            require(sha(src) == sha(dst), f"Existing fresh gate file differs: {dst}")
        else:
            shutil.copyfile(src, dst)


def inspect_member(name: str, location: str) -> None:
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, f"Unsafe ZIP member in {location}: {name}")
    require(path.suffix.lower() not in FONT_SUFFIXES, f"Standalone font in {location}: {name}")
    require("__pycache__" not in path.parts, f"Python cache in {location}: {name}")
    require("toolchain" not in path.parts and ".lake" not in path.parts,
            f"Runtime or dependency cache in {location}: {name}")
    require(path.suffix.lower() not in {".so", ".dll", ".dylib"}, f"Runtime binary in {location}: {name}")
    require(not path.name.startswith("Lean_Compact_") and path.name != "Lean_Portable_Compact.tar.xz",
            f"Portable runtime payload in {location}: {name}")


def inspect_zip(archive: zipfile.ZipFile, location: str) -> None:
    for item in archive.infolist():
        inspect_member(item.filename, location)
        require((item.external_attr >> 16) & 0o170000 != 0o120000,
                f"Symbolic ZIP member in {location}: {item.filename}")
        if item.filename.lower().endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(archive.read(item))) as child:
                inspect_zip(child, location + "!" + item.filename)


def release_summary(f, g, comparison, modules, controls, predecessor_count: int,
                    new_theorems: int, new_controls: int) -> str:
    differences = [name for name, record in comparison["nonproduction_objects"].items() if not record["identical"]]
    rejected = sum(control["expected_compile"] == "rejected" for control in controls)
    axiom_controls = sum(control["expected_compile"] == "accepted_then_axiom_audit_rejects" for control in controls)
    review = (ROOT / "REVIEW_NOTES.md").read_text(encoding="utf-8")
    require("Block 14" in review.splitlines()[0], "Current Block 14 review notes are required before packaging")
    heading = "## Corrections and actual failures"
    if heading in review:
        failure_notes = review.split(heading, 1)[1].split("\n## ", 1)[0].strip()
    else:
        failure_notes = review.strip()
    require(bool(failure_notes), "Current failure/review account is empty")
    supervisors = [load(ROOT / "evidence" / (name + "_supervisor.json")) for name in ["final14", "fresh14"]]
    return f"""# Block 14: completed current-source release results

**Machine-Native Reasoning · Formal companion 0.14.0 · Reviewed Core 0.2 · Komorebi P.**

Generated from both completed cumulative cold gates, their successful supervisor exits, and the completed extracted-source comparison. Core 8.1, target-relative joint reconstruction, is the one newly admitted source result.

| Check | Actual result |
|---|---:|
| Selected source results formalized | {f['source_results_formalized']}/27 |
| Authored theorem declarations | {f['authored_theorem_count']} |
| New supporting theorem declarations | {new_theorems} |
| Authored declarations overall | {f['authored_declaration_count']} |
| Elaborated theorem constants, including generated auxiliaries | {f['compiled_theorem_constants_including_generated']} |
| Transitive axiom-audited declarations | {f['axiom_audited_declarations']} |
| Production modules compiled per gate | {len(modules)} |
| Substantive same-kernel replays per gate | {len(modules) - 1} |
| Expected negative-control outcomes per gate | {f['negative_controls']} |
| Newly added negative controls | {new_controls} |
| Inputs unchanged before and after each gate | {len(f['input_sha256_before'])} |
| Predecessor substantive modules preserved | {predecessor_count} |
| Predecessor files preserved, including source book files | {f['preserved_predecessor_files']} |
| Pinned upstream artifacts matched | {f['matched_upstream_artifacts']} |
| First cold gate | PASS, {f['total_seconds']:.3f} seconds |
| Fresh extracted-source gate | PASS, {g['total_seconds']:.3f} seconds |
| Cold-rebuild comparisons | {len(comparison['comparisons'])}, all passed |
| Production proof objects byte-identical | {len(modules)}/{len(modules)} |

The actual transitive axiom union is {', '.join(f['actual_axiom_union'])}. Production compilations treat warnings as errors. Each of the {len(modules) - 1} substantive modules was replayed through the same Lean kernel. Of the {len(controls)} controls, {rejected} deliberately false or unfinished fixtures reject for their stipulated diagnostics and {axiom_controls} deliberately introduced axiom fixture compiles and is rejected by the axiom policy. Neither completed gate failed a required command contract or timed out.

The {new_theorems} added supporting theorem declarations formalize one source result and its extensions and examples. They are not {new_theorems} independent discoveries. All {predecessor_count} predecessor substantive modules and the reviewed source book remain byte-identical.

## Mathematical outcome

The source-facing theorem retains a finite-dimensional state space over a field. For actual linear record and target maps A and Q, a linear decoder D defined on the **full record space** satisfies Q = D.comp A exactly when ker A is contained in ker Q. The decoder is not merely defined on attainable records. The kernel condition makes the image-level definition independent of representatives, and the linear extension supplies a decoder on the whole codomain.

For the identity target, reconstruction is equivalent to injectivity of the record map. The kernel of a stacked record map is the intersection of the kernels of its components. Reconstruction is target-relative: unresolved nuisance directions are permitted when the target map ignores them. Stronger supporting library results do not silently expand the source-admitted finite-dimensional scope.

The theorem concerns accessible records and mathematical existence of a linear decoder. It does not send those records, establish truthful interpretation or permission to disclose them, or install an executable decoder at a fixed recipient. Those remain separate contracts. Exact examples are bound to actual linear maps, not substituted truth-table labels.

## Current authoring failures and corrections

The following is copied from the current pinned review notes. Historical Block 13 preparation or authoring failures are not relabeled as new Block 14 failures.

{failure_notes}

## Preservation and assurance boundaries

The current gates use a {f['lean_internal_memory_limit_MiB']:,} MiB internal Lean limit and record the preserved executable-location adapter. There is no separately imposed operating-system memory cap. The per-command wall allowance is {f['per_command_timeout_seconds']} seconds. The first and fresh supervisors recorded wall limits of {supervisors[0]['supervisor_wall_limit']} and {supervisors[1]['supervisor_wall_limit']} seconds respectively. Runtime checks are recorded separately in `evidence/runtime14`.

Nonproduction object differences in this actual comparison: **{', '.join(differences) if differences else 'none'}**. Generated audit source and complete axiom records match. Every production proof object is byte-identical. No cause is guessed for a differing helper binary, and no production-object exception is allowed.

Both complete gates start from empty local object directories, with the second using a separately extracted frozen source snapshot. They reuse the same pinned upstream imports. Their measured gate durations are execution receipts, not performance claims. Upstream dependencies were hash-checked, not rebuilt from source or independently authenticated. Same-kernel replay is not an independent kernel implementation or peer review.

The filled legacy-v1 computation manifest also passed the current computation-audit skill validator, with the package root supplied for output-hash verification. Its complete result and legacy provenance limits are retained in `evidence/skill_manifest14.log`. This schema check does not independently authenticate the proof runs or supply a repository revision. The separate completed gate receipts bind the local inputs and command outcomes.

No physical sensor calibration, communication implementation, hardware benchmark, Windows execution or hosted publication occurred. No runtime or standalone font binaries are shipped. Five selected source results remain outside this formalization. Core 8.2, the quotient preserving legal operations, is the next connected target.

## Current evidence

`evidence/final14/report.json`, `evidence/fresh14/report.json`, both supervisor receipts, `evidence/FRESH_REBUILD_BLOCK14.json`, `evidence/COMPUTATION_MANIFEST_BLOCK14.json`, `evidence/runtime14/recovery.json` and `evidence/COLD_SOURCE_BLOCK14.zip` bind the current source and actual outcomes. Final archive integrity is recorded separately beside the delivered ZIP, avoiding a circular archive checksum.
"""


def main() -> int:
    require(ROOT.name == PREFIX, f"Unexpected package location: {ROOT}")
    f = validate_receipt(ROOT, "final14")
    g = validate_receipt(FRESH, "fresh14")
    old = load(ROOT / "evidence/final13/report.json")
    modules = load(ROOT / "MODULES.json")
    controls = load(ROOT / "checks/NEGATIVE_CONTROLS.json")
    preservation = load(ROOT / "evidence/final14/preservation.json")
    preserved_modules = [name for name, passed in preservation["checks"].items()
                         if passed and name.startswith("MachineTheory/") and name.endswith(".lean")]
    new_theorems = f["authored_theorem_count"] - old["authored_theorem_count"]
    new_controls = len(controls) - old["negative_controls"]
    old_modules = [step["name"].removeprefix("build_") for step in old["steps"] if step["name"].startswith("build_")]
    predecessor_substantive = len(old_modules) - 1
    require(len(preserved_modules) == predecessor_substantive == 58 and all(preservation["checks"].values()),
            "Expected 58 unchanged predecessor substantive modules and passing preservation checks")
    require(len(modules) == 61 and len(set(modules) - set(old_modules)) == 2,
            "Expected 61 production modules and exactly two newly added substantive modules")
    inventory = load(ROOT / "evidence/final14/source_inventory.json")
    new_module_files = {name.replace(".", "/") + ".lean" for name in set(modules) - set(old_modules)}
    new_source_theorems = sum(row["file"] in new_module_files and row["kind"] in {"theorem", "lemma"} for row in inventory)
    require(new_theorems == new_source_theorems and new_theorems > 0,
            "The declaration-count change must equal the actual newly authored theorem inventory")
    require(new_controls > 0, "No added controls recorded")
    require(f["negative_controls"] == len(controls), "Receipt/control inventory disagreement")
    copy_fresh_evidence()
    run_checked("compare14", [sys.executable, str(ROOT / "scripts/compare_rebuild.py"),
                "--final", str(ROOT / "evidence/final14"), "--fresh", str(ROOT / "evidence/fresh14"),
                "--snapshot", str(ROOT / "evidence/COLD_SOURCE_BLOCK14.zip"),
                "--out", str(ROOT / "evidence/FRESH_REBUILD_BLOCK14.json")])
    comparison = load(ROOT / "evidence/FRESH_REBUILD_BLOCK14.json")
    require(comparison["status"] == "PASS" and all(comparison["comparisons"].values()),
            "Cold-rebuild comparison did not pass")
    run_checked("computation_record14", [sys.executable, str(ROOT / "scripts/computation_record.py"), "--write"])
    run_checked("skill_manifest14", [sys.executable, str(ROOT / "evidence/validate_manifest_from_skill14.py"),
                str(ROOT / "evidence/COMPUTATION_MANIFEST_BLOCK14.json"), "--root", str(ROOT)])
    summary = release_summary(f, g, comparison, modules, controls, len(preserved_modules), new_theorems, new_controls)
    (ROOT / "evidence/RELEASE_RESULTS_BLOCK14.md").write_text(summary, encoding="utf-8")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    exports = {
        "_Theorem_Map.md": (ROOT / "docs/THEOREM_MAP.md").read_text(encoding="utf-8"),
        "_Proof_Guide.md": (ROOT / "docs/BLOCK14_PROOF_GUIDE.md").read_text(encoding="utf-8"),
        "_Review_Notes.md": summary + "\n---\n\n" + (ROOT / "REVIEW_NOTES.md").read_text(encoding="utf-8"),
        "_Progress_Ledger.md": (ROOT / "PROGRESS_LEDGER.md").read_text(encoding="utf-8"),
    }
    for suffix, text in exports.items():
        (OUTPUT / (PREFIX + suffix)).write_text(text, encoding="utf-8")
    # Frozen input documents and code are checked again before freezing the payload.
    for rel, expected in f["input_sha256_after"].items():
        require(sha(ROOT / rel) == expected, f"Pinned proof input changed during packaging: {rel}")
    payload = []
    for path in sorted(ROOT.rglob("*")):
        if "__pycache__" in path.parts:
            continue
        require(not path.is_symlink(), f"Symlink in package: {path}")
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT))
        inspect_member(rel, str(ROOT))
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                inspect_zip(archive, rel)
        payload.append(path)
    hashes = {str(path.relative_to(ROOT)): {"bytes": path.stat().st_size, "sha256": sha(path)}
              for path in payload if path.name != "SHA256SUMS.json"}
    write_json(ROOT / "SHA256SUMS.json", {"schema": "komorebi.frozen-payload.v1", "files": hashes})
    archive_path = OUTPUT / (PREFIX + "_complete.zip")
    temporary_archive = archive_path.with_suffix(".zip.partial")
    with zipfile.ZipFile(temporary_archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(ROOT.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, str(path.relative_to(ROOT.parent)))
    temporary_archive.replace(archive_path)
    with tempfile.TemporaryDirectory(prefix="block14_delivery_check_", dir=OUTPUT) as temporary:
        extraction = Path(temporary)
        with zipfile.ZipFile(archive_path) as archive:
            require(archive.testzip() is None, "Final ZIP CRC check failed")
            require(all(Path(name).parts[0] == PREFIX for name in archive.namelist()), "Unexpected ZIP root")
            archive.extractall(extraction)
        extracted_root = extraction / PREFIX
        command = [sys.executable, str(extracted_root / "scripts/verify_release.py")]
        proc = subprocess.run(command, cwd=extracted_root, text=True, capture_output=True, timeout=90)
        verifier_output = proc.stdout + proc.stderr
        require(proc.returncode == 0, "Extracted payload checksum verification failed:\n" + verifier_output)
        print(verifier_output, end="", flush=True)
    receipt = {
        "schema": "komorebi.block14.delivery.v1", "status": "PASS",
        "archive": archive_path.name, "archive_bytes": archive_path.stat().st_size,
        "archive_sha256": sha(archive_path), "payload_files": len(hashes),
        "zip_crc": "PASS", "independent_extraction": "PASS", "extracted_payload_verifier": "PASS",
        "payload_verifier_exit_code": proc.returncode, "payload_verifier_output": verifier_output,
        "source_results": f["source_results_formalized"], "source_result_total": 27,
        "production_modules": len(modules), "substantive_kernel_replays": len(modules) - 1,
        "axiom_audited": f["axiom_audited_declarations"], "new_theorems": new_theorems,
        "negative_controls": len(controls), "new_controls": new_controls,
        "predecessor_substantive_modules_preserved": len(preserved_modules),
        "first_gate_seconds": f["total_seconds"], "fresh_gate_seconds": g["total_seconds"],
        "skill_manifest_validator": {
            "status": "PASS", "source_sha256": sha(ROOT / "evidence/validate_manifest_from_skill14.py"),
            "log_sha256": sha(ROOT / "evidence/skill_manifest14.log"),
            "scope": "Filled legacy-v1 schema and output hashes; provenance limits remain in the complete log",
        },
        "runtime_and_font_scan": "No runtime/cache/shared-library or standalone-font payload by recursive filename inspection",
        "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "boundary": "Archive extraction and checksum verification only; not another Lean run or external authenticity attestation",
    }
    review_path = OUTPUT / (PREFIX + "_Review_Notes.md")
    with review_path.open("a", encoding="utf-8") as stream:
        stream.write(f"\n## Final delivery integrity\n\nThe final ZIP was independently extracted and its shipped checksum verifier passed for **{len(hashes)} payload files**. Archive size: **{archive_path.stat().st_size:,} bytes** ({archive_path.stat().st_size / 1024 / 1024:.2f} MiB). SHA-256: `{receipt['archive_sha256']}`. This packaging check is not another Lean run.\n")
    receipt["exports"] = [{"name": PREFIX + suffix, "bytes": (OUTPUT / (PREFIX + suffix)).stat().st_size,
                            "sha256": sha(OUTPUT / (PREFIX + suffix))} for suffix in exports]
    write_json(OUTPUT / (PREFIX + "_Delivery.json"), receipt)
    print(json.dumps(receipt, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
