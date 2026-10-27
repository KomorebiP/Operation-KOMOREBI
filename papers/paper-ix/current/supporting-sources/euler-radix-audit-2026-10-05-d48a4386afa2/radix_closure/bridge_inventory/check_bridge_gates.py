"""Exact finite audits of the source-to-Euler bridge gates; no numerical tests."""
from fractions import Fraction as F
from itertools import combinations
from math import comb, factorial, gcd
from functools import reduce
from pathlib import Path
import json

def det(a):
    a = [[F(x) for x in row] for row in a]
    out = F(1)
    for j in range(len(a)):
        pivot = next((i for i in range(j,len(a)) if a[i][j]), None)
        if pivot is None: return F(0)
        if pivot != j:
            a[j],a[pivot]=a[pivot],a[j]
            out=-out
        d=a[j][j]; out*=d
        for i in range(j+1,len(a)):
            q=a[i][j]/d
            for k in range(j,len(a)): a[i][k]-=q*a[j][k]
    return out

def coeff(num, den, n):
    out=[]
    for j in range(n):
        a=num[j] if j<len(num) else 0
        out.append(F(a-sum(den[k]*out[j-k] for k in range(1,min(j+1,len(den)))) ,den[0]))
    return out

# Rational spatial section sequences, exact over Q and periodic with period 12.
R=coeff([0,2,0,2],[1,0,-1,0,1],36)
S=coeff([2,2],[1,-1,1],36)
U=coeff([1],[1,1,1],36)
V=coeff([0,1],[1,1,1],36)
for seq in (R,S,U,V): assert seq[:24]==seq[12:36]
cols=[R,S,[2*u+4*v for u,v in zip(U,V)],[2*u-2*v for u,v in zip(U,V)]]
matrix=[[int(col[i]) for col in cols] for i in range(12)]
divisors=[1]
for k in range(1,5):
    g=0
    for rows in combinations(range(12),k):
        for cc in combinations(range(4),k):
            d=det([[matrix[i][j] for j in cc] for i in rows])
            assert d.denominator==1
            g=gcd(g,abs(d.numerator))
    divisors.append(g)
smith=[divisors[i]//divisors[i-1] for i in range(1,5)]

# Orbit closure relative to basis R,S,2U+4V,2U-2V.
# All six recurrent states are integral combinations of the last two.
orbit=[(2,4),(2,-2),(-4,-2),(4,2),(-2,2),(-2,-4)]
coordinates=[]
for a,b in orbit:
    x=F(a+b,6); y=F(2*a-b,6)
    assert x.denominator==y.denominator==1
    coordinates.append([int(x),int(y)])

# Actual beta obtained by formal sinh-series division, independently by Bernoulli.
N=36
beta=[F(1)]
for n in range(1,N+1):
    beta.append(-sum(beta[n-k]*F(2**(2*k+1),factorial(2*k+2)) for k in range(1,n+1)))
B=[F(1)]
for n in range(1,2*N+1): B.append(-sum(F(comb(n+1,k))*B[k] for k in range(n))/F(n+1))
for n in range(1,N+1):
    assert beta[n]==-F(2**(2*n)*(2*n-1),factorial(2*n))*B[2*n]
    assert beta[n]
section_determinants={}
for r in (1,2,3,4):
    gamma=lambda q:8**q*beta[r+q]/beta[r]
    mat=[[gamma((2**e)*n) for e in range(4)] for n in range(1,5)]
    d=det(mat)
    assert d
    section_determinants[str(r)]={"nonzero":True,"numerator_bits":abs(d.numerator).bit_length(),"denominator_bits":d.denominator.bit_length()}

# The actual prefix C_(16,1) state has every t^(2n-2) mode nonzero.
# Further zero sections give independent eigenmodes with eigenvalues 2^(2-2n).
prefix=[]
for r in range(1,9):
    powers=[2*n-2 for n in range(r)]
    initial=[-beta[n]*F(4)**(n-1)/2*F(16)**(-(2*n-2)) for n in range(r)]
    eigen=[F(2)**(-k) for k in powers]
    d=det([[initial[j]*eigen[j]**i for j in range(r)] for i in range(r)])
    assert d
    prefix.append({"r":r,"rank":r,"negative_valuation_eigenmodes":max(0,r-2)})

result={"arithmetic":"exact Python Fraction and integers", "spatial_period":12,"spatial_rational_rank":4,
        "raw_lattice_basis":["R","S","2U+4V","2U-2V"],"determinantal_divisors":divisors,
        "smith_invariants":smith,"orbit_coordinates":coordinates,"beta_independent_checks":N,
        "four_section_gamma_checks":section_determinants,"prefix_eigenmode_checks":prefix,
        "non_claim":"Does not establish Euler critical-value nonvanishing; rank beyond finite sample is proved separately in the note."}
out=Path("radix_closure/bridge_inventory/certified_run/results.json")
out.write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
