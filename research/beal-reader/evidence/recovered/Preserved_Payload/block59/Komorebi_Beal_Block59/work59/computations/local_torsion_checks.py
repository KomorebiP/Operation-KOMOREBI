#!/usr/bin/env python3
"""Exact same-lattice local algebra. Generic Q tests are not prime-power claims."""
import argparse,json
from fractions import Fraction as R
from pathlib import Path

Z=(R(0),R(0));I=(R(1),R(0))
def k(a,b=0):return(R(a),R(b))
def add(a,b):return(a[0]+b[0],a[1]+b[1])
def neg(a):return(-a[0],-a[1])
def sub(a,b):return add(a,neg(b))
def mul(a,b):return(a[0]*b[0]+a[1]*b[1],a[0]*b[1]+a[1]*b[0]+a[1]*b[1])
def inv(a):
    x,y=a;n=x*x+x*y-y*y
    if not n:raise ZeroDivisionError
    return((x+y)/n,-y/n)
def div(a,b):return mul(a,inv(b))
def vv(z):
    if z==0:return 10**9
    a,b=z.numerator,z.denominator;n=0
    while a%7==0:a//=7;n+=1
    while b%7==0:b//=7;n-=1
    return n
def v(a):return min(vv(a[0]),vv(a[1]))
def plus(A,B):return tuple(add(a,b) for a,b in zip(A,B))
def mm(A,B):return(add(mul(A[0],B[0]),mul(A[1],B[2])),add(mul(A[0],B[1]),mul(A[1],B[3])),add(mul(A[2],B[0]),mul(A[3],B[2])),add(mul(A[2],B[1]),mul(A[3],B[3])))
def sm(q,A):return tuple(mul(q,a) for a in A)
ID=(I,Z,Z,I);ZERO=(Z,Z,Z,Z)
def model(t,s,x,yunit,munit,pu,Q):
    n=t+2*s;m=n//2+1;y=mul(k(7**s),yunit);mu=mul(k(7**t),munit)
    p=mul(k(7**(n-s)),pu);r=div(sub(k(Q-1),mul(x,p)),y)
    N=sm(mu,(neg(mul(x,y)),mul(x,x),neg(mul(y,y)),mul(x,y)))
    F=plus(ID,(mul(x,p),mul(x,r),mul(y,p),mul(y,r)))
    assert min(v(x),v(y))==0
    assert mm(N,N)==ZERO and mm(F,N)==sm(k(Q),N) and mm(N,F)==N
    assert sub(mul(F[0],F[3]),mul(F[1],F[2]))==k(Q)
    assert min(map(v,N))==t and v(N[2])==n and v(F[2])>=n
    assert v(sub(F[3],I))>=m and v(N[3])>=m
    d=min(t,t//2+1)
    wF=min(map(v,tuple(sub(a,b) for a,b in zip(F,ID))))
    assert min(t,wF)>=d
    if n==2:
        assert t==2 and s==0 and min(t,wF)>=2
    return N,F, min(t,wF)==d

def enc(A):return [[[str(x),str(y)] for x,y in A[:2]],[[str(x),str(y)] for x,y in A[2:]]]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    units=[k(1),k(0,1),k(1,1),k(2,1)];count=nonrat=tight=n2=0
    for t in range(1,7):
      for s in range(5):
       n=t+2*s;m=n//2+1
       for yu in units:
        for mu in units:
         for pu in units:
          for extra in range(3):
           # Nonunit x is also tested at s=0; y is then a unit.
           x=mul(k(7 if s==0 and extra==2 else 1),units[extra])
           N,F,is_tight=model(t,s,x,yu,mu,pu,1+7**m*(extra+1))
           count+=1;tight+=is_tight;n2+=n==2
           nonrat+=any(z[1] for z in N+F)
    controls=[]
    for q in (97,197,14503):
        Q=q*q;N,F,_=model(2,0,k(1),k(1),k(1),k(0),Q)
        assert all(v(z)>=2 for z in N+tuple(sub(a,b) for a,b in zip(F,ID)))
        controls.append({'q':q,'Q':Q,'N':enc(N),'F':enc(F),
                         'matrix_model_only':True,'actual_Frey_realization_claimed':False})
    out={'status':'PASS_EXACT_LOCAL_ALGEBRA','cases':count,'nonrational_cases':nonrat,
         'tight_precision_cases':tight,'depth_two_cases':n2,'generic_Q_not_assumed_prime_power':True,
         'local_matrix_controls':controls}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
if __name__=='__main__':
    if not __debug__: raise RuntimeError('Run without Python optimization; assertions are required')
    main()
