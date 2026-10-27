#!/usr/bin/env python3
"""Pinned, serial, source-only Paper II replay. Dependency caches remain trusted.

Writes all objects/logs outside the checkpoint. Existing output is never reused.
No Lake network access, automatic toolchain update, or cached project object reuse.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/workspace/scratch/9f53d520971c/release_package/Komorebi_Paper_II_Release_2026-10-15/formal')
SOURCE = ROOT / 'current'
COMPILER_SHA = 'e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550'
VERSION_COMMIT = '6a10ac8c22beadecabdbb0919c2b50214762f91d'
BASELINE = ['KomorebiVerification/'+m for m in [
 'ProjectorCore','ExactCoordinates','FibreRefinement','ResidueProjectors',
 'PaperII/NestedRefinement','PaperII/ResidueFourierCRT','PaperII/WeightedTransfer',
 'PaperII/TransferZeta','PaperII/ResultantSeparation','PaperII/SmithDyadic',
 'PaperII/LinearDefects','PaperII/TypedLinearDefects','PaperII']]
BASELINE += ['KomorebiVerification','KomorebiVerification/PaperII/KernelAudit']
EXTENSION = ['KomorebiVerification/PaperII/'+m for m in
 ['CommonRefinement','FiniteCommonRefinement','CommonRefinementConsumers']]
EXTENSION += ['PaperIIRefinement','ReleaseAudit']
FLAGS = ['-j1','-DwarningAsError=true','-DautoImplicit=false',
 '-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3','-Dpp.unicode.fun=true']

def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def fingerprints() -> dict[str,str]:
    return {str(p.relative_to(SOURCE)):sha(p) for p in sorted(SOURCE.rglob('*')) if p.is_file()}

def validate_runtime(kit: Path) -> tuple[dict,dict[str,str]]:
    lean=kit/'toolchain/bin/lean'; deps=kit/'workspace/.lake/packages'
    if not lean.is_file() or sha(lean)!=COMPILER_SHA:
        raise RuntimeError('Pinned compiler missing or SHA-256 mismatch')
    adapter=kit/'compat/app_path.so'
    adapter_env=os.environ.copy()
    adapter_env['LD_PRELOAD']=str(adapter)+((':'+adapter_env['LD_PRELOAD']) if adapter_env.get('LD_PRELOAD') else '')
    version=subprocess.run([str(lean),'--version'],env=adapter_env,capture_output=True,text=True,timeout=30,check=True).stdout.strip()
    if '4.34.0-rc2' not in version or VERSION_COMMIT not in version:
        raise RuntimeError('Compiler version/commit mismatch')
    locked=json.loads((SOURCE/'lake-manifest.json').read_text())['packages']
    rows=[]; paths=[]
    for item in locked:
        d=deps/item['name'];lib=d/'.lake/build/lib/lean'
        head=subprocess.run(['git','-C',str(d),'rev-parse','HEAD'],capture_output=True,text=True,timeout=30,check=True).stdout.strip()
        dirty=subprocess.run(['git','-C',str(d),'status','--porcelain','--untracked-files=no'],capture_output=True,text=True,timeout=30,check=True).stdout.strip()
        if head!=item['rev'] or dirty:
            raise RuntimeError('Dependency pin/cache/worktree mismatch: '+item['name'])
        rows.append(dict(name=item['name'],head=head,expected=item['rev'],tracked_changes=dirty,compiled_cache_present=lib.is_dir()))
        # A manifest package need not be imported by this proof closure (e.g. Cli).
        # Required missing imports still fail in the compiler, never count as passes.
        if lib.is_dir(): paths.append(str(lib))
        if item['name']=='mathlib' and not lib.is_dir():
            raise RuntimeError('The required Mathlib cache is absent')
    env=adapter_env.copy()
    for key in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']:env.pop(key,None)
    env.update(PATH=str(kit/'toolchain/bin')+os.pathsep+env.get('PATH',''),
               LEAN_PATH=os.pathsep.join(paths),MALLOC_ARENA_MAX='2',LEAN_NUM_THREADS='1',
               PYTHONDONTWRITEBYTECODE='1')
    return dict(lean_version=version,lean_sha256=sha(lean),adapter_path=str(adapter),adapter_sha256=sha(adapter),dependencies=rows,
                trust='Pinned Lean and imported dependency objects are trusted; not independently rebuilt.'),env

def execute(args: argparse.Namespace) -> int:
    out=args.output.resolve();kit=args.runtime.resolve()
    if out==ROOT or ROOT in out.parents:raise ValueError('Output must be outside the checkpoint')
    if not 0<args.timeout<86400:raise ValueError('Invalid per-module deadline')
    out.mkdir(parents=True,exist_ok=False)
    evidence={'status':'RUNNING','start_utc':datetime.now(timezone.utc).isoformat(),
              'baseline_modules':len(BASELINE),'new_production_modules':3,'modules':[],
              'boundary':'Separate original module layout, three import-only repairs, unchanged inherited bodies; not an unmodified full-Mathlib/Lake native build.'}
    report=out/'REPLAY.json';save(report,evidence)
    original=fingerprints()
    shutil.copytree(SOURCE, out/'source_snapshots')
    save(out/'SOURCE_HASHES.json',original)
    shutil.copy2(Path(__file__),out/'replay_current.py')
    try:
        runtime,env=validate_runtime(kit);save(out/'RUNTIME.json',runtime)
        build=out/'objects';build.mkdir();env['LEAN_PATH']=str(build)+os.pathsep+env['LEAN_PATH']
        for mod in BASELINE+EXTENSION:
            source=SOURCE/(mod+'.lean'); obj=build/(mod+'.olean');info=build/(mod+'.ilean')
            obj.parent.mkdir(parents=True,exist_ok=True)
            log=out/(mod.replace('/','__')+'.log');cmd=[str(kit/'toolchain/bin/lean'),*FLAGS,'-o',str(obj),'-i',str(info),mod+'.lean']
            print('START '+mod,flush=True);start=time.monotonic();code=None
            with log.open('w') as f:
                try:code=subprocess.run(cmd,cwd=SOURCE,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=args.timeout).returncode
                except subprocess.TimeoutExpired:code=124
            text=log.read_text(errors='replace')
            accepted=code==0 and obj.is_file() and not re.search(r'\berror(?:\(|:)',text)
            if mod.endswith('/KernelAudit'):
                accepted=accepted and re.search(r'FAIL-CLOSED KERNEL AUDIT PASS: [1-9][0-9]* Komorebi declarations', text) is not None
            if mod=='ReleaseAudit':
                required=['FROZEN_MAP_PASS rows=25 unique_compiled_declarations=160',
                  'EXTENDED FAIL-CLOSED KERNEL AUDIT PASS:',
                  'ENDPOINT_BODY_RECHECK_PASS count=6','NEW_DECLARATION_BODY_AUDIT_PASS entries=',
                  'PAPER_II_SUPPORTED_COMMON_REFINEMENT_RELEASE_PASS']
                accepted=accepted and all(s in text for s in required) and 'sorryAx' not in text
            row=dict(module=mod,returncode=code,status='PASS' if accepted else 'TIMEOUT' if code==124 else 'FAIL',
                     seconds=time.monotonic()-start,command=cmd,source_sha256=sha(source),log=log.name,log_sha256=sha(log),
                     objects={str(f.relative_to(build)):sha(f) for f in sorted(obj.parent.glob(obj.stem+'.*')) if f.is_file()})
            evidence['modules'].append(row);save(report,evidence);print(row['status']+' '+mod,flush=True)
            if not accepted:raise RuntimeError('Module failed; no later result accepted: '+mod)
        evidence['sources_unchanged']=original==fingerprints()
        if not evidence['sources_unchanged']:raise RuntimeError('Source tree changed during replay')
        evidence.update(status='PASS',finished_utc=datetime.now(timezone.utc).isoformat())
    except Exception as e:
        evidence.update(status='FAIL',failure=type(e).__name__+': '+str(e),sources_unchanged=original==fingerprints())
    save(report,evidence)
    print(evidence['status'],flush=True)
    return 0 if evidence['status']=='PASS' else 1

if __name__=='__main__':
    if not __debug__:raise SystemExit('Python optimization is not allowed')
    p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--timeout',type=float,default=240)
    try:raise SystemExit(execute(p.parse_args()))
    except (ValueError,FileExistsError) as e:raise SystemExit(str(e))
