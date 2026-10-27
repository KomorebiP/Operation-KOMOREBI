"""Reviewer-owned bounded checks of the exact WR15 harness; no Lean execution."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PHASE = ROOT / "wr15_v1.12.0"
OUT = Path(__file__).resolve().parent
BASE = ROOT / "recovery/v1.11.0/Komorebi_Space_Lean_Continuation_v1.11.0/limits_v1.11.0/integration/runs/clean_limits_01"
PARENT_HASHES = {"receipt.json": "1fbbed1df05f74aa0c6b967cd3828b3985c7b3c4bb533027636719640978bdd0", "postflight.json": "37e7f09b13c7db2a9cb979f64402199d1a377a19f58ec698a605d7b78765bb9d", "axioms.json": "b6806e522fa0a562e91adfa3fcc3347401de7ffd7d21d7e0e5a90888d955b1f8"}

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def filemap(root):
    paths = sorted(root.rglob("*"))
    assert not any(p.is_symlink() for p in paths)
    return {p.relative_to(root).as_posix(): digest(p) for p in paths
            if p.is_file() and "__pycache__" not in p.parts}

def namespace(path):
    result = {"__file__": str(path), "__name__": "reviewer_bounded_check"}
    exec(compile(path.read_bytes(), str(path), "exec"), result)
    return result

def main():
    scripts = PHASE / "integration/scripts"
    validator = PHASE / "integration/postflight/validate.py"
    helpers = filemap(scripts)
    for path in [*scripts.glob("*.py"), validator]:
        ast.parse(path.read_bytes())
    common, post = namespace(scripts / "common.py"), namespace(validator)
    assert {p:digest(BASE/p) for p in PARENT_HASHES} == PARENT_HASHES
    receipt = json.loads((BASE/"receipt.json").read_text())
    parent_postflight = json.loads((BASE/"postflight.json").read_text())
    parent_sources = filemap(BASE/"source")
    assert parent_sources == receipt["source_snapshot_sha256"] == parent_postflight["source_snapshot_sha256"]
    rows = json.loads((BASE/"axioms.json").read_text())["declarations"]
    assert len(rows) == len({r["name"] for r in rows}) == 4982
    graph = common["graph"](BASE/"source")
    assert graph["compile_targets"] == 154 and graph["production_modules"] == 151
    assert graph["source_sha256"] == receipt["source_sha256"]
    assert len(receipt["controls"]) == 39
    positions = {m:i for i,m in enumerate(graph["compile_order"])}
    assert all(positions[d] < positions[m] for m,deps in graph["local_imports"].items() for d in deps)
    with tempfile.TemporaryDirectory(dir=OUT) as tmp:
        runtime = Path(tmp)/"runtime"
        scope = runtime/"cache"
        scope.mkdir(parents=True)
        (scope/"first").write_text("first")
        (scope/"second").write_text("second")
        (scope/"link").symlink_to("first")
        snapshot = common["runtime_hashes"](runtime, ["cache"])
        assert snapshot == post["runtime_tree"](runtime, ["cache"])
        (scope/"first").write_text("changed")
        assert common["runtime_hashes"](runtime, ["cache"]) != snapshot
        (scope/"link").unlink()
        (scope/"link").symlink_to("second")
        assert common["runtime_hashes"](runtime, ["cache"])["symlink_targets"] != snapshot["symlink_targets"]
        for target in ["missing", "."]:
            (scope/"link").unlink()
            (scope/"link").symlink_to(target)
            for scanner in [common["runtime_hashes"], post["runtime_tree"]]:
                try:
                    scanner(runtime, ["cache"])
                except ValueError:
                    pass
                else:
                    raise AssertionError("Broken/directory runtime symlink accepted")
    assert filemap(scripts) == helpers
    assert {p:digest(BASE/p) for p in PARENT_HASHES} == PARENT_HASHES
    summary = {"schema":"komorebi-space-wr15-reviewer-helper-checks-v1", "status":"PASS", "checked_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(), "lean_executed":False, "scope":"Syntax, accepted-parent ancestry and focused runtime-inventory behavior only; production/control review and actual clean replay remain pending.", "helper_sha256":helpers, "postflight_sha256":digest(validator), "parent_record_sha256":PARENT_HASHES, "parent_source_files":len(parent_sources), "parent_compile_targets":154, "parent_production_modules":151, "parent_declarations":4982, "parent_controls":39, "bounded_checks":["Python syntax", "Accepted fixed receipt/postflight/audit hashes", "All parent source/control bytes", "Distinct inherited declaration names", "Parent complete dependency-ordered graph", "Runtime implementations agree on files and file symlinks", "Runtime content and symlink target changes detected", "Broken and directory symlinks rejected"]}
    destination = OUT/"helper_checks.json"
    assert not destination.exists(), "Preserve previous reviewer records"
    destination.write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
