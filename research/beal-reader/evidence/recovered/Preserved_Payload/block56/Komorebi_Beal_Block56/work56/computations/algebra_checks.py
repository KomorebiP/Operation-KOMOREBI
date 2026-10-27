#!/usr/bin/env python3
"""Exact finite audits for Block56's universal algebra and local controls.

Generated matrices are algebraic tests, not global Frey representations.
All numbers are integers in Z[phi], phi^2=phi+1, or exact residue rings.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def need(x,msg):
    if not x:raise ValueError(msg)

def add(x,y):return (x[0]+y[0],x[1]+y[1])
def neg(x):return (-x[0],-x[1])
def sub(x,y):return add(x,neg(y))
def mul(x,y):
    a,b=x;c,d=y
    return (a*c+b*d,a*d+b*c+b*d)
def scale(k,x):return (k*x[0],k*x[1])
def norm(x):a,b=x;return a*a+a*b-b*b
def invmod(x,M):
    a,b=x;k=pow(norm(x),-1,M)
    return ((a+b)*k%M,-b*k%M)
def mod(x,M):return (x[0]%M,x[1]%M)
def val(x):
    d=math.gcd(*x)
    if d==0:return None
    n=0
    while d%7==0:d//=7;n+=1
    return n

def matmul(A,B):return [[sum(A[i][k]*B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def mat_scale(s,A):return [[s*x for x in row] for row in A]
def fpow(a,n,q):
    r=(1,0)
    while n:
        if n&1:r=mod(mul(r,a),q)
        a=mod(mul(a,a),q);n//=2
    return r

def run():
    cases=0;tight=0;improved=0;nonrational=0
    for n in range(1,11):
        m=n//2+1;M=7**(n+5)
        for h in range(7):
            r=min(n,m+h)
            for k in (1,2,3):
                Q=1+7**h*k
                for u in ((1,0),(0,1),(1,1),(2,3),(6,5)):
                    eta=add((1,0),scale(7**m,u));d=invmod(eta,M)
                    need(mod(mul(eta,d),M)==(1,0),'Inverse failure')
                    for z in ((0,0),(1,0),(0,1),(2,1)):
                        a=add(scale(Q,eta),scale(7**n,z));c=sub(mul(a,d),(Q,0))
                        need(c[0]%7**n==0 and c[1]%7**n==0,'Depth hypothesis')
                        tr=add(a,d);err=sub(tr,(Q+1,0));w=val(err)
                        need(w is None or w>=r,'Trace precision failure')
                        detI=sub((Q+1,0),tr)
                        need(norm(detI)%7**(2*r)==0,'Norm order precision failure')
                        # Norm of rank-two polynomial, written via trace/norm of its trace.
                        trsum=2*tr[0]+tr[1]
                        P=[Q*Q,-Q*trsum,norm(tr)+2*Q,-trsum,1]
                        target=[Q*Q,-2*Q*(Q+1),(Q+1)**2+2*Q,-2*(Q+1),1]
                        need(all((x-y)%7**r==0 for x,y in zip(P,target)),'Restriction-of-scalars precision')
                        cases+=1;tight+=(w==r);improved+=(r>m);nonrational+=(u[1]!=0 or z[1]!=0)
    # Positive precision control: n=2 never licenses an n=3 conclusion merely from h=2.
    Q=491;F=[[540,1],[49,1]]
    need(F[0][0]*F[1][1]-F[0][1]*F[1][0]==Q,'Boundary determinant')
    need((F[0][0]+F[1][1]-(Q+1))%49==0 and (F[0][0]+F[1][1]-(Q+1))%343!=0,'Missing sharpness control')
    local=[]
    for q,c in ((97,1),(293,6)):
        Q=q*q;mu=7*c;N=[[-7*mu,mu],[-49*mu,7*mu]];F=[[Q,0],[7*(Q-1),1]]
        need(matmul(N,N)==[[0,0],[0,0]],'Nilpotence')
        need(matmul(F,N)==mat_scale(Q,N) and matmul(N,F)==N,'Toric Frobenius identities')
        need(F[0][0]*F[1][1]-F[0][1]*F[1][0]==Q,'Toric determinant')
        need(N[1][0]%343==0 and N[1][0]%2401!=0 and F[1][0]%343==0,'Actual local depth3 control')
        etaI=pow(1+49*c,-1,343);lam=((etaI-1)//49)%7
        need(lam==(-c)%7,'Inertia coordinate normalization')
        need(pow(etaI,7,343)==1 and etaI!=1,'Inertia order7')
        sym=fpow((0,1),(Q-1)//7,q)
        need(sym!=(1,0) and fpow(sym,7,q)==(1,0),'Nonzero phi symbol')
        for a in ((2,0),(3,0),(-1,2),(7,0)):
            need(fpow(a,(Q-1)//7,q)==(1,0),'Fixed-unit symbol not zero')
        local.append({'q':q,'Q':Q,'N':N,'F':F,'eta_inertia_mod343':etaI,'lambda':lam,
                      'eta_Frobenius_mod343':1,'phi_seventh_symbol':list(sym),
                      'natural_F12':0,'interpretation':'local model only, not a global Frey realization'})
    need(sum(r['lambda'] for r in local)%7==0,'Reciprocal 97/293 line')
    # Generic Weil-polynomial constraints alone do not give the new exclusions.
    weil_controls=[]
    for q,f,trace,modulus in ((491,1,2,49),(197,2,51,343)):
        Q=q**f
        need(trace*trace<4*Q,'Non-Weil rank-two roots')
        P=[Q*Q,-2*Q*trace,trace*trace+2*Q,-2*trace,1]
        target=[Q*Q,-2*Q*(Q+1),(Q+1)**2+2*Q,-2*(Q+1),1]
        need(all((a-b)%modulus==0 for a,b in zip(P,target)),'Weil-control congruence')
        need(sum(P)==(Q+1-trace)**2,'Weil-control order')
        weil_controls.append({'q':q,'f':f,'local_rank_two_trace':trace,'modulus':modulus,
                              'polynomial_ascending':P,'order':sum(P),
                              'interpretation':'compatible Weil polynomial, not a counted Frey reduction'})
    prior=1566013238790
    need(math.prod((2,3,5,7,11,13,19,29,31,43,71))==prior,'Inherited divisor arithmetic')
    return {'schema':'beal.block56.algebra.v1','status':'PASS_DECLARED_ALGEBRA_CHECKS',
            'matrix_cases':cases,'nonrational_cases':nonrational,'tight_precision_cases':tight,
            'cases_improving_the_old_m_bound':improved,
            'range':{'n':[1,10],'h':[0,6],'norm_unit_factors':[1,2,3],'five_eta_units':True,'four_depth_errors':True},
            'sharpness_control':{'n':2,'Q':491,'matrix':[[540,1],[49,1]],'trace_difference':49},
            'local_97_293_survivors':local,'generic_Weil_controls':weil_controls,
            'necessary_divisors':{'n_ge_2':prior*491,'n_ge_3':prior*491*197},
            'nonclaims':['Finite matrices are not global Galois representations','Local controls do not prove a Beal solution']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    x=run();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:x[k] for k in ('status','matrix_cases','tight_precision_cases','cases_improving_the_old_m_bound')}))
if __name__=='__main__':main()
