from math import comb
from fractions import Fraction as F

def rec(g,N=40):
 C=[F(1)]
 for n in range(1,N+1):C.append(-sum(comb(4*n,4*k)*C[k]*g(n-k) for k in range(n)))
 return C

def val(x):
 if not x:return 9999
 n,d=x.numerator,x.denominator
 return (abs(n)&-abs(n)).bit_length()-(d&-d).bit_length()

def check(g):
 C=rec(g)
 vals=[]
 for k in range(1,len(C)):
  C=[b-a for a,b in zip(C,C[1:])]
  vals.append(min(map(val,C)))
 return vals
for name,g in [('const',lambda n:F(1)),('affine',lambda n:F(1+2*n)),('inverse',lambda n:F(1,1+2*n)),('binom',lambda n:F(1+4*comb(n,2))),('geometric',lambda n:F(3)**n)]:
 print(name,check(g)[:20])
