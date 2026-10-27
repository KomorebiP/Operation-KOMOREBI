"""Rebuild every new module against verified frozen predecessor proof objects.

Usage: python3 checks/replay_residues.py PORTABLE_LEAN_KIT
       python3 checks/replay_residues.py --verify-only
This does not rebuild all predecessor modules.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from lean_env import lean_env

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def verify():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    for row in manifest["predecessor_sources"] + manifest["modules_in_build_order"]:
        name = row["module"]
        for folder, suffix, key in [("lean", ".lean", "source_sha256"), ("build", ".olean", "olean_sha256")]:
            if digest(ROOT / folder / "PaperX" / (name + suffix)) != row[key]:
                raise RuntimeError("File hash differs: " + folder + "/" + name)
    return manifest

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: replay_residues.py PORTABLE_LEAN_KIT or --verify-only")
    manifest = verify()
    if sys.argv[1] == "--verify-only":
        print(json.dumps({"source_and_object_hashes": "passed", "cumulative_modules":
            len(manifest["predecessor_sources"]) + len(manifest["modules_in_build_order"]),
            "compiler_invoked": False}))
        return
    lean, env = lean_env(sys.argv[1])
    if digest(Path(lean)) != manifest["lean_executable_sha256"]:
        raise RuntimeError("Pinned Lean executable hash differs")
    # Preserve every replay's logs, including failed attempts.
    run = Path(tempfile.mkdtemp(prefix="replay-", dir=ROOT))
    objects = run / "build/PaperX"
    objects.mkdir(parents=True)
    for row in manifest["predecessor_sources"]:
        shutil.copy2(ROOT / "build/PaperX" / (row["module"] + ".olean"), objects)
    paths = [p for p in env["LEAN_PATH"].split(os.pathsep) if not (Path(p) / "PaperX").exists()]
    env["LEAN_PATH"] = os.pathsep.join([str(objects.parent), *paths])
    available = {r["module"] for r in manifest["predecessor_sources"]}
    results = []
    for row in manifest["modules_in_build_order"]:
        name = row["module"]
        if not set(row["PaperX_dependencies"]) <= available:
            raise RuntimeError("Dependency order differs: " + name)
        source = ROOT / "lean/PaperX" / (name + ".lean")
        obj = objects / (name + ".olean")
        start = time.monotonic()
        with (run / (name + ".log")).open("w") as log:
            proc = subprocess.run([lean, "-DwarningAsError=true", "-o", str(obj), str(source)],
                cwd=ROOT / "lean", env=env, stdout=log, stderr=subprocess.STDOUT)
        result = {"module": name, "exit_code": proc.returncode,
            "elapsed_seconds": time.monotonic() - start, "source_sha256": digest(source)}
        if proc.returncode == 0:
            result["olean_sha256"] = digest(obj)
            result["matches_author_olean"] = digest(obj) == row["olean_sha256"]
        results.append(result)
        (run / "compilation.json").write_text(json.dumps(results, indent=2) + "\n")
        if proc.returncode or not result["matches_author_olean"]:
            raise RuntimeError("Replay failed: " + name + "; see " + str(run))
        available.add(name)
        print("PASS " + name, flush=True)
    with (run / "NamedAxioms.log").open("w") as log:
        proc = subprocess.run([lean, "-DwarningAsError=true", str(ROOT / "checks/NamedAxioms.lean")],
            cwd=ROOT / "lean", env=env, stdout=log, stderr=subprocess.STDOUT)
    if proc.returncode:
        raise RuntimeError("Named axiom query failed; see " + str(run))
    output = (run / "NamedAxioms.log").read_text()
    matches = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", output)
    found = {name for name, _ in matches}
    expected = set(manifest["named_declarations"])
    if found != expected or len(matches) != len(expected):
        raise RuntimeError("Axiom query coverage differs")
    observed = {a.strip() for _, group in matches for a in group.split(",") if a.strip()}
    if not observed <= ALLOWED:
        raise RuntimeError("Unexpected axioms: " + repr(observed))
    (run / "verification.json").write_text(json.dumps({"status": "passed", "new_modules": len(results),
        "predecessor_proof_objects_verified_and_imported": len(manifest["predecessor_sources"]),
        "new_author_objects_imported": False, "full_cumulative_rebuild_claimed": False,
        "named_declarations_axiom_audited": len(expected), "observed_axioms": sorted(observed)}, indent=2) + "\n")
    print("PASS new modules and named axiom queries; evidence: " + str(run))

if __name__ == "__main__":
    main()
