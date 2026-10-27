#!/usr/bin/env python3
"""Rerun exact checks or build the book in a temporary tree, without changing this package.

Python 3.10+ is sufficient for the standard-library exact checks.
PDF reproduction additionally requires latexmk, pdfLaTeX, and the packages used in book.tex.
This program does not run Lean and never treats archived Lean evidence as a fresh run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def unzip_checked(archive: Path, dest: Path) -> Path:
    seen=set()
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            p=PurePosixPath(member.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in member.filename or member.filename in seen:
                raise ValueError(f'Unsafe or repeated archive path: {member.filename!r}')
            seen.add(member.filename)
            if ((member.external_attr>>16)&0o170000)==0o120000:
                raise ValueError(f'Symlink not allowed: {member.filename}')
        z.extractall(dest)
    candidates=list(dest.glob('*/SHA256SUMS.json'))
    if len(candidates)!=1:raise ValueError('Expected one reviewed-core checksum manifest')
    core=candidates[0].parent
    manifest=json.loads(candidates[0].read_text(encoding='utf-8'))
    for name,expected in manifest['files'].items():
        p=core/name
        if not p.is_file() or digest(p)!=expected:
            raise ValueError(f'Reviewed-core baseline mismatch: {name}')
    return core

def run(command: list[str], cwd: Path, out: Path, label: str, timeout: float) -> dict:
    t=time.monotonic()
    try:
        p=subprocess.run(command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                         timeout=timeout,check=False)
        code=p.returncode;content=p.stdout;error=None
    except subprocess.TimeoutExpired as e:
        code=None;content=e.stdout or b'';error=f'Timeout after {timeout} seconds'
    except OSError as e:
        code=None;content=b'';error=f'{type(e).__name__}: {e}'
    (out/f'{label}.log').write_bytes(content)
    record={'label':label,'command':command,'exit_code':code,'elapsed_seconds':time.monotonic()-t,
            'error':error,'log_sha256':digest(out/f'{label}.log')}
    print(label, 'PASS' if code==0 else 'FAIL',flush=True)
    return record

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=['exact','pdf','all'],default='exact')
    ap.add_argument('--output',type=Path,required=True,help='New or empty output directory outside the package')
    ap.add_argument('--timeout',type=float,default=45,help='Seconds allowed per command; not a total runtime claim')
    a=ap.parse_args();out=a.output.expanduser().resolve()
    if ROOT==out or ROOT in out.parents:
        ap.error('Output must be outside the sealed package')
    if out.exists() and any(out.iterdir()):ap.error('Output directory must be empty')
    out.mkdir(parents=True,exist_ok=True)
    inputs={p.relative_to(ROOT).as_posix():digest(p) for p in ROOT.rglob('*')
            if p.is_file() and (p.suffix in {'.py','.tex'} or p.parent==ROOT/'sources/archives')
            and not any(x in p.parts for x in ('_build','__pycache__'))}
    records=[];error=None
    try:
        with tempfile.TemporaryDirectory(prefix='mnr-reproduce-') as td:
            work=Path(td);(work/'verification').mkdir()
            if a.mode in ('exact','all'):
                shutil.copytree(ROOT/'formal',work/'formal',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
                for name in ('check_core83','check_joint_contract','check_control_transport','check_migration','check_proof_fields'):
                    records.append(run([sys.executable,str(work/'formal'/f'{name}.py')],work,out,name,a.timeout))
                    if records[-1]['exit_code']!=0:raise RuntimeError(f'{name} did not complete successfully')
                for p in (work/'verification').glob('*.json'):shutil.copy2(p,out/p.name)
                archive=ROOT/'sources/archives/Komorebi_Machine_Theory_Reviewed_Core_v0.2_complete.zip'
                core=unzip_checked(archive,work/'original')
                for name in ('check_core','check_admissions'):
                    records.append(run([sys.executable,str(core/'code'/f'{name}.py')],core,out,'original_'+name,a.timeout))
                    if records[-1]['exit_code']!=0:raise RuntimeError(f'Original {name} failed')
                for name in ('core_checks.json','admission_checks.json','admission_examples.json'):
                    shutil.copy2(core/'evidence'/name,out/name)
            if a.mode in ('pdf','all'):
                if not shutil.which('latexmk'):raise RuntimeError('latexmk is not installed')
                tex=work/'book';tex.mkdir()
                for p in ROOT.glob('*.tex'):shutil.copy2(p,tex/p.name)
                shutil.copytree(ROOT/'figures',tex/'figures',ignore=shutil.ignore_patterns('*.py','__pycache__'))
                records.append(run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','-outdir=_build','book.tex'],tex,out,'pdf_build',a.timeout))
                if records[-1]['exit_code']!=0:raise RuntimeError('PDF build failed')
                shutil.copy2(tex/'_build/book.pdf',out/'Machine_Native_Reasoning.pdf')
                shutil.copy2(tex/'_build/book.log',out/'latex.log')
    except Exception as e:
        error=f'{type(e).__name__}: {e}'
    after={name:digest(ROOT/name) for name in inputs}
    unchanged=inputs==after
    report={'status':'PASS' if error is None and unchanged else 'FAIL','mode':a.mode,
            'python':sys.version,'platform':platform.platform(),'commands':records,
            'source_sha256_before':inputs,'source_sha256_after':after,'inputs_unchanged':unchanged,
            'error':error,'lean_executed':False,
            'limits':['Finite checks do not prove general mathematical statements.',
                      'This runner does not execute the archived Lean gates.',
                      'Publication source changes require a new correspondence review.']}
    (out/'REPRODUCTION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if error: print(error,file=sys.stderr)
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
