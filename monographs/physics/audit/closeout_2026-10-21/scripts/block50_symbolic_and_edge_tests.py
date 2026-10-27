#!/usr/bin/env python3
"""Exact sympy Clifford checks, zero-mass & sign edge cases for Block 50."""
import json
from pathlib import Path
import numpy as np
import sympy as sp
ROOT=Path(__file__).resolve().parent.parent
I=sp.I;z=sp.zeros(2);u=sp.eye(2)
pauli=[sp.Matrix([[0,1],[1,0]]),sp.Matrix([[0,-I],[I,0]]),sp.Matrix([[1,0],[0,-1]])]
A=[sp.BlockMatrix([[z,p],[p,z]]).as_explicit() for p in pauli]
B=sp.BlockMatrix([[u,z],[z,-u]]).as_explicit();id4=sp.eye(4)
for a in A: assert a*a==id4 and a.H==a and a*B+B*a==sp.zeros(4)
for a in A:
 for b in A:
  if a!=b:assert a*b+b*a==sp.zeros(4)
a,b,c,m=sp.symbols('a b c m',real=True)
HM=m*B+a*A[0]+b*A[1]+c*A[2]
assert sp.simplify(HM**2-(m*m+a*a+b*b+c*c)*id4)==sp.zeros(4)
x,y,z=sp.symbols('x y z',real=True)
DEL=x*A[0]+y*A[1]+z*A[2]
assert sp.simplify(DEL**2-(x*x+y*y+z*z)*id4)==sp.zeros(4)

# Numerically test special boundary cases: mass zero, negative mass and negative h.
nm=sp.Matrix([1,0,0,0]);data=[]
for mass in [0.,-0.82,0.82]:
 for h in [-.3,-.06,.06,.3]:
  k=np.array([0.,2*np.pi*3,-2*np.pi*2]); q=np.sin(h*k)/h
  M=np.array(HM.subs({m:mass,a:q[0],b:q[1],c:q[2]}),dtype=complex)
  assert np.linalg.norm(M-M.conj().T)<2e-13
  E2=mass*mass+float(q@q)
  assert np.linalg.norm(M@M-E2*np.eye(4))<5e-12
  data.append({'m':mass,'h':h,'energy_squared':E2})
assert all(abs(r['energy_squared'])>=0 for r in data)
results={'symbolic_anticommutators':'PASS (exact sympy)',
         'mode_energy_square':'PASS (symbolic m,k variables)',
         'difference_norm_square':'PASS (symbolic delta variables)',
         'edge_cases_mh':'PASS 3 masses × 4 positive/negative spacing values',
         'edge_cases':data}
(ROOT/'results'/'symbolic_and_edge_audit.json').write_text(json.dumps(results,indent=2))
print('Exact Clifford algebra: PASS')
print('Centered difference norm square: PASS')
print('Zero/negative mass and negative spacing edge cases: PASS',len(data))
