#!/usr/bin/env python3
"""Run the proof-carrying staged affine controller through its Lean entrypoint."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def reject_constant(s:str): raise ValueError(f"non-finite JSON number: {s}")
def unique_object(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ValueError(f"duplicate JSON key: {k}")
        out[k]=v
    return out

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('request',type=Path)
    ap.add_argument('--timeout',type=float,default=60.0)
    ns=ap.parse_args()
    try:
        if not 0<ns.timeout<=120: raise ValueError('timeout must be in (0,120]')
        path=ns.request.resolve(strict=True)
        if path.is_symlink() or path.stat().st_size>4_194_304: raise ValueError('invalid request file')
        json.loads(path.read_text(),parse_constant=reject_constant,object_pairs_hook=unique_object)
        kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
        lean=kit/'toolchain/bin/lean'; build=ROOT/'.lake/build/lib/lean'
        if not lean.is_file() or not (build/'tools/StagedAffineMain.olean').is_file():
            raise ValueError('build the staged modules with the pinned runtime first')
        paths=[build]+[p/'.lake/build/lib/lean' for p in (kit/'workspace/.lake/packages').iterdir() if p.is_dir()]
        env=os.environ.copy();env['LEAN_PATH']=':'.join(map(str,paths));env['PATH']=str(lean.parent)+':'+env.get('PATH','')
        cp=subprocess.run([str(lean),'-j1','--run',str(ROOT/'tools/StagedAffineMain.lean'),str(path)],
                          cwd=ROOT,env=env,text=True,capture_output=True,timeout=ns.timeout)
        sys.stdout.write(cp.stdout);sys.stderr.write(cp.stderr)
        return cp.returncode
    except (OSError,ValueError,subprocess.TimeoutExpired,json.JSONDecodeError) as exc:
        print(f'staged affine execution failed: {exc}',file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
