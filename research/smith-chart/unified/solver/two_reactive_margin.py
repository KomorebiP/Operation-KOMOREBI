"""Exact coefficient-box separator for all two-reactive ordinary RLC networks.
Author: Komorebi P. The physical coverage uses the stated classical
regularity/Reichert classification; this arithmetic replay does not prove it.
"""
from fractions import Fraction as F
import json
from kernel import exact_polynomials as p
from pure_type_margins import gamma

VARIABLES=tuple('ABCDEF')
SAMPLES=tuple(map(F,('1/2','3/4','1','3/2','2')))
TARGET=tuple(F(x,30) for x in (6,3,4,6,2,9))
EPSILON=F(1,1000)
MARGIN=F(1,1000000)

def matrix():
    return [[(1-gamma(s))*s*s,(1-gamma(s))*s,1-gamma(s),
             -(1+gamma(s))*s*s,-(1+gamma(s))*s,-(1+gamma(s))] for s in SAMPLES]+[[F(1)]*6]

def inverse(A):
    n=len(A);rows=[list(row)+[F(i==j) for j in range(n)] for i,row in enumerate(A)]
    for c in range(n):
        k=next(i for i in range(c,n) if rows[i][c]);rows[c],rows[k]=rows[k],rows[c]
        t=rows[c][c];rows[c]=[x/t for x in rows[c]]
        for i in range(n):
            if i!=c:
                t=rows[i][c];rows[i]=[x-t*y for x,y in zip(rows[i],rows[c])]
    return [row[n:] for row in rows]

def polynomials():
    A,B,C,D,E,F_=map(p.var,VARIABLES)
    t=p.sub(p.mul(A,F_),p.mul(C,D))
    ae_bd=p.sub(p.mul(A,E),p.mul(B,D));bf_ce=p.sub(p.mul(B,F_),p.mul(C,E))
    K=p.sub(p.square(t),p.mul(ae_bd,bf_ce))
    return {'t':t,'K':K,'lambda1':p.sub(p.mul(E,bf_ce),p.mul(F_,t)),
      'lambda2':p.sub(p.mul(B,ae_bd),p.mul(A,t)),
      'mu1':p.sub(K,p.scale(p.mul(p.mul(C,D),p.sub(p.scale(t,2),p.mul(B,E))),4))}

def evaluate(poly,values):
    result=F(0)
    for monomial,c in poly.items():
        for name,n in monomial:c*=values[name]**n
        result+=c
    return result

def enclosure(poly,box):
    """Outward exact rational monomial enclosure on a nonnegative box."""
    low=high=F(0)
    for monomial,c in poly.items():
        a=b=F(1)
        for name,n in monomial:
            l,h=box[name]
            if not 0<=l<=h:raise ValueError('Nonnegative ordered box required')
            a*=l**n;b*=h**n
        low+=c*(a if c>=0 else b);high+=c*(b if c>=0 else a)
    return low,high

def certificate():
    M=matrix();N=inverse(M)
    for i in range(6):
        for j in range(6):
            assert sum(N[i][k]*M[k][j] for k in range(6))==int(i==j)
            assert sum(M[i][k]*N[k][j] for k in range(6))==int(i==j)
    assert [sum(x*y for x,y in zip(row,TARGET)) for row in M]==[0,0,0,0,0,1]
    constants=[sum(abs(c)*max(F(1),s*s) for c,s in zip(row,SAMPLES)) for row in N]
    C=max(constants);assert C==F(439774,507) and C*MARGIN<EPSILON
    box={name:(v-EPSILON,v+EPSILON) for name,v in zip(VARIABLES,TARGET)}
    bounds={name:enclosure(poly,box) for name,poly in polynomials().items()}
    assert bounds['t'][0]>0 and bounds['K'][0]>0
    assert all(bounds[name][1]<0 for name in ('lambda1','lambda2','mu1'))
    return {'format':'komorebi-two-reactive-coefficient-separation-v1','status':'PASS',
      'margin':str(MARGIN),'samples':list(map(str,SAMPLES)),
      'target_impedance':{'P':[4,3,6],'Q':[9,2,6]},
      'normalized_coefficients_descending':list(map(str,TARGET)),
      'matrix_inverse':[[str(x) for x in row] for row in N],
      'coefficient_error_factor':str(C),'coefficient_box_radius':str(EPSILON),
      'polynomial_box_bounds':{k:list(map(str,v)) for k,v in bounds.items()},
      'physical_dependency':'Nonnegative degree-at-most-two network polynomials; classical regularity/Reichert classification in Morelli 2019, Theorem 3.1, Section 3.1.1, Table 5.10 and Theorem A.9.',
      'scope':'All ordinary positive uncoupled transformer-free networks with at most two L/C branches, arbitrary resistor count. Five positive-real Laplace samples; not an imaginary-axis matching guarantee or a three/four-reactive exclusion.',
      'formal_scope':'Exact matrix and rational polynomial-box arithmetic, with a separately written physical/classical coverage proof; this module does not execute that universal proof in Lean.'}

def verify(record):
    if record!=certificate():raise ValueError('Target, inverse, interval or margin binding differs')
    return {'status':'PASS','margin':str(MARGIN),'reactive_budget':2}

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps(certificate(),indent=2))
