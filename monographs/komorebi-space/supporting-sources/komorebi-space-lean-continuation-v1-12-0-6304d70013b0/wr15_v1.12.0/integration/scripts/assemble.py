#!/usr/bin/env python3
"""Freeze an additive Lean source assembly over the accepted v1.11.0 replay.

No Lean execution occurs here. The receipt, postflight, source snapshot, and
declaration report are hash-bound to the accepted parent. Attempts are immutable.
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
from pathlib import Path

# Load reviewed source directly, never a timestamp-cached .pyc.
_common_path = Path(__file__).resolve().with_name("common.py")
_common_ns = {"__file__": str(_common_path), "__name__": "_ks_reviewed_common"}
exec(compile(_common_path.read_bytes(), str(_common_path), "exec"), _common_ns)
ROOT_MODULE = _common_ns["ROOT_MODULE"]
graph = _common_ns["graph"]
sha = _common_ns["sha"]
write_json = _common_ns["write_json"]
tree_hashes = _common_ns["tree_hashes"]

HOME = Path(__file__).resolve().parents[1]
PARENT_RECEIPT = "1fbbed1df05f74aa0c6b967cd3828b3985c7b3c4bb533027636719640978bdd0"
PARENT_POSTFLIGHT = "37e7f09b13c7db2a9cb979f64402199d1a377a19f58ec698a605d7b78765bb9d"
NEW_MODULES = ["KomorebiSpace.CoordinateBasisChange", "KomorebiSpace.CoordinateCovector"]
IDENTITY_KEYS = ("name", "module", "kind", "unsafe", "axioms")


def identity(row):
    return {k: sorted(row[k]) if k == "axioms" else row[k] for k in IDENTITY_KEYS}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--overlay", type=Path, required=True)
    p.add_argument("--label", required=True)
    a = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+_[0-9]{2,}", a.label): p.error("Require safe numbered label ending _NN")
    dest = HOME / "assemblies" / a.label
    if dest.exists(): p.error("Refusing to overwrite assembly")
    base, overlay = a.base.resolve(), a.overlay.resolve()
    recpath, postpath, auditpath = base / "receipt.json", base / "postflight.json", base / "axioms.json"
    if sha(recpath) != PARENT_RECEIPT or sha(postpath) != PARENT_POSTFLIGHT:
        raise ValueError("Wrong accepted parent receipt or postflight")
    rec, post = json.loads(recpath.read_text()), json.loads(postpath.read_text())
    if (rec["status"] != "PASS" or not rec["lean_executed"] or post["status"] != "PASS"
            or post["run_receipt_sha256"] != PARENT_RECEIPT):
        raise ValueError("Unaccepted parent")
    inherited = tree_hashes(base / "source")
    if inherited != rec["source_snapshot_sha256"] or inherited != post["source_snapshot_sha256"]:
        raise ValueError("Parent source/control bytes changed")
    parent_graph = graph(base / "source")
    if parent_graph["compile_targets"] != 154 or parent_graph["production_modules"] != 151:
        raise ValueError("Unexpected accepted parent graph size")
    if parent_graph["source_sha256"] != rec["source_sha256"]:
        raise ValueError("Parent graph differs from accepted receipt")
    inherited_controls = json.loads((base / "source/control_manifest.json").read_text())["controls"]
    if inherited_controls != rec["controls"] or len(inherited_controls) != 39:
        raise ValueError("Parent control manifest differs from accepted receipt")
    if sha(auditpath) != rec["axiom_report_sha256"] or sha(auditpath) != post["axiom_report_sha256"]:
        raise ValueError("Parent declaration report changed")
    audit = json.loads(auditpath.read_text())
    parent_identities = sorted([identity(r) for r in audit["declarations"]], key=lambda r: r["name"])
    if audit["unexpected"] or len(parent_identities) != 4982 or len({r["name"] for r in parent_identities}) != 4982:
        raise ValueError("Invalid parent declaration inventory")
    del audit
    overlay_before = tree_hashes(overlay)
    modules = sorted((overlay / "KomorebiSpace").rglob("*.lean"))
    if not modules: raise ValueError("No new modules")
    new_names = [".".join(x.relative_to(overlay).with_suffix("").parts) for x in modules]
    if new_names != NEW_MODULES: raise ValueError("Unexpected WR15 module inventory")
    new_controls = json.loads((overlay / "tests/control_manifest.json").read_text())["controls"]
    if not new_controls: raise ValueError("Missing new controls")
    actual_control_paths = {x.relative_to(overlay / "tests").as_posix()
                            for x in (overlay / "tests").rglob("*.lean")}
    if len({c["path"] for c in new_controls}) != len(new_controls): raise ValueError("Duplicate controls")
    if {c["path"] for c in new_controls} != actual_control_paths: raise ValueError("Control manifest incomplete/extra")
    for c in new_controls:
        rel = Path(c["path"])
        if rel.is_absolute() or ".." in rel.parts or len(rel.parts) != 2 or rel.parts[0] != c["kind"]:
            raise ValueError("Unsafe/unclassified control path")
        if c["kind"] not in ("positive", "negative", "policy"): raise ValueError("Unknown control kind")
        if c["kind"] != "positive" and not c.get("required_markers"):
            raise ValueError("Every rejection control needs an intended error marker")
        if not all(isinstance(x, str) and x for x in c.get("required_markers", [])):
            raise ValueError("Invalid control markers")
    if not {"positive", "negative"} <= {c["kind"] for c in new_controls}:
        raise ValueError("Need positive and negative controls")
    dest.mkdir(parents=True)
    source = dest / "source"
    shutil.copytree(base / "source", source)
    for f in modules:
        rel = f.relative_to(overlay)
        if (source / rel).exists(): raise ValueError(f"Overlay overwrites inherited module: {rel}")
        (source / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, source / rel)
    root = source / f"{ROOT_MODULE}.lean"
    root.write_text(root.read_text() + "".join(f"import {m}\n" for m in new_names))
    controls = list(inherited_controls)
    for c in sorted(new_controls, key=lambda c: (c["kind"], c["path"])):
        f = source / "tests/wr15" / c["path"]
        if f.exists(): raise ValueError("New control collision")
        f.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(overlay / "tests" / c["path"], f)
        controls.append({"path": f.relative_to(source).as_posix(), "kind": c["kind"],
                         "scope": "wr15", "required_markers": c.get("required_markers", [])})
    controls.sort(key=lambda c: c["path"])
    info = graph(source)
    (source / "wanted_modules.txt").write_text("\n".join(info["compile_order"]) + "\n")
    old_type_modules = (base / "source/type_modules.txt").read_text().splitlines()
    old_new_modules = (base / "source/new_modules.txt").read_text().splitlines()
    (source / "type_modules.txt").write_text("\n".join(sorted(set(old_type_modules + old_new_modules + new_names))) + "\n")
    (source / "new_modules.txt").write_text("\n".join(new_names) + "\n")
    shutil.copyfile(HOME / "scripts/ExportAudit.lean", source / "ExportAudit.lean")
    write_json(source / "control_manifest.json", {"controls": controls})
    write_json(source / "parent_declarations.json", {
        "parent_receipt_sha256": PARENT_RECEIPT, "parent_postflight_sha256": PARENT_POSTFLIGHT,
        "parent_axiom_report_sha256": rec["axiom_report_sha256"], "declarations": parent_identities})
    changed_allowed = {f"{ROOT_MODULE}.lean", "ExportAudit.lean", "control_manifest.json",
                       "new_modules.txt", "type_modules.txt", "wanted_modules.txt", "parent_declarations.json"}
    source_after = tree_hashes(source)
    if any(source_after.get(rel) != digest for rel, digest in inherited.items() if rel not in changed_allowed):
        raise ValueError("Unexpected inherited file modification")
    if (tree_hashes(overlay) != overlay_before or tree_hashes(base / "source") != inherited
            or sha(recpath) != PARENT_RECEIPT or sha(postpath) != PARENT_POSTFLIGHT
            or sha(auditpath) != rec["axiom_report_sha256"]):
        raise ValueError("Source inputs changed during assembly")
    info.update({"schema": "komorebi-space-wr15-assembly-v1", "status": "STATIC_ONLY_NOT_LEAN_VERIFIED",
                 "parent_receipt_sha256": PARENT_RECEIPT, "parent_receipt_path": str(recpath),
                 "parent_postflight_sha256": PARENT_POSTFLIGHT,
                 "parent_recovered_run_path": str(base),
                 "parent_historical_assembly_path": rec["assembly_path"],
                 "parent_historical_runtime_path": rec["runtime"],
                 "parent_recovery_policy": "Recovered paths are bound by accepted content hashes; historical receipt paths remain immutable.",
                 "parent_axiom_report_sha256": rec["axiom_report_sha256"],
                 "parent_declarations": len(parent_identities), "parent_controls": inherited_controls,
                 "parent_source_snapshot_sha256": inherited, "allowed_inherited_changes": sorted(changed_allowed),
                 "new_modules": new_names, "controls": controls,
                 "overlay_path": str(overlay), "overlay_input_sha256": overlay_before,
                 "project_file_sha256": source_after,
                 "assembler_sha256": sha(Path(__file__)), "helpers_sha256": tree_hashes(HOME / "scripts")})
    write_json(dest / "inventory.json", info)
    print(json.dumps({"assembly": str(dest), "production_modules": info["production_modules"],
                      "compile_targets": info["compile_targets"], "controls": len(controls),
                      "lean_executed": False}, indent=2))


if __name__ == "__main__": main()
