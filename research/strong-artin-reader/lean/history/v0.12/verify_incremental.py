#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, re, subprocess, sys
from pathlib import Path

EXPECTED_LEAN = "4.34.0-rc2"
EXPECTED_MATHLIB = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
MODULES = [
    "CyclicDefectAlgebra",
    "CyclicTransverseObstruction",
    "ProjectorProbeSurjectivity",
    "CyclicRelativeProbeObstruction",
]

def run(cmd, **kw):
    print("+", " ".join(map(str, cmd)), flush=True)
    return subprocess.run(cmd, text=True, **kw)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kit", required=True, type=Path)
    args = ap.parse_args()
    root = Path(__file__).resolve().parent
    src = root / "src"
    out = root / "verification" / "incremental_run"
    out.mkdir(parents=True, exist_ok=True)
    build = out / "olean"; build.mkdir(exist_ok=True)
    kit = args.kit.resolve(); launcher = kit / "run.sh"; workspace = kit / "workspace"
    ver = run(["bash", str(launcher), "lean", "--version"], cwd=workspace,
              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(ver.stdout, end="")
    if ver.returncode or EXPECTED_LEAN not in ver.stdout: return 3
    ml = workspace / ".lake" / "packages" / "mathlib"
    gh = run(["git", "-C", str(ml), "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    actual = gh.stdout.strip(); print("mathlib:", actual)
    if gh.returncode or actual != EXPECTED_MATHLIB: return 4
    bad=[]
    for name in MODULES[1:]:
        text=(src/f"{name}.lean").read_text()
        for token in ("sorry","admit"):
            if re.search(rf"\b{token}\b", text): bad.append((name,token))
        if re.search(r"(?m)^\s*axiom\s", text): bad.append((name,"axiom"))
    if bad:
        print("prohibited proof escape:", bad, file=sys.stderr); return 5
    for mod in MODULES:
        source=src/f"{mod}.lean"; olean=build/f"{mod}.olean"; log=out/f"{mod}.log"
        shell='export LEAN_PATH="$1:$2:${LEAN_PATH:-}"; lean -j1 -DwarningAsError=true -R "$2" -o "$3" "$4"'
        proc=run(["bash", str(launcher), "lake", "env", "bash", "-c", shell,
                  "_", str(build), str(src), str(olean), str(source)], cwd=workspace,
                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log.write_text(proc.stdout); print(proc.stdout, end="")
        if proc.returncode:
            print("FAILED:", mod, file=sys.stderr); return proc.returncode
    print("PASS: v0.12 additive obstruction/probe chain compiled with warnings as errors")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
