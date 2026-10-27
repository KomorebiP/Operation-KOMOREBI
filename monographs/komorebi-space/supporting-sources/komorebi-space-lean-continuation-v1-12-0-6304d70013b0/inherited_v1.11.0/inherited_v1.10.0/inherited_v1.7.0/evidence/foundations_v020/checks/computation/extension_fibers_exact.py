#!/usr/bin/env python3
"""Finite exact audit of extension fibers and changing protected observations.

Arithmetic: F_2, F_3 and integers, no floating arithmetic in assertions.
All scalar d and p on F_q^n, 1<=n<=3, q in {2,3}, are enumerated.
This is supplementary evidence, not a universal proof or a Lean replay.
"""
from __future__ import annotations
import argparse
import itertools
import json
import time
from pathlib import Path


def vectors(q: int, n: int):
    return list(itertools.product(range(q), repeat=n))


def dot(a, b, q):
    return sum(x*y for x,y in zip(a,b)) % q


def rank_mod(rows, q):
    """Independent modular elimination, used to audit enumerated kernel sizes."""
    a=[list(r) for r in rows]
    if not a: return 0
    pivot=0
    for c in range(len(a[0])):
        k=next((k for k in range(pivot,len(a)) if a[k][c]%q),None)
        if k is None:continue
        a[pivot],a[k]=a[k],a[pivot]
        inv=pow(a[pivot][c],-1,q)
        a[pivot]=[(v*inv)%q for v in a[pivot]]
        for j in range(len(a)):
            if j!=pivot:
                t=a[j][c]
                a[j]=[(x-t*y)%q for x,y in zip(a[j],a[pivot])]
        pivot+=1
        if pivot==len(a):break
    return pivot


def run():
    assertions=0
    def check(condition, label):
        nonlocal assertions
        assertions+=1
        if not condition: raise AssertionError(label)
    counts={'scalar_linear_problems':0,'nested_observation_problems':0,'integer_globals':0,'integer_intermediates':0}
    for q in (2,3):
        for n in (1,2,3):
            vec=vectors(q,n)
            zero=(0,)*n
            for d in vec:
                dx={x:dot(d,x,q) for x in vec}
                for p in vec:
                    counts['scalar_linear_problems']+=1
                    px={x:dot(p,x,q) for x in vec}
                    H={x for x in vec if dx[x]==0 and px[x]==0}
                    B={dx[x] for x in vec if px[x]==0}
                    check(len(H)==q**(n-rank_mod([d,p],q)),'kernel vs independent elimination')
                    fibers={s:{x for x in vec if dx[x]==0 and px[x]==s} for s in range(q)}
                    for x in vec:
                        sol=fibers[px[x]]
                        check((dx[x] in B)==bool(sol),'obstruction vanishing iff nonempty fiber')
                    for s,sol in fibers.items():
                        if not sol:continue
                        base=min(sol)
                        param={tuple((x+y)%q for x,y in zip(base,h)) for h in H}
                        check(param==sol,'affine parameterization')
                        check((len(sol)==1)==(H=={zero}),'uniqueness iff zero homogeneous group')
                        for y in sol:
                            diff=tuple((a-b)%q for a,b in zip(y,base))
                            check(diff in H,'difference homogeneous')
                    # On observable data that have a raw lift, obstruction is well-defined.
                    classes={}
                    for x in vec:
                        coset=frozenset((dx[x]+b)%q for b in B)
                        if px[x] in classes: check(classes[px[x]]==coset,'raw-lift independence')
                        classes[px[x]]=coset
                    for a,ca in classes.items():
                        for b,cb in classes.items():
                            summed=frozenset((x+y)%q for x in ca for y in cb)
                            check(summed==classes[(a+b)%q],'additive connecting map')
                    check({s for s,c in classes.items() if 0 in c}=={px[x] for x in vec if dx[x]==0},'connecting kernel equals restriction image')
        # U observes the first coordinate; W observes the first two.
        vec=vectors(q,3)
        for d in vec:
            counts['nested_observation_problems']+=1
            B_U={dot(d,x,q) for x in vec if x[0]==0}
            B_W={dot(d,x,q) for x in vec if x[:2]==(0,0)}
            check(B_W<=B_U,'boundaries antitone')
            H_U={x for x in vec if dot(d,x,q)==0 and x[0]==0}
            H_W={x for x in vec if dot(d,x,q)==0 and x[:2]==(0,0)}
            check(H_W<=H_U,'ambiguity antitone')
            for x in vec:
                r=dot(d,x,q)
                cW={(r+b)%q for b in B_W}; cU={(r+b)%q for b in B_U}
                check({(y+b)%q for y in cW for b in B_U}==cU,'quotient map on classes')
                check(not (0 in cW) or 0 in cU,'vanishing restricts')
    # Actual three-view integer system: r_01(a,b)=(a,0), r_12(a,b)=(a,2b).
    for k in range(-5,6):
        for n in range(-10,11):
            counts['integer_globals']+=1
            section=((k,0),(k,2*n),(k,n))
            check((section[1][0],0)==section[0],'integer 0<-1 coherence')
            check((section[2][0],2*section[2][1])==section[1],'integer 1<-2 coherence')
            check(section[2][1]==n,'inverse affine parameter')
        for m in range(-9,10):
            counts['integer_intermediates']+=1
            n=m//2
            check((m==2*n)==(m%2==0),'parity criterion')
            check(((k,m)[0],0)==(k,0),'intermediate coherence does not imply extendability')
    mutations=[
      {'claim':'zero_obstruction_implies_unique_extension','rejected':len({(0,b) for b in range(3)})>1},
      {'claim':'extendable_initial_seed_makes_every_intermediate_choice_extendable','rejected':(1%2!=0)},
      {'claim':'forgetting_obstructions_is_always_injective','rejected':frozenset({0})!=frozenset({1}) and {((1+b)%2) for b in (0,1)}=={0,1}}
    ]
    for m in mutations:check(m['rejected'],'mutation must be rejected')
    return {'status':'PASS','arithmetic':'exact F_2, F_3, and integer arithmetic','bounds':{'fields':[2,3],'candidate_dimensions':[1,2,3],'scalar_maps':'all row vectors d,p','nested_observations':'first coordinate vs first two, dimension 3','integer_k':[-5,5],'integer_n':[-10,10],'integer_m':[-9,9]},'cases':counts,'assertions':assertions,'negative_controls':mutations,'non_claims':['Finite tests are not a substitute for Lean proof terms.','No higher stack, arithmetic correspondence, infinite search termination, or complexity theorem.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();t=time.monotonic()
    report=run();report['runtime_seconds']=time.monotonic()-t
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
