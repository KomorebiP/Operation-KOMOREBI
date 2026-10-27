#!/usr/bin/env python3
"""Independent finite audit of nonabelian overlap descent, using exact S3 tables.

All 216 cocycles on a four-view chain with constant S3 coefficients are used.
Local frames are deterministic, not exhaustive. Each datum is reconstructed
with all 81 choices of reference patches (four proper three-view patches).
This is bounded implementation evidence, not a proof for arbitrary categories.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, itertools as it, json, platform, time
from pathlib import Path

P = tuple(it.permutations(range(3)))
IDX = {p:i for i,p in enumerate(P)}
E = IDX[(0,1,2)]
MUL = tuple(tuple(IDX[tuple(a[b[k]] for k in range(3))] for b in P) for a in P)
INV = tuple(next(j for j in range(6) if MUL[i][j] == E and MUL[j][i] == E) for i in range(6))
def mul(a:int,b:int)->int:return MUL[a][b]
def inv(a:int)->int:return INV[a]
def conjugate_edge(a:int,c:int,b:int)->int:return mul(mul(a,c),inv(b))

class Audit:
    def __init__(self)->None:self.assertions=0
    def check(self, condition:bool, label:str)->None:
        self.assertions+=1
        if not condition:raise AssertionError(label)

def run()->dict:
    start=time.monotonic();stamp=dt.datetime.now(dt.timezone.utc).isoformat();a=Audit()
    views=range(4);patches=[set(views)-{i} for i in views]
    edges=[(x,y) for x in views for y in views if x<=y]
    triples=[(x,y,z) for x in views for y in views for z in views if x<=y<=z]
    choices=list(it.product(*[[i for i in views if x in patches[i]] for x in views]))
    a.check(len(choices)==81,'reference count')
    for x,y,z in triples:a.check(any({x,y,z}<=p for p in patches),'composition cover')
    configurations=0;unequal_local_cases=0;wrong_inverse_rejected=False
    for seed,gens in enumerate(it.product(range(6),repeat=3)):
        c={}
        for x,y in edges:
            v=E
            for k in range(x,y):v=mul(v,gens[k])
            c[x,y]=v
        # A deterministic family spanning nonidentity, noncommuting local frames.
        k={(i,x):(seed+3*i+5*x+i*x)%6 for i in views for x in patches[i]}
        local={(i,x,y):conjugate_edge(k[i,x],c[x,y],k[i,y])
               for i in views for x,y in edges if {x,y}<=patches[i]}
        trans={(i,j,x):mul(k[j,x],inv(k[i,x]))
               for i in views for j in views for x in patches[i]&patches[j]}
        unequal_local_cases+=any(local[i,x,y]!=local[j,x,y]
            for x,y in edges for i in views for j in views if {x,y}<=patches[i]&patches[j])
        for i in views:
            for x,y,z in triples:
                if {x,y,z}<=patches[i]:a.check(local[i,x,z]==mul(local[i,x,y],local[i,y,z]),'local cocycle')
        for x in views:
            ids=[i for i in views if x in patches[i]]
            for i,j,l in it.product(ids,repeat=3):
                a.check(trans[i,l,x]==mul(trans[j,l,x],trans[i,j,x]),'triple overlap')
        previous=None;first=None;previous_from_first=None
        for choice in choices:
            b={(i,x):trans[choice[x],i,x] for i in views for x in patches[i]}
            glued={}
            for x,y in edges:
                vals=[mul(mul(inv(b[i,x]),local[i,x,y]),b[i,y])
                      for i in views if {x,y}<=patches[i]]
                a.check(all(v==vals[0] for v in vals),'strictified agreement')
                glued[x,y]=vals[0]
                for i in views:
                    if {x,y}<=patches[i]:
                        a.check(conjugate_edge(b[i,x],glued[x,y],b[i,y])==local[i,x,y],'local identification')
                        wrong=mul(mul(b[i,x],local[i,x,y]),inv(b[i,y]))
                        if conjugate_edge(b[i,x],wrong,b[i,y])!=local[i,x,y]:wrong_inverse_rejected=True
            for x,y,z in triples:a.check(glued[x,z]==mul(glued[x,y],glued[y,z]),'global cocycle')
            for (i,j,x),v in trans.items():a.check(b[j,x]==mul(v,b[i,x]),'effectuation overlap')
            if first is None:first=(glued,b)
            basec,baseb=first
            basecomp={}
            for x in views:
                vals=[mul(inv(b[i,x]),baseb[i,x]) for i in views if x in patches[i]]
                a.check(all(v==vals[0] for v in vals),'base comparison independent')
                basecomp[x]=vals[0]
            for x,y in edges:a.check(conjugate_edge(basecomp[x],basec[x,y],basecomp[y])==glued[x,y],'base global gauge')
            if previous is not None:
                oldc,oldb=previous
                h={}
                for x in views:
                    vals=[mul(inv(b[i,x]),oldb[i,x]) for i in views if x in patches[i]]
                    a.check(all(v==vals[0] for v in vals),'comparison independent')
                    h[x]=vals[0]
                    a.check(mul(h[x],previous_from_first[x])==basecomp[x],'comparison composition')
                for x,y in edges:a.check(conjugate_edge(h[x],oldc[x,y],h[y])==glued[x,y],'comparison global gauge')
            previous=(glued,b);previous_from_first=basecomp;configurations+=1
    t=IDX[(1,0,2)];u=IDX[(0,2,1)]
    a.check(mul(t,u)!=mul(u,t),'noncommutative order counterexample')
    triple_solutions=[b for b in it.product(range(6),repeat=3)
                     if b[1]==mul(t,b[0]) and b[2]==mul(t,b[1]) and b[2]==mul(t,b[0])]
    a.check(not triple_solutions,'incoherent triple has no frames')
    # Arrow coverage alone: pair patches on 0<1<2 miss the composition constraint.
    # Local labels 1 on 01 and 12, t on 02 cannot arise from one coherent cocycle
    # and one common family of local comparison values.
    count=0
    for g01,g12 in it.product(range(6),repeat=2):
        for b0,b1,b2 in it.product(range(6),repeat=3):
            if (conjugate_edge(b0,g01,b1)==E and conjugate_edge(b1,g12,b2)==E
                    and conjugate_edge(b0,mul(g01,g12),b2)==t):count+=1
    a.check(count==0,'arrow-cover-only counterexample')
    a.check(wrong_inverse_rejected,'inverse omission mutation detected')
    return {'status':'PASS','started_at_utc':stamp,'runtime_seconds':time.monotonic()-start,
        'coefficient_domain':'exact permutations of Fin 3; multiplication a*b means a after b',
        'cases':{'chain_cocycles':216,'reference_choices_per_datum':81,
                 'reconstructions':configurations,'data_with_unequal_local_labels':unequal_local_cases,
                 'incoherent_triple_frame_candidates':216,'arrow_cover_counterexample_candidates':7776},
        'assertions':a.assertions,
        'negative_controls':[{'claim':'reverse_overlap_multiplication_order','rejected':True},
          {'claim':'pairwise_gauges_without_triple_coherence_suffice','rejected':True},
          {'claim':'use_frame_instead_of_its_inverse_when_strictifying','rejected':True},
          {'claim':'arrow_coverage_alone_implies_object_descent','rejected':True}],
        'randomness':{'used':False},'python_version':platform.python_version(),
        'non_claims':['Local frames are deterministic fixtures, not all possible frames.',
                      'Constant S3 coefficients only in this finite audit.',
                      'Universal theorem is supplied by Lean, not by finite enumeration.']}

def main()->None:
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=run();result['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
