#!/usr/bin/env python3
"""Exact finite cross-checks of the v0.8 cascade formulas.

No floating-point tolerances. These bounded tests do not establish any infinite
limit theorem; those are separately proved in the Lean modules. Three mutations
must be rejected. Run with --output PATH to record auditable results.
"""
from __future__ import annotations
import argparse
import datetime as dt
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import random
import sys
import time

SEED = 80820260927
checks = 0
rng = random.Random(SEED)

def check(ok: bool, label: str) -> None:
    global checks
    checks += 1
    if not ok:
        raise AssertionError(label)

def eye(n: int):
    return [[Q(int(i == j)) for j in range(n)] for i in range(n)]

def mm(a, b):
    return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*b)] for row in a]

def mv(a, v):
    return [sum((x*y for x,y in zip(row,v)),Q(0)) for row in a]

def sub(a,b):
    return [[x-y for x,y in zip(ar,br)] for ar,br in zip(a,b)]

def vadd(a,b):
    return [x+y for x,y in zip(a,b)]

def vsub(a,b):
    return [x-y for x,y in zip(a,b)]

def vn(v):
    return max(map(abs,v),default=Q(0))

def mn(a):
    return max((sum(map(abs,row),Q(0)) for row in a),default=Q(0))

def random_matrix(n,m):
    return [[Q(rng.randrange(-2,3),4) for _ in range(m)] for _ in range(n)]

def vector(n):
    return [Q(rng.randrange(-5,6),3) for _ in range(n)]

def variable_cascades():
    cases=0
    for depth in range(1,7):
        for variant in range(6):
            dim=2*depth+2
            cs=[];js=[]
            for j in range(depth):
                n=dim-2*j; k=n-2
                m=random_matrix(k,2); b=random_matrix(2,k)
                c=[eye(k)[i]+m[i] for i in range(k)]
                lift=sub(eye(k),mm(m,b))+b
                check(mm(c,lift)==eye(k),'finite section identity')
                cs.append(c);js.append(lift)
            levels=[vector(dim)]; restores=[eye(dim)]; observes=[eye(dim)]
            qs=[eye(dim)]; details=[]; terms=[]; gain=Q(1)
            partial=[Q(0)]*dim
            for n in range(depth):
                levels.append(mv(cs[n],levels[-1]))
                h=vsub(levels[n],mv(js[n],levels[n+1]))
                details.append(h); terms.append(mv(restores[n],h))
                partial=vadd(partial,terms[-1])
                restores.append(mm(restores[n],js[n]))
                observes.append(mm(cs[n],observes[n]))
                qs.append(mm(restores[-1],observes[-1]))
                gain*=mn(js[n])
                check(mm(observes[-1],restores[-1])==eye(len(levels[-1])),
                      'coarse observation after restoration')
                rem=mv(qs[-1],levels[0])
                check(vadd(partial,rem)==levels[0],'finite reconstruction')
                check(vn(rem)<=gain*vn(levels[-1]),'restoration gain error bound')
                check(mm(qs[-1],qs[-1])==qs[-1],'remainder idempotence')
                check(mv(qs[-1],partial)==[Q(0)]*dim,'partial lies in finite core')
            for m in range(depth+1):
                for n in range(m,depth+1):
                    check(mm(qs[m],qs[n])==qs[n],'nested remainders left')
                    check(mm(qs[n],qs[m])==qs[n],'nested remainders right')
            boundary=mv(restores[-1],[Q(1),Q(-1)])
            check(boundary!=[Q(0)]*dim,'terminal persistent boundary nonzero')
            for n in range(depth):
                x=mv(observes[n],boundary)
                y=mv(observes[n+1],boundary)
                check(vsub(x,mv(js[n],y))==[Q(0)]*len(x),
                      'all measured details can vanish with terminal boundary')
            cases+=1
    return cases

def down_pair(v):
    return [v[2*n]+v[2*n+1] for n in range(len(v)//2)]

def up_pair(v):
    return [x for q in v for x in (Q(0),q)]

def up_repeated(v,n):
    for _ in range(n):v=up_pair(v)
    return v

def dyadic_cascades():
    cases=0
    for depth in range(1,9):
        length=2**depth
        for variant in range(6):
            root=vector(length)
            if variant==0:root=[Q(1)]*length
            if variant==1:root=[Q(1 if k%2==0 else -1) for k in range(length)]
            partial=[Q(0)]*length; current=root[:]
            for n in range(depth+1):
                rem=up_repeated(current,n)
                # Independent closed formula: block sum at each block's last coordinate.
                width=2**n
                closed=[Q(0)]*length
                for end in range(width-1,length,width):
                    closed[end]=sum(root[end-width+1:end+1],Q(0))
                check(rem==closed,'dyadic closed remainder formula')
                check(vadd(partial,rem)==root,'dyadic reconstruction')
                for k in range(min(width-1,length)):
                    check(partial[k]==root[k],'finite-depth coordinate exactness')
                if n<depth:
                    coarse=down_pair(current)
                    h=vsub(current,up_pair(coarse))
                    partial=vadd(partial,up_repeated(h,n))
                    current=coarse
            cases+=1
    return cases

def sequence_examples():
    cases=0
    for q in [Q(0),Q(1,4),Q(1,2),Q(3,4),Q(7,8)]:
        for n in range(33):
            values=[q**k for k in range(n+17)]
            reconstructed=[values[k] if k<n else Q(0) for k in range(len(values))]
            check(vn(vsub(values,reconstructed))==q**n,'geometric exact tail error')
            check(vn(values[n:])==q**n,'geometric tail norm witness')
            cases+=1
    for n in range(65):
        coarse=Q(1,2)**n; gain=Q(2)**n
        check(gain*coarse==1,'scalar restored coarse remains one')
        check(coarse>0,'nonzero finite coarse datum')
        if n:check(coarse<Q(1,2)**(n-1),'strictly decreasing raw coarse')
        cases+=1
    return cases

def negative_controls():
    controls=[]
    # Claim mutation: dropping the last coarse datum preserves reconstruction.
    root=[Q(1)]*8
    check(up_repeated([sum(root)],3)!=[Q(0)]*8,'terminal remainder witness')
    controls.append({'mutation':'omit_final_coarse_term',
                     'rejected':vsub(root,up_repeated([sum(root)],3))!=root})
    # Claim mutation: use raw coarse size as the reconstructed error without lift gain.
    controls.append({'mutation':'omit_restoration_gain',
                     'rejected':Q(2)**12*Q(1,2)**12 > Q(1,2)**12})
    # Claim mutation: replace k+1 < 2^N with k+1 <= 2^N.
    n=4;k=2**n-1;v=[Q(0)]*2**n;v[k]=Q(1)
    rem=up_repeated([Q(1)],n);partial=vsub(v,rem)
    controls.append({'mutation':'coordinate_bound_nonstrict',
                     'rejected':k+1==2**n and partial[k]!=v[k]})
    for c in controls:check(c['rejected'],'negative control '+c['mutation'])
    return controls

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(); start=time.monotonic(); started=dt.datetime.now(dt.timezone.utc).isoformat()
    source=Path(__file__).resolve()
    before=hashlib.sha256(source.read_bytes()).hexdigest()
    try:
        counts={'variable_dimension_cascades':variable_cascades(),
                'dyadic_configurations':dyadic_cascades(),
                'sequence_and_scalar_cases':sequence_examples()}
        controls=negative_controls(); status='PASS'; error=None
    except Exception as exc:
        counts={};controls=[];status='FAIL';error=repr(exc)
    after=hashlib.sha256(source.read_bytes()).hexdigest()
    if before!=after:status='FAIL';error='script changed during execution'
    report={'status':status,'started_at_utc':started,'elapsed_seconds':time.monotonic()-start,
       'argv':sys.argv,'python_version':platform.python_version(),'coefficient_domain':'rational numbers, fractions.Fraction',
       'conventions':'column-vector action; induced infinity matrix norm; causal remainder Q_N=L_N C_(N-1)...C_0; strict dyadic coordinate bound',
       'counts':counts,'positive_assertions':checks,'negative_controls':controls,
       'randomness':{'generator':'random.Random (MT19937)','seed':SEED},
       'ranges':{'cascade_depth':[1,6],'cascade_variants':6,'dimension_rule':'2*depth+2, dropping two per level',
         'dyadic_depth':[1,8],'dyadic_variants':6,'geometric_q':['0','1/4','1/2','3/4','7/8'],
         'geometric_depth':[0,32],'scalar_depth':[0,64]},
       'non_claims':['Finite testing does not prove infinite convergence, density, or completeness.',
          'Norm convergence of every dyadic bounded residual is not asserted.',
          'No floating-point tolerance is used; no complexity or novelty claim.'],
       'script_sha256_before':before,'script_sha256_after':after,'error':error}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','counts','positive_assertions','negative_controls','elapsed_seconds')},indent=2))
    return 0 if status=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
