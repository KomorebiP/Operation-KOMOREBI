#!/usr/bin/env python3
"""Deterministic exact-rational checks for moving kernel spaces.

This audits finite matrix identities against independent nullspace computation.
It is supplementary: Hilbert-space and all-real conclusions are proved in Lean.
No floating point, randomized sampling, or numerical eigenvalue is used.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import argparse, json

Matrix = list[list[F]]
assertions = 0
counts = {'split_systems':0, 'candidate_vectors':0, 'measurement_cases':0,
          'moving_line_slopes':0, 'rank_loss_witnesses':0}

def check(value: bool, message: str) -> None:
    global assertions
    assertions += 1
    if not value:
        raise AssertionError(message)

def eye(n: int) -> Matrix:
    return [[F(i == j) for j in range(n)] for i in range(n)]

def zeros(n:int,m:int) -> Matrix:
    return [[F(0) for _ in range(m)] for _ in range(n)]

def transpose(a:Matrix) -> Matrix:
    return list(map(list,zip(*a)))

def add(a:Matrix,b:Matrix) -> Matrix:
    return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]

def neg(a:Matrix) -> Matrix:
    return [[-v for v in row] for row in a]

def sub(a:Matrix,b:Matrix) -> Matrix:
    return add(a,neg(b))

def scale(c:F,a:Matrix) -> Matrix:
    return [[c*x for x in row] for row in a]

def mul(a:Matrix,b:Matrix) -> Matrix:
    if len(a[0]) != len(b):
        raise ValueError('Incompatible matrix dimensions')
    return [[sum((x*y for x,y in zip(ar,bc)),F(0)) for bc in zip(*b)] for ar in a]

def rref(a:Matrix):
    a=[row[:] for row in a]; nr=len(a);nc=len(a[0]);piv=[];r=0
    for c in range(nc):
        candidate=next((i for i in range(r,nr) if a[i][c]),None)
        if candidate is None:continue
        a[r],a[candidate]=a[candidate],a[r];s=a[r][c]
        a[r]=[v/s for v in a[r]]
        for i in range(nr):
            if i!=r:
                s=a[i][c];a[i]=[x-s*y for x,y in zip(a[i],a[r])]
        piv.append(c);r+=1
        if r==nr:break
    return a,piv

def inverse(a:Matrix) -> Matrix:
    n=len(a)
    if len(a[0])!=n:raise ValueError('Inverse requires square matrix')
    aug=[row+ident for row,ident in zip(a,eye(n))]
    rr,piv=rref(aug)
    if piv[:n]!=list(range(n)):raise ValueError('Singular inverse')
    inv=[row[n:] for row in rr]
    check(mul(a,inv)==eye(n) and mul(inv,a)==eye(n),'Inverse identities')
    return inv

def kernel_projection(a:Matrix) -> Matrix:
    n=len(a[0]); rr,piv=rref(a);free=[j for j in range(n) if j not in piv]
    if not free:return zeros(n,n)
    cols=[]
    for j in free:
        x=[F(0)]*n;x[j]=1
        for i,p in enumerate(piv):x[p]=-rr[i][j]
        cols.append(x)
    basis=transpose(cols)
    return mul(mul(basis,inverse(mul(transpose(basis),basis))),transpose(basis))

def psd(a:Matrix) -> bool:
    if a!=transpose(a):return False
    a=[row[:] for row in a];n=len(a)
    for k in range(n):
        if a[k][k]<0:return False
        if a[k][k]==0:
            if any(a[j][k] for j in range(k+1,n)):return False
            continue
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):a[i][j]-=a[i][k]*a[k][j]/pivot
    return True

def norm_sq(a:Matrix) -> F:
    return sum((x*x for row in a for x in row),F(0))

def sqrt_upper(q:F,den:int=256) -> F:
    if q<0:raise ValueError('Negative squared norm')
    qq=q*den*den;n=isqrt(qq.numerator//qq.denominator)
    if F(n*n)<qq:n+=1
    ans=F(n,den)
    check(ans>=0 and ans*ans>=q,'Directed rational square-root upper bound')
    return ans

def operator_bound(a:Matrix,c:F) -> bool:
    return c>=0 and psd(sub(scale(c*c,eye(len(a[0]))),mul(transpose(a),a)))

def run() -> dict:
    slopes=[F(i,j) for j in [1,2,8] for i in range(-3,4)]
    for t in sorted(set(slopes)):
        d=[[F(1),t]];q=kernel_projection(d);q0=kernel_projection([[F(1),F(0)]])
        expected=scale(1/(1+t*t),[[t*t,-t],[-t,F(1)]])
        check(q==expected,'Moving-line projection from independent nullspace')
        diff=sub(q,q0)
        check(mul(transpose(diff),diff)==scale(t*t/(1+t*t),eye(2)),
              'All-vector squared motion identity')
        check(operator_bound(diff,abs(t)),'Uniform line Lipschitz estimate')
        check(mul(d,[[-t],[F(1)]])==[[F(0)]],'Moving exact vector')
        if t:
            check(mul(d,[[F(0)],[F(7)]])!=[[F(0)]],'Old exact vector not preserved')
        counts['moving_line_slopes']+=1

    for n in [2,3,4]:
        for r in range(1,n):
            d=[[F(i==j) if j<r else F(((i+1)*(j+2))%5-2,3)
                 for j in range(n)] for i in range(r)]
            a=mul(transpose(d),inverse(mul(d,transpose(d))))
            aa=sqrt_upper(norm_sq(a))
            check(mul(d,a)==eye(r),'Old section right inverse')
            q=kernel_projection(d)
            check(sub(eye(n),mul(a,d))==q,'Independent old projection agreement')
            perturb=[[F(((i+2)*(j+1))%7-3,4) for j in range(n)] for i in range(r)]
            for t in [F(-1,16),F(-1,32),F(-1,64),F(1,64),F(1,32),F(1,16)]:
                e=add(d,scale(t,perturb));eps=sqrt_upper(norm_sq(sub(d,e)))
                check(aa*eps<1,'Strict split perturbation radius')
                ap=mul(a,inverse(mul(e,a)));cp=aa/(1-aa*eps);motion=cp*eps
                qe=kernel_projection(e)
                check(mul(e,ap)==eye(r),'Constructed perturbed section right inverse')
                check(operator_bound(ap,cp),'Derived section norm bound')
                check(qe==transpose(qe) and mul(qe,qe)==qe,'New projection geometry')
                check(mul(e,qe)==zeros(r,n),'New exact range')
                check(psd(sub(scale(cp*cp,mul(transpose(e),e)),sub(eye(n),qe))),
                      'All-vector perturbed residual estimate')
                check(operator_bound(sub(q,qe),motion),'Constructed projection-motion budget')
                a_true=mul(transpose(e),inverse(mul(e,transpose(e))))
                c_true=sqrt_upper(norm_sq(a_true))
                check(operator_bound(sub(q,qe),max(aa,c_true)*eps),'Two-sided maximum gain bound')
                retract_new=sub(eye(n),mul(ap,e));retract_old=sub(eye(n),mul(a,d))
                check(mul(mul(retract_old,retract_new),q)==q,'Old/new kernel inverse I')
                check(mul(mul(retract_new,retract_old),qe)==qe,'Old/new kernel inverse II')
                for k in range(-4,5):
                    x=[[F(((k+2)*(j+3))%11-5,3)] for j in range(n)]
                    px=mul(qe,x);res=mul(e,x)
                    check(norm_sq(sub(x,px))<=cp*cp*norm_sq(res),'Candidate new repair')
                    old_exact=mul(q,x);new_exact=mul(retract_new,old_exact)
                    check(mul(e,new_exact)==zeros(r,1),'Kernel transport exactness')
                    check(norm_sq(sub(new_exact,old_exact))<=motion*motion*norm_sq(old_exact),
                          'Kernel transport displacement')
                    counts['candidate_vectors']+=1
                    noise=[[F(1 if (j+k)%2==0 else -1,128)] for j in range(r)]
                    measured=add(res,noise);eta=sqrt_upper(norm_sq(noise));yn=sqrt_upper(norm_sq(measured))
                    check(norm_sq(sub(x,px))<=cp*cp*(yn+eta)**2,'Measured new-space error budget')
                    counts['measurement_cases']+=1
                counts['split_systems']+=1

    for n in range(1,33):
        t=F(1,n+1);d=[[F(1),F(0)],[F(0),F(0)]];e=[[F(1),F(0)],[F(0),t]]
        q=kernel_projection(d);qe=kernel_projection(e);unit=[[F(0)],[F(1)]]
        check(norm_sq(mul(sub(q,qe),unit))==1,'Rank-loss projection jump')
        check(norm_sq(mul(e,unit))==t*t,'Gain blow-up witness')
        check(F(1,t)*t==1,'Necessary gain lower threshold')
        counts['rank_loss_witnesses']+=1

    rejected={}
    d=[[F(1),F(0)]];t=F(1,8);e=[[F(1),t]]
    q=kernel_projection(d);qe=kernel_projection(e)
    check(q!=qe,'Counterexample: same kernel from small error')
    rejected['small_error_forces_equal_kernels']=True
    d_rank=[[F(1),F(0)],[F(0),F(0)]];e_rank=[[F(1),F(0)],[F(0),F(1,100)]]
    check(not operator_bound(sub(kernel_projection(d_rank),kernel_projection(e_rank)),F(1,100)),
          'Counterexample: old gain alone without onto premise')
    rejected['old_gain_alone_without_surjectivity_or_new_gain']=True
    check(len(rref([[F(0)]])[1])==0,'Counterexample: radius endpoint loses surjectivity')
    rejected['closed_perturbation_radius_is_sufficient']=True
    old_unit=[[F(0)],[F(1)]];transport=[[-t],[F(1)]]
    check(mul(qe,old_unit)!=transport,'Counterexample: graph transport equals orthogonal projection')
    rejected['kernel_transport_is_orthogonal_projection']=True
    return {'schema':'komorebi-moving-spaces-exact-audit-v1','status':'PASS',
            'arithmetic':'fractions.Fraction, exact Gaussian elimination and rational PSD checks',
            'randomness':False,'counts':counts,'assertions':assertions,
            'rejected_false_claims':rejected,
            'nonclaims':['Finite matrices do not prove arbitrary Hilbert-space theorems.',
             'Rational Frobenius bounds are conservative, not optimal singular values.',
             'The Python checker is not formally verified; Lean proofs do not trust its output.',
             'Input dimensions 2 through 4 and the declared perturbation/slopes are bounded fixtures.']}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=run();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
