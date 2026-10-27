#!/usr/bin/env python3
"""Generate GF(5) rank-factorization witnesses, then run the proved Lean checker.

Read-only. The Gaussian-elimination proposer is not assumed correct by Lean:
all accepted factors and rank lower witnesses are independently rechecked.
The operation meter is a declared nominal tariff, not wall-clock accounting.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODULUS = 5
CAP = 8
SOURCES = ['AVOC/AffineSignature.lean', 'AVOC/TypedAffineProgram.lean',
           'AVOC/AffineFusion.lean','AVOC/AffineCodec.lean',
           'AVOC/AffineFactorization.lean','AVOC/AffineFactorChoice.lean',
           'AVOC/AffineFactorCodec.lean','tools/AffineFactorMain.lean']

class CreditExhausted(RuntimeError):
    pass

@dataclass
class Meter:
    limit: int
    spent: int = 0
    events: dict[str, int] = field(default_factory=dict)

    def charge(self, name: str, amount: int = 1) -> None:
        if amount < 0 or self.spent + amount > self.limit:
            raise CreditExhausted('generation would exceed its remaining credit')
        self.spent += amount
        self.events[name] = self.events.get(name, 0) + amount

def integer(v: Any, cap: int, name: str) -> int:
    if type(v) is not int or not 0 <= v <= cap:
        raise ValueError(f'{name}: expected an integer in [0,{cap}]')
    return v

def matrix_shape(x: Any, rows: int, cols: int) -> None:
    if not isinstance(x,list) or len(x) != rows:
        raise ValueError('matrix row mismatch')
    for row in x:
        if not isinstance(row,list) or len(row) != cols:
            raise ValueError('matrix column mismatch')
        for a in row: integer(a,4,'coefficient')

def vector_shape(x: Any, n: int) -> None:
    if not isinstance(x,list) or len(x) != n: raise ValueError('vector shape mismatch')
    for a in x: integer(a,4,'coefficient')

def shape(p: Any, depth: int = 0) -> tuple[int,int,int,int]:
    """Return dimensions, syntactic node count, and normalization arithmetic tariff."""
    if depth >= 24 or not isinstance(p,list) or not p or not isinstance(p[0],str):
        raise ValueError('malformed/deep program')
    if p[0]=='map' and len(p)==5:
        n=integer(p[1],CAP,'input dimension');m=integer(p[2],CAP,'output dimension')
        matrix_shape(p[3],m,n);vector_shape(p[4],m);return n,m,1,0
    if p[0]=='id' and len(p)==2:
        n=integer(p[1],CAP,'identity dimension');return n,n,1,0
    if p[0] in ('seq','sum') and len(p)==3:
        n,k,a,ca=shape(p[1],depth+1);j,m,b,cb=shape(p[2],depth+1)
        if a+b+1>256:raise ValueError('node cap')
        if p[0]=='seq':
            if k!=j:raise ValueError('composition shape mismatch')
            return n,m,a+b+1,ca+cb+2*m*n*k+m*(2*k+1)
        if (n,k)!=(j,m):raise ValueError('sum shape mismatch')
        return n,m,a+b+1,ca+cb+m*(n+1)
    raise ValueError('unknown or malformed constructor')

def matmul(a: list[list[int]], b: list[list[int]], rows: int, mid: int, cols: int) -> list[list[int]]:
    return [[sum(a[i][k]*b[k][j] for k in range(mid))%5 for j in range(cols)] for i in range(rows)]

def normal(p: list) -> tuple[int,int,list[list[int]],list[int]]:
    """Proposer-only normalizer. Lean independently normalizes the original AST."""
    tag=p[0]
    if tag=='map':return p[1],p[2],[r[:] for r in p[3]],p[4][:]
    if tag=='id':
        n=p[1];return n,n,[[int(i==j) for j in range(n)] for i in range(n)],[0]*n
    n,k,a,b=normal(p[1]);j,m,c,d=normal(p[2])
    if tag=='seq':
        return n,m,matmul(c,a,m,k,n),[(sum(c[i][l]*b[l] for l in range(k))+d[i])%5 for i in range(m)]
    return n,m,[[(a[i][j]+c[i][j])%5 for j in range(n)] for i in range(m)],[(b[i]+d[i])%5 for i in range(m)]

def certificate(n: int,m: int,a: list[list[int]],b: list[int],meter: Meter) -> list:
    """RREF with tracked row operations; emits A=C D and U A V = I witnesses.
    No returned 'rank' is trusted until the Lean certificate is accepted.
    """
    work=[a[i][:]+[int(i==j) for j in range(m)] for i in range(m)]
    pivots=[];r=0
    for col in range(n):
        pivot=None
        for row in range(r,m):
            meter.charge('pivot_tests')
            if work[row][col] !=0:pivot=row;break
        if pivot is None:continue
        if pivot!=r:
            meter.charge('row_swap_entries',n+m)
            work[r],work[pivot]=work[pivot],work[r]
        meter.charge('field_inversions')
        inv=pow(work[r][col],-1,5)
        for j in range(n+m):
            meter.charge('field_multiplications');work[r][j]=work[r][j]*inv%5
        for i in range(m):
            if i==r:continue
            meter.charge('elimination_tests')
            scale=work[i][col]
            if scale:
                for j in range(n+m):
                    meter.charge('field_multiplications');prod=scale*work[r][j]%5
                    meter.charge('field_additions');work[i][j]=(work[i][j]-prod)%5
        pivots.append(col);r+=1
        if r==m:break
    # Emitting factors and witnesses incurs an entry tariff (including the biases).
    meter.charge('emitted_coefficients',r*n+r+m*r+m+r*m+n*r)
    d=[work[i][:n] for i in range(r)]
    c=[[a[i][col] for col in pivots] for i in range(m)]
    u=[work[i][n:] for i in range(r)]
    v=[[int(i==col) for col in pivots] for i in range(n)]
    return [r,d,[0]*r,c,b[:],u,v]

def prepare(config: dict[str, Any]) -> tuple[list | None,dict]:
    if not isinstance(config,dict) or set(config)-{'program','calls','credit','inputs'}:
        raise ValueError('unknown configuration fields')
    p=config.get('program');n,m,_,norm=shape(p)
    calls=integer(config.get('calls',1),1000000,'calls')
    budget=integer(config.get('credit',100000),100000000,'credit')
    inputs=config.get('inputs',[])
    if not isinstance(inputs,list) or len(inputs)>128:raise ValueError('input vector cap')
    for x in inputs:vector_shape(x,n)
    # Reserve the later checker's reference normalization separately. The Python
    # normalizer also pays the same dense arithmetic tariff before running.
    if norm>budget:
        return None,dict(status='unfunded_normalization',spent=0,remaining=budget,selected=p)
    meter=Meter(budget-norm)
    try:
        meter.charge('python_normalization',norm)
        _,_,a,b=normal(p)
        c=certificate(n,m,a,b,meter)
    except CreditExhausted:
        return None,dict(status='generation_budget_exhausted',spent=meter.spent,
                         remaining=budget-meter.spent,selected=p,meter=meter.events)
    request=['affine-factor-f5-v1',p,c,calls,meter.spent,budget,inputs]
    return request,dict(generator='tracked-rref-f5-v1',events=meter.events,spent=meter.spent)

def environment(check_records: bool = True) -> tuple[Path,dict[str,str]]:
    kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'))
    lean=kit/'toolchain/bin/lean';out=ROOT/'.lake/build/lib/lean'
    if not lean.is_file():raise FileNotFoundError('Set AVOC_LEAN_KIT to the pinned runtime')
    if check_records:
        for rel in SOURCES:
            source=ROOT/rel;obj=out/Path(rel).with_suffix('.olean')
            hashes={name:hashlib.sha256((out/Path(name.replace('.','/')).with_suffix('.olean')).read_bytes()).hexdigest()
                    for name in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',source.read_text(),re.M)}
            ok=False
            for prefix in ['clean_','']:
                rec=ROOT/'results/v0.29.0'/f'{prefix}{source.stem}.json'
                if not rec.exists() or not obj.exists():continue
                r=json.loads(rec.read_text())
                ok=ok or (r.get('returncode')==0 and not r.get('timed_out') and r.get('source_unchanged')
                     and r.get('imports_unchanged') and r.get('import_outputs')==hashes
                     and r.get('source_sha256')==hashlib.sha256(source.read_bytes()).hexdigest()
                     and r.get('output_sha256')==hashlib.sha256(obj.read_bytes()).hexdigest())
            if not ok:raise ValueError(f'Missing/stale compilation record: {rel}')
    paths=[out]+[d/'.lake/build/lib/lean' for d in (kit/'workspace/.lake/packages').iterdir() if d.is_dir()]
    env=os.environ.copy();env['LEAN_PATH']=':'.join(map(str,paths));env['PATH']=str(lean.parent)+':'+env.get('PATH','')
    return lean,env

def reject_float(x: str):raise ValueError('only exact JSON integers are accepted')
def unique_object(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise ValueError('duplicate JSON key')
        result[k]=v
    return result

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('config',type=Path)
    ap.add_argument('--timeout',type=float,default=45);ap.add_argument('--certificate-out',type=Path)
    args=ap.parse_args()
    try:
        if not 0<args.timeout<=120:raise ValueError('timeout must be in (0,120]')
        if args.config.stat().st_size>4*1024*1024:raise ValueError('input byte cap')
        cfg=json.loads(args.config.read_text(encoding='utf-8'),parse_float=reject_float,
                       parse_constant=reject_float,object_pairs_hook=unique_object)
        t=time.monotonic();req,record=prepare(cfg)
        if req is None:print(json.dumps(record));return 0
        # Temporary request is not a durable admission or deployment record.
        import tempfile
        lean,env=environment()
        with tempfile.TemporaryDirectory(prefix='avoc_factor_') as td:
            path=Path(td)/'request.json';path.write_text(json.dumps(req))
            proc=subprocess.run([str(lean),'--run',str(ROOT/'tools/AffineFactorMain.lean'),str(path)],
                                cwd=ROOT,env=env,capture_output=True,text=True,timeout=args.timeout)
        if proc.returncode:raise RuntimeError(proc.stderr+proc.stdout)
        result=json.loads(proc.stdout);result['generator_record']=record
        result['elapsed_seconds']=round(time.monotonic()-t,6)
        if args.certificate_out:
            # Explicit opt-in file output. Never overwrite an existing certificate.
            with args.certificate_out.open('x',encoding='utf-8') as f:json.dump(req,f,indent=2);f.write('\n')
        print(json.dumps(result,indent=2));return 0
    except (OSError,ValueError,RuntimeError,RecursionError,subprocess.TimeoutExpired) as exc:
        print(f'Factorization failed: {exc}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
