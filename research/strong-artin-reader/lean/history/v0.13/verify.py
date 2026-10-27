#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, shutil, subprocess, sys, zipfile
from pathlib import Path

EXPECTED_LEAN = "4.34.0-rc2"
EXPECTED_MATHLIB = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
BASE_ZIP = "Strong_Artin_Lean_v0.12.0_Transverse_Obstruction_Checked.zip"
BASE_MODULES = [
    "CyclicDefectAlgebra",
    "CyclicTransverseObstruction",
    "ProjectorProbeSurjectivity",
    "CyclicRelativeProbeObstruction",
]
NEW_MODULES = [
    "CenteredProbeTransverse",
    "ProjectorTraceTransverse",
    "ActualProjectorCyclicObstruction",
    "AdequateProbeDetection",
    "ConjugationProjectorProbes",
    "AdequateProjectorCyclicObstruction",
    "FiniteProbeExtraction",
    "FiniteProjectorProbeExtraction",
    "RelativeSpectralDetection",
    "RelativeAdequacyProjectorCapstone",
]

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def run(cmd, **kw):
    print('+', ' '.join(map(str,cmd)), flush=True)
    return subprocess.run(cmd, text=True, **kw)

def locate_base_src(extract_root: Path) -> Path:
    hits=list(extract_root.rglob('src/CyclicDefectAlgebra.lean'))
    if len(hits)!=1:
        raise RuntimeError(f'expected one base source root, found {len(hits)}')
    return hits[0].parent

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--kit', required=True, type=Path)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--max-checks', type=int, default=0,
                    help='compile at most this many modules this run; 0 means all')
    ap.add_argument('--resume', action='store_true')
    args=ap.parse_args()
    root=Path(__file__).resolve().parent
    kit=args.kit.resolve(); launcher=kit/'run.sh'; workspace=kit/'workspace'
    out=(args.out or (root/'verification'/'local_replay')).resolve()
    out.mkdir(parents=True, exist_ok=True)
    olean=out/'olean'; logs=out/'logs'; base_extract=out/'base_extract'
    olean.mkdir(exist_ok=True); logs.mkdir(exist_ok=True)

    ver=run(['bash',str(launcher),'lean','--version'],cwd=workspace,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    print(ver.stdout,end='')
    if ver.returncode or EXPECTED_LEAN not in ver.stdout: return 3
    ml=workspace/'.lake/packages/mathlib'
    gh=run(['git','-C',str(ml),'rev-parse','HEAD'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    actual=gh.stdout.strip(); print('mathlib:',actual)
    if gh.returncode or actual!=EXPECTED_MATHLIB: return 4

    bad=[]
    for name in NEW_MODULES:
        text=(root/'src'/f'{name}.lean').read_text()
        for token in ('sorry','admit'):
            if re.search(rf'\b{token}\b',text): bad.append((name,token))
        if re.search(r'(?m)^\s*axiom\s',text): bad.append((name,'axiom'))
    if bad:
        print('prohibited proof escape:',bad,file=sys.stderr); return 5

    base_zip=root/'base'/BASE_ZIP
    if base_extract.exists() and not args.resume: shutil.rmtree(base_extract)
    if not base_extract.exists():
        base_extract.mkdir(parents=True)
        with zipfile.ZipFile(base_zip) as z: z.extractall(base_extract)
    base_src=locate_base_src(base_extract)
    new_src=root/'src'
    jobs=[('base',m,base_src/f'{m}.lean') for m in BASE_MODULES]
    jobs += [('new',m,new_src/f'{m}.lean') for m in NEW_MODULES]
    done=0
    evidence=[]
    for kind,name,source in jobs:
        stamp=logs/f'{name}.json'
        digest=sha256(source)
        if args.resume and stamp.exists():
            try:
                old=json.loads(stamp.read_text())
                if old.get('returncode')==0 and old.get('source_sha256')==digest and (olean/f'{name}.olean').exists():
                    print('REUSE',name,digest)
                    evidence.append(old); continue
            except Exception: pass
        if args.max_checks and done>=args.max_checks:
            print('PARTIAL: max-checks reached; rerun with --resume')
            return 2
        shell='export LEAN_PATH="$1:$2:$3:${LEAN_PATH:-}"; lean -j1 -DwarningAsError=true -R "$2" -o "$4" "$5"'
        proc=run(['bash',str(launcher),'lake','env','bash','-c',shell,'_',
                  str(olean),str(new_src),str(base_src),str(olean/f'{name}.olean'),str(source)],
                 cwd=workspace,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (logs/f'{name}.log').write_text(proc.stdout)
        print(proc.stdout,end='')
        rec={'kind':kind,'module':name,'source_sha256':digest,'returncode':proc.returncode}
        stamp.write_text(json.dumps(rec,indent=2)+'\n'); evidence.append(rec); done+=1
        if proc.returncode: return proc.returncode
    (out/'result.json').write_text(json.dumps({
        'pass':True,'lean':EXPECTED_LEAN,'mathlib':EXPECTED_MATHLIB,
        'base_zip_sha256':sha256(base_zip),'modules':evidence},indent=2)+'\n')
    print('PASS: v0.13 base prerequisites and all ten additive modules compiled with warnings as errors')
    return 0

if __name__=='__main__': raise SystemExit(main())
