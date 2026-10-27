#!/usr/bin/env python3
"""Exact finite checks for source inflation and normalized abelian lifting.

These checks do not prove a limiting statement or continuous group theorem.
No random sampling, floating arithmetic, network access, or external dependencies.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools as it
import json
import platform
import time
from pathlib import Path
from math import gcd, isqrt

Mat = tuple[int, ...]
I2: Mat = (1, 0, 0, 1)

def eye(d: int) -> Mat:
    return tuple(int(i == j) for i in range(d) for j in range(d))

def mm(A: Mat, B: Mat, q: int | None = None) -> Mat:
    d = isqrt(len(A))
    assert d*d == len(A) == len(B)
    if d == 2:
        a,b,c,d0=A; e,f,g,h=B
        out=(a*e+b*g,a*f+b*h,c*e+d0*g,c*f+d0*h)
    else:
        out=tuple(sum(A[i*d+k]*B[k*d+j] for k in range(d))
                  for i in range(d) for j in range(d))
    return out if q is None else tuple(x%q for x in out)

def mpow(A: Mat, n: int, q: int) -> Mat:
    out=eye(isqrt(len(A)))
    while n:
        if n&1: out=mm(out,A,q)
        A=mm(A,A,q); n//=2
    return out

def comm(A: Mat, B: Mat, q: int | None = None) -> Mat:
    if len(A)==4:
        a,b,c,d=A; e,f,g,h=B
        z=b*g-f*c
        out=(z,f*(a-d)+b*(h-e),c*(e-h)+g*(d-a),-z)
    else:
        out=tuple(x-y for x,y in zip(mm(A,B),mm(B,A)))
    return out if q is None else tuple(x%q for x in out)

def commute2(A: Mat,B: Mat,q: int) -> bool:
    a,b,c,d=A; e,f,g,h=B
    return ((b*g-f*c)%q==0 and (f*(a-d)+b*(h-e))%q==0
            and (c*(e-h)+g*(d-a))%q==0)

def val(x: int,p: int,n: int) -> int:
    if x==0:return n
    k=0
    while k<n and x%p==0:k+=1;x//=p
    return k

def scalar_depth(A: Mat,p: int,n: int) -> int:
    return min(val(A[1],p,n),val(A[2],p,n),val(A[0]-A[3],p,n))

def cv2(B: Mat,p: int) -> tuple[int,int]:
    for x,y in [(1,0),(0,1),(1,1)]:
        u=B[0]*x+B[1]*y;v=B[2]*x+B[3]*y
        if (x*v-y*u)%p: return x,y
    raise ValueError('Noncyclic input to the two-dimensional cyclic certificate.')

def poly_coeff2(B: Mat, M: Mat, p: int, q: int) -> tuple[int,int]:
    x,y=cv2(B,p);u=B[0]*x+B[1]*y;v=B[2]*x+B[3]*y
    z=M[0]*x+M[1]*y;w=M[2]*x+M[3]*y
    di=pow((x*v-y*u)%q,-1,q)
    return ((v*z-u*w)*di%q,(-y*z+x*w)*di%q)

def classify2(As: tuple[Mat,...],p: int,n: int) -> dict:
    q=p**n
    assert As and all(len(A)==4 for A in As)
    a=min(scalar_depth(A,p,n) for A in As)
    if a==n:
        lifts=tuple((A[0],0,0,A[0]) for A in As)
        return {'ok':True,'a':a,'lifts':lifts,'coefficients':[]}
    star=next(i for i,A in enumerate(As) if scalar_depth(A,p,n)==a)
    pa=p**a;t=p**(n-a)
    lam=[A[0] for A in As]
    Bs=tuple(tuple(((x-l*e)//pa)%t for x,e in zip(A,I2))
             for A,l in zip(As,lam))
    B=Bs[star]
    defects=tuple(comm(B,M,t) for M in Bs)
    if any(any(x for x in D) for D in defects):
        return {'ok':False,'a':a,'star':star,'defects':defects}
    coeff=tuple(poly_coeff2(B,M,p,t) for M in Bs)
    lifts=tuple(tuple(l*e+pa*(u*e+v*x) for e,x in zip(I2,B))
                for l,(u,v) in zip(lam,coeff))
    assert all(tuple(x%q for x in L)==A for L,A in zip(lifts,As))
    assert all(not any(comm(L,M)) for L,M in it.combinations(lifts,2))
    assert all((L[0]*L[3]-L[1]*L[2])%p for L in lifts)
    return {'ok':True,'a':a,'star':star,'lifts':lifts,'coefficients':coeff}

def unipotent_modp(A: Mat,p: int) -> bool:
    return (A[0]+A[3]-2)%p==0 and (A[0]*A[3]-A[1]*A[2]-1)%p==0

def inflation_checks() -> dict:
    cocycles=0; repairs=0; evaluations=0
    J=(0,1,1,0)
    for p in [3,5,7]:
        q=p**3;A=tuple((e+p*x)%q for e,x in zip(I2,J))
        assert mpow(A,p,q)==tuple((e+p*p*x)%q for e,x in zip(I2,J))
        assert mpow(A,p*p,q)==I2
        for a,b,c in it.product(range(p),repeat=3):
            carry=lambda x,y:(x+y)//p
            assert (carry(b,c)-carry((a+b)%p,c)+carry(a,(b+c)%p)-carry(a,b))%p==0
            cocycles+=1
        assert sum((1+t)//p for t in range(p))%p==1
        for x,y in it.product(range(p*p),repeat=2):
            lo_carry=((x%p)+(y%p))//p
            delta=(x//p+y//p-((x+y)%(p*p))//p)%p
            assert (lo_carry+delta)%p==0;repairs+=1
        for x in range(p*p):
            b=x//p;s=x%p
            repair=tuple((e+p*p*b*j)%q for e,j in zip(I2,J))
            assert mm(repair,mpow(A,s,q),q)==mpow(A,x,q)
            evaluations+=1
    return {'primes':[3,5,7],'cocycle_triples':cocycles,
            'all_refined_quotient_pairs':repairs,'repaired_matrix_values':evaluations,
            'negative_finite_quotient_sum_certificates':3}

def centralizer_checks() -> dict:
    tested=0;cyclic=0
    for p,n in [(2,1),(3,1),(5,1),(2,2)]:
        q=p**n; mats=list(it.product(range(q),repeat=4))
        for B in mats:
            if scalar_depth(B,p,1)==1:continue
            cyclic+=1
            polynomials={tuple((u*e+v*x)%q for e,x in zip(I2,B))
                         for u,v in it.product(range(q),repeat=2)}
            assert len(polynomials)==q*q
            actual=set()
            for M in mats:
                tested+=1
                if commute2(B,M,q):actual.add(M)
            assert actual==polynomials
    # All companion matrices over Z/9, compared with every rank-two matrix.
    q=9;p=3;mats=list(it.product(range(q),repeat=4))
    for b,c in it.product(range(q),repeat=2):
        B=(0,-c%q,1,-b%q);cyclic+=1
        polys={tuple((u*e+v*x)%q for e,x in zip(I2,B))
               for u,v in it.product(range(q),repeat=2)}
        actual=set()
        for M in mats:
            tested+=1
            if commute2(B,M,q):actual.add(M)
        assert actual==polys
    return {'full_matrix_rings':[[2,1],[3,1],[5,1],[2,2]],
            'additional_family':'all 81 companion matrices over Z/9',
            'cyclic_matrices':cyclic,'candidate_centralizer_pairs':tested}

def exhaustive_rank2() -> dict:
    results=[];positive_sets={}
    for p,n in [(2,1),(3,1),(2,2),(3,2)]:
        q=p**n
        mats=[A for A in it.product(range(q),repeat=4) if unipotent_modp(A,p)]
        commut=0;positive=0;negative=0;bydepth={};posset=set()
        for A in mats:
            for B in mats:
                if not commute2(A,B,q):continue
                commut+=1
                C=classify2((A,B),p,n)
                bydepth[str(C['a'])]=bydepth.get(str(C['a']),0)+1
                if C['ok']:
                    positive+=1
                    if (p,n)==(2,2):posset.add((A,B))
                else:negative+=1
        results.append({'p':p,'n':n,'generator_matrices':len(mats),
                        'ordered_pairs_examined':len(mats)**2,
                        'valid_continuous_Zp2_actions':commut,
                        'positive_exact_integral_certificates':positive,
                        'negative_normalized_commutator_certificates':negative,
                        'scalar_depth_counts':bydepth})
        if (p,n)==(2,2):positive_sets[(p,n)]=posset
    # Independent test: enumerate every commuting pair over Z/8 with p-power
    # residuals, then take the complete image at level 4. No lift branch skipped.
    mats8=[A for A in it.product(range(8),repeat=4) if unipotent_modp(A,2)]
    images=set();valid8=0
    for A in mats8:
        for B in mats8:
            if commute2(A,B,8):
                valid8+=1;images.add((tuple(x%4 for x in A),tuple(x%4 for x in B)))
    assert images==positive_sets[(2,2)]
    # All tangent triples over F2, not just pairs.
    tangent=list(it.product(range(2),repeat=4));trip=0;pos=0
    for Xs in it.product(tangent,repeat=3):
        As=tuple(tuple((e+2*x)%4 for e,x in zip(I2,X)) for X in Xs)
        test=all(commute2(X,Y,2) for X,Y in it.combinations(Xs,2))
        C=classify2(As,2,2);assert C['ok']==test
        trip+=1;pos+=int(test)
    return {'complete_rank_two_tables':results,
            'independent_Z8_reduction_image':{'all_generator_matrices':len(mats8),
              'all_ordered_pairs':len(mats8)**2,'commuting_actions':valid8,
              'distinct_level4_reductions':len(images),'equal_to_classifier':True},
            'all_F2_tangent_triples':trip,'positive_tangent_triples':pos}

def sharp_horizon_checks() -> dict:
    fixture=0;corrections=0
    E=(0,1,0,0);F=(0,0,1,0);D=(1,0,0,-1)
    for p in [2,3,5,7]:
        for n in range(2,8):
            a=p**(n-1);q=p**(2*n-1)
            A=tuple(e+a*x for e,x in zip(I2,E));B=tuple(e+a*x for e,x in zip(I2,F))
            assert comm(A,B)==tuple(a*a*x for x in D)
            assert not any(comm(A,B,p**(2*n-2))) and any(comm(A,B,q))
            assert classify2((tuple(x%(p**n) for x in A),tuple(x%(p**n) for x in B)),p,n)['ok'] is False
            fixture+=1
    # Exhaustive all matrix corrections from level n to level 2n-1 for
    # precisely these three fixtures, including the two-digit case at p=2.
    for p,n in [(2,2),(3,2),(2,3)]:
        q=p**(2*n-1);step=p**n;k=p**(n-1)
        A=tuple(e+p**(n-1)*x for e,x in zip(I2,E))
        B=tuple(e+p**(n-1)*x for e,x in zip(I2,F))
        ms=list(it.product(range(k),repeat=4))
        As=[tuple((x+step*y)%q for x,y in zip(A,P)) for P in ms]
        Bs=[tuple((x+step*y)%q for x,y in zip(B,Q)) for Q in ms]
        target=tuple((p**(2*n-2)*x)%q for x in D)
        for X in As:
            for Y in Bs:
                assert comm(X,Y,q)==target;corrections+=1
    return {'sharpness_families':fixture,'p_values':[2,3,5,7],'n_range':[2,7],
            'exhaustive_correction_fixtures':[[2,2],[3,2],[2,3]],
            'all_correction_pairs':corrections}

def mv(A: Mat,v: tuple[int,...]) -> tuple[int,...]:
    d=len(v);return tuple(sum(A[i*d+j]*v[j] for j in range(d)) for i in range(d))

def solve_unit(Q: Mat,b: tuple[int,...],p: int,q: int) -> tuple[int,...]:
    d=len(b);rows=[list(Q[i*d:(i+1)*d])+[b[i]%q] for i in range(d)]
    for j in range(d):
        k=next(k for k in range(j,d) if rows[k][j]%p)
        rows[j],rows[k]=rows[k],rows[j]
        u=pow(rows[j][j]%q,-1,q)
        rows[j]=[(x*u)%q for x in rows[j]]
        for k in range(d):
            if k!=j:
                u=rows[k][j];rows[k]=[(x-u*y)%q for x,y in zip(rows[k],rows[j])]
    return tuple(row[-1] for row in rows)

def poly_eval(B: Mat,c: tuple[int,...],q: int|None=None) -> Mat:
    d=isqrt(len(B));out=(0,)*(d*d);power=eye(d)
    for a in c:
        out=tuple(x+a*y for x,y in zip(out,power))
        if q:out=tuple(x%q for x in out)
        power=mm(power,B,q)
    return out

def higher_rank_certificates() -> dict:
    count=0;coeff_count=0
    for p,d,a,extra in it.product([2,3,5],[2,3,4],[1,2],[1,2,3]):
        n=a+extra;q=p**n;t=p**extra;I=eye(d)
        # Companion of t^d+t+1, with the e1 cyclic basis, over Z.
        B=[0]*(d*d)
        for i in range(d-1):B[(i+1)*d+i]=1
        B[d-1]=-1;B[2*d-1]=-1
        B=tuple(B)
        cs=[tuple(int(j==1) for j in range(d)),
            tuple(j+2 for j in range(d)),tuple((j+1)**2 for j in range(d))]
        exact=[tuple(e+p**a*x for e,x in zip(I,poly_eval(B,c))) for c in cs]
        As=[tuple(x%q for x in A) for A in exact]
        Bs=[tuple(((x-e)//(p**a))%t for x,e in zip(A,I)) for A in As]
        base=Bs[0];v=(1,)+(0,)*(d-1);cols=[];w=v
        for j in range(d):cols.append(w);w=mv(base,w)
        Q=tuple(cols[j][i]%t for i in range(d) for j in range(d))
        rec=[]
        for M in Bs:
            assert not any(comm(base,M,t))
            c=solve_unit(Q,tuple(x%t for x in mv(M,v)),p,t)
            assert poly_eval(base,c,t)==M
            rec.append(tuple(e+p**a*x for e,x in zip(I,poly_eval(base,c))))
            coeff_count+=1
        assert all(tuple(x%q for x in A)==B0 for A,B0 in zip(rec,As))
        assert all(not any(comm(A,B0)) for A,B0 in it.combinations(rec,2))
        # Matrices are I mod p. Finite powers test the proved continuity bound.
        for A in rec:
            for j in range(4):
                assert mpow(A,p**j,p**(j+1))==I
        count+=1
    return {'p_values':[2,3,5],'ranks':[2,3,4],'scalar_depths':[1,2],
            'precision_above_depth':[1,2,3],'three_generator_fixtures':count,
            'recovered_polynomial_certificates':coeff_count,
            'finite_continuity_checks':count*3*4}

def worked_example() -> dict:
    A=(1,3,9,1);B=(7,12,9,7);C=(7,12,36,7)
    assert comm(A,B)==(-81,0,0,81)
    assert not any(comm(A,C)) and tuple(x%27 for x in C)==B
    cert=classify2((A,B),3,3);assert cert['ok']
    return {'p':3,'n':3,'input':[A,B],'displayed_exact_lift':[A,C],
            'algorithmic_certificate':cert,
            'note':'The deterministic scalar choices may give a different valid integral lift.'}

def main() -> int:
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('profinite_results.json'))
    args=parser.parse_args();start=time.monotonic();records={};times={}
    for name,fun in [('source_inflation',inflation_checks),('centralizers',centralizer_checks),
                     ('rank_two_decision',exhaustive_rank2),('sharp_horizon',sharp_horizon_checks),
                     ('higher_rank_cyclic_strata',higher_rank_certificates),('worked_example',worked_example)]:
        tic=time.monotonic();records[name]=fun();times[name]=time.monotonic()-tic
        print(name,'PASS',round(times[name],3),flush=True)
    result={'schema':'komorebi-profinite-regression-v1','status':'PASS',
            'python':platform.python_version(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'arithmetic':'exact integers and modular arithmetic','randomness':'none',
            'tested_families':records,'timings_seconds':times,'wall_seconds':time.monotonic()-start,
            'nonclaims':['No universal theorem or continuous limit is proved by the sweep.',
                        'No general Galois, determinant-constrained, or automorphic lifting test.',
                        'Only specified matrix families are exhaustive. Higher-rank strata are constructed fixtures.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n');return 0

if __name__=='__main__':raise SystemExit(main())
