#!/usr/bin/env python3
"""Verify or rebuild the recovered Paper IX reader package, without modifying sources."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def verify()->None:
    manifest=json.loads((ROOT/'MANIFEST.json').read_text());failures=[]
    for e in manifest['files']:
        rel=Path(e['path']);p=ROOT/rel
        if rel.is_absolute()or'..'in rel.parts or p.is_symlink():failures.append((e['path'],'unsafe path'));continue
        if not p.is_file():failures.append((e['path'],'missing'));continue
        if p.stat().st_size!=e['bytes']or sha(p)!=e['sha256']:failures.append((e['path'],'hash/size mismatch'))
    if failures:raise RuntimeError(json.dumps(failures[:20],indent=2))
    print('PASS:',len(manifest['files']),'file hashes; sources and saved evidence match this package.')

def output_path(value:Path)->Path:
    out=value.resolve()
    for protected in ['original_snapshot','visual_appendix','reading_editions','editorial_evidence','tools']:
        p=ROOT/protected
        if out==p or p in out.parents:raise ValueError('Output must be outside preserved source and evidence trees.')
    if out==ROOT:raise ValueError('Use a new output subdirectory, not the package root.')
    return out

def main()->None:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['verify','examples','appendix','original']);p.add_argument('--output-dir',type=Path);p.add_argument('--skip-tex',action='store_true');a=p.parse_args()
    if a.action=='verify':verify();return
    out=output_path(a.output_dir or(ROOT/'rebuilt'/a.action));env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    if a.action=='examples':
        out.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='paper_ix_examples_')as td:
            t=Path(td);shutil.copytree(ROOT/'visual_appendix/source',t/'source',ignore=shutil.ignore_patterns('__pycache__'));(t/'checks').mkdir()
            shutil.copy2(ROOT/'visual_appendix/checks/verify_examples.py',t/'checks/verify_examples.py')
            with (out/'stdout.log').open('w')as h:r=subprocess.run([sys.executable,'-W','error',str(t/'checks/verify_examples.py')],env=env,stdout=h,stderr=subprocess.STDOUT,timeout=180)
            if r.returncode:raise RuntimeError('Example check failed; see '+str(out/'stdout.log'))
            shutil.copy2(t/'checks/EXACT_CHECKS.json',out/'EXACT_CHECKS.json')
        z=json.loads((out/'EXACT_CHECKS.json').read_text());print('PASS:',z['checks_passed'],'exact assertions;',z['negative_controls_rejected'],'false controls rejected.');return
    script=ROOT/('visual_appendix/build.py'if a.action=='appendix'else'tools/replay_original.py')
    command=[sys.executable,str(script),'--output-dir',str(out)]
    if a.action=='original'and a.skip_tex:command.append('--skip-tex')
    subprocess.run(command,env=env,check=True)
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError)as e:raise SystemExit(str(e))from e
