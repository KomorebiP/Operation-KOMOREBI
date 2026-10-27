#!/usr/bin/env python3
"""Invoke the pinned Lean recorder endpoint without changing any operation log."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from observation_recorder import load_exact, loads_exact

ROOT = Path(__file__).resolve().parents[1]


def runtime_provenance():
    """Pin the interpreter and transitive project-local compiled import closure."""
    kit = Path(os.environ.get("AVOC_LEAN_KIT",
        "/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2")).resolve()
    lean = kit / "toolchain/bin/lean"
    sources, objects, visited = {}, {}, set()
    def file_hash(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    def visit(module):
        if module in visited:
            return
        visited.add(module)
        source = ROOT / (module.replace(".", "/") + ".lean")
        if not source.is_file():
            return
        object_path = ROOT / ".lake/build/lib/lean" / (module.replace(".", "/") + ".olean")
        sources[str(source.relative_to(ROOT))] = file_hash(source)
        objects[str(object_path.relative_to(ROOT))] = file_hash(object_path)
        for line in source.read_text().splitlines():
            match = re.match(r"^\s*import\s+(.+)$", line)
            if match:
                for imported in match[1].split("--", 1)[0].split():
                    visit(imported)
    visit("tools.RecorderMain")
    return {"lean_executable": str(lean), "lean_sha256": file_hash(lean),
        "local_source_sha256": sources, "local_olean_sha256": objects,
        "local_module_count": len(sources),
        "dependency_boundary": "External package cache objects are supplied by the pinned portable runtime; this map pins project-local transitive imports."}


def run(request: Path, timeout: int = 180) -> dict:
    if type(timeout) is not int or not 1 <= timeout <= 300:
        raise ValueError("timeout must be an integer in [1,300]")
    load_exact(request)
    path = request.resolve(strict=True)
    kit = Path(os.environ.get("AVOC_LEAN_KIT",
        "/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2")).resolve()
    lean = kit / "toolchain/bin/lean"
    build = ROOT / ".lake/build/lib/lean"
    if not lean.is_file() or not (build / "tools/RecorderMain.olean").is_file():
        raise ValueError("build RecorderMain with the pinned runtime first")
    paths = [build] + [p / ".lake/build/lib/lean"
        for p in (kit / "workspace/.lake/packages").iterdir() if p.is_dir()]
    env = os.environ.copy()
    env["LEAN_PATH"] = ":".join(map(str, paths))
    env["PATH"] = str(lean.parent) + ":" + env.get("PATH", "")
    cp = subprocess.run([str(lean), "-j1", "--run",
        str(ROOT / "tools/RecorderMain.lean"), str(path)],
        cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout)
    if cp.returncode not in (0, 2):
        diagnostic = "\n".join(part.strip() for part in (cp.stderr, cp.stdout) if part.strip())
        raise RuntimeError(diagnostic or f"Lean exited {cp.returncode}")
    lines = [line for line in cp.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("Lean returned no JSON")
    data = loads_exact(lines[-1])
    if data.get("status") == "error":
        raise ValueError(data.get("error", "Lean request rejected"))
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or "Lean endpoint failed")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.request, args.timeout), sort_keys=True))
        return 0
    except Exception as error:
        print(json.dumps({"status": "error", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
