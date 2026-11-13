"""Exact degree-three/four target-fiber reduction. Author: Komorebi P.

Arithmetic certificate only: proximity to this fiber excludes no physical graph.
Coefficients are ascending, normalized by P(1)+Q(1)=1.
"""
from fractions import Fraction as F
from itertools import combinations
import json
from pure_type_margins import SAMPLES,P,Q,gamma
from two_reactive_margin import inverse


def multiply(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out


def fiber(q,m):
    if q not in (3,4) or len(m)!=q-1:raise ValueError('Degree three/four required')
    return multiply(P,m)+multiply(Q,m)


def matrix(q,indices):
    n=2*q+2
    rows=[[(1-gamma(SAMPLES[k]))*SAMPLES[k]**i for i in range(q+1)]+
          [-(1+gamma(SAMPLES[k]))*SAMPLES[k]**i for i in range(q+1)] for k in indices]
    rows.append([F(1)]*n)
    rows.extend([[F(j==i) for j in range(n)] for i in range(3,q+1)])
    return rows


def certificate(q):
    candidates=[]
    for indices in combinations(range(7),q+3):
        M=matrix(q,indices);N=inverse(M);n=len(M)
        assert all(sum(M[i][k]*N[k][j] for k in range(n))==int(i==j)
                   and sum(N[i][k]*M[k][j] for k in range(n))==int(i==j)
                   for i in range(n) for j in range(n))
        weights=[max(F(1),SAMPLES[k]**q) for k in indices]
        factors=[sum(abs(row[j])*weights[j] for j in range(q+3)) for row in N]
        candidates.append((max(factors),indices,M,N,factors))
    C,indices,M,N,factors=min(candidates,key=lambda row:(row[0],row[1]))
    n=len(M)
    for j in range(q-1):
        m=[F(i==j) for i in range(q-1)];x=fiber(q,m)
        assert all(sum(a*b for a,b in zip(row,x))==0 for row in M[:q+3])
    if q==3:
        vertices=[(F(1,30),F(0)),(F(0),F(1,30))]
        interior=(F(1,50),F(1,75));rho=F(2,25)
        inequalities=['a >= 0','b >= 0','a+b = 1/30']
    else:
        vertices=[(F(1,30),F(0),F(0)),(F(0),F(1,30),F(0)),
                  (F(0),F(0),F(1,30)),(F(3,130),F(-1,195),F(1,65))]
        interior=(F(3,190),F(2,285),F(1,95));rho=F(6,95)
        inequalities=['a >= 0','c >= 0','b >= -2*a/9','b >= -c/3','a+b+c = 1/30']
    for m in vertices:
        x=fiber(q,m);assert min(x)>=0 and sum(x)==1
    assert min(fiber(q,interior))==rho and sum(fiber(q,interior))==1
    return {'status':'PASS','degree':q,'coefficient_order':'P_0..P_q,Q_0..Q_q',
      'sample_indices':list(indices),'rank_of_sample_rows':q+3,
      'affine_fiber_dimension':q-2,'retained_free_P_indices':list(range(3,q+1)),
      'inverse':[[str(v) for v in row] for row in N],
      'coordinate_error_factors':list(map(str,factors)),
      'coefficient_error_factor':str(C),'rounded_error_factor':(C.numerator+C.denominator-1)//C.denominator,
      'exact_nonnegative_fiber':{'inequalities':inequalities,'multiplier_vertices':[list(map(str,m)) for m in vertices]},
      'interior_multiplier':list(map(str,interior)),'interior_minimum_coefficient':str(rho),
      'nonnegative_fiber_error_factor':str(C/rho),
      'scope':'Maximum seven-sample reflection error delta gives distance <= C*delta to the affine fiber. Mixing that vector with the displayed interior vector gives an actual nonnegative fiber vector at distance <= epsilon/(rho+epsilon), epsilon=C*delta, in every coefficient. No physical graph is excluded.',
      'non_claims':['No physical graph excluded','No endpoint or imaginary-axis error bound without additional denominator control']}


def verify(record):
    if record!=certificate(record.get('degree')):raise ValueError('Coefficient-fiber binding differs')
    return {'status':'PASS','degree':record['degree']}


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps({'status':'PASS','certificates':[certificate(3),certificate(4)]},indent=2))
