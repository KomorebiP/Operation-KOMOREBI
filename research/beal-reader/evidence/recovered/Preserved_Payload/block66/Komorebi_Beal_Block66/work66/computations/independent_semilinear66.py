#!/usr/bin/env python3
"""Independent coefficient algebra in F7[t]/(t^2-t-1); imports no project arithmetic."""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path

def check(ok,msg):
    if not ok:raise AssertionError(msg)
# Polynomial multiplication reduced by t^2=t+1, distinct from the w-basis implementation.
def mult(x,y):
    a,b=x%7,x//7;c,d=y%7,y//7
    poly=[a*c,a*d+b*c,b*d]
    return (poly[0]+poly[2])%7+7*((poly[1]+poly[2])%7)
def add(x,y):return (x%7+y%7)%7+7*((x//7+y//7)%7)
def neg(x):return (-(x%7))%7+7*((-(x//7))%7)
def conj(x):return (x%7+x//7)%7+7*((-(x//7))%7)
def from_w(x):return (x%7-x//7)%7+7*(2*(x//7)%7)
def to_w(x):return (x%7+4*(x//7))%7+7*(4*(x//7)%7)
A=[[add(x,y) for y in range(49)] for x in range(49)]
M=[[mult(x,y) for y in range(49)] for x in range(49)]
N=[neg(x) for x in range(49)];S=[conj(x) for x in range(49)]
def values(u,r,b,c,xyz):
    x,y,z=xyz;mid=A[M[r][y]][z]
    return M[b][A[M[u][x]][mid]],M[c][A[N[M[u][x]]][mid]]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);arg=ap.parse_args()
    d=json.loads(arg.certificate.read_text());check(d['status']=='PASS_FINITE_ALGEBRA','Wrong input status')
    # Begin with the z-probe, then use a different affine probe ordering.
    probes=[(1,1,1),(1,0,1),(0,1,1),(1,1,0),(1,0,0),(0,1,0)]
    result=[];tested=0
    for b in range(1,49):
        for c in (range(49)):
            if c!=b and c!=S[b]:continue
            for u in range(1,49):
                for r in range(1,49):
                    tested+=1
                    ok=True
                    for xyz in probes:
                        p,q=values(u,r,b,c,xyz)
                        if q!=p and q!=S[p]:ok=False;break
                    if ok:result.append((u,r,b,c))
    canon=sorted([list(map(to_w,row)) for row in result])
    check(canon==d['accepted_quadruples'],'Changed semilinear classification')
    allchecks=0
    for u,r,b,c in result:
        check(S[u]==N[u] and S[r]==r and c==S[b],'Semilinear formula false')
        for xyz in itertools.product(range(7),repeat=3):
            p,q=values(u,r,b,c,xyz);check(q==S[p],'Full paired polynomial control failed');allchecks+=1
    check(allchecks==d['all_coordinate_checks']==592704,'Changed coordinate count')
    # Direct component extraction in the theta basis: b=(a+b_theta/2) + w*(b_theta/2).
    comps=[]
    for x in range(49):
        c0=(x%7+4*(x//7))%7;c1=4*(x//7)%7
        check(from_w(c0+7*c1)==x,'Component reconstruction')
        comps.append([to_w(x),c0,c1])
    check(sorted(comps)==d['component_splits'],'Changed component coefficients')
    minus=[q for q in range(1,7) if (q+pow(q,-1,7))%7==0]
    plus=[q for q in range(1,7) if (q-pow(q,-1,7))%7==0]
    check(d['local_tame_residues']=={'-1':minus,'1':plus} and not minus,'Wrong tame eigenspace')
    # Independent projective hyperplanes via normalization of the LAST nonzero coefficient.
    pts=list(itertools.product(range(7),repeat=3));hyper=[]
    for v in pts[1:]:
        last=next(x for x in reversed(v) if x)
        if last==1:hyper.append({p for p in pts if sum(a*b for a,b in zip(v,p))%7==0})
    maxu=max(len(x|y) for x in hyper for y in hyper)
    check((len(hyper),len(hyper)**2,maxu)==(d['projective_scalar_forms'],d['two_kernel_pairs'],d['max_two_kernel_union']),'Changed union-of-kernels test')
    w=from_w(7);mw=from_w(42);control=0
    for xyz in pts:
        p,q=values(w,1,w,mw,xyz);check(q==S[p],'Anti-invariant control fails');control+=1
    check(w!=S[w] and control==343,'False ordinary descent control')
    c29=d['mixed29_control']
    p29,q29=values(from_w(c29['u']),from_w(c29['r']),from_w(c29['b']),from_w(c29['b_prime']),(4,1,5))
    check([to_w(p29),to_w(q29)]==c29['products']==[2,2] and c29['b']>=7,'Changed mixed29 control')
    square13=[[c,((1+pow(13,-1,7))*c)%7,((1-pow(13,-1,7))*c)%7] for c in range(7)]
    check(square13==d['prime13_square_values'],'Changed prime13 square control')
    out={'schema' :'beal.block66.independent_semilinear.v1','status':'PASS_INDEPENDENT_ALGEBRA',
         'basis':'theta^2-theta-1','primary_arithmetic_imports':False,
         'quadruples_after_z_probe':tested,'accepted_quadruples':len(result),
         'all_coordinate_checks':allchecks,'hyperplane_pairs':len(hyper)**2,'max_union':maxu,
         'anti_invariant_control_cases':control,'mixed29_control':True,'prime13_value_cases':7,'tame_plus_residues':plus,'tame_minus_residues':minus,
         'scope':'Finite algebra only; not an independent Galois or geometric proof review.'}
    arg.output.parent.mkdir(parents=True,exist_ok=True);arg.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],len(result),allchecks)
if __name__=='__main__':main()
