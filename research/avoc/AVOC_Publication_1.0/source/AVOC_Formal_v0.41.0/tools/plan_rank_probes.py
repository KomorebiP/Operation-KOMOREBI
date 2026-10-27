#!/usr/bin/env python3
"""Exact finite-catalogue adaptive rank-probe planner.

The planner chooses among the currently available 2x2-minor probes and stop.
It calls the Lean evaluator proved optimal for the supplied uniform catalogue.
The catalogue and costs are model inputs; the command does not calibrate them.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
VERSION='v0.32.0'
ENTRY='tools/AdaptiveProbeMain.lean'
LIMIT=4*1024*1024

def reject_float(x:str): raise ValueError('floating-point numbers are not accepted')
def unique_object(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError('duplicate JSON field: '+k)
        d[k]=v
    return d

def decode(text:str):
    return json.loads(text,parse_float=reject_float,parse_constant=reject_float,object_pairs_hook=unique_object)

def digest(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

def runtime(entry:str)->tuple[Path,dict[str,str]]:
    kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
    lean=kit/'toolchain/bin/lean'
    if not lean.is_file(): raise ValueError('set AVOC_LEAN_KIT to the pinned portable Lean kit')
    build=ROOT/'.lake/build/lib/lean'; visited=set()
    def validate(rel:str):
        if rel in visited:return
        visited.add(rel);source=ROOT/rel;obj=build/Path(rel).with_suffix('.olean')
        record=ROOT/f'results/{VERSION}/clean_{source.stem}.json'
        if not source.is_file() or not obj.is_file() or not record.is_file():
            raise ValueError('build current source first: '+rel)
        r=json.loads(record.read_text())
        imports=re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',source.read_text(),re.M)
        hashes={}
        for module in imports:
            dep=module.replace('.','/')+'.lean';validate(dep)
            hashes[module]=digest(build/Path(dep).with_suffix('.olean'))
        if (r.get('returncode')!=0 or r.get('timed_out') or not r.get('source_unchanged')
            or not r.get('imports_unchanged') or r.get('source_sha256')!=digest(source)
            or r.get('output_sha256')!=digest(obj) or r.get('import_outputs')!=hashes):
            raise ValueError('stale source/import/output record: '+rel)
    validate(entry)
    paths=[build]+[d/'.lake/build/lib/lean' for d in (kit/'workspace/.lake/packages').iterdir() if d.is_dir()]
    env=os.environ.copy();env['LEAN_PATH']=':'.join(map(str,paths));env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
    return lean,env

def invoke(request:Any,*,batch:bool=False,timeout:float=60,records:list|None=None)->Any:
    if not 0<timeout<=120: raise ValueError('timeout must be in (0,120]')
    lean,env=runtime(ENTRY);payload=(json.dumps(request,separators=(',',':'))+'\n').encode()
    if len(payload)>LIMIT:raise ValueError('request byte cap')
    with tempfile.TemporaryDirectory(prefix='avoc_adaptive_probe_') as td:
        path=Path(td)/'request.json';path.write_bytes(payload)
        cmd=[str(lean),'-j1','--run',str(ROOT/ENTRY)]
        if batch:cmd.append('--batch')
        cmd.append(str(path));start=time.monotonic()
        cp=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True,timeout=timeout)
    if records is not None:records.append({'argv':cmd,'returncode':cp.returncode,
      'seconds':round(time.monotonic()-start,6),'request_sha256':hashlib.sha256(payload).hexdigest(),
      'stdout_sha256':hashlib.sha256(cp.stdout.encode()).hexdigest(),'stderr':cp.stderr})
    if cp.returncode not in (0,2):raise RuntimeError('Lean execution failure: '+cp.stderr[-3000:])
    if batch:
        values=[decode(x) for x in cp.stdout.splitlines() if x.strip()]
        if len(values)!=len(request):raise RuntimeError('wrong response count')
        return values
    result=decode(cp.stdout)
    if cp.returncode and result.get('status')!='error':raise RuntimeError('unexpected Lean return status')
    return result

def read_request(path:Path)->Any:
    if path.is_symlink() or not path.is_file() or path.stat().st_size>LIMIT:
        raise ValueError('expected regular nonsymlink input within byte cap')
    return decode(path.read_text())

def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('request',type=Path)
    p.add_argument('--timeout',type=float,default=60);a=p.parse_args()
    try:
        out=invoke(read_request(a.request),timeout=a.timeout)
        print(json.dumps(out,indent=2));return 2 if out.get('status')=='error' else 0
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as e:
        print(json.dumps({'status':'error','error':str(e)}));return 2
if __name__=='__main__':raise SystemExit(main())
