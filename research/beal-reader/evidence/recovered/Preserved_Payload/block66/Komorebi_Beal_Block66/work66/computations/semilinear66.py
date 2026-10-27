#!/usr/bin/env python3
"""Exact finite algebra for the conjugate-class argument. No Galois theorem is computed."""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path

def require(ok,msg):
    if not ok:raise AssertionError(msg)
ADD=[[(x%7+y%7)%7+7*((x//7+y//7)%7) for y in range(49)] for x in range(49)]
NEG=[(-x%7)%7+7*((-(x//7))%7) for x in range(49)]
MUL=[[((x%7)*(y%7)+5*(x//7)*(y//7))%7+7*(((x%7)*(y//7)+(x//7)*(y%7))%7) for y in range(49)] for x in range(49)]
SIG=[x%7+7*((-(x//7))%7) for x in range(49)]
def pair(u,r,b,c,x,y,z):
    middle=ADD[MUL[r][y]][z]
    return MUL[b][ADD[MUL[u][x]][middle]],MUL[c][ADD[NEG[MUL[u][x]]][middle]]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    # The z-axis condition discards the other candidates exactly before expanding u,r.
    initial=48*49*48*48
    probes=[(0,0,1),(1,0,0),(0,1,0),(1,0,1),(0,1,1),(1,1,0),(1,1,1)]
    candidates=[(u,r,b,c) for b in range(1,49) for c in sorted({b,SIG[b]}) for u in range(1,49) for r in range(1,49)]
    stages=[{'probe':list(probes[0]),'remaining':len(candidates)}]
    for x,y,z in probes[1:]:
        keep=[]
        for u,r,b,c in candidates:
            p,q=pair(u,r,b,c,x,y,z)
            if q in (p,SIG[p]):keep.append((u,r,b,c))
        candidates=keep;stages.append({'probe':[x,y,z],'remaining':len(candidates)})
    expected=sorted((7*v,r,b,SIG[b]) for v in range(1,7) for r in range(1,7) for b in range(1,49))
    require(sorted(candidates)==expected,'Semilinear classification differs')
    follow=0
    for u,r,b,c in candidates:
        for x,y,z in itertools.product(range(7),repeat=3):
            p,q=pair(u,r,b,c,x,y,z);require(q==SIG[p],'Universal conjugacy fails');follow+=1
    # Exhaust all nonzero F7 linear scalar forms on F7^3: no union of two proper kernels covers.
    vectors=list(itertools.product(range(7),repeat=3))
    # Canonical projective linear forms suffice; multiplying a form does not change its kernel.
    forms=[]
    for f in vectors[1:]:
        first=next(v for v in f if v)
        if first==1:forms.append(f)
    masks=[]
    for f in forms:
        masks.append(sum(1<<i for i,x in enumerate(vectors) if sum(a*b for a,b in zip(f,x))%7==0))
    max_union=0
    for A in masks:
        for B in masks:
            n=(A|B).bit_count();max_union=max(max_union,n);require(n<343,'Two proper kernels cover')
    # Coefficient-module splitting and local tame covariances.
    splits=[]
    for b in range(49):
        bplus=MUL[4][ADD[b][SIG[b]]]
        # bminus=(b-sigma(b))/(2w); w^-1=3w, so (2w)^-1=5w.
        bminus=MUL[35][ADD[b][NEG[SIG[b]]]]
        require(bplus<7 and bminus<7 and ADD[bplus][MUL[7][bminus]]==b,'Wrong component split')
        splits.append([b,bplus,bminus])
    tame={str(e):[q for q in range(1,7) if q*q%7==e%7] for e in (1,-1)}
    require(tame=={'1':[1,6],'-1':[]},'Twisted tame support mismatch')
    control=[]
    for x,y,z in vectors:
        p,q=pair(7,1,7,42,x,y,z);require(q==SIG[p],'Anti control fails');control.append([x,y,z,p,q])
    require(SIG[7]!=7,'Anti control must not descend')
    # Validate separation of chi and chi^-1 in every 7-dimensional coordinate vector.
    # Three Kummer and four coordinates of the conjugate beta pair.
    projection_count=0
    for v in itertools.product(range(7),repeat=7):
        Tv=[3*x%7 for x in v[:3]]+[5*x%7 for x in v[3:]]
        Pv=[((y-5*x)*3)%7 for x,y in zip(v,Tv)]  # inverse(3-5)=3 mod7
        require(Pv==list(v[:3])+[0]*4,'Joint-image projector failure');projection_count+=1
    p29,q29=pair(7,6,13,48,4,1,5)
    require((p29,q29)==(2,2) and SIG[13]==48 and 13>=7,'Mixed29 control failed')
    prime13=[]
    for c in range(7):
        plus=0;minus=2*c%7
        require((minus==0)==(c==0),'Prime13 minus condition failed')
        prime13.append([c,plus,minus])
    out={'schema' :'beal.block66.semilinear.v1','status':'PASS_FINITE_ALGEBRA',
         'domain':'k=F7[w]/(w^2-5), codes a+7b','initial_nonzero_b_quadruples':initial,
         'stages':stages,'accepted_quadruples':[list(t) for t in expected],
         'all_coordinate_checks':follow,'projective_scalar_forms':len(forms),
         'two_kernel_pairs':len(forms)**2,'max_two_kernel_union':max_union,
         'component_splits':splits,'local_tame_residues':tame,
         'anti_descent_control':{'u':7,'r':1,'b':7,'b_conjugate_base':42,'coordinate_cases':len(control)},
         'joint_projector_vectors':projection_count,'mixed29_control':{'u':7,'r':6,'b':13,'b_prime':48,'products':[p29,q29]},'prime13_square_values':prime13,
         'nonclaims':['No proof by finite check of Chebotarev or actual Galois realization','No ordinary beta descent without vanishing anti-component']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],len(expected),follow,projection_count)
if __name__=='__main__':main()
