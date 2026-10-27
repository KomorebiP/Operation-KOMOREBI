#!/usr/bin/env python3
"""Paper VII source-and-evidence bundle runner (Python 3.10+).

verify: standard-library hash/inventory verification, no source changes.
examples: isolated exact-example replay (requires SymPy).
build: isolated vector-appendix and combined-PDF rebuild (see dependencies).
original: original numerical, figure, TeX and verifier-software replay; NOT Lean.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe_output(out):
    out=out.resolve()
    for protected in [ROOT/'original_snapshot',ROOT/'original_companion',ROOT/'visual_appendix',ROOT/'related_editorial_v0.5.1',ROOT/'editorial_evidence',ROOT/'reading']:
        if out==protected or protected in out.parents:raise ValueError('Choose an output directory outside preserved source/evidence trees.')
    if out==ROOT:raise ValueError('Choose a dedicated output directory, not the bundle root.')
    return out

def verify():
    man=json.loads((ROOT/'MANIFEST.json').read_text());bad=[]
    for rel,rec in man['files'].items():
        p=(ROOT/rel).resolve()
        if ROOT not in p.parents or not p.is_file():bad.append((rel,'missing or unsafe'));continue
        if p.stat().st_size!=rec['bytes'] or sha(p)!=rec['sha256']:bad.append((rel,'size/hash mismatch'))
    sums=0
    for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines():
        h,rel=line.split(maxsplit=1);p=(ROOT/rel.strip()).resolve()
        if ROOT not in p.parents or not p.is_file() or sha(p)!=h:bad.append((rel,'SHA256SUMS mismatch'))
        sums+=1
    if bad:
        print(json.dumps({'status':'FAIL','failures':bad},indent=2));return 1
    print(json.dumps({'status':'PASS','payload_files':len(man['files']),'sha256_entries':sums,'scope':'file integrity only; no new Lean check'},indent=2));return 0

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['verify','examples','build','original']);ap.add_argument('--output-dir',type=Path);args=ap.parse_args()
    if args.action=='verify':return verify()
    out=safe_output(args.output_dir or ROOT/('rebuilt_'+args.action));out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    if args.action=='build':return subprocess.call([sys.executable,str(ROOT/'visual_appendix/build.py'),'--output-dir',str(out)],env=env)
    if args.action=='original':return subprocess.call([sys.executable,str(ROOT/'tools/audit_original.py'),'--out',str(out)],env=env)
    with tempfile.TemporaryDirectory(prefix='paper_vii_examples_') as td:
        w=Path(td);shutil.copytree(ROOT/'visual_appendix/source',w/'source',ignore=shutil.ignore_patterns('__pycache__'));(w/'checks').mkdir();shutil.copy2(ROOT/'visual_appendix/checks/verify_examples.py',w/'checks/verify_examples.py')
        p=subprocess.run([sys.executable,'-W','error',str(w/'checks/verify_examples.py')],cwd=w,env=env)
        if p.returncode:return p.returncode
        shutil.copy2(w/'checks/EXACT_CHECKS.json',out/'EXACT_CHECKS.json');print('Report:',out/'EXACT_CHECKS.json');return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError,KeyError,json.JSONDecodeError,subprocess.SubprocessError) as exc:raise SystemExit('Failed: '+str(exc)) from exc
