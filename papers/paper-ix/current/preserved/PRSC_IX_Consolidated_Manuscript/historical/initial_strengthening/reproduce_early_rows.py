from fractions import Fraction
from math import comb, factorial

def coeff(N,j,end):
    a=[Fraction(1)]
    for n in range(1,end+1):
        a.append(-sum((Fraction(comb(N*n+j,N*q))*a[q] for q in range(n)),Fraction(0))/comb(N*n+j,N*n))
    return tuple(a)

def vp(p,x):
    if x==0:return None
    a,b=abs(x.numerator),x.denominator
    v=0
    while a%p==0:a//=p;v+=1
    while b%p==0:b//=p;v-=1
    return v

for j in range(4):
    a=tuple(factorial(j)*x for x in coeff(4,j,64))
    failures=[]
    for r in range(1,7):
        for n in range(13):
            v=vp(2,a[n+2**(r-1)]-a[n])
            if v is not None and v<r:failures.append((r,n,v))
    print(j,78,failures)
a=coeff(6,0,3)
print('odd zero-row difference:',a[1]-a[0],'valuation:',vp(3,a[1]-a[0]))
