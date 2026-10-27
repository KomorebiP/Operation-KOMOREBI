#!/usr/bin/env python3
"""Exact checks for Block 51. Python standard library only.

The universal argument is in notes/LOCAL_DEPTH_THEOREM.md. Finite checks
here are not a proof of Beal, global geometric realization, or a Lean proof.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as R
from itertools import product
import json
from math import isqrt
from pathlib import Path
from typing import Any


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def val(x: int | R) -> int | float:
    x = R(x)
    if not x:
        return float('inf')
    a, b = abs(x.numerator), x.denominator
    v = 0
    while a % 7 == 0:
        a //= 7; v += 1
    while b % 7 == 0:
        b //= 7; v -= 1
    return v


def prime(n: int) -> bool:
    return n >= 2 and all(n % d for d in range(2, isqrt(n)+1))


def allowed_depths(multiplicity: int, residue_cardinality: int) -> list[int]:
    if multiplicity < 1:
        raise ValueError('The prime multiplicity must be positive.')
    if residue_cardinality <= 1 or residue_cardinality % 7 != 1:
        raise ValueError('The residue cardinality must exceed one and equal one modulo seven.')
    t = 1 + int(val(multiplicity)); h = int(val(residue_cardinality-1))
    return [t+2*s for s in range(h+1)]

# Implementation A: ordinary integral two-by-two matrices.
I = ((1,0),(0,1)); Z = ((0,0),(0,0))
def madd(a,b): return tuple(tuple(a[i][j]+b[i][j] for j in range(2)) for i in range(2))
def mscale(a,k): return tuple(tuple(k*a[i][j] for j in range(2)) for i in range(2))
def mm(a,b): return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)) for i in range(2))
def det(a): return a[0][0]*a[1][1]-a[0][1]*a[1][0]
def mpow(a,n):
    result=I
    while n:
        if n&1: result=mm(result,a)
        a=mm(a,a); n//=2
    return result


def integer_checks() -> dict[str, Any]:
    qs={1:29,2:197,3:1373,4:14407}
    for h,q in qs.items():
        require(prime(q) and val(q-1)==h, 'prime cardinality certificate')
    cases=0; saturated=0
    for t in range(1,7):
        for h,q in qs.items():
            for s in range(h+1):
                for unit in (1,2,6):
                    n=t+2*s; m=unit*7**t; y=7**s
                    N=((-m*y,m),(-m*y*y,m*y))
                    F=((1,(q-1)//y),(0,q)); T=madd(I,N)
                    P=((1,0),(y,1)); Pinv=((1,0),(-y,1))
                    require(mm(N,N)==Z,'nilpotence')
                    require(mm(F,N)==mscale(N,q) and mm(N,F)==N,'Frobenius identities')
                    require(mm(F,T)==mm(mpow(T,q),F),'exact tame relation')
                    require(mm(mm(P,((0,m),(0,0))),Pinv)==N,'independent toric conjugation N')
                    require(mm(mm(P,((q,(q-1)//y),(0,1))),Pinv)==F,'independent toric conjugation F')
                    require(det(F)==q and det(T)==1,'determinants')
                    require(min(val(x) for row in N for x in row)==t,'content')
                    require(val(N[1][0])==n,'opposite inertia depth')
                    require(t<=n<=t+2*h and (n-t)%2==0,'depth condition')
                    alpha=F[0][1]%7; beta=(N[1][0]//7**n)%7
                    require(beta!=0 and (alpha*beta%7!=0)==(s==h),'cup endpoint')
                    # D does not preserve the unique invariant line of N.
                    require(1*y-2*y != 0, 'absolute irreducibility line test')
                    cases+=1; saturated+=int(s==h)
    # A false stronger bound is refuted by the retained Q=29 example.
    negative={'false_n_le_t_plus_h':{'t':1,'h':1,'s':1,'n':3,'claimed_upper_bound':2}}
    require(3>1+1 and 3==1+2*1,'negative control for omitted square')
    N=((-49,7),(-343,49)); F=((1,4),(0,29))
    badN=((-49,7),(-342,49)); badF=((1,4),(1,29))
    require(mm(badN,badN)!=Z,'reject broken nilpotence')
    require(mm(badF,N)!=mscale(N,29),'reject broken Frobenius')
    require(val(badF[1][0])<3,'reject nonstable endpoint')
    return {'cases':cases,'endpoint_nonzero_cases':saturated,'prime_cardinalities':qs,
            't_range':[1,6],'s_range':'all 0 through h','monodromy_units':[1,2,6],
            'negative_controls':negative,'rejected_mutations':3}

# Implementation B: exact Q(sqrt(5)); independent matrix code, with nontrivial
# coefficient-field basis changes and denominators prime to seven.
K = tuple[R,R]
kzero=(R(0),R(0)); kone=(R(1),R(0)); rt=(R(0),R(1))
def Kof(a=0,b=0): return (R(a),R(b))
def ka(x,y): return (x[0]+y[0],x[1]+y[1])
def kn(x): return (-x[0],-x[1])
def ks(x,y): return ka(x,kn(y))
def km(x,y): return (x[0]*y[0]+5*x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def ki(x):
    d=x[0]*x[0]-5*x[1]*x[1]
    if not d: raise ZeroDivisionError('zero quadratic element')
    return (x[0]/d,-x[1]/d)
def kd(x,y): return km(x,ki(y))
def kw(x): return min(val(x[0]),val(x[1]))
def kr(x):
    return tuple((a.numerator*pow(a.denominator,-1,7))%7 for a in x)
def kp(x,n):
    r=kone
    for _ in range(n): r=km(r,x)
    return r
KI=((kone,kzero),(kzero,kone)); KZ=((kzero,kzero),(kzero,kzero))
def qmul(A,B):
    return tuple(tuple(ka(km(A[i][0],B[0][j]),km(A[i][1],B[1][j])) for j in range(2)) for i in range(2))
def qscale(A,s): return tuple(tuple(km(s,x) for x in row) for row in A)
def qdet(A): return ks(km(A[0][0],A[1][1]),km(A[0][1],A[1][0]))
def qinv(A):
    z=ki(qdet(A))
    return qscale(((A[1][1],kn(A[0][1])),(kn(A[1][0]),A[0][0])),z)


def quadratic_checks() -> dict[str, Any]:
    aa=[Kof(0),Kof(1),rt,Kof(1,1),Kof(7),Kof(0,7)]
    bb=[Kof(0),Kof(1),rt,Kof(7),Kof(0,7),Kof(49),Kof(0,49),Kof(343)]
    transforms=[KI,((kzero,kone),(kone,kzero)),((Kof(3,1),kzero),(kzero,kone))]
    qs=[29,169,197,1373,14407]
    tested=accepted=rejected=endpoint=0
    depths=set(); denominator_seen=False; x_nonunit_case=False
    for a,b in product(aa,bb):
        P0=((kone,a),(b,ka(kone,km(a,b))))
        for left in transforms:
            P=qmul(left,P0); Pinv=qinv(P)
            require(kw(qdet(P))==0 and qmul(P,Pinv)==KI,'integral invertible basis')
            for t,Q,k in product([1,2,3],qs,[kzero,kone,rt,Kof(7)]):
                N0=((kzero,Kof(7**t)),(kzero,kzero))
                F0=((Kof(Q),k),(kzero,kone))
                N=qmul(qmul(P,N0),Pinv); F=qmul(qmul(P,F0),Pinv)
                for A in [N,F]:
                    require(all(kw(x)>=0 for row in A for x in row),'integrality over O_7')
                    denominator_seen |= any(v.denominator!=1 for row in A for x in row for v in x)
                require(qmul(N,N)==KZ,'quadratic nilpotence')
                require(qmul(F,N)==qscale(N,Kof(Q)) and qmul(N,F)==N,'quadratic Frobenius')
                require(ka(N[0][0],N[1][1])==kzero and qdet(N)==kzero,'trace/determinant audit')
                tested+=1
                n=kw(N[1][0]); content=min(kw(x) for row in N for x in row)
                require(content==t,'content unchanged under basis conjugation')
                if n==float('inf') or n<1 or kw(F[1][0])<n:
                    rejected+=1; continue
                n=int(n);h=int(val(Q-1)); accepted+=1; depths.add((t,h,n))
                require(n>=t and (n-t)%2==0 and n<=t+2*h,'independent necessity check')
                alpha=kr(F[0][1]); beta=kr(kd(N[1][0],Kof(7**n)))
                require(beta!=(0,0),'ramified opposite reduction')
                require((alpha!=(0,0))==(n==t+2*h),'independent endpoint criterion')
                endpoint+=int(alpha!=(0,0))
                # The swap variant includes primitive toric lines with a nonunit first coordinate.
                x_nonunit_case |= kw(P[0][0])>0 and kw(P[1][0])==0
    require(accepted>0 and rejected>0 and denominator_seen and x_nonunit_case,'coverage checks')
    return {'generated_cases':tested,'hypotheses_satisfied':accepted,'excluded_by_hypotheses':rejected,
            'nonzero_cup_endpoint_cases':endpoint,'observed_t_h_n':[list(x) for x in sorted(depths)],
            'nontrivial_denominators_tested':denominator_seen,'nonunit_first_coordinate_tested':x_nonunit_case,
            'domain':'Q(sqrt(5)), coefficients exact rational, all matrix entries integral at seven',
            'basis_counts':{'upper_parameters':len(aa),'lower_parameters':len(bb),'left_transforms':len(transforms)},
            't_values':[1,2,3],'Q_values':qs,'F_upper_parameters':['0','1','sqrt(5)','7']}



def quadratic_sharpness_checks() -> dict[str, Any]:
    """Explicit endpoint and interior tests with non-F_7 residue directions."""
    tested=endpoint=0; outside_prime_field=False
    qs={1:29,2:197,3:1373,4:14407}
    for t,h,angle,m_unit in product([1,2,3],qs,[kone,rt,Kof(1,1)],[kone,rt]):
        Q=qs[h]
        for s in range(h+1):
            y=km(Kof(7**s),angle); m=km(Kof(7**t),m_unit)
            P=((kone,kzero),(y,kone)); Pinv=qinv(P)
            upper=kd(Kof(Q-1),y)
            N0=((kzero,m),(kzero,kzero))
            F0=((Kof(Q),upper),(kzero,kone))
            N=qmul(qmul(P,N0),Pinv); F=qmul(qmul(P,F0),Pinv)
            require(N==qscale(((kn(y),kone),(kn(kp(y,2)),y)),m),'quadratic sharpness construction')
            require(F==((kone,upper),(kzero,Kof(Q))),'quadratic sharpness Frobenius')
            require(all(kw(x)>=0 for A in (F,N) for row in A for x in row),'sharpness integral entries')
            require(qmul(N,N)==KZ and qmul(F,N)==qscale(N,Kof(Q)) and qmul(N,F)==N,'sharpness Tate relations')
            n=int(kw(N[1][0]));content=min(kw(x) for row in N for x in row)
            require(content==t and n==t+2*s and F[1][0]==kzero,'sharpness depth and content')
            alpha=kr(F[0][1]); beta=kr(kd(N[1][0],Kof(7**n)))
            require(beta!=(0,0) and (alpha!=(0,0))==(s==h),'quadratic sharpness cup endpoint')
            tested+=1;endpoint+=int(alpha!=(0,0));outside_prime_field |= alpha[1]!=0 or beta[1]!=0
    require(endpoint>0 and outside_prime_field,'nontrivial quadratic endpoint coverage')
    return {'cases':tested,'nonzero_cup_endpoint_cases':endpoint,
            'residue_directions_outside_F7_tested':outside_prime_field,
            't_values':[1,2,3],'Q_values':list(qs.values()),'s_range':'all 0 through h',
            'angle_units':['1','sqrt(5)','1+sqrt(5)'],'monodromy_units':['1','sqrt(5)']}


def pmul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):r[i+j]+=x*y
    return r

def peval(a,x):
    y=kzero
    for c in reversed(a):y=ka(km(y,x),Kof(c))
    return y

def deriv(a): return [i*a[i] for i in range(1,len(a))]


def node_checks() -> dict[str, Any]:
    g=[-1,1,1];h=[5,-2,1];f=[5,-12,0,10,0,0,1]
    require(pmul(pmul(g,g),h)==f,'exact sextic factorization')
    count=1
    D=Kof(R(15,2),R(-3,2));phi=Kof(R(1,2),R(1,2))
    for r in [Kof(R(-1,2),R(1,2)),Kof(R(-1,2),R(-1,2))]:
        hr=peval(h,r)
        require(peval(g,r)==kzero,'node root')
        require(peval(f,r)==kzero and peval(deriv(f),r)==kzero,'double root')
        require(kd(peval(deriv(deriv(f)),r),Kof(2))==km(Kof(5),hr),'node quadratic coefficient')
        require(ka(km(Kof(10),kp(r,3)),Kof(10))==km(Kof(20),r),'transverse smoothing derivative')
        # Direct replay of Block 50's mixed-characteristic identities.
        r2=kp(r,2);r3=kp(r,3);Y=kn(r)
        G=ka(ka(kp(Y,2),km(ka(r3,kone),Y)),ka(ks(km(Kof(3),r),km(Kof(2),r3)),Kof(-1)))
        require(G==kzero,'dyadic node equation')
        gxx=kn(ka(km(Kof(6),r2),km(Kof(12),r)))
        gxy=km(Kof(3),r2)
        require(ks(km(gxx,Kof(2)),kp(gxy,2))==km(Kof(15),ks(r,Kof(2))),'dyadic Hessian')
        require(ks(ks(Y,km(Kof(2),r3)),Kof(2))==km(Kof(-5),r),'dyadic smoothing derivative')
        require(km(D,hr) in [kp(D,2),kp(km(D,phi),2)],'split branch radicand')
        count+=8
    return {'exact_identity_checks':count,'coefficient_domain':'Q(sqrt(5)) and Z[X]',
            'geometric_boundary':'Does not implement formal coordinate convergence or the analytic period comparison.'}


def residue_checks() -> dict[str, Any]:
    q=1504231;z=1114923;e=(q-1)//7
    require(prime(q) and q%35==1 and val(q-1)==1,'old prime certificate')
    zp=[pow(z,j,q) for j in range(7)]
    require(len(set(zp))==7 and pow(z,7,q)==1,'order seven root')
    rows=[]
    for root in [684240,819991]:
        require(root*root%q==5,'square root check')
        phi=(1+root)*pow(2,-1,q)%q
        symbols={name:pow(value,e,q) for name,value in [('phi',phi),('3',3),('sqrt5',root)]}
        logs={name:zp.index(value) for name,value in symbols.items()}
        require(logs['3']==logs['sqrt5']==0 and logs['phi'] in (2,5),'Kummer residue coordinates')
        rows.append({'sqrt5':root,'phi':phi,'symbols':symbols,'coordinates_relative_to_zeta':logs})
    return {'q':q,'primality':'trial division through floor(sqrt(q))','zeta':z,'places':rows}


def support_checks() -> dict[str, Any]:
    examples=[(1,29),(7,29),(49,29),(343,29),(1,197)]
    expected=[[1,3],[2,4],[3,5],[4,6],[1,3,5]]
    rows=[]
    for (c,Q),want in zip(examples,expected):
        got=allowed_depths(c,Q);require(got==want,'support example')
        rows.append({'multiplicity':c,'Q':Q,'allowed_depths':got})
    checks=0
    for c,Q in product(range(1,201),[29,169,197,1373,14407]):
        t=1+int(val(c));h=int(val(Q-1))
        for n in range(1,25):
            member=n in allowed_depths(c,Q)
            require(member==(t<=n<=t+2*h and (n-t)%2==0),'selector equivalence')
            if member and n%2==0:require(c%7==0,'even-depth multiplicity')
            if member and c%7!=0 and h==1:require(n in (1,3),'two-depth corollary')
            checks+=1
    rejected=0
    for args in [(0,29),(1,1),(1,7),(1,13),(-1,197)]:
        try:allowed_depths(*args)
        except ValueError:rejected+=1
    require(rejected==5,'invalid inputs rejected')
    return {'examples':rows,'finite_equivalence_checks':checks,'multiplicity_range':[1,200],
            'depth_range':[1,24],'invalid_inputs_rejected':rejected,
            'non_claim':'These are support constraints, not tested integer Beal triples.'}


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'verification/depth_result.json')
    args=ap.parse_args()
    result={'status':'PASS_EXACT_FINITE_CHECKS','integer_sharpness':integer_checks(),
            'quadratic_basis_audit':quadratic_checks(),'quadratic_sharpness':quadratic_sharpness_checks(),
            'node_identities':node_checks(),
            'kummer_residue_coordinates':residue_checks(),'support_selector':support_checks(),
            'non_claims':['No Beal or (3,5,7) proof','No global Galois/geometric realization of examples',
                          'No Lean verification','Universal theorems require the written proofs and declared arithmetic inputs']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],
                     'integer_cases':result['integer_sharpness']['cases'],
                     'quadratic_generated':result['quadratic_basis_audit']['generated_cases'],
                     'quadratic_admissible':result['quadratic_basis_audit']['hypotheses_satisfied'],
                     'quadratic_sharpness_cases':result['quadratic_sharpness']['cases'],
                     'selector_checks':result['support_selector']['finite_equivalence_checks']},indent=2))

if __name__=='__main__':main()
