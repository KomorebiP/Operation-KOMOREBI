#!/usr/bin/env python3
"""Verify or rebuild Paper IV's source-and-visual-appendix bundle without touching originals."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def verify_payload():
    manifest=json.loads((ROOT/'FILE_MANIFEST.json').read_text())
    for rec in manifest['files']:
        f=(ROOT/rec['path']).resolve()
        if ROOT not in f.parents:raise RuntimeError('Unsafe manifest path: '+rec['path'])
        if not f.is_file():raise RuntimeError('Missing file: '+rec['path'])
        actual=hashlib.sha256(f.read_bytes()).hexdigest()
        if actual!=rec['sha256']:raise RuntimeError('Checksum mismatch: '+rec['path'])
    # The SHA manifest also authenticates FILE_MANIFEST.json internally.
    covered=0
    for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines():
        digest,relative=line.split(maxsplit=1);f=(ROOT/relative).resolve()
        if ROOT not in f.parents:raise RuntimeError('Unsafe checksum path: '+relative)
        if hashlib.sha256(f.read_bytes()).hexdigest()!=digest:raise RuntimeError('SHA256SUMS mismatch: '+relative)
        covered+=1
    print(f'PASS: {len(manifest["files"])} payload hashes and {covered} SHA256SUMS entries.',flush=True)

def run(args,cwd=ROOT):
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    subprocess.run([sys.executable,'-W','error',*map(str,args)],cwd=cwd,env=env,check=True,timeout=240)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['verify','examples','build','original','original-audit'])
    p.add_argument('--output-dir',type=Path,default=ROOT/'rebuilt')
    a=p.parse_args()
    if a.command in ('verify','examples'):
        if a.command=='verify':verify_payload()
        with tempfile.TemporaryDirectory(prefix='paper_iv_verify_') as td:
            work=Path(td)
            shutil.copytree(ROOT/'visual_appendix/source',work/'source',ignore=shutil.ignore_patterns('__pycache__'))
            (work/'checks').mkdir();shutil.copy2(ROOT/'visual_appendix/checks/verify_examples.py',work/'checks/verify_examples.py')
            run(['checks/verify_examples.py'],cwd=work)
            if a.command=='verify':
                run([ROOT/'tools/audit_original.py','--output-dir',work/'original_static'])
        print('No Lean compilation was invoked.',flush=True)
    elif a.command=='build':run([ROOT/'visual_appendix/build.py','--output-dir',a.output_dir])
    elif a.command=='original':run([ROOT/'tools/build_original.py','--output-dir',a.output_dir/'original'])
    else:run([ROOT/'tools/audit_original.py','--output-dir',a.output_dir/'original_static'])

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as e:raise SystemExit(f'Paper IV command failed: {e}')
