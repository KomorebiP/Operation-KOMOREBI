#!/usr/bin/env python3
"""Seal a completed Komorebi Space release without modifying its input tree.

Requires the terminated current Lean receipt and a matching closeout record.
Checks included current objects and logs, not intentionally omitted old objects.
All packaging receipts and failed attempts stay outside the immutable ZIP.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
CANONICAL = "Komorebi_Space_Release_1.16.0"
VERSION = "1.16.0"
RUN = "verification/closeout/run01"
ALLOWED = {"Classical.choice", "Quot.sound", "propext"}
FONT_SUFFIXES = {".ttf", ".otf", ".ttc", ".woff", ".woff2", ".pfb", ".pfa", ".pcf", ".fon"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical(value):
    require(isinstance(value, str) and bool(value), "Empty payload path")
    require("\\" not in value and ":" not in value and all(ord(c) >= 32 for c in value),
            "Invalid payload path characters: " + value)
    p = PurePosixPath(value)
    require(not p.is_absolute() and all(x not in ("", ".", "..") for x in value.split("/")),
            "Unsafe payload path: " + value)
    require(str(p) == value, "Noncanonical payload path: " + value)
    return p


def files(root):
    answer = []
    for p in sorted(root.rglob("*")):
        mode = p.lstat().st_mode
        require(not stat.S_ISLNK(mode), "Symlink is not a deliverable regular file: " + str(p))
        if stat.S_ISDIR(mode):
            continue
        require(stat.S_ISREG(mode), "Nonregular payload: " + str(p))
        canonical(p.relative_to(root).as_posix())
        require(p.suffix.lower() not in FONT_SUFFIXES,
                "Standalone font requires explicit packaging review: " + str(p))
        answer.append(p)
    return answer


def cache_file(relative):
    return "__pycache__" in relative.parts or relative.suffix in (".pyc", ".pyo")


def source_distribution_map(root):
    return {p.relative_to(root).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p)}
            for p in files(root)
            if p.relative_to(root).as_posix() not in ("MANIFEST.json", "SHA256SUMS")
            and not cache_file(p.relative_to(root))}


def module(path, prefix):
    name = prefix + "_" + hashlib.sha256(str(path).encode()).hexdigest()[:12]
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def check_submanifest(root, name):
    p = root / name
    data = load(p)
    entries = data["files"]
    require(isinstance(entries, list) and entries, "Empty submanifest: " + name)
    expected = {}
    for row in entries:
        canonical(row["path"])
        require(row["path"] not in expected, "Duplicate submanifest row: " + row["path"])
        q = p.parent / row["path"]
        require(q.is_file() and not q.is_symlink(), "Missing submanifest payload: " + str(q))
        require(q.stat().st_size == row["bytes"] and sha(q) == row["sha256"],
                "Submanifest payload changed: " + str(q))
        expected[row["path"]] = row
    actual = {q.relative_to(p.parent).as_posix() for q in files(p.parent)}
    require(actual == set(expected) | {p.name}, "Submanifest file set changed: " + name)
    return {"status": "PASS", "files": len(expected), "manifest_sha256": sha(p)}


def reader_binding(root):
    rel = "verification/readers/READER_BUNDLE_MANIFEST.json"
    manifest = load(root / rel)
    bound = {}
    for name, expected in manifest["source_and_support_files"].items():
        canonical(name)
        target = "verification/readers/" + name[len("verification/"):] if name.startswith("verification/") else name
        canonical(target)
        require(target not in bound, "Duplicate mapped reader path: " + target)
        require(sha(root / target) == expected, "Reader bundle hash differs: " + target)
        bound[target] = expected
    for name, expected in manifest["books"].items():
        canonical(name)
        require(sha(root / name) == expected, "Reader PDF hash differs: " + name)
    supplement = manifest["supplement_pdf"]
    canonical(supplement["path"])
    require(sha(root / supplement["path"]) == supplement["sha256"], "Worked-proof PDF hash differs")
    return {"status": "PASS", "manifest_sha256": sha(root / rel), "mapped_files": len(bound),
            "books": manifest["books"], "supplement_pdf": supplement,
            "worked_proofs_manifest": check_submanifest(root, "supplements/komorebi-space-worked-proofs-v4/DELIVERY_MANIFEST.json"),
            "examples_manifest": check_submanifest(root, "verification/examples/MANIFEST.json")}


def bind_release(root):
    """Reconcile the delivered bytes with a terminated current verification run."""
    run = root / RUN
    receipt_path = run / "receipt.json"
    r = load(receipt_path)
    c = load(root / "release/CLOSEOUT_RECORD.json")
    require(r.get("status") == "PASS" and r.get("lean_executed") is True, "Current Lean run not PASS")
    require(c.get("status") == "PASS" and c.get("version") == VERSION, "Closeout record not accepted")
    require(c.get("gate_receipt_sha256") == sha(receipt_path), "Closeout is not bound to the current receipt")
    require(bool(r.get("finished_utc")) and all(r.get(x) is True for x in
            ("source_unchanged", "objects_unchanged", "runtime_unchanged")), "Missing terminal identity checks")
    require((r["compile_targets"], r["production_modules"], r["exported_declarations"],
             r["explicit_theorem_lemma_count"]) == (166, 162, 5339, 1859), "Unexpected formal scope")
    runner = module(root / "verification/runner/runner.py", "space_runner")
    pins = runner.source_hashes(root)
    require(len(pins) == 229 and pins == r["input_sha256"], "Delivered formal inputs differ from receipt")
    if "source_inputs_sha256" in c:
        require(c["source_inputs_sha256"] == pins, "Closeout source hashes differ")
    require(runner.source_hashes(run / "snapshot") == pins, "Source snapshot differs from delivered inputs")
    require({p.relative_to(run / "snapshot").as_posix() for p in files(run / "snapshot")} == set(pins),
            "Source snapshot exact file set differs")
    graph = runner.graph(root / "lean")
    for key in ("compile_order", "compile_targets", "production_modules", "entrypoints",
                "explicit_theorem_lemma_count", "local_imports"):
        require(graph[key] == r[key], "Source graph differs: " + key)
    control_path = root / "verification/runner/control_manifest.json"
    require(sha(control_path) == r["control_manifest_sha256"], "Control manifest hash differs")
    controls = load(control_path)["controls"]
    require(len(controls) == 56 and controls == r["control_specifications"], "Control specifications differ")
    require(r["control_counts"] == {"accept": 18, "elaboration_reject": 35, "policy_reject": 3},
            "Control category count differs")
    require(dict(collections.Counter(x["expected"] for x in controls)) == r["control_counts"],
            "Control counts do not follow specifications")
    pins_deps = load(root / "lean/lake-manifest.json")["packages"]
    require(len(pins_deps) == len(r["dependencies"]) == 9, "Pinned dependency count differs")
    dependencies = {x["name"]: x for x in r["dependencies"]}
    for pin in pins_deps:
        row = dependencies[pin["name"]]
        require(row["actual_revision"] == row["expected_revision"] == pin["rev"], "Dependency revision differs")
    expected = ["lake_environment", "lean_version", "lean_prefix"]
    for pin in pins_deps:
        expected += ["pin_" + pin["name"], "clean_" + pin["name"]]
    expected += ["compile_" + x for x in graph["compile_order"]]
    expected += ["declaration_inventory"] + ["control_" + x["id"] for x in controls]
    for pin in pins_deps:
        expected += ["terminal_pin_" + pin["name"], "terminal_clean_" + pin["name"]]
    commands = r["commands"]
    require(len(commands) == len(expected) == len(set(expected)) == 262, "Command count differs")
    require([x["label"] for x in commands] == r["exact_command_labels"] == expected,
            "Command order differs or command is omitted")
    by_label = {x["label"]: x for x in commands}
    expected_logs = set()
    for command in commands:
        canonical(command["log"])
        require(not command["timeout"], "A command timed out")
        require(sha(run / command["log"]) == command["log_sha256"], "Command log hash differs")
        expected_logs.add(command["log"])
        if not command["label"].startswith("control_"):
            require(command["exit_code"] == 0, "Required command failed: " + command["label"])
        if command["label"].startswith(("compile_", "control_")) or command["label"] == "declaration_inventory":
            require(all(flag in command["argv"] for flag in ("-j1", "-DwarningAsError=true", "-DautoImplicit=false")),
                    "Compiler policy differs: " + command["label"])
    require({x.relative_to(run).as_posix() for x in files(run / "logs")} == expected_logs,
            "Command log file set differs")
    classified = []
    for control in controls:
        command = by_label["control_" + control["id"]]
        text = (run / command["log"]).read_text(encoding="utf-8", errors="replace")
        result = runner.classify_control(control, command, text)
        require(result["passed"], "Control outcome differs: " + control["id"])
        classified.append(result)
    require(classified == r["controls"], "Reclassified controls differ from receipt")
    objects = {x.relative_to(run / "build").as_posix(): sha(x) for x in files(run / "build")}
    require(len(objects) == 166 and objects == r["fresh_object_sha256"], "Current project objects differ")
    require(set(objects) == {x.replace(".", "/") + ".olean" for x in graph["compile_order"]},
            "Current object set differs from production targets")
    for filename, key in (("Inventory.lean", "generated_audit_sha256"),
                          ("declarations.json", "declarations_sha256"),
                          ("runtime_snapshot.json", "runtime_snapshot_sha256")):
        require(sha(run / filename) == r[key], "Generated evidence hash differs: " + filename)
    require((run / "wanted_modules.txt").read_text().splitlines() == graph["compile_order"],
            "Generated module list differs")
    inventory = load(run / "declarations.json")
    rows = inventory["declarations"]
    require(len(rows) == inventory["count"] == len({x["name"] for x in rows}) == 5339 and not inventory["rejected"],
            "Declaration inventory inconsistent")
    require(all(not x["unsafe"] and not x["axiom_declaration"] and set(x["axioms"]) <= ALLOWED for x in rows),
            "Forbidden declaration in inventory")
    require({x["module"] for x in rows} == set(graph["compile_order"]) - set(graph["entrypoints"]),
            "Declaration module provenance differs")
    require(sorted({a for x in rows for a in x["axioms"]}) == r["axiom_union"] == sorted(ALLOWED),
            "Actual axiom union differs")
    historical = {
        "history/Komorebi_Space_Publication_v1.15.0.zip": (9899433, "7f68336e652bc6af817ba0fc8c96476f7cc39318ff333f404e202f4388dfe63f"),
        "history/Komorebi_Space_Technical_Record_v1.15.0.zip": (139563911, "2cc2a0291669781e3c5bb6608cc4f3c86cce513ec686c2b17031d35278d353db"),
    }
    for name, (size, expected_hash) in historical.items():
        require((root / name).stat().st_size == size and sha(root / name) == expected_hash,
                "Preserved accepted archive differs: " + name)
    if "historical_publication_sha256" in c:
        require(c["historical_publication_sha256"] == historical["history/Komorebi_Space_Publication_v1.15.0.zip"][1], "Closeout historical publication hash differs")
    if "historical_technical_record_sha256" in c:
        require(c["historical_technical_record_sha256"] == historical["history/Komorebi_Space_Technical_Record_v1.15.0.zip"][1], "Closeout technical record hash differs")
    if "reader_bundle_manifest_sha256" in c:
        require(c["reader_bundle_manifest_sha256"] == sha(root / "verification/readers/READER_BUNDLE_MANIFEST.json"), "Closeout reader manifest hash differs")
    if "reader_records_sha256" in c:
        require(c["reader_records_sha256"] == sha(root / "verification/readers/FINAL_PDF_CHECKS.json"), "Closeout final PDF checks hash differs")
    return {"status": "PASS", "gate_receipt_sha256": sha(receipt_path),
            "closeout_record_sha256": sha(root / "release/CLOSEOUT_RECORD.json"),
            "source_inputs": len(pins), "compiled_targets": len(objects), "exported_declarations": len(rows),
            "preserved_archives_sha256": {name: pair[1] for name, pair in historical.items()},
            "commands": len(commands), "controls_reclassified": len(classified),
            "control_counts": r["control_counts"], "reader_binding": reader_binding(root),
            "runtime_inventory_sha256": r["runtime_snapshot_sha256"],
            "scope": "Included receipt/source/log/object binding and control reclassification; not a new Lean run or runtime-cache reread."}


def sums_check(root):
    rows = []
    for line in (root / "SHA256SUMS").read_text().splitlines():
        h, name = line.split("  ", 1)
        canonical(name)
        require(re.fullmatch("[0-9a-f]{64}", h) is not None, "Malformed SHA256SUMS digest")
        rows.append((name, h))
    names = [name for name, _ in rows]
    require(len(names) == len(set(names)), "Duplicate SHA256SUMS entries")
    actual = {x.relative_to(root).as_posix() for x in files(root)} - {"SHA256SUMS", "MANIFEST.json"}
    require(set(names) == actual, "SHA256SUMS exact file set differs")
    require(all(sha(root / name) == h for name, h in rows), "SHA256SUMS hash mismatch")
    return {"status": "PASS", "entries": len(rows), "sha256": sha(root / "SHA256SUMS")}


def seal(root, out, canonical_name):
    initial = source_distribution_map(root)
    binding = bind_release(root)
    stage = out / "staging" / canonical_name
    stage.mkdir(parents=True)
    omitted = []
    for p in files(root):
        relative = p.relative_to(root)
        if relative.as_posix() in ("MANIFEST.json", "SHA256SUMS"):
            continue
        if cache_file(relative):
            omitted.append({"path": relative.as_posix(), "bytes": p.stat().st_size, "sha256": sha(p),
                            "reason": "Regenerable Python bytecode cache"})
            continue
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        require(sha(target) == initial[relative.as_posix()]["sha256"], "Source changed while staging")
    helper = stage / "release/tools/package_release.py"
    helper.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), helper)
    write(stage / "release/PACKAGE_CACHE_OMISSIONS.json", omitted)
    require(bind_release(stage) == binding, "Staged binding differs")
    (stage / "SHA256SUMS").write_text("".join(sha(p) + "  " + p.relative_to(stage).as_posix() + "\n"
                                             for p in files(stage)), encoding="utf-8")
    vp = module(stage / "tools/verify_package.py", "space_package_integrity")
    require(vp.SCHEMA == "komorebi.source-package.sha256.v1", "Unsupported package verifier schema")
    entries = [{"path": p.relative_to(stage).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}
               for p in files(stage)]
    write(stage / "MANIFEST.json", {"schema": vp.SCHEMA, "version": VERSION,
                                    "flavor": "source-current-evidence-readers-and-preserved-archives", "files": entries})
    stage_integrity = vp.verify(stage)
    stage_sums = sums_check(stage)
    archive = out / (canonical_name + ".zip")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for p in files(stage):
            z.write(p, canonical_name + "/" + p.relative_to(stage).as_posix(),
                    compress_type=zipfile.ZIP_STORED if p.suffix == ".zip" else zipfile.ZIP_DEFLATED)
    with tempfile.TemporaryDirectory(prefix="clean_extract_", dir=out) as temp:
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            expected = {canonical_name + "/" + row["path"] for row in entries} | {canonical_name + "/MANIFEST.json"}
            require(len(names) == len(set(names)) and set(names) == expected, "ZIP membership differs")
            require(z.testzip() is None, "ZIP CRC failure")
            for info in z.infolist():
                p = canonical(info.filename)
                require(p.parts[0] == canonical_name and len(p.parts) > 1, "Unexpected ZIP root")
                require(stat.S_ISREG(info.external_attr >> 16), "Nonregular ZIP member")
            z.extractall(temp)
        extracted = Path(temp) / canonical_name
        extracted_integrity = vp.verify(extracted)
        extracted_sums = sums_check(extracted)
        extracted_binding = bind_release(extracted)
        require(extracted_binding == binding, "Clean-extracted evidence binding differs")
        require(vp.verify(extracted) == extracted_integrity, "Verification changed clean extraction")
    require(vp.verify(stage) == stage_integrity, "Packaging changed sealed stage")
    require(bind_release(root) == binding and source_distribution_map(root) == initial,
            "Input distribution changed during packaging")
    archive_hash = sha(archive)
    receipt = {"schema": "komorebi.space.release-delivery.v1", "status": "PASS", "version": VERSION,
               "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "archive": archive.name, "archive_bytes": archive.stat().st_size, "archive_sha256": archive_hash,
               "manifest_payload_files": len(entries), "zip_members": len(names),
               "stage_integrity": stage_integrity, "clean_extraction_integrity": extracted_integrity,
               "stage_sha256sums": stage_sums, "clean_extraction_sha256sums": extracted_sums,
               "gate_and_reader_binding": binding, "clean_extraction_verified": True,
               "current_project_objects_included": 166, "bytecode_cache_files_omitted": len(omitted),
               "packager_sha256": sha(Path(__file__)),
               "historical_objects": "The accepted v1.15 technical archive intentionally omitted its project objects; this release includes the new run's objects and preserves historical receipts without relabeling bytes.",
               "scope": "Delivery integrity and current evidence binding; not a new Lean proof run, cache authentication, or independent kernel."}
    write(out / (canonical_name + "_Delivery_Verification.json"), receipt)
    (out / (archive.name + ".sha256")).write_text(archive_hash + "  " + archive.name + "\n", encoding="utf-8")
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True, help="New directory outside source tree")
    ap.add_argument("--canonical-name", default=CANONICAL)
    args = ap.parse_args()
    root = args.root.resolve(strict=True)
    out = args.out_dir.resolve()
    require(root.is_dir(), "Publication root must be a directory")
    require(out != root and not out.is_relative_to(root), "Output must be outside publication")
    require(not out.exists(), "Refusing existing output directory: " + str(out))
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.canonical_name) is not None, "Unsafe canonical root")
    out.mkdir(parents=True)
    try:
        result = seal(root, out, args.canonical_name)
    except Exception as error:
        failure = {"status": "FAIL", "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "failure": f"{type(error).__name__}: {error}",
                   "scope": "Packaging failed. Partial outputs retained; no passing delivery claimed."}
        write(out / "PACKAGING_FAILURE.json", failure)
        print(json.dumps(failure, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
