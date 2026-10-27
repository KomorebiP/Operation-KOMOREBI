#!/usr/bin/env python3
"""Independent terminal integrity seal for the reviewed clean cumulative replay.

This does not run Lean or change the active verifier. It validates a terminal
receipt, all expected commands and logs, the complete copied source snapshot,
and final objects against the hashes captured after compilation. It cannot
detect a transient alteration restored before both endpoint checks.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path

HOME = Path(__file__).resolve().parents[1]
ARCHIVE = "914bb768686bc186d4baefd53c1e13690346b0f506560ede916d1fb87d7e6794"
INVENTORY = "dbcfb506fc91966fd3dbcd7f3d0aa4215109cf1932fb215b1b7872a8e2ed5614"
REVIEWED = {
    "assemble.py": "bfbbff3984d8a1aabfba492e288e1798d4c1c3613e2bf507e869635251238aa2",
    "verify.py": "c4235ab052f48b2dd1923e6ec7097f481ddc295f7877a6af29571577350b32b7",
    "common.py": "7c8264f4088372365bde08162ceb6fde2f31646c2ddbf1e28fc78595203a7614",
    "ExportAudit.lean": "62cb9468adf739e56c52f500abdd856c980efde62e5fc9e3d3581e2bbaa0ded6",
}
CONTROLS = {"formal": {"positive": 1, "negative": 6, "policy": 1},
            "extension": {"positive": 1, "negative": 4, "policy": 1}}
AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def tree(root: Path) -> dict[str, str]:
    if not root.is_dir():
        raise ValueError(f"Missing directory: {root}")
    return {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def safe_file(root: Path, rel: str) -> Path:
    path = (root / rel).resolve()
    need(not Path(rel).is_absolute() and path.is_relative_to(root.resolve()),
         f"Unsafe relative path in receipt: {rel}")
    return path


def validate(base: Path) -> dict:
    receipt_path = base / "receipt.json"
    initial_receipt = digest(receipt_path)
    rec = json.loads(receipt_path.read_text())
    need(rec.get("schema") == "komorebi-space-combined-replay-v1", "Wrong base receipt schema")
    need(rec.get("status") == "PASS", "Base must have terminal PASS")
    need(rec.get("lean_executed") is True and rec.get("clean_project_build") is True,
         "Base lacks executed clean-build scope")
    need(rec.get("source_unchanged_during_run") is True and rec.get("finished_utc"),
         "Base lacks terminal preservation evidence")
    need(digest(HOME / "inventory.json") == INVENTORY == rec.get("inventory_sha256"),
         "Inventory differs from independently reviewed inventory")
    inventory = json.loads((HOME / "inventory.json").read_text())
    need(inventory.get("source_archive_sha256") == ARCHIVE == rec.get("source_archive_sha256"),
         "Wrong frozen source archive")
    need(tree(HOME / "scripts") == REVIEWED == rec.get("verifier_input_sha256"),
         "Base verifier differs from independently reviewed scripts")
    expected_project = inventory["project_file_sha256"]
    need(tree(HOME / "project") == expected_project == rec.get("project_file_sha256"),
         "Assembled project differs from archive-bound inventory")
    expected_source = dict(expected_project, **{"ExportAudit.lean": REVIEWED["ExportAudit.lean"]})
    source, build = base / "source", base / "build"
    actual_source = tree(source)
    need(actual_source == expected_source,
         "Full replay snapshot differs: production, controls, exporter, pins, lists, or extra files")
    for key in ("compile_order", "compile_targets", "production_modules", "source_sha256", "entrypoints"):
        need(rec.get(key) == inventory[key], f"Receipt has wrong complete graph field: {key}")
    need(rec["production_modules"] == 141 and rec["compile_targets"] == 144,
         "Wrong frozen cumulative scope")
    need((source / "wanted_modules.txt").read_text().splitlines() == rec["compile_order"],
         "Exporter module list differs from complete graph")
    need(rec.get("compile_policy") == {"threads": 1, "warningAsError": True, "autoImplicit": False},
         "Wrong compile policy")
    final_objects = tree(build)
    need(final_objects == rec.get("object_sha256"), "Compiled objects changed after their recorded snapshot")
    need(set(final_objects) == {m.replace(".", "/") + ".olean" for m in rec["compile_order"]},
         "Object tree does not contain exactly one compiled object per expected module")
    runtime = Path(rec["runtime"])
    lean = runtime / "toolchain/bin/lean"
    flags = [str(lean), "-j1", "-DwarningAsError=true", "-DautoImplicit=false"]
    pins = json.loads((source / "pinned-dependencies.json").read_text())["packages"]
    expected = [("lean_version", [str(lean), "--version"], False, None)]
    expected_dependencies = []
    for pin in pins:
        pkg = runtime / "workspace/.lake/packages" / pin["name"]
        expected.append(("pin_" + pin["name"], ["git", "-C", str(pkg), "rev-parse", "HEAD"], False, None))
        expected.append(("clean_" + pin["name"], ["git", "-C", str(pkg), "diff", "--exit-code", "HEAD", "--"], False, None))
        expected_dependencies.append({"name": pin["name"], "expected": pin["rev"], "actual": pin["rev"]})
    need(rec.get("dependencies") == expected_dependencies, "Missing or wrong dependency pin receipts")
    for mod in rec["compile_order"]:
        rel = mod.replace(".", "/")
        expected.append(("compile_" + mod, flags + ["-o", str(build / (rel + ".olean")),
                                                   str(source / (rel + ".lean"))], False, None))
    expected.append(("axiom_export", flags + [str(source / "ExportAudit.lean")], False, None))
    for scope, groups in CONTROLS.items():
        for kind, count in groups.items():
            paths = sorted((source / "tests" / scope / kind).glob("*.lean"))
            need(len(paths) == count, f"Wrong control inventory for {scope}/{kind}")
            for path in paths:
                marker = None
                if kind == "policy":
                    marker = "AXIOM_POLICY_REJECTION" if scope == "formal" else "custom axiom rejected by the extension policy"
                elif kind == "negative" and path.stem == "Placeholder":
                    marker = "sorry"
                expected.append((f"{scope}_{kind}_{path.stem}", flags + [str(path)], kind != "positive", marker))
    commands = rec.get("commands", [])
    labels = [cmd.get("label") for cmd in commands]
    expected_labels = [item[0] for item in expected]
    need(labels == expected_labels and len(set(labels)) == len(labels),
         "Missing, duplicated, unexpected, or reordered compiler/audit/control commands")
    bad_errors = ("unknown module", "unknown identifier", "unknown constant", "object file",
                  "failed to load", "no such file", "not found", "cannot execute", "segmentation fault", "stack overflow")
    log_hashes = {}
    for cmd, (label, argv, negative, marker) in zip(commands, expected, strict=True):
        need(cmd.get("argv") == argv, f"Command checks wrong target or flags: {label}")
        need(cmd.get("passed") is True and cmd.get("timeout") is False,
             f"Command failed or timed out: {label}")
        need(cmd.get("expected_rejection") is negative and cmd.get("required_marker") == marker,
             f"Wrong command expectation: {label}")
        need(cmd.get("log") == f"logs/{label}.log", f"Wrong log path: {label}")
        log = safe_file(base, cmd["log"])
        log_hashes[cmd["log"]] = digest(log)
        need(log_hashes[cmd["log"]] == cmd.get("log_sha256"), f"Command log changed: {label}")
        output = log.read_text(errors="replace")
        code = cmd["exit_code"]
        if negative:
            need(code > 0 and "error" in output.lower() and not any(x in output.lower() for x in bad_errors)
                 and (marker is None or marker in output), f"Negative failed for unaccepted reason: {label}")
        else:
            need(code == 0, f"Positive command did not succeed: {label}")
        if label.startswith("pin_"):
            pin = next(p for p in pins if "pin_" + p["name"] == label)
            need(output.strip() == pin["rev"], f"Pin log mismatch: {label}")
    need("4.34.0-rc2" in rec["lean_version"] and "6a10ac8c22beadecabdbb0919c2b50214762f91d" in rec["lean_version"],
         "Wrong Lean version/commit")
    need(digest(lean) == rec["lean_binary_sha256"], "Compiler binary changed")
    adapter = rec.get("executable_path_adapter")
    if adapter:
        need(digest(Path(adapter["path"])) == adapter["sha256"], "Path adapter changed")
    audit_path = base / "axioms.json"
    need(digest(audit_path) == rec["axiom_report_sha256"], "Axiom report changed")
    audit = json.loads(audit_path.read_text())
    rows = audit["declarations"]
    need(rows and len(rows) == audit["count"] == rec["axiom_declarations"] and not audit["unexpected"],
         "Axiom report count or unexpected declarations disagree")
    need(len({r["name"] for r in rows}) == len(rows), "Duplicate audited names")
    audited = {r["module"] for r in rows}
    need(set(rec["compile_order"]) - set(rec["entrypoints"]) <= audited <= set(rec["compile_order"]),
         "Axiom audit omits production modules or includes unrequested modules")
    need(all(not row["unsafe"] and set(row["axioms"]) <= AXIOMS for row in rows),
         "Axiom report has unsafe or unapproved declarations")
    need(rec["axiom_union"] == sorted({a for row in rows for a in row["axioms"]}), "Axiom union disagrees")
    need(json.loads((base / "declarations_sorted.json").read_text()) == sorted(rows, key=lambda row: (row["module"], row["name"])),
         "Sorted declaration catalogue disagrees")
    need(digest(receipt_path) == initial_receipt and tree(source) == actual_source and tree(build) == final_objects,
         "Receipt, source, or objects changed during postflight validation")
    return {"base_receipt_sha256": initial_receipt, "source_snapshot_sha256": actual_source,
            "object_sha256": final_objects, "exact_command_labels": expected_labels,
            "command_count": len(expected_labels), "command_log_sha256": log_hashes,
            "axiom_report_sha256": digest(audit_path), "axiom_declarations": len(rows),
            "inventory_sha256": INVENTORY, "reviewed_verifier_sha256": REVIEWED,
            "source_archive_sha256": ARCHIVE, "gates": {
                "complete_command_inventory": True, "complete_source_snapshot": True,
                "final_object_inventory": True, "complete_audit_and_controls": True}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True, type=Path)
    args = ap.parse_args()
    base = args.base.resolve()
    output = base / "postflight.json"
    if output.exists():
        ap.error("Refusing to overwrite postflight.json")
    rep = {"schema": "komorebi-space-base-postflight-v1", "status": "RUNNING",
           "validator_sha256": digest(Path(__file__)), "base_path": str(base),
           "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "scope": "Independent terminal integrity validation; no new Lean execution",
           "limitation": "Endpoint hashes cannot detect a transient modification restored before recheck."}
    try:
        rep.update(validate(base))
        rep["status"] = "PASS"
    except Exception as exc:
        rep["status"], rep["failure"] = "FAIL", f"{type(exc).__name__}: {exc}"
    rep["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    output.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": rep["status"], "receipt": str(output), "failure": rep.get("failure")}, indent=2))
    return 0 if rep["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
