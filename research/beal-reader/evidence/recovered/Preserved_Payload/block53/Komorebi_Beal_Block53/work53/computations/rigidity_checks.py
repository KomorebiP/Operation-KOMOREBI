#!/usr/bin/env python3
"""Exact bounded checks for Block53. These do not certify global source inputs."""
from __future__ import annotations
import argparse
import json
from math import gcd
from pathlib import Path
from typing import Optional

Q = tuple[int, int]  # a+b*phi, phi^2=phi+1
ZERO: Q = (0, 0)
ONE: Q = (1, 0)

def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def add(x: Q, y: Q) -> Q:
    return x[0]+y[0], x[1]+y[1]

def neg(x: Q) -> Q:
    return -x[0], -x[1]

def mul(x: Q, y: Q) -> Q:
    a,b=x; c,d=y
    return a*c+b*d, a*d+b*c+b*d

def scale(a: int, x: Q) -> Q:
    return a*x[0], a*x[1]

def norm(x: Q) -> int:
    a,b=x
    return a*a+a*b-b*b

def val(a: int) -> Optional[int]:
    if a == 0:
        return None
    a=abs(a); r=0
    while a % 7 == 0:
        r+=1; a//=7
    return r

def qval(x: Q) -> Optional[int]:
    vals=[v for a in x if (v:=val(a)) is not None]
    return min(vals) if vals else None

def div(x: Q, p: int) -> bool:
    return x[0] % p == 0 and x[1] % p == 0

def mm(A: tuple[Q,Q,Q,Q], B: tuple[Q,Q,Q,Q]) -> tuple[Q,Q,Q,Q]:
    a,b,c,d=A; e,f,g,h=B
    return add(mul(a,e),mul(b,g)),add(mul(a,f),mul(b,h)),add(mul(c,e),mul(d,g)),add(mul(c,f),mul(d,h))

def check_nilpotent(N: tuple[Q,Q,Q,Q], n: int) -> int:
    need(isinstance(n,int) and not isinstance(n,bool) and n>=1,'n must be a positive integer')
    u,b,c,d=N
    need(d==neg(u),'trace-zero shape required')
    need(mm(N,N)==(ZERO,)*4,'matrix is not nilpotent')
    need(div(b,7),'upper entry is not divisible by seven')
    need(div(c,7**n),'lower entry violates the stated depth')
    m=n//2+1
    need(div(u,7**m),'diagonal precision failed')
    return m

def generated_nilpotents() -> dict:
    units=(ONE,(0,1),(1,1),(2,-1))
    need(all(norm(x)%7!=0 for x in units),'chosen coefficient is not a unit')
    matrices=instances=nonrational=tight=0
    # Every pair of coordinate valuations here is primitive. No claim that
    # this grid exhausts all possible O-valued matrices is made.
    for t in range(1,5):
        for vx in range(4):
            for vy in range(7):
                if min(vx,vy)!=0:
                    continue
                for ux in units:
                    for uy in units:
                        x=scale(7**vx,ux); y=scale(7**vy,uy)
                        u=scale(-7**t,mul(x,y))
                        b=scale(7**t,mul(x,x))
                        c=scale(-7**t,mul(y,y))
                        N=(u,b,c,neg(u))
                        need(mm(N,N)==(ZERO,)*4,'construction violated nilpotence')
                        need(min(qval(z) for z in N if z!=ZERO)==t,'content mismatch')
                        depth=qval(c)
                        need(depth is not None,'unexpected zero lower coordinate')
                        matrices+=1
                        nonrational+=int(any(z[1] for z in N))
                        for n in range(1,depth+1):
                            m=check_nilpotent(N,n)
                            instances+=1
                            tight+=int(qval(u)==m)
    for t in range(1,5):
        N=(ZERO,ZERO,(-7**t,0),ZERO)
        for n in range(1,t+1):
            check_nilpotent(N,n)
            instances+=1
        matrices+=1
    return {'matrices':matrices,'admissible_matrix_depth_instances':instances,
            'nonrational_coefficient_matrices':nonrational,'tight_instances':tight,
            'domain':'Z[phi], phi^2=phi+1, exact integers',
            'range':{'content_t':[1,4],'x_valuation':[0,3],'y_valuation':[0,6],
                     'primitive_only':True,'coordinate_units':[list(u) for u in units],
                     'depths':'every 1<=n<=valuation(lower-left) for each generated matrix'},
            'zero_diagonal_family_included':True}

def trace_generator_checks() -> dict:
    rows=[]
    for n in range(1,4):
        mod=7**n; tested=solutions=0
        for lam in range(mod):
            if lam%7 in (0,1):
                continue
            for a in range(lam%7,mod,7):
                d=lam*pow(a,-1,mod)%mod
                tested+=1
                if (a+d-lam-1)%mod==0:
                    solutions+=1
                    need(a==lam and d==1,'separated root was not unique')
        rows.append({'n':n,'tested_generator_pairs':tested,'unique_correct_solutions':solutions})
    # The proof at a general group element uses a second trace identity.
    second=0
    for lam0 in (2,3,4,5,6,9):
        mod=49
        need(gcd(lam0-1,mod)==1,'separating value not a unit')
        for lam in range(mod):
            if lam%7==0: continue
            for a in range(lam%7,mod,7):
                d=(lam+1-a)%mod
                if (lam0*a+d-lam0*lam-1)%mod==0:
                    need(a==lam and d==1,'two-trace identification failed')
                second+=1
    return {'cyclic_generator_root_enumerations':rows,'second_trace_instances':second}

def norm_and_precision() -> dict:
    vals=(ZERO,ONE,(0,1),(1,-1),(2,3))
    matrices=identities=0
    for n in range(1,13):
        m=n//2+1
        need(m<=n and 2*m>=n+1,'half-depth arithmetic failed')
        for Qv in (4,9,11,29,31,169,1849):
            for A in vals:
                for D in vals:
                    for b in vals:
                        c=vals[(n+Qv)%len(vals)]
                        a=add((Qv,0),scale(7**m,A))
                        d=add(ONE,scale(7**m,D))
                        determinant=add(mul(add(ONE,neg(a)),add(ONE,neg(d))),neg(scale(7**n,mul(b,c))))
                        need(div(determinant,7**m),'good-place determinant precision failed')
                        need(norm(determinant)%7**(2*m)==0,'norm precision failed')
                        matrices+=1
        mod=7**n
        for u in vals:
            for v in vals:
                lhs=mul(add(ONE,scale(7**m,u)),add(ONE,scale(7**m,v)))
                rhs=add(ONE,scale(7**m,add(u,v)))
                need(div(add(lhs,neg(rhs)),mod),'square-zero linearization failed')
                identities+=1
    # Exact rational Weil comparison. No floating-point square roots.
    thresholds=[]
    for q in (11,31):
        r=49-q-1
        need(q%5 in (1,4) and r>0 and r*r>4*q,'Weil or splitting test failed')
        thresholds.append({'q':q,'splits_in_K':True,'positive_difference':r,
                           'difference_squared':r*r,'four_q':4*q})
    product=1
    for p in (2,3,5,7,11,13,19,29,31,43,71): product*=p
    need(product==1566013238790,'combined divisibility product failed')
    return {'determinant_norm_instances':matrices,'square_zero_products':identities,
            'depth_range':[1,12],'Q_values':[4,9,11,29,31,169,1849],
            'exact_Weil_tests':thresholds,'n_ge_2_squarefree_required_divisor':product,
            'Minkowski_exact_test':{'discriminant':5,'bound_squared':'5/4','less_than_four':5<16}}

def negative_controls() -> list[dict]:
    out=[]
    n2=((-7,0),ONE,(-49,0),(7,0))
    need(mm(n2,n2)==(ZERO,)*4 and not div(n2[0],49),'missing-content control invalid')
    try: check_nilpotent(n2,2)
    except ValueError: out.append({'control':'remove_natural_upper_divisibility','status':'REJECTED'})
    else: raise ValueError('invalid natural-content input accepted')
    n3=((-49,0),(7,0),(-343,0),(49,0))
    check_nilpotent(n3,3)
    need(not div(n3[0],343),'full-depth false extension not detected')
    out.append({'control':'replace_half_depth_by_full_depth','status':'COUNTEREXAMPLE_CONFIRMED','n':3})
    for bad in (0,-1,True):
        try: check_nilpotent(n3,bad)
        except ValueError: pass
        else: raise ValueError('invalid depth accepted')
    out.append({'control':'invalid_depth_inputs','status':'REJECTED','count':3})
    for k in range(7):
        lam=pow(8,k,49); a=pow(15,k,49); d=pow(43,k,49)
        need((a*d-lam)%49==0 and (a+d-lam-1)%49==0,'nonseparated cyclic example failed')
    out.append({'control':'remove_residual_character_separation','status':'COUNTEREXAMPLE_CONFIRMED',
                'lambda_a_d_mod49':[8,15,43],'all_seven_group_elements_checked':True})
    need((-26-170)%49==0 and (-13)**2==169,'scalar pseudotrace agreement failed')
    need((-13)%49 not in (169%49,1),'scalar control has wrong values')
    out.append({'control':'use_only_characteristic_polynomial_at13','status':'COUNTEREXAMPLE_CONFIRMED',
                'scalar_diagonal_mod49':[36,36],'cyclotomic_diagonal_mod49':[22,1]})
    need((-pow(13,-1,49))%49==15 and val(-14)==1,'good13 obstruction arithmetic failed')
    out.append({'control':'good13_eta_claimed_one_mod49','status':'REJECTED','actual_eta_mod49':15})
    # The old local n=3 example remains admissible locally but not a global
    # everywhere-unramified character. Do not relabel it as a Frey example.
    out.append({'control':'old_local_sharpness_n3','status':'PRESERVED_LOCAL_EXAMPLE_ONLY'})
    return out

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result={'schema':'komorebi.beal.block53.rigidity_checks.v1','status':'PASS',
            'generated_nilpotents':generated_nilpotents(),
            'character_identification':trace_generator_checks(),
            'norm_and_precision':norm_and_precision(),
            'negative_controls':negative_controls(),
            'non_claims':['No verification of Hilbert class field theory or inherited geometry',
                          'No Lean certificate','No full Beal or signature exclusion',
                          'The generated matrix grid is not an exhaustive set of O-valued representations']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
