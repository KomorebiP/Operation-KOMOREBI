#!/usr/bin/env python3
"""Discovery LP for six-monomial carriers; exact verification after optimization.

Columns v are nonzero nonnegative integer exponent vectors with a.v = 0 mod m.
Find nonnegative w with Vw=1 and sum(w)>1. At a basic solution at most six
columns suffice. A square nonsingular support gives exponent matrix A.
Floating LP is only discovery; all reported matrices/weights are checked over Q.
"""
import itertools,json,math,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
import sympy as sp
from carrier_search import weighted_model,fracstr

def comps(n,k):
    if k==1:
        yield (n,)
        return
    for x in range(n+1):
        for rest in comps(n-x,k-1):yield (x,)+rest

def run(m,a,maxdegree=14):
    cols=[]
    for d in range(1,maxdegree+1):
        for v in comps(d,6):
            if sum(ai*vi for ai,vi in zip(a,v))%m==0:
                cols.append(v)
    V=np.array(cols,dtype=float).T
    res=linprog(-np.ones(len(cols)),A_eq=V,b_eq=np.ones(6),bounds=(0,None),method='highs')
    if not res.success:
        return {'status':res.message,'columns':len(cols),'max_degree':maxdegree}
    supp=np.flatnonzero(res.x>1e-8)
    mat=sp.Matrix([[cols[j][i] for j in supp] for i in range(6)])
    sol=mat.gauss_jordan_solve(sp.ones(6,1))
    assert sol[1].rows==0
    ws=tuple(F(v) for v in sol[0])
    assert all(w>0 for w in ws) and mat*sol[0]==sp.ones(6,1)
    q=[sum(a[i]*int(mat[i,j]) for i in range(6))//m for j in range(mat.cols)]
    r={'modulus':m,'character':a,'max_degree':maxdegree,'columns':len(cols),
       'support_size':len(supp),'matrix':[[int(mat[i,j]) for j in range(mat.cols)] for i in range(6)],
       'weights':[fracstr(w) for w in ws],'weight_sum':fracstr(sum(ws,F(0))),
       'residue_numerator':[qi-1 for qi in q],
       'discovery':'scipy.optimize.linprog floating search with exact rational verification'}
    if mat.rows==mat.cols and mat.det()!=0:
        r['determinant']=int(mat.det())
        r['model']=weighted_model(ws)
        r['inverse_matrix']=[[str(x) for x in row] for row in mat.inv().tolist()]
    if hasattr(res,'eqlin'):
        dual=tuple(F(float(-v)).limit_denominator(10**8) for v in res.eqlin.marginals)
        valid=all(sum(dual[i]*col[i] for i in range(6))>=1 for col in cols)
        r['candidate_dual']=[fracstr(v) for v in dual]
        r['dual_verified_on_enumerated_columns']=valid
        r['dual_sum']=fracstr(sum(dual,F(0)))
    return r

if __name__=='__main__':
    r=run(70,(1,20,24,42,61,62),18)
    Path(__file__).with_name('general70.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
