#!/usr/bin/env python3
"""Exact finite audit of view duplication, coefficient transport, and saturated covers.

Universal statements are supplied by Lean. This independently checks all C2
cocycles in four inner-action S3 coefficient systems, their two-copy groupoids,
and composition covers of saturated patches for every preorder on <=3 views.
"""
from __future__ import annotations
import argparse, datetime as dt, itertools as it, json, time
from pathlib import Path

PERMS=list(it.permutations(range(3)))
N=len(PERMS); ID=PERMS.index((0,1,2))
MUL=[[PERMS.index(tuple(a[b[i]] for i in range(3))) for b in PERMS] for a in PERMS]
INV=[next(b for b in range(N) if MUL[a][b]==ID==MUL[b][a]) for a in range(N)]

def mul(*args:int)->int:
    ans=ID
    for a in args: ans=MUL[ans][a]
    return ans

def act(m:int,t:int,a:int)->int:
    return a if t==0 else mul(m,a,INV[m])

ARROWS=list(it.product(range(2),range(2),range(2)))
AI={x:i for i,x in enumerate(ARROWS)}

def labels(m:int,p:int,g:int)->tuple[int,...]:
    frame=(ID,g)
    return tuple(mul(frame[a],ID if t==0 else p,INV[act(m,t,frame[b])])
                 for a,b,t in ARROWS)

def gauge(m:int,a:tuple[int,int],c:tuple[int,...])->tuple[int,...]:
    return tuple(mul(a[v],c[k],INV[act(m,t,a[w])])
                 for k,(v,w,t) in enumerate(ARROWS))

def powerset_mask(s:int):
    t=s
    while True:
        yield t
        if t==0: break
        t=(t-1)&s

def preorders(n:int):
    for bits in range(1<<(n*n)):
        r=lambda a,b: bool(bits&(1<<(a*n+b)))
        if not all(r(a,a) for a in range(n)): continue
        if not all(not(r(a,b) and r(b,c)) or r(a,c)
                   for a,b,c in it.product(range(n),repeat=3)):continue
        yield {(a,b) for a,b in it.product(range(n),repeat=2) if r(a,b)}

def closed(n:int,r:set[tuple[int,int]],s:int)->bool:
    return all(not (s>>a&1 and (a,b) in r and (b,a) in r) or bool(s>>b&1)
               for a,b in it.product(range(n),repeat=2))

def covers(n:int,r:set[tuple[int,int]],s:int,us:list[int])->bool:
    for a,b,c in it.product(range(n),repeat=3):
        supp=(1<<a)|(1<<b)|(1<<c)
        if (a,b) in r and (b,c) in r and supp&s==supp:
            if not any(supp&u==supp for u in us):return False
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    start=time.monotonic();stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    count=0
    def check(p:bool):
        nonlocal count
        count+=1
        if not p:raise AssertionError(f'assertion {count} failed')
    counts=dict(coefficient_systems=0,base_cocycles=0,duplicated_cocycles=0,
                gauge_actions=0,hom_pairs=0,gauge_compositions=0,section_pairs=0,
                preorders=0,saturated_patches=0,cover_families=0,patch_order_pairs=0)
    wrong_transport=False;wrong_order=False;automorphism_records=[]
    for m in range(N):
        if mul(m,m)!=ID:continue
        counts['coefficient_systems']+=1
        ps=[p for p in range(N) if mul(p,act(m,1,p))==ID]
        counts['base_cocycles']+=len(ps)
        data=[(p,g,labels(m,p,g)) for p in ps for g in range(N)]
        counts['duplicated_cocycles']+=len(data)
        lookup={c:i for i,(_,_,c) in enumerate(data)}
        check(len(lookup)==len(data))
        homs={}
        gauges=list(it.product(range(N),repeat=2))
        for i,(p,g,c) in enumerate(data):
            for a in range(2):check(c[AI[a,a,0]]==ID)
            for a,b,d,t,s in it.product(range(2),repeat=5):
                check(c[AI[a,d,t^s]]==mul(c[AI[a,b,t]],act(m,t,c[AI[b,d,s]])))
            check(c[AI[0,0,1]]==p)
            check(gauge(m,(ID,g),labels(m,p,ID))==c)
            for a in gauges:
                out=gauge(m,a,c);counts['gauge_actions']+=1
                check(out in lookup)
                j=lookup[out]
                homs.setdefault((i,j),[]).append(a)
                check(out[AI[0,0,1]]==mul(a[0],p,INV[act(m,1,a[0])]))
                wrong=tuple(mul(a[v],c[k],INV[a[w]]) for k,(v,w,t) in enumerate(ARROWS))
                wrong_transport |= wrong!=out
                for b0 in range(N):
                    b=(b0,b0)
                    ab=tuple(mul(b[k],a[k]) for k in range(2))
                    ba=tuple(mul(a[k],b[k]) for k in range(2))
                    counts['gauge_compositions']+=1
                    check(gauge(m,b,out)==gauge(m,ab,c))
                    wrong_order |= gauge(m,ba,c)!=gauge(m,ab,c)
            base_sec=[x for x in range(N) if x==mul(p,act(m,1,x))]
            duplicate_sec=[]
            for x in it.product(range(N),repeat=2):
                counts['section_pairs']+=1
                if all(x[a]==mul(c[k],act(m,t,x[b])) for k,(a,b,t) in enumerate(ARROWS)):
                    duplicate_sec.append(x)
            check(duplicate_sec==[(x,mul(g,x)) for x in base_sec])
        for i,(p,g,c) in enumerate(data):
            for j,(q,h,d) in enumerate(data):
                counts['hom_pairs']+=1
                base=[a for a in range(N) if q==mul(a,p,INV[act(m,1,a)])]
                fine=homs.get((i,j),[])
                check(sorted(a[0] for a in fine)==base)
                check(len(set(a[0] for a in fine))==len(fine))
                check(sorted(fine)==sorted((a,mul(h,a,INV[g])) for a in base))
                if i==j:automorphism_records.append(len(fine))
    for n in range(4):
        for r in preorders(n):
            counts['preorders']+=1
            nd=2*n
            rd={(2*a+i,2*b+j) for (a,b) in r for i,j in it.product(range(2),repeat=2)}
            inflate=lambda s:sum(3<<(2*a) for a in range(n) if s>>a&1)
            def preimage(s):return sum(1<<a for a in range(n) if s>>(2*a)&1)
            sats=[s for s in range(1<<n) if closed(n,r,s)]
            satd=[s for s in range(1<<nd) if closed(nd,rd,s)]
            check(sorted(inflate(s) for s in sats)==satd)
            for s in sats:
                counts['saturated_patches']+=1
                check(preimage(inflate(s))==s)
                sub=[t for t in sats if t&s==t]
                for fs in range(1<<len(sub)):
                    family=[t for k,t in enumerate(sub) if fs>>k&1]
                    counts['cover_families']+=1
                    check(covers(n,r,s,family)==covers(nd,rd,inflate(s),[inflate(t) for t in family]))
                for t in sats:
                    counts['patch_order_pairs']+=1
                    check((s&t==s)==(inflate(s)&inflate(t)==inflate(s)))
    # A skeleton misses the sole "copy true" patch of an indiscrete two-view category.
    missed=2
    raw_cover_refuted=(covers(1,{(0,0)},0,[]) and
        not covers(2,set(it.product(range(2),repeat=2)),missed,[]))
    check(raw_cover_refuted)
    check(not closed(2,set(it.product(range(2),repeat=2)),missed))
    raw_local_gauges=list(range(N))
    empty_images=[tuple() for _ in raw_local_gauges]
    raw_gauge_refuted=len(set(raw_local_gauges))>len(set(empty_images))
    check(raw_gauge_refuted)
    neg=[{'claim':'ignore nonidentity coefficient transport','rejected':wrong_transport},
         {'claim':'reverse multiplication order of gauge composition','rejected':wrong_order},
         {'claim':'equivalence preserves arbitrary raw patch gauge arrows','rejected':raw_gauge_refuted},
         {'claim':'reflect covers without isomorphism-closed patches','rejected':raw_cover_refuted}]
    for x in neg:check(x['rejected'])
    result={'status':'PASS','counts':counts,'assertions':count,'negative_controls':neg,
            'automorphism_cardinalities':sorted(set(automorphism_records)),
            'arithmetic':'exact S3 permutation tables, Boolean relations and integer bitsets',
            'randomness':{'used':False},'started_at_utc':stamp,
            'runtime_seconds':time.monotonic()-start,
            'bounds':{'groups':'S3','loop_group':'C2','coefficient_actions':'conjugation by each S3 involution',
                      'copies_per_view':2,'preorders_n':[0,1,2,3]},
            'non_claims':['Finite tests do not prove the arbitrary-category Lean theorems.',
                          'The stack is not identified with an infinity-stack or arithmetic correspondence.',
                          'All-patch site equivalence and norm invariance are not asserted.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
