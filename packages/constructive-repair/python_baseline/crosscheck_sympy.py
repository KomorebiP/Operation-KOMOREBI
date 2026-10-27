"""Optional independent checks with SymPy 1.14; not required for main stdlib audit."""
import json
from fractions import Fraction
from pathlib import Path
from sympy import Matrix, GF, QQ, Integer, Rational, euler, Symbol, tan, series, factorial, expand
from sympy.polys.matrices import DomainMatrix
from sympy.functions.combinatorial.numbers import stirling
from extra_audit import euler_numbers, tangent_numbers

folder=Path(__file__).resolve().parent
records=[json.loads(s) for s in (folder/'case_records.jsonl').read_text().splitlines()]

def sympy_rank(n,cols,field):
    if not cols:return 0
    A=Matrix([[int(col[i]) for col in cols] for i in range(n)])
    if field=='Q':return A.rank()
    return DomainMatrix.from_Matrix(A).convert_to(GF(int(field))).rank()

checked=0
for z in records:
    if z['kind']!='free_rank_case':continue
    n=z['n'];D=z['D'];R=z['R'];field=z['field']
    k=sympy_rank(n,D+R,field)-sympy_rank(n,D,field)
    if k!=z['obstruction_rank']:
        raise AssertionError((z,k))
    selected=[R[i] for i in z['free_basis_indices']]
    if sympy_rank(n,D+selected,field)!=sympy_rank(n,D+R,field):
        raise AssertionError(('basis insuff', z))
    for residual,w in zip(R,z['witness_coefficients']):
        if field=='Q':
            actual=[sum(Fraction(col[i])*Fraction(c) for col,c in zip(D+selected,w))
                    for i in range(n)]
            if actual!=[-Fraction(q) for q in residual]:
                raise AssertionError(('wrong witness', z))
        else:
            p=int(field)
            actual=[sum(int(col[i])*int(c) for col,c in zip(D+selected,w))%p
                    for i in range(n)]
            if actual!=[(-int(q))%p for q in residual]:
                raise AssertionError(('wrong witness',z))
    checked+=1
print(f'SYMPY PASS: {checked} exact rank and witness verifications, Q and GF(2,3,5,7)')

trace={ (z['p'], z['eta'],z['degree']):Fraction(z['coefficient']) for z in records
         if z['kind']=='cyclotomic_trace' }
checks=0
for p in [3,5,7,11]:
    for eta in [1,-1]:
        for j in range(31):
            independent=Fraction(sum(int(stirling(j,k,kind=1,signed=True))*eta**k
                                     for k in range(0,j+1,p)),int(factorial(j)))
            if independent!=trace[(p,eta,j)]:
                raise AssertionError((p,eta,j,independent,trace[(p,eta,j)]))
            checks+=1
print(f'SYMPY PASS: {checks} cyclotomic trace coefficients independently checked with signed Stirling numbers')

E=euler_numbers(18)
checks=0
for n in range(0,19,2):
    if Integer(E[n])!=euler(n):
        raise AssertionError(('Euler disagreement',n,E[n],euler(n)))
    checks+=1
print(f'SYMPY PASS: {checks} independently sourced classical Euler values')
print('NOTE: Computational agreement is not a substitute for mathematical proof or Lean acceptance.')
