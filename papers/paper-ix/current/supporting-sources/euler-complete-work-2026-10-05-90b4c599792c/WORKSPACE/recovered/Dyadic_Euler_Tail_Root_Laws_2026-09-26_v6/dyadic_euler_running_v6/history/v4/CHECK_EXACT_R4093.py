import sympy as sp
from fractions import Fraction as F
from math import comb

def v2_int(n):
    if n==0:return 10**9
    n=abs(n); return (n & -n).bit_length()-1

def v2_frac(q): return v2_int(q.numerator)-v2_int(q.denominator)

def bernF(n):
    b=sp.bernoulli(n)
    return F(int(sp.numer(b)),int(sp.denom(b)))

def kappa(m):
    if m==0:return F(1)
    return -F(2**(4*m)*(2*m-1))*bernF(2*m)

def A(q):
    return F(3**(2*q+2)-1,4*(2*q+1)*(2*q+2))

r=4093
ks=[kappa(m) for m in range(r,r+17)]
for x in range(0,17):
    N=r+x
    tail=sum((ks[j]*comb(2*N,2*(r+j))*A(x-j) for j in range(x+1)),F(0))
    vb=v2_int(comb(N,r))
    actual=v2_frac(tail)
    base=4*r-2+vb # 4r-1 + binom + mu, mu=-1
    print(x,N,vb,actual,'Gval',actual-base,'parity',x&1)
