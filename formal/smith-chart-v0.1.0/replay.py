"""Replay the Smith chart Lean companion in a new, isolated output directory.

This checks pinned source and dependency identities and hashes the directly
imported cached Mathlib objects. It does not rebuild all transitive libraries.
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
import sys
import time

ROOT = Path(__file__).resolve().parent
MODULES = [
    "SmithPackets", "SmithGeometry", "SmithFourier", "SmithAlgebra",
    "SmithSampling", "SmithSamplingIntegral", "SmithSamplingInverse", "SmithExplicitInverse", "SmithEnergy", "SmithEnergyIntegral", "SmithResults", "SmithExamples", "SmithAnalyticFourier",
    "SmithParseval", "SmithCanonicalRoot", "SmithBoundaries", "SmithFiniteSamples",
]
AUDIT = "AxiomAudit.lean"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
LEAN_SHA256 = "37dfe799f69b990251f3b6bcff8a1c10c1afe2adcdecc5c580cc6726ffb63433"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    return sha(path.read_bytes())


def capture(argv: list[str], cwd: Path | None = None) -> bytes:
    return subprocess.check_output(argv, cwd=cwd, stderr=subprocess.STDOUT)


def git_state(git: Path, path: Path) -> dict[str, str]:
    rev = capture([str(git), "-C", str(path), "rev-parse", "HEAD"]).decode().strip()
    status = capture([str(git), "-C", str(path), "status", "--porcelain", "--untracked-files=no"]).decode().strip()
    return {"revision": rev, "tracked_status": status}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--mathlib", required=True, type=Path)
    parser.add_argument("--git", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path,
                        help="Repository containing the pinned Git objects")
    parser.add_argument("--output", required=True, type=Path,
                        help="A new directory; existing directories are never overwritten")
    args = parser.parse_args()
    lean, mathlib, git, repo, output = (getattr(args, x).resolve() for x in
                                        ("lean", "mathlib", "git", "repo", "output"))
    output.mkdir(parents=True, exist_ok=False)
    build = output / "build"
    build.mkdir()
    started = time.monotonic()
    receipt: dict = {"status": "FAIL", "steps": [], "limits": [
        "Mathlib and its packages use precompiled caches; their transitive objects are not rebuilt or exhaustively hashed.",
        "The source mapping and mathematical audit are self-review, not an independent review.",
        "This proves selected mathematical claims, not the correctness of the browser JavaScript or RF performance.",
    ]}
    try:
        inputs = [f"{m}.lean" for m in MODULES] + [AUDIT, "replay.py", "dependency-lock.json",
                  "source-bindings.json", "lean-toolchain", "README.md", "AUDIT.md", "STATUS.md",
                  "SAMPLING_DERIVATION.md", "SAMPLING_INTEGRAL_AUDIT.md", "EXPLICIT_INVERSE_AUDIT.md", "ENERGY_DERIVATION.md",
                  "ENERGY_INTEGRAL_AUDIT.md", "BOUNDARY_FORMAL_AUDIT.md"]
        before = {name: hash_file(ROOT / name) for name in inputs}
        receipt["input_sha256_before"] = before
        lock = json.loads((ROOT / "dependency-lock.json").read_text(encoding="utf-8"))
        binding = json.loads((ROOT / "source-bindings.json").read_text(encoding="utf-8"))
        version = capture([str(lean), "--version"]).decode().strip()
        receipt["lean"] = {"version": version, "sha256": hash_file(lean)}
        if "version 4.34.0-rc2" not in version or receipt["lean"]["sha256"] != LEAN_SHA256:
            raise RuntimeError("Lean compiler does not match the recorded Windows pin")
        if hash_file(mathlib / "lake-manifest.json") != lock["mathlib_manifest_sha256"]:
            raise RuntimeError("Mathlib manifest hash does not match the dependency lock")
        deps = {"mathlib": git_state(git, mathlib)}
        if deps["mathlib"]["revision"] != lock["mathlib_revision"]:
            raise RuntimeError("Mathlib revision differs from the lock")
        for package in lock["packages"]:
            name = package["name"]
            deps[name] = git_state(git, mathlib / ".lake" / "packages" / name)
            if deps[name]["revision"] != package["rev"]:
                raise RuntimeError(f"Dependency revision mismatch: {name}")
        if any(state["tracked_status"] for state in deps.values()):
            raise RuntimeError("A pinned dependency has tracked modifications")
        receipt["dependencies_before"] = deps
        bound = {}
        for path, expected in binding["files"].items():
            actual = sha(capture([str(git), "-C", str(repo), "show", f"{binding['revision']}:{path}"]))
            if actual != expected:
                raise RuntimeError(f"Source binding mismatch: {path}")
            bound[path] = actual
        receipt["source_binding"] = {"revision": binding["revision"], "sha256": bound}
        libdirs = [mathlib / ".lake" / "build" / "lib" / "lean"]
        libdirs += [mathlib / ".lake" / "packages" / p["name"] / ".lake" / "build" / "lib" / "lean"
                    for p in lock["packages"]]
        env = os.environ.copy()
        env["LEAN_PATH"] = os.pathsep.join(str(p) for p in [build, *libdirs])
        imports: set[str] = set()
        for name in inputs:
            if name.endswith(".lean"):
                text = (ROOT / name).read_text(encoding="utf-8")
                if re.search(r"\b(?:sorry|admit)\b|^\s*(?:axiom|unsafe)\s", text, re.MULTILINE):
                    raise RuntimeError(f"Prohibited placeholder or declaration in {name}")
                imports.update(re.findall(r"(?m)^import\s+(Mathlib\.[A-Za-z0-9_.]+)\s*$", text))
                shutil.copyfile(ROOT / name, build / name)
        object_hashes = {}
        for module in sorted(imports):
            relative = Path(*module.split(".")).with_suffix(".olean")
            matches = [directory / relative for directory in libdirs if (directory / relative).is_file()]
            if len(matches) != 1:
                raise RuntimeError(f"Expected exactly one cached object for {module}, found {len(matches)}")
            object_hashes[str(matches[0])] = hash_file(matches[0])
        receipt["direct_mathlib_objects_before"] = object_hashes

        def execute(label: str, argv: list[str]) -> bytes:
            print(label, flush=True)
            proc = subprocess.run(argv, cwd=build, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (output / f"{label}.stdout.txt").write_bytes(proc.stdout)
            (output / f"{label}.stderr.txt").write_bytes(proc.stderr)
            receipt["steps"].append({"name": label, "argv": argv, "exit_code": proc.returncode,
                                     "stdout_sha256": sha(proc.stdout), "stderr_sha256": sha(proc.stderr)})
            if proc.returncode != 0:
                raise RuntimeError(f"{label} failed: {(proc.stdout + proc.stderr).decode(errors='replace')}")
            return proc.stdout

        for module in MODULES:
            execute(f"compile-{module}", [str(lean), "-j1", "-DwarningAsError=true", "-o",
                                          f"{module}.olean", f"{module}.lean"])
        audit_bytes = execute("axiom-audit", [str(lean), "-j1", "-DwarningAsError=true", AUDIT])
        audit_text = audit_bytes.decode("utf-8")
        wanted = re.findall(r"(?m)^#print axioms\s+(\S+)", (ROOT / AUDIT).read_text(encoding="utf-8"))
        found = re.findall(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", audit_text)
        if [name for name, _ in found] != wanted:
            raise RuntimeError("Axiom audit output does not match the declared audit list")
        audited = {name: [s.strip() for s in values.split(",") if s.strip()] for name, values in found}
        unexpected = {name: values for name, values in audited.items() if not set(values) <= ALLOWED_AXIOMS}
        if unexpected:
            raise RuntimeError(f"Unexpected proof axioms: {unexpected}")
        receipt["audited_axioms"] = audited
        after = {name: hash_file(ROOT / name) for name in inputs}
        if before != after:
            raise RuntimeError("Companion inputs changed during the replay")
        receipt["input_sha256_after"] = after
        after_objects = {path: hash_file(Path(path)) for path in object_hashes}
        if object_hashes != after_objects:
            raise RuntimeError("A direct cached Mathlib object changed during the replay")
        receipt["direct_mathlib_objects_after"] = after_objects
        deps_after = {"mathlib": git_state(git, mathlib)}
        for package in lock["packages"]:
            name = package["name"]
            deps_after[name] = git_state(git, mathlib / ".lake" / "packages" / name)
        if deps_after != deps:
            raise RuntimeError("Pinned dependency state changed during the replay")
        receipt["dependencies_after"] = deps_after
        receipt["status"] = "PASS"
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        receipt["error"] = str(exc)
        print(f"FAIL: {exc}", file=sys.stderr, flush=True)
    finally:
        receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
        (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"{receipt['status']}: {output / 'receipt.json'}", flush=True)
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
