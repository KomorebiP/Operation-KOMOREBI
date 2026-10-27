"""Independent bounded harness checks; no Lean proof execution is claimed."""
from pathlib import Path
import ast
import collections
import hashlib
import json
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PHASE = ROOT / "limits_v1.11.0"
BASE = ROOT / "budget_v1.10.0/integration/runs/clean_budget_01"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def filemap(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def namespace(path):
    result = {"__file__": str(path), "__name__": "reviewed_source_for_bounded_check"}
    exec(compile(path.read_bytes(), str(path), "exec"), result)
    return result


def main():
    scripts = PHASE / "integration/scripts"
    validator = PHASE / "integration/postflight/validate.py"
    helpers = filemap(scripts)
    for p in [*scripts.glob("*.py"), validator]:
        ast.parse(p.read_bytes())
    common = namespace(scripts / "common.py")
    post = namespace(validator)
    rec = json.loads((BASE / "receipt.json").read_text())
    parent_sources = filemap(BASE / "source")
    assert parent_sources == rec["source_snapshot_sha256"]
    assert digest(BASE / "receipt.json") == "42ded58f00f816a1f7895039e6521b9e510f652baf9b6e86acd1eaa47d49f376"
    assert digest(BASE / "postflight.json") == "b1d47aeab1cbe838109a751edd9bba55a57593d9e9ce0e852dc0f8988983f2f2"
    assert digest(BASE / "axioms.json") == "5bd29f14954a05a1d59135dbec241f180da8c98532715cd9d94b0570e3942cfd"
    old = json.loads((BASE / "axioms.json").read_text())["declarations"]
    assert len(old) == len({r["name"] for r in old}) == 4935
    with tempfile.TemporaryDirectory(dir=OUT) as tmp:
        project = Path(tmp) / "project"
        shutil.copytree(BASE / "source", project)
        newfiles = sorted((PHASE / "formal/KomorebiSpace").glob("*.lean"))
        newnames = ["KomorebiSpace." + p.stem for p in newfiles]
        for p in newfiles:
            target = project / "KomorebiSpace" / p.name
            assert not target.exists()
            shutil.copyfile(p, target)
        with (project / "KomorebiSpaceCombined.lean").open("a") as stream:
            stream.write("".join("import " + m + "\n" for m in newnames))
        graph = common["graph"](project)
        assert graph["compile_targets"] == 154 and graph["production_modules"] == 151
        positions = {m:i for i,m in enumerate(graph["compile_order"])}
        assert all(positions[d] < positions[m] for m,deps in graph["local_imports"].items() for d in deps)
        runtime = Path(tmp) / "runtime"
        scope = runtime / "cache"
        scope.mkdir(parents=True)
        (scope / "first").write_text("first")
        (scope / "second").write_text("second")
        (scope / "link").symlink_to("first")
        snapshot = common["runtime_hashes"](runtime, ["cache"])
        assert snapshot == post["runtime_tree"](runtime, ["cache"])
        (scope / "first").write_text("changed")
        assert common["runtime_hashes"](runtime, ["cache"]) != snapshot
        (scope / "link").unlink()
        (scope / "link").symlink_to("second")
        changed = common["runtime_hashes"](runtime, ["cache"])
        assert changed["symlink_targets"] != snapshot["symlink_targets"]
        for bad in ["missing", "."]:
            (scope / "link").unlink()
            (scope / "link").symlink_to(bad)
            for f in [common["runtime_hashes"], post["runtime_tree"]]:
                try:
                    f(runtime, ["cache"])
                except ValueError:
                    pass
                else:
                    raise AssertionError("Broken/directory runtime symlink accepted")
    manifest_path = PHASE / "formal/tests/control_manifest.json"
    controls = json.loads(manifest_path.read_text())["controls"]
    actual = {p.relative_to(manifest_path.parent).as_posix() for p in manifest_path.parent.rglob("*.lean")}
    assert actual == {c["path"] for c in controls}
    assert all(c.get("required_markers") for c in controls if c["kind"] != "positive")
    assert filemap(scripts) == helpers
    summary = {
        "status":"PASS", "lean_executed":False,
        "scope":"Bounded syntax, source ancestry, graph, manifest, and runtime-inventory implementation checks",
        "helper_sha256":helpers, "postflight_sha256":digest(validator),
        "baseline_declarations":len(old), "baseline_source_files":len(parent_sources),
        "production_modules":graph["production_modules"], "compile_targets":graph["compile_targets"],
        "new_modules":newnames, "new_source_sha256":{p.name:digest(p) for p in newfiles},
        "new_controls":dict(collections.Counter(c["kind"] for c in controls)),
        "new_control_source_sha256":filemap(manifest_path.parent),
        "expected_commands":1 + 4*len(json.loads((BASE/"source/pinned-dependencies.json").read_text())["packages"]) + graph["compile_targets"] + 1 + len(rec["controls"]) + len(controls),
        "bounded_checks":["Python syntax", "Accepted parent receipt/postflight/audit hashes", "Parent complete source hash inventory", "4935 distinct inherited names", "154-target/151-production acyclic cumulative graph", "Dependency-before-dependent compile order", "All new control paths covered exactly", "Required rejection markers present", "Both runtime inventories agree", "Changed runtime bytes detected", "Changed symlink target detected", "Broken and directory symlinks rejected"]
    }
    (OUT / "preflight_checks.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
