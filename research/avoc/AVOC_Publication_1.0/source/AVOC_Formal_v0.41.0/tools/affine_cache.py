#!/usr/bin/env python3
"""Checked affine-certificate reuse and guarded exploration, over GF(5).

The Lean entrypoint performs all semantic checks, lower-bound preflight and plan
selection. Python provides a tested untrusted factor proposer and a protected,
single-writer, snapshot store. No cached success bit substitutes for revalidation.
Nominal tariffs are not physical timings or an authenticated payment ledger.
"""
from __future__ import annotations
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable

import factor_affine as proposer

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'avoc-affine-cache-f5-dense-v1'
FORMAT = {'schema': SCHEMA, 'field': 5, 'key': 'input/output dimensions and exact linear coefficients',
          'offset_policy': 'revalidate old certificate, then algebraically retarget the offset',
          'cost': 'dense-ring-arithmetic-tariff-v1'}
ENTRYPOINT = 'tools/AffineReuseMain.lean'
SOURCE_NAMES = ['AVOC/AffineSignature.lean','AVOC/TypedAffineProgram.lean','AVOC/AffineFusion.lean',
 'AVOC/AffineCodec.lean','AVOC/AffineFactorization.lean','AVOC/AffineFactorChoice.lean',
 'AVOC/AffineFactorCodec.lean','AVOC/AffineReuse.lean','AVOC/AffineSearchGuard.lean',
 'AVOC/AffineReuseCodec.lean',ENTRYPOINT]
LIMIT = 4 * 1024 * 1024


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)+'\n').encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(text: str) -> Any:
    return json.loads(text, parse_float=proposer.reject_float, parse_constant=proposer.reject_float,
                      object_pairs_hook=proposer.unique_object)


def read_json(path: Path) -> Any:
    if path.is_symlink() or not path.is_file(): raise ValueError('expected a regular nonsymlink file')
    if path.stat().st_size > LIMIT: raise ValueError('file size cap')
    return decode(path.read_text(encoding='utf-8'))


def runtime() -> tuple[Path, dict[str,str]]:
    lean, env = proposer.environment(check_records=False)
    out = ROOT/'.lake/build/lib/lean'
    for rel in SOURCE_NAMES:
        p=ROOT/rel; obj=out/Path(rel).with_suffix('.olean')
        rp=ROOT/'results/v0.30.0'/('clean_'+p.stem+'.json')
        if not rp.is_file() or not obj.is_file(): raise ValueError('build new checker first: '+rel)
        r=json.loads(rp.read_text())
        imports={name: sha(out/Path(name.replace('.','/')).with_suffix('.olean'))
                 for name in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',p.read_text(),re.M)}
        if (r.get('returncode')!=0 or r.get('timed_out') or not r.get('source_unchanged')
            or not r.get('imports_unchanged') or r.get('source_sha256')!=sha(p)
            or r.get('output_sha256')!=sha(obj) or r.get('import_outputs')!=imports):
            raise ValueError('stale checker compilation: '+rel)
    return lean,env


def fingerprint() -> str:
    # Source descriptor plus already-checked object hashes. Not remote attestation.
    data={name:sha(ROOT/name) for name in SOURCE_NAMES}
    return hashlib.sha256(canonical(data)).hexdigest()


def invoke(request: Any, timeout: float=45, records: list|None=None, batch: bool=False) -> Any:
    lean,env=runtime()
    if not 0 < timeout <= 120: raise ValueError('timeout must be in (0,120]')
    payload=canonical(request)
    if len(payload)>LIMIT: raise ValueError('request size cap')
    with tempfile.TemporaryDirectory(prefix='avoc_affine_cache_') as td:
        path=Path(td)/'request.json';path.write_bytes(payload)
        cmd=[str(lean),'-j1','--run',str(ROOT/ENTRYPOINT)]
        if batch:cmd.append('--batch')
        cmd.append(str(path)); started=time.monotonic()
        cp=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=timeout)
    if records is not None:
        records.append({'argv':cmd,'returncode':cp.returncode,
          'seconds':round(time.monotonic()-started,6),
          'request_sha256':hashlib.sha256(payload).hexdigest(),
          'stdout_sha256':hashlib.sha256(cp.stdout.encode()).hexdigest(),
          'stderr':cp.stderr[-2000:]})
    if cp.returncode not in (0,2):raise RuntimeError('Lean process failed: '+cp.stderr[-3000:])
    if batch:
        values=[decode(x) for x in cp.stdout.splitlines() if x.strip()]
        if len(values)!=len(request):raise RuntimeError('batch response count mismatch')
        return values
    try:result=decode(cp.stdout)
    except (ValueError,TypeError) as exc:raise RuntimeError('malformed checker reply') from exc
    if cp.returncode and result.get('status')!='error':raise RuntimeError('unexpected checker exit')
    return result


def key_of(normal: dict) -> str:
    return hashlib.sha256(canonical([SCHEMA,normal['input_dim'],normal['output_dim'],normal['matrix']])).hexdigest()


def validate_config(cfg: Any) -> None:
    if not isinstance(cfg,dict) or set(cfg)-{'program','calls','credit','inputs'}:
        raise ValueError('unknown configuration fields')
    n,_,_,_=proposer.shape(cfg.get('program'))
    proposer.integer(cfg.get('calls',1),1000000,'calls')
    proposer.integer(cfg.get('credit',100000),100000000,'credit')
    xs=cfg.get('inputs',[])
    if not isinstance(xs,list) or len(xs)>128:raise ValueError('input batch cap')
    for x in xs:proposer.vector_shape(x,n)


def record_normal(record: list) -> dict:
    if not isinstance(record,list) or len(record)!=6 or record[0]!=SCHEMA:
        raise ValueError('certificate schema mismatch')
    n=proposer.integer(record[1],8,'input dimension');m=proposer.integer(record[2],8,'output dimension')
    proposer.matrix_shape(record[3],m,n);proposer.vector_shape(record[4],m)
    return dict(input_dim=n,output_dim=m,matrix=record[3],offset=record[4])


def envelope(record: list) -> dict:
    return {'schema':SCHEMA,'checker_fingerprint':fingerprint(),'record':record}


def load_entry(path: Path, expected_key: str|None=None) -> list:
    e=read_json(path)
    if not isinstance(e,dict) or set(e)!={'schema','checker_fingerprint','record'}:
        raise ValueError('malformed certificate envelope')
    if e['schema']!=SCHEMA or e['checker_fingerprint']!=fingerprint():
        raise ValueError('cache descriptor/source mismatch')
    rec=e['record'];normal=record_normal(rec)
    if expected_key is not None and key_of(normal)!=expected_key:
        raise ValueError('exact linear cache key mismatch')
    return rec


def lookup(store: Path, key: str) -> Path|None:
    if not store.exists():return None
    if store.is_symlink() or not store.is_dir():raise ValueError('invalid protected store')
    if read_json(store/'format.json')!=FORMAT:raise ValueError('store format mismatch')
    leaf=store/(key+'.json')
    if leaf.is_symlink():raise ValueError('certificate symlink rejected')
    return leaf if leaf.exists() else None


def write_exclusive(path: Path, data: bytes) -> None:
    # Single-writer protected store; link publishes without overwriting an existing key.
    fd,tmp=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.link(tmp,path)
        d=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(d)
        finally:os.close(d)
    finally:
        Path(tmp).unlink(missing_ok=True)


def publish(store: Path, key: str, record: list, hook: Callable|None=None) -> Path:
    if store.is_symlink():raise ValueError('store symlink rejected')
    store.mkdir(parents=True,exist_ok=True)
    lock=store/'LOCK'
    if lock.is_symlink():raise ValueError('lock symlink rejected')
    with lock.open('a+b') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        meta=store/'format.json'
        if meta.exists():
            if read_json(meta)!=FORMAT:raise ValueError('store format mismatch')
        else:write_exclusive(meta,canonical(FORMAT))
        target=store/(key+'.json')
        if target.exists() or target.is_symlink():raise FileExistsError('refusing to overwrite certificate')
        if hook:hook('before_certificate_publication',store,target)
        write_exclusive(target,canonical(envelope(record)))
        return target


def fallback(pre: dict, status: str, **extra: Any) -> dict:
    r=dict(pre);r.update(status=status,certificate_executed=False,generator_executed=False,**extra)
    r['baseline_deployment']=r.get('calls',0)*r.get('per_call_original',0)
    r['campaign_total']=r.get('spent',0)+r.get('calls',0)*r.get('per_call_selected',0)
    r['net_gain']=r['baseline_deployment']-r['campaign_total']
    r['breaks_even']=r['net_gain']>=0
    return r


def run(cfg: dict, store: Path|None=None, timeout: float=45,
        hook: Callable|None=None) -> dict:
    validate_config(cfg)
    p=cfg['program'];calls=cfg.get('calls',1);credit=cfg.get('credit',100000);logs=[]
    pre=invoke(['affine-preflight-f5-v1',p,calls,credit],timeout,logs)
    if pre.get('status')=='error':raise ValueError(pre['error'])
    if pre['status']!='preflight':
        ans=fallback(pre,pre['status']);ans['invocations']=logs;return ans
    normal=pre['normal'];key=key_of(normal);leaf=lookup(store,key) if store is not None else None
    use_cache=leaf is not None
    may=pre['cache_may_pay'] if use_cache else pre['search_may_pay']
    if not may:
        ans=fallback(pre,'skip_cache_bound' if use_cache else 'skip_search_bound',cache_hit=use_cache)
        ans['invocations']=logs;return ans
    paid=pre['spent'];gen_record=None;raw_record=None
    if use_cache:
        raw_record=load_entry(leaf,key)
    else:
        floor=pre['minimum_cold_remaining_charge']
        if floor>credit-paid:
            ans=fallback(pre,'unfunded_search_floor',cache_hit=False);ans['invocations']=logs;return ans
        reserve=pre['minimum_warm_remaining_charge']
        meter=proposer.Meter(credit-paid-reserve)
        try:
            # Canonical coefficients come from Lean preflight, not a second Python normalizer.
            if hook:hook('before_generate',None,None)
            c=proposer.certificate(normal['input_dim'],normal['output_dim'],normal['matrix'],normal['offset'],meter)
        except proposer.CreditExhausted:
            ans=fallback(pre,'generation_budget_exhausted',cache_hit=False)
            ans.update(spent=paid+meter.spent,remaining=credit-paid-meter.spent,generator_executed=True,
                       generation_charge=meter.spent,generation_events=meter.events)
            ans['campaign_total']=ans['spent']+calls*ans['per_call_selected']
            ans['net_gain']=ans['baseline_deployment']-ans['campaign_total']
            ans['breaks_even']=ans['net_gain']>=0;ans['invocations']=logs;return ans
        paid+=meter.spent
        raw_record=[SCHEMA,normal['input_dim'],normal['output_dim'],normal['matrix'],normal['offset'],c]
        gen_record={'charge':meter.spent,'events':meter.events}
    result=invoke(['affine-reuse-f5-v1',p,raw_record,calls,paid,credit,cfg.get('inputs',[])],timeout,logs)
    result.update(cache_hit=use_cache,preflight=pre,generator_executed=not use_cache,
                  generation_charge=0 if use_cache else gen_record['charge'],
                  generation_events={} if use_cache else gen_record['events'],semantic_key=key,invocations=logs)
    if result.get('status')=='certified_reuse':
        result['route']='warm_revalidation' if use_cache else 'cold_generation_and_validation'
        if not use_cache and store is not None:
            result['saved_certificate']=str(publish(store,key,raw_record,hook))
        elif use_cache:result['saved_certificate']=str(leaf)
    return result


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    r=sub.add_parser('run');r.add_argument('config',type=Path);r.add_argument('--store',type=Path)
    r.add_argument('--timeout',type=float,default=45)
    v=sub.add_parser('validate');v.add_argument('certificate',type=Path);v.add_argument('--credit',type=int,default=100000)
    v.add_argument('--timeout',type=float,default=45)
    a=p.parse_args()
    try:
        runtime()
        if a.action=='run':result=run(read_json(a.config),a.store,a.timeout)
        else:
            rec=load_entry(a.certificate);n=record_normal(rec)
            source=['map',n['input_dim'],n['output_dim'],n['matrix'],n['offset']]
            result=invoke(['affine-reuse-f5-v1',source,rec,0,0,a.credit,[]],a.timeout)
        print(json.dumps(result,indent=2))
        return 2 if result.get('status') in ('error','rejected_cache_certificate') else 0
    except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as exc:
        print(json.dumps({'status':'error','error':str(exc)}));return 2

if __name__=='__main__':raise SystemExit(main())
