#!/usr/bin/env python3
"""Invoke the proved binomial calibration Lean endpoint on one exact JSON request."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def reject_constant(s: str):
    raise ValueError(f"non-finite JSON number: {s}")

def reject_float(s: str):
    raise ValueError(f"decimal/exponent numeric token rejected: {s}")

def unique_object(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"duplicate JSON key: {k}")
        out[k] = v
    return out

def run(request: Path, timeout: float = 180.0) -> dict:
    if request.is_symlink():
        raise ValueError("symlink request rejected")
    path = request.resolve(strict=True)
    if path.stat().st_size > 4_194_304:
        raise ValueError("invalid request file")
    json.loads(path.read_text(), parse_constant=reject_constant, parse_float=reject_float,
               object_pairs_hook=unique_object)
    kit = Path(os.environ.get("AVOC_LEAN_KIT",
        "/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2")).resolve()
    lean = kit / "toolchain/bin/lean"
    build = ROOT / ".lake/build/lib/lean"
    if not lean.is_file() or not (build / "tools/CalibrationMain.olean").is_file():
        raise ValueError("build CalibrationMain with the pinned runtime first")
    paths = [build] + [p / ".lake/build/lib/lean"
        for p in (kit / "workspace/.lake/packages").iterdir() if p.is_dir()]
    env = os.environ.copy()
    env["LEAN_PATH"] = ":".join(map(str, paths))
    env["PATH"] = str(lean.parent) + ":" + env.get("PATH", "")
    cp = subprocess.run([str(lean), "-j1", "--run",
        str(ROOT / "tools/CalibrationMain.lean"), str(path)],
        cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout)
    if cp.returncode not in (0, 2):
        raise RuntimeError(cp.stderr.strip() or f"Lean exited {cp.returncode}")
    lines = [x for x in cp.stdout.splitlines() if x.strip()]
    if not lines:
        raise RuntimeError("Lean returned no JSON")
    data = json.loads(lines[-1], parse_constant=reject_constant,
                      object_pairs_hook=unique_object)
    if data.get("status") == "error":
        raise ValueError(data.get("error", "Lean request rejected"))
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or "Lean endpoint failed")
    return data

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("request", type=Path)
    ap.add_argument("--timeout", type=float, default=180.0)
    ns = ap.parse_args()
    try:
        if not 0 < ns.timeout <= 300:
            raise ValueError("timeout must be in (0,300]")
        print(json.dumps(run(ns.request, ns.timeout), sort_keys=True))
        return 0
    except Exception as exc:
        print(f"calibration execution failed: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
