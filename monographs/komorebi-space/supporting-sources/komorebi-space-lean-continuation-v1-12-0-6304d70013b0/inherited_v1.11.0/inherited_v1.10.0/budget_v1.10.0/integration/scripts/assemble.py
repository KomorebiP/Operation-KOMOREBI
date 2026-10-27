#!/usr/bin/env python3
"""Freeze a source-only cumulative assembly. This does not execute Lean.

The accepted parent receipt binds all inherited source/control bytes. The v1.9
published production files must agree. The overlay may only add production
modules and controls. All destinations/attempts are immutable.
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
from pathlib import Path
# Load the reviewed helper source directly, never a timestamp-cached .pyc.
_common_path = Path(__file__).resolve().with_name("common.py")
_common_ns = {"__file__": str(_common_path), "__name__": "_ks_reviewed_common"}
exec(compile(_common_path.read_bytes(), str(_common_path), "exec"), _common_ns)
ROOT_MODULE = _common_ns["ROOT_MODULE"]
graph = _common_ns["graph"]
sha = _common_ns["sha"]
write_json = _common_ns["write_json"]
tree_hashes = _common_ns["tree_hashes"]

HOME = Path(__file__).resolve().parents[1]
PARENT_RECEIPT = "ed08da780d623b1b53936a80207a76f63b9fd3ca02fa8f43e47ee7ca5660467b"
INHERITED_COUNTS = {"formal": {"positive": 1, "negative": 6, "policy": 1},
                    "extension": {"positive": 1, "negative": 4, "policy": 1},
                    "new": {"positive": 2, "negative": 4, "policy": 0}}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--overlay", type=Path, required=True)
    p.add_argument("--label", required=True)
    a = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", a.label): p.error("Unsafe label")
    dest = HOME / "assemblies" / a.label
    if dest.exists(): p.error("Refusing to overwrite assembly")
    base, published, overlay = a.base.resolve(), a.published.resolve(), a.overlay.resolve()
    recpath = base / "receipt.json"
    if sha(recpath) != PARENT_RECEIPT: raise ValueError("Wrong accepted parent receipt")
    rec = json.loads(recpath.read_text())
    if rec["status"] != "PASS" or not rec["lean_executed"]: raise ValueError("Unaccepted parent")
    inherited = tree_hashes(base / "source")
    if inherited != rec["source_snapshot_sha256"]: raise ValueError("Parent source/control bytes changed")
    parent_graph = graph(base / "source")
    published_graph = graph(published)
    if parent_graph["source_sha256"] != published_graph["source_sha256"]:
        raise ValueError("Published v1.9 production differs from accepted v1.8 formal source")
    if parent_graph["compile_targets"] != 147 or parent_graph["production_modules"] != 144:
        raise ValueError("Unexpected accepted parent graph size")
    overlay_before = tree_hashes(overlay)
    modules = sorted((overlay / "KomorebiSpace").rglob("*.lean"))
    if not modules: raise ValueError("No new modules")
    new_names = [".".join(x.relative_to(overlay).with_suffix("").parts) for x in modules]
    manifest_path = overlay / "tests/control_manifest.json"
    new_controls = json.loads(manifest_path.read_text())["controls"]
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
        if not all(isinstance(x,str) and x for x in c.get("required_markers", [])):
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
    controls = []
    for scope in sorted(INHERITED_COUNTS):
        for kind in ("positive", "negative", "policy"):
            paths = sorted((source / "tests" / scope / kind).glob("*.lean"))
            if len(paths) != INHERITED_COUNTS[scope][kind]: raise ValueError("Wrong inherited control count")
            for f in paths:
                markers = []
                if kind == "policy": markers = ["AXIOM_POLICY_REJECTION" if scope == "formal"
                                                   else "custom axiom rejected by the extension policy"]
                elif kind == "negative":
                    if f.stem == "Placeholder": markers = ["declaration uses `sorry`"]
                    elif f.stem == "FalseArithmetic": markers = ["Tactic `decide` proved that the proposition", "is false"]
                    elif f.stem in ("FinitePrefixesImplyPoint", "WR02MissingBudget"): markers = ["Type mismatch"]
                    else: markers = ["unsolved goals", "⊢ False"]
                controls.append({"path": f.relative_to(source).as_posix(), "kind": kind,
                                 "scope": scope, "required_markers": markers})
    for c in sorted(new_controls, key=lambda c: (c["kind"], c["path"])):
        f = source / "tests/budget" / c["path"]
        if f.exists(): raise ValueError("New control collision")
        f.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(overlay / "tests" / c["path"], f)
        controls.append({"path": f.relative_to(source).as_posix(), "kind": c["kind"],
                         "scope": "budget", "required_markers": c.get("required_markers",[])})
    controls.sort(key=lambda c: c["path"])
    info = graph(source)
    (source / "wanted_modules.txt").write_text("\n".join(info["compile_order"]) + "\n")
    old_new = (base / "source/new_modules.txt").read_text().splitlines()
    (source / "type_modules.txt").write_text("\n".join(sorted(set(old_new + new_names))) + "\n")
    (source / "new_modules.txt").write_text("\n".join(new_names) + "\n")
    shutil.copyfile(HOME / "scripts/ExportAudit.lean", source / "ExportAudit.lean")
    write_json(source / "control_manifest.json", {"controls": controls})
    if (tree_hashes(overlay) != overlay_before or tree_hashes(base / "source") != inherited
            or sha(recpath) != PARENT_RECEIPT
            or graph(published)["source_sha256"] != published_graph["source_sha256"]):
        raise ValueError("Source inputs changed during assembly")
    info.update({"schema": "komorebi-space-budget-assembly-v1", "status": "STATIC_ONLY_NOT_LEAN_VERIFIED",
                 "parent_receipt_sha256": PARENT_RECEIPT, "parent_receipt_path": str(recpath),
                 "parent_source_snapshot_sha256": inherited,
                 "published_production_sha256": published_graph["source_sha256"],
                 "new_modules": new_names, "controls": controls,
                 "overlay_path": str(overlay), "overlay_input_sha256": overlay_before,
                 "project_file_sha256": tree_hashes(source),
                 "assembler_sha256": sha(Path(__file__)), "helpers_sha256": tree_hashes(HOME / "scripts")})
    write_json(dest / "inventory.json", info)
    print(json.dumps({"assembly": str(dest), "production_modules": info["production_modules"],
                      "compile_targets": info["compile_targets"], "controls": len(controls),
                      "lean_executed": False}, indent=2))

if __name__ == "__main__": main()
