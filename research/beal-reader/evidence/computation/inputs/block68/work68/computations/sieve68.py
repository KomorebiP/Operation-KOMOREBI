#!/usr/bin/env python3
"""Complete F7 affine sieve for all 28 declared conductor primes.
Uses frozen actual common-polynomial lists. Every new conductor column is included.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,time
from pathlib import Path

def need(x,msg):
    if not x:raise ValueError(msg)
def product(kr,v,r,b,factor):
    b=b*factor%7
    return b*(kr[1]*r+kr[2])%7+7*(b*kr[0]*v%7)
def values_allowed(d,ell,v,r):
    if ell in (71,29):return [0]
    factor=2 if ell==43 else 1
    out=[]
    for b in range(7):
        pp=[product(kr,v,r,b,factor) for kr in d['kummer_rows'][str(ell)]]
        good=any(all(z in pair for z in pp) for pair in d['paired_trace_sets'][str(ell)])
        bad=not any(pp)
        if good or bad:out.append(b)
    return out

def append_eq(state,row,rhs):
    a=list(row)
    for p,b,c in state:
        t=a[p]
        if t:
            a=[(x-t*y)%7 for x,y in zip(a,b)];rhs=(rhs-t*c)%7
    p=next((i for i,x in enumerate(a) if x),None)
    if p is None:return state if rhs==0 else None
    t=pow(a[p],-1,7);a=tuple(x*t%7 for x in a);rhs=rhs*t%7
    return state+((p,a,rhs),)

def solutions(state,n):
    piv={p for p,_,_ in state};free=[j for j in range(n) if j not in piv]
    for ff in itertools.product(range(7),repeat=len(free)):
        x=[0]*n
        for i,z in zip(free,ff):x[i]=z
        for p,a,b in reversed(state):x[p]=(b-sum(y*z for y,z in zip(a,x)))%7
        if any(x):yield x

def solve(universe,cols,d):
    answers=[];stages=[]
    for r in range(1,7):
        cc=[q for q in universe if cols[q]['ratio'] in (r,'all')]
        order=[ell for ell in d['test_order'] if ell not in cc]
        rr={ell:tuple(cols[q]['rows'][str(ell)] for q in cc) for ell in order}
        records=[]
        for v in range(1,7):
            states=[()];ns=[]
            for ell in order:
                allowed=values_allowed(d,ell,v,r)
                states=[out for st in states for b in allowed if (out:=append_eq(st,rr[ell],b)) is not None]
                count=sum(7**(len(cc)-len(st))-int(all(b==0 for p,a,b in st)) for st in states)
                ns.append(count)
            for st in states:
                for x in solutions(st,len(cc)):
                    answers.append({'alpha':[7*v,r,1],'columns':cc,'inertia':x,'values':{str(ell):sum(y*z for y,z in zip(rr[ell],x))%7 for ell in order}})
            records.append({'v':v,'counts':ns})
        stages.append({'ratio':r,'columns':cc,'tests':order,'records':records})
        print('ratio',r,'columns',len(cc),'survivors',sum(t['counts'][-1] for t in records),flush=True)
    canon=lambda z:json.dumps(z,sort_keys=True,separators=(',',':'))
    answers.sort(key=canon);need(len({canon(x) for x in answers})==len(answers),'Duplicate candidate')
    escape=[q for q in universe if answers and all(any(qq==q and x for qq,x in zip(s['columns'],s['inertia'])) for s in answers)]
    return {'universe':universe,'stages':stages,'count':len(answers),'survivors':answers,'mandatory_support_in_survivors':escape,'survivor_sha256':hashlib.sha256(('\n'.join(canon(s) for s in answers)+'\n').encode()).hexdigest()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fixture',type=Path,required=True);ap.add_argument('--columns',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    d=json.loads(a.fixture.read_text());c=json.loads(a.columns.read_text());need(c['status']=='PASS_EXACT_COLUMNS','Bad columns')
    cc={z['q']:z for z in c['columns']}
    baseline=solve(d['inherited_universe'],cc,d);need(baseline['count']==0,'Frozen 25-prime exclusion failed to reproduce')
    expanded=solve(c['universe'],cc,d)
    out={'schema':'beal.block68.sieve.v1','status':'PASS_FINITE_SIEVE','fixture_sha256':hashlib.sha256(a.fixture.read_bytes()).hexdigest(),'columns_sha256':hashlib.sha256(a.columns.read_bytes()).hexdigest(),'baseline25':baseline,'expanded28':expanded,'nonclaims':['Survivors are necessary-system tuples, not global representations','Only depth one finite correction lists','When test43 is an allowed conductor prime its unramified test is omitted','All additional divisors unramified in beta are allowed']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print(out['status'],'baseline',baseline['count'],'expanded',expanded['count'],flush=True)
if __name__=='__main__':main()
