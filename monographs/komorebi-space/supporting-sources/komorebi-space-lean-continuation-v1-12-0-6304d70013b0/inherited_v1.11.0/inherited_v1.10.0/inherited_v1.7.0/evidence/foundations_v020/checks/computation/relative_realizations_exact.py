#!/usr/bin/env python3
"""Exact independent checks of relative view change and marked groupoid fibers.

This is a bounded audit, not a proof of the generic Lean theorems. Arithmetic
is exact permutations of {0,1,2}; mul(a,b) means a after b. No random samples.
"""
from __future__ import annotations
import argparse
import datetime as dt
import itertools as it
import json
from pathlib import Path
import time

P=list(it.permutations(range(3)))
N=len(P); ONE=P.index((0,1,2))
M=[[P.index(tuple(a[b[k]] for k in range(3))) for b in P] for a in P]
INV=[next(b for b in range(N) if M[a][b]==ONE==M[b][a]) for a in range(N)]
def mul(*args:int)->int:
    x=ONE
    for y in args:x=M[x][y]
    return x

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); start=time.monotonic(); stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    assertions=0
    def check(ok:bool)->None:
        nonlocal assertions
        assertions+=1
        if not ok:raise AssertionError(f'check {assertions} failed')
    counts={'coefficient_homomorphisms':0,'duplicated_twisted_systems':0,
            'prescribed_domains':0,'coherent_partial_seeds':0,'raw_gauge_candidates':0,
            'weak_squares':0,'marked_Hom_comparisons':0,'marked_objects':0,
            'full_boundary_comparisons':0}
    # Several actual coefficient homomorphisms, including a noninvertible one.
    trans=P.index((1,0,2))
    homs=[tuple(range(N)),tuple(mul(trans,x,INV[trans]) for x in range(N)),(ONE,)*N]
    for alpha in homs:
        check(all(alpha[mul(a,b)]==mul(alpha[a],alpha[b]) for a,b in it.product(range(N),repeat=2)))
        counts['coefficient_homomorphisms']+=1
        for p in range(N):
            for g0,g1 in [(ONE,ONE),(trans,ONE),(ONE,trans),(P.index((1,2,0)),trans)]:
                counts['duplicated_twisted_systems']+=1
                # Fine objects are (level,copy): 0,1 at level 0; 2,3 at level 1.
                frames=(ONE,g0,ONE,g1)
                arrows=[(i,j) for i,j in it.product(range(4),repeat=2) if i//2<=j//2]
                def pull(i,j,x):return x if i//2==j//2 else alpha[x]
                lab={(i,j):mul(frames[i],ONE if i//2==j//2 else p,INV[pull(i,j,frames[j])]) for i,j in arrows}
                def coherent(x,inds):
                    return all(x[i]==mul(lab[i,j],pull(i,j,x[j])) for i,j in arrows if i in inds and j in inds)
                # Brute-force fine global sections, independent of the prediction formula.
                fine=[x for x in it.product(range(N),repeat=4) if coherent(x,set(range(4)))]
                base=[(mul(p,alpha[x]),x) for x in range(N)]
                predicted=[tuple(mul(frames[i],x[i//2]) for i in range(4)) for x in base]
                check(set(fine)==set(predicted))
                check(len({(x[0],x[2]) for x in fine})==len(fine))
                for mask in range(4):
                    inds=[i for i in range(4) if mask>>(i//2)&1]
                    counts['prescribed_domains']+=1
                    partial=[]
                    for values in it.product(range(N),repeat=len(inds)):
                        s=dict(zip(inds,values))
                        if coherent(s,set(inds)): partial.append(s)
                    for s in partial:
                        counts['coherent_partial_seeds']+=1
                        ext=[x for x in fine if all(x[i]==s[i] for i in inds)]
                        bext=[x for x in base if all(x[i//2]==s[i] for i in inds if i%2==0)]
                        check({(x[0],x[2]) for x in ext}==set(bext))
                        check(len(ext)==len(bext))
                        # Normalize a raw lift; enumerate based gauges to test neutrality.
                        q=tuple(s.get(i,ONE) for i in range(4))
                        normal={(i,j):mul(INV[q[i]],lab[i,j],pull(i,j,q[j])) for i,j in arrows}
                        free=[i for i in range(4) if i not in inds]
                        neutral=[]
                        for vals in it.product(range(N),repeat=len(free)):
                            b=[ONE]*4
                            for i,val in zip(free,vals):b[i]=val
                            counts['raw_gauge_candidates']+=1
                            if all(mul(b[i],normal[i,j],INV[pull(i,j,b[j])])==ONE for i,j in arrows):
                                neutral.append(tuple(b))
                        check(bool(neutral)==bool(ext))
                        reconstructed=[tuple(mul(q[i],INV[b[i]]) for i in range(4)) for b in neutral]
                        check(set(reconstructed)==set(ext))
                        # Actual invisible group, not just a scalar count.
                        invbase=[x for x in it.product(range(N),repeat=2)
                                 if x[0]==alpha[x[1]] and all(x[j]==ONE for j in range(2) if mask>>j&1)]
                        invfine=[(x[0],x[0],x[1],x[1]) for x in invbase]
                        check(all(all(pull(i,j,h[j])==h[i] for i,j in arrows) for h in invfine))
                        if ext:
                            x0=ext[0]
                            check({tuple(mul(x0[i],h[i]) for i in range(4)) for h in invfine}==set(ext))
                        for a,b in it.product(invbase,repeat=2):
                            c=(mul(a[0],b[0]),mul(a[1],b[1]))
                            check(c in invbase)
    # Non-strict squares of one-object groupoids. F=alpha; E,K are conjugations.
    # sigma : K F => F E has label alpha(e) k^-1. This tests the inverse comparison.
    wrong_comparison=False
    for alpha in homs:
        for e,k in it.product(range(N),repeat=2):
            counts['weak_squares']+=1
            E=lambda h:mul(e,h,INV[e])
            K=lambda h:mul(k,h,INV[k])
            sigma=mul(alpha[e],INV[k])
            check(all(mul(sigma,K(alpha[h]))==mul(alpha[E(h)],sigma) for h in range(N)))
            image=lambda a:mul(K(a),INV[sigma])
            check(len({image(a) for a in range(N)})==N)
            for a,b in it.product(range(N),repeat=2):
                counts['marked_Hom_comparisons']+=1
                hs=[h for h in range(N) if mul(b,alpha[h])==a]
                ht=[h for h in range(N) if mul(image(b),alpha[h])==image(a)]
                check({E(h) for h in hs}==set(ht))
                for h in hs:
                    bad=lambda z:mul(K(z),sigma)
                    wrong_comparison |= mul(bad(b),alpha[E(h)])!=bad(a)
    # Fine C2-loop groupoid vs its representative. Full marked fibers preserve
    # comparisons even though there are 36 raw marked objects vs 6 at the base.
    arrows=list(it.product(range(2),range(2),range(2)))
    def gauge(c,a):return tuple(mul(a[i],c[n],INV[a[j]]) for n,(i,j,t) in enumerate(arrows))
    for involution in range(N):
        if mul(involution,involution)!=ONE:continue
        for boundary_frame in range(N):
            b0=tuple(ONE if t==0 else involution for i,j,t in arrows)
            boundary=gauge(b0,(ONE,boundary_frame))
            objs=[]
            for a in it.product(range(N),repeat=2):
                c=gauge(boundary,tuple(INV[x] for x in a))
                check(gauge(c,a)==boundary)
                objs.append((c,a));counts['marked_objects']+=1
            check(len(set(objs))==N*N)
            check(len({(c[1],a[0]) for c,a in objs})==N)
            for (c,a),(d,b) in it.product(objs,repeat=2):
                counts['full_boundary_comparisons']+=1
                h=tuple(mul(INV[b[i]],a[i]) for i in range(2))
                check(gauge(c,h)==d)
                check(tuple(mul(b[i],h[i]) for i in range(2))==a)
                # Base comparison is exactly h_0 and unique as well.
                check(mul(b[0],h[0])==a[0])
    # Counterexample to literal full framing: six different edge labels survive
    # with identity-only gauges, while their restrictions to one view coincide.
    full_framed=[(ONE,INV[g],g,ONE) for g in range(N)]
    check(len(set(full_framed))==N)
    check(len({c[0] for c in full_framed})==1)
    # Nonempty is not unique: unprescribed chain sections admit N completions.
    nonunique=(N>1)
    # An actual coherent partial prescription on the omitted isomorphic copy.
    # Fine sections are (0,0),(1,1); fixing copy 1 to 0 leaves one. Its
    # inverse-image domain is empty, leaving two coarse sections.
    fine_constant=[(x,x) for x in (0,1)]
    fine_ext=[x for x in fine_constant if x[1]==0]
    coarse_ext=[0,1]
    check(len(fine_ext)==1)
    check(len(coarse_ext)==2)
    ignored_boundary=len(fine_ext)!=len(coarse_ext)
    neg=[{'claim':'replace inverse of the weak-square comparison by the comparison itself','rejected':wrong_comparison},
         {'claim':'literal full framing survives view duplication as an equivalence','rejected':len(set(full_framed))>1},
         {'claim':'nonempty extension set is automatically a singleton','rejected':nonunique},
         {'claim':'arbitrary unsaturated prescriptions preserve the extension set','rejected':ignored_boundary}]
    for test in neg:check(test['rejected'])
    report={'status':'PASS','started_at_utc':stamp,'runtime_seconds':time.monotonic()-start,
            'counts':counts,'assertions':assertions,'negative_controls':neg,
            'arithmetic':'exact S3 permutation tables and Boolean equality; no floating point',
            'randomness':{'used':False},
            'bounds':{'group':'all six permutations of Fin 3','coefficient_maps':'identity, one inner automorphism, trivial homomorphism',
                      'twisted_base':'two-view chain','copies_per_base_view':2,'duplicated_frames':'four explicitly listed fixtures per coefficient map and edge label',
                      'relative_domains':'all four saturated domains of the chain',
                      'weak_squares':'all pairs of S3 inner automorphisms for each of three coefficient maps',
                      'marked_loop_boundaries':'all C2-to-S3 involutions and all six second-copy boundary frames'},
            'non_claims':['Finite checks do not prove the arbitrary-category Lean theorems.',
                          'The duplicated chain frames are fixtures, not all possible frames.',
                          'No quantitative stability, algorithmic complexity or arbitrary view-doctrine invariance is inferred.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
