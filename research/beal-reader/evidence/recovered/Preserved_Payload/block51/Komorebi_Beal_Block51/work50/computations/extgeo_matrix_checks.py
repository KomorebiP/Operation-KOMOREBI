#!/usr/bin/env python3
"""Exact finite checks, not a verifier for the universal proof or Frey geometry."""
import json
from itertools import product
from math import isqrt
from pathlib import Path

I = ((1, 0), (0, 1))
F = ((1, 4), (0, 29))
N = ((-49, 7), (-343, 49))
D = ((2, 0), (0, 1))
P = ((1, 0), (7, 1))
Pinv = ((1, 0), (-7, 1))
def add(A, B):
    return tuple(tuple(a+b for a,b in zip(ar,br)) for ar,br in zip(A,B))
def scale(A, x):
    return tuple(tuple(x*a for a in r) for r in A)
def mul(A, B):
    return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(2)) for j in range(2)) for i in range(2))
def mpow(A, n):
    r=I
    for _ in range(n): r=mul(r,A)
    return r
def mod(A, n=7):
    return tuple(tuple(a % n for a in r) for r in A)
def det(A):
    return A[0][0]*A[1][1]-A[0][1]*A[1][0]
def opposite(A):
    assert A[1][0] % 343 == 0
    return ((A[0][0],343*A[0][1]),(A[1][0]//343,A[1][1]))
T=add(I,N)
assert mul(N,N)==scale(I,0)
assert mul(F,N)==scale(N,29)
assert mul(N,F)==N
assert mul(F,T)==mul(mpow(T,29),F)
assert mul(mul(P,((0,7),(0,0))),Pinv)==N
assert mul(mul(P,((29,4),(0,1))),Pinv)==F
assert det(T)==1 and det(F)==29 and det(D)==2
assert mod(opposite(F))==I
assert mod(opposite(T))==((1,0),(6,1))
assert mul(N,((1,0),(7,0)))==scale(I,0)
# det of (1,7),D(1,7) is -7, nonzero in Q7.
assert 1*7-2*7 == -7

def hmul(a,b):
    x,y,z=a; X,Y,Z=b
    return ((x+X)%7,(y+Y)%7,(z+Z+x*Y)%7)
def hinv(a):
    x,y,z=a
    return ((-x)%7,(-y)%7,(x*y-z)%7)
def hpow(a,n):
    r=(0,0,0)
    for _ in range(n): r=hmul(r,a)
    return r
for u in product(range(7),repeat=3):
    assert hpow(u,7)==(0,0,0)
commutators=[]
for z,w in product(range(7),repeat=2):
    f=(4,0,z); t=(0,6,w)
    c=hmul(hmul(hmul(f,t),hinv(f)),hinv(t))
    assert c==(0,0,3)
    commutators.append(c)

q=1504231
trial_bound=isqrt(q)
assert q>1 and all(q%d for d in range(2,trial_bound+1))
assert q%35==1
assert (q-1)%7==0 and (q-1)%49!=0
power_residues={str(t):pow(t,(q-1)//7,q) for t in [2,3,5,7]}
assert set(power_residues.values())=={1}
factors={}
x=q-1
for d in range(2,isqrt(x)+1):
    while x%d==0:
        factors[str(d)]=factors.get(str(d),0)+1
        x//=d
if x>1: factors[str(x)]=factors.get(str(x),0)+1
factor_product=1
for d,e in factors.items(): factor_product*=int(d)**e
assert factor_product==q-1
# Display a certified generator for the order-seven quotient via a primitive root.
primitive_root=next(g for g in range(2,q) if all(pow(g,(q-1)//int(r),q)!=1 for r in factors))
order7root=pow(primitive_root,(q-1)//7,q)
assert order7root!=1 and pow(order7root,7,q)==1
unit_checks=0
for n in [2,3,4]:
    modulus=7**(n+1)
    for t,z in product(range(1,7),range(7)):
        u=1+7**(n-1)*t+7**n*z
        assert pow(u,7,modulus)==(1+7**n*t)%modulus
        assert pow(u,49,modulus)==1
        assert pow(u,7,modulus)!=1
        unit_checks+=1
result={
 "status":"all exact assertions passed",
 "matrix_entries":{"F":F,"N":N,"T":T,"D":D},
 "opposite_mod7":{"F":mod(opposite(F)),"T":mod(opposite(T))},
 "heisenberg":{"exponent_cases":343,"central_lift_pairs":49,"commutator":[0,0,3]},
 "global_character_prime":{"q":q,"primality_method":"all integer trial divisors 2 through floor(sqrt(q))","trial_bound":trial_bound,"q_minus_1_factorization":factors,"power_residues":power_residues,"primitive_root":primitive_root,"order7root":order7root},
 "finite_lift_check":{"depths":[2,3,4],"base_ring":"Z/7^(n+1)","cases":unit_checks,"all_lifts_have_order":49},
 "non_claims":["No global irreducible representation is constructed","No Beal or Frey solution is excluded by this computation","General cohomology and polarization claims require the written proofs and sources"]
}
Path('work50/verification/extgeo_run/result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
