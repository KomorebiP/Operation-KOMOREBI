#!/usr/bin/env python3
"""Package Block 15 only after both actual completed gates pass.

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
PREFIX = "Komorebi_Machine_Theory_Lean_Block15_v0.15.0"
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
    require(receipt["source_results_formalized"] == 23 and receipt["source_results_not_formalized"] == 4,
            f"{name} has an unexpected source-coverage count")
    require(receipt["lean_internal_memory_limit_MiB"] == 4096, f"Unexpected memory limit in {name}")
    require(bool(receipt.get("runtime_adapter")), f"Missing adapter disclosure in {name}")
    return receipt


def file_inventory(root: Path):
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def copy_fresh_evidence() -> None:
    source = FRESH / "evidence/fresh15"
    target = ROOT / "evidence/fresh15"
    if target.exists():
        require(file_inventory(source) == file_inventory(target),
                "An existing fresh15 evidence directory differs; refusing to merge or overwrite it")
    else:
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
    for suffix in ("_supervisor.json", "_supervisor.log", "_launch.log"):
        src = FRESH / "evidence" / ("fresh15" + suffix)
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
    require("\\" not in name, f"Backslash in archive member name: {location}: {name}")
    require(not path.is_absolute() and ".." not in path.parts, f"Unsafe ZIP member in {location}: {name}")
    require(path.suffix.lower() not in FONT_SUFFIXES, f"Standalone font in {location}: {name}")
    require("__pycache__" not in path.parts, f"Python cache in {location}: {name}")
    require("toolchain" not in path.parts and ".lake" not in path.parts,
            f"Runtime or dependency cache in {location}: {name}")
    require(path.suffix.lower() not in {".so", ".dll", ".dylib"}, f"Runtime binary in {location}: {name}")
    require(not path.name.startswith("Lean_Compact_") and path.name != "Lean_Portable_Compact.tar.xz",
            f"Portable runtime payload in {location}: {name}")


def inspect_zip(archive: zipfile.ZipFile, location: str) -> None:
    names = archive.namelist()
    require(len(names) == len(set(names)), f"Duplicate ZIP member in {location}")
    require(archive.testzip() is None, f"ZIP CRC failed in {location}")
    for item in archive.infolist():
        inspect_member(item.filename, location)
        require((item.external_attr >> 16) & 0o170000 != 0o120000,
                f"Symbolic ZIP member in {location}: {item.filename}")
        if item.filename.lower().endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(archive.read(item))) as child:
                inspect_zip(child, location + "!" + item.filename)


def validate_predecessor_archive() -> dict:
    recovery = load(ROOT / "evidence/RECOVERY_BLOCK15.json")
    require(recovery["status"] == "PASS", "Predecessor recovery receipt is not PASS")
    rel = Path(recovery["archive"])
    require(not rel.is_absolute() and ".." not in rel.parts, "Unsafe predecessor archive path")
    path = ROOT / rel
    actual_hash = sha(path)
    predecessor = load(ROOT / "PREDECESSOR.json")
    require(actual_hash == recovery["archive_sha256"] == predecessor["source_archive_sha256"],
            "Retained predecessor archive identity changed")
    require(path.name == predecessor["source_archive"], "Predecessor archive filename disagrees with preservation contract")
    old_prefix = "Komorebi_Machine_Theory_Lean_Block14_v0.14.0/"
    with zipfile.ZipFile(path) as archive:
        names = [item.filename for item in archive.infolist() if not item.is_dir()]
        require(len(names) == len(set(names)), "Duplicate predecessor ZIP member")
        require(all(name.startswith(old_prefix) for name in names), "Unexpected predecessor ZIP root")
        for name in names:
            inspect_member(name, str(rel))
        frozen = json.loads(archive.read(old_prefix + "SHA256SUMS.json"))
        require(set(names) == {old_prefix + "SHA256SUMS.json"} | {old_prefix + name for name in frozen["files"]},
                "Predecessor ZIP inventory does not cover all payload files")
        for name, expected in frozen["files"].items():
            inspect_member(name, str(rel))
            h = hashlib.sha256()
            size = 0
            with archive.open(old_prefix + name) as stream:
                for chunk in iter(lambda: stream.read(4 << 20), b""):
                    size += len(chunk)
                    h.update(chunk)
            require(size == expected["bytes"] and h.hexdigest() == expected["sha256"],
                    f"Retained predecessor payload mismatch: {name}")
    require(len(frozen["files"]) == recovery["payload_members_hash_verified"],
            "Predecessor verified payload count changed")
    result = {"schema": "komorebi.block15.preserved-history.v1", "status": "PASS",
              "archive": str(rel), "archive_sha256": actual_hash,
              "payload_members_hash_verified": len(frozen["files"]),
              "scope": "Complete original Block14 archive retained byte-identically and every payload hash rechecked; no historical proof rerun"}
    write_json(ROOT / "evidence/HISTORICAL_ARCHIVE_BLOCK14_CHECK.json", result)
    return result


def release_summary(f, g, comparison, modules, controls, predecessor_count: int,
                    new_theorems: int, new_controls: int) -> str:
    differences = [name for name, record in comparison["nonproduction_objects"].items() if not record["identical"]]
    rejected = sum(control["expected_compile"] == "rejected" for control in controls)
    axiom_controls = sum(control["expected_compile"] == "accepted_then_axiom_audit_rejects" for control in controls)
    review = (ROOT / "REVIEW_NOTES.md").read_text(encoding="utf-8")
    require("Block 15" in review.splitlines()[0], "Current Block 15 review notes are required before packaging")
    heading = "## Corrections and actual failures"
    if heading in review:
        failure_notes = review.split(heading, 1)[1].split("\n## ", 1)[0].strip()
    else:
        failure_notes = review.strip()
    require(bool(failure_notes), "Current failure/review account is empty")
    supervisors = [load(ROOT / "evidence" / (name + "_supervisor.json")) for name in ["final15", "fresh15"]]
    history = load(ROOT / "evidence/HISTORICAL_ARCHIVE_BLOCK14_CHECK.json")
    return f"""# Block 15: completed current-source release results

**Machine-Native Reasoning · Formal companion 0.15.0 · Reviewed Core 0.2 · Komorebi P.**

Generated from both completed cumulative cold gates, their successful supervisor exits, and the completed extracted-source comparison. Core 8.2, a quotient preserving declared legal operations, is the one newly admitted source result.

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
| Historical Block 14 payload files retained and hash-checked inside original ZIP | {history['payload_members_hash_verified']} |

The actual transitive axiom union is {', '.join(f['actual_axiom_union'])}. Production compilations treat warnings as errors. Each of the {len(modules) - 1} substantive modules was replayed through the same Lean kernel. Of the {len(controls)} controls, {rejected} deliberately false or unfinished fixtures reject for their stipulated diagnostics and {axiom_controls} deliberately introduced axiom fixture compiles and is rejected by the axiom policy. Neither completed gate failed a required command contract or timed out.

The {new_theorems} added supporting theorem declarations formalize one source result and its extensions and examples. They are not {new_theorems} independent discoveries. All {predecessor_count} predecessor substantive modules and the reviewed source book remain byte-identical.

## Mathematical outcome

For the source's finite state and action setting, a surjective state map supports quotient labels, enabled sets and legal successors exactly when equal fibres have equal labels, equal enabled sets and equal projected successors for every enabled action. The quotient protects both what a state reports and which actions the supplied model permits.

The quotient labels, enabled sets and **enabled-action successors** are unique. Arbitrary values used to pad a total step function on disabled actions are outside that uniqueness claim. The legal trace theorem preserves every finite legal action sequence and the complete associated label sequence, not just the final output or a tested trace horizon.

A predictive summary that merges states with different enabled actions can fail this contract even if its sensor predictions agree. The theorem formalizes declared operational permissions. It does not derive moral or external legal authority from an enabled-set label.

## Current authoring failures and corrections

The following is copied from the current pinned review notes. Historical preparation or authoring failures are not relabeled as new Block 15 failures.

{failure_notes}

## Preservation and assurance boundaries

The current gates use a {f['lean_internal_memory_limit_MiB']:,} MiB internal Lean limit and record the preserved executable-location adapter. There is no separately imposed operating-system memory cap. The per-command wall allowance is {f['per_command_timeout_seconds']} seconds. The first and fresh supervisors recorded wall limits of {supervisors[0]['supervisor_wall_limit']} and {supervisors[1]['supervisor_wall_limit']} seconds respectively. Runtime checks are recorded separately in `evidence/runtime15`.

Nonproduction object differences in this actual comparison: **{', '.join(differences) if differences else 'none'}**. Generated audit source and complete axiom records match. Every production proof object is byte-identical. No cause is guessed for a differing helper binary, and no production-object exception is allowed.

Both complete gates start from empty local object directories, with the second using a separately extracted frozen source snapshot. They reuse the same pinned upstream imports. Their measured gate durations are execution receipts, not performance claims. Upstream dependencies were hash-checked, not rebuilt from source or independently authenticated. Same-kernel replay is not an independent kernel implementation or peer review.

The filled legacy-v1 computation manifest also passed the current computation-audit skill validator, with the package root supplied for output-hash verification. Its complete result and legacy provenance limits are retained in `evidence/skill_manifest15.log`. This schema check does not independently authenticate the proof runs or supply a repository revision. The separate completed gate receipts bind the local inputs and command outcomes.

No physical sensor calibration, external legal-authority validation, hardware benchmark, Windows execution or hosted publication occurred. No runtime or standalone font binaries are shipped. Four selected source results remain outside this formalization. Core 8.3, safe continuation retaining an ending strategy, is the next connected target.

## Historical evidence layout

The complete original Block 14 archive remains byte-identical under `evidence/history/block14`. Its {history['payload_members_hash_verified']} payload files were streamed through their frozen byte-length and SHA-256 checks during recovery and rechecked during packaging. Historical evidence is retained inside that original ZIP rather than expanded again into this release. Current source, documentation and checks, the essential predecessor receipt, and the new Block 15 evidence are directly accessible. The final outer payload count and the nested historical payload count are separate quantities.

## Current evidence

`evidence/final15/report.json`, `evidence/fresh15/report.json`, both supervisor receipts, `evidence/FRESH_REBUILD_BLOCK15.json`, `evidence/COMPUTATION_MANIFEST_BLOCK15.json`, `evidence/runtime15/recovery.json` and `evidence/COLD_SOURCE_BLOCK15.zip` bind the current source and actual outcomes. Final archive integrity is recorded separately beside the delivered ZIP, avoiding a circular archive checksum.
"""


def main() -> int:
    require(ROOT.name == PREFIX, f"Unexpected package location: {ROOT}")
    f = validate_receipt(ROOT, "final15")
    g = validate_receipt(FRESH, "fresh15")
    old = load(ROOT / "evidence/final14/report.json")
    modules = load(ROOT / "MODULES.json")
    controls = load(ROOT / "checks/NEGATIVE_CONTROLS.json")
    preservation = load(ROOT / "evidence/final15/preservation.json")
    preserved_modules = [name for name, passed in preservation["checks"].items()
                         if passed and name.startswith("MachineTheory/") and name.endswith(".lean")]
    new_theorems = f["authored_theorem_count"] - old["authored_theorem_count"]
    new_controls = len(controls) - old["negative_controls"]
    old_modules = [step["name"].removeprefix("build_") for step in old["steps"] if step["name"].startswith("build_")]
    predecessor_substantive = len(old_modules) - 1
    require(len(preserved_modules) == predecessor_substantive == 60 and all(preservation["checks"].values()),
            "Expected 60 unchanged predecessor substantive modules and passing preservation checks")
    require(len(modules) == 64 and len(set(modules) - set(old_modules)) == 3,
            "Expected 64 production modules and exactly three newly added substantive modules")
    inventory = load(ROOT / "evidence/final15/source_inventory.json")
    new_module_files = {name.replace(".", "/") + ".lean" for name in set(modules) - set(old_modules)}
    new_source_theorems = sum(row["file"] in new_module_files and row["kind"] in {"theorem", "lemma"} for row in inventory)
    require(new_theorems == new_source_theorems and new_theorems > 0,
            "The declaration-count change must equal the actual newly authored theorem inventory")
    require(new_controls > 0, "No added controls recorded")
    require(f["negative_controls"] == len(controls), "Receipt/control inventory disagreement")
    history = validate_predecessor_archive()
    copy_fresh_evidence()
    run_checked("compare15", [sys.executable, str(ROOT / "scripts/compare_rebuild.py"),
                "--final", str(ROOT / "evidence/final15"), "--fresh", str(ROOT / "evidence/fresh15"),
                "--snapshot", str(ROOT / "evidence/COLD_SOURCE_BLOCK15.zip"),
                "--out", str(ROOT / "evidence/FRESH_REBUILD_BLOCK15.json")])
    comparison = load(ROOT / "evidence/FRESH_REBUILD_BLOCK15.json")
    require(comparison["status"] == "PASS" and all(comparison["comparisons"].values()),
            "Cold-rebuild comparison did not pass")
    run_checked("computation_record15", [sys.executable, str(ROOT / "scripts/computation_record.py"), "--write"])
    run_checked("skill_manifest15", [sys.executable, str(ROOT / "evidence/validate_manifest_from_skill15.py"),
                str(ROOT / "evidence/COMPUTATION_MANIFEST_BLOCK15.json"), "--root", str(ROOT)])
    summary = release_summary(f, g, comparison, modules, controls, len(preserved_modules), new_theorems, new_controls)
    (ROOT / "evidence/RELEASE_RESULTS_BLOCK15.md").write_text(summary, encoding="utf-8")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    exports = {
        "_Theorem_Map.md": (ROOT / "docs/THEOREM_MAP.md").read_text(encoding="utf-8"),
        "_Proof_Guide.md": (ROOT / "docs/BLOCK15_PROOF_GUIDE.md").read_text(encoding="utf-8"),
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
    extraction_parent = Path("/dev/shm")
    require(extraction_parent.is_dir(), "Expected /dev/shm for temporary delivery verification")
    with zipfile.ZipFile(archive_path) as archive:
        required_bytes = sum(item.file_size for item in archive.infolist())
    require(shutil.disk_usage(extraction_parent).free >= required_bytes + (64 << 20),
            "Insufficient /dev/shm space for complete independent archive extraction")
    with tempfile.TemporaryDirectory(prefix="block15_delivery_check_", dir=extraction_parent) as temporary:
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
        "schema": "komorebi.block15.delivery.v1", "status": "PASS",
        "archive": archive_path.name, "archive_bytes": archive_path.stat().st_size,
        "archive_sha256": sha(archive_path), "payload_files": len(hashes),
        "zip_crc": "PASS", "independent_extraction": "PASS", "extracted_payload_verifier": "PASS",
        "temporary_extraction_parent": str(extraction_parent),
        "payload_verifier_exit_code": proc.returncode, "payload_verifier_output": verifier_output,
        "source_results": f["source_results_formalized"], "source_result_total": 27,
        "production_modules": len(modules), "substantive_kernel_replays": len(modules) - 1,
        "axiom_audited": f["axiom_audited_declarations"], "new_theorems": new_theorems,
        "negative_controls": len(controls), "new_controls": new_controls,
        "predecessor_substantive_modules_preserved": len(preserved_modules),
        "first_gate_seconds": f["total_seconds"], "fresh_gate_seconds": g["total_seconds"],
        "preserved_history": history,
        "skill_manifest_validator": {
            "status": "PASS", "source_sha256": sha(ROOT / "evidence/validate_manifest_from_skill15.py"),
            "log_sha256": sha(ROOT / "evidence/skill_manifest15.log"),
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
