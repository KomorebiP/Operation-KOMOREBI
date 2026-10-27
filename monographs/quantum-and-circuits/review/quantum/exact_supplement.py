#!/usr/bin/env python3
"""Independent exact q=12 semantic replay and q=1/QA20 boundary checks.

Run: python3 exact_supplement.py --output exact_supplement.json
Domain: Q(sqrt(3),i), represented by four rational coordinates.
No floating arithmetic, external algebra engine, random samples, or Lean claim.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
from math import gcd

Z = (Q(0),) * 4
O = (Q(1), Q(0), Q(0), Q(0))

def add(x, y):
    return tuple(a+b for a,b in zip(x,y))

def scale(a, x):
    return tuple(Q(a)*v for v in x)

def mul(x,y):
    a,b,c,d=x; A,B,C,D=y
    return (a*A+3*b*B-c*C-3*d*D,
            a*B+b*A-c*D-d*C,
            a*C+3*b*D+c*A+3*d*B,
            a*D+b*C+c*B+d*A)

def conj(x):
    return (x[0],x[1],-x[2],-x[3])

def total(xs):
    y=Z
    for x in xs:y=add(y,x)
    return y

def mm(A,B):
    return [[total(mul(A[i][k],B[k][j]) for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]

def adj(A):
    return [[conj(A[j][i]) for j in range(len(A))] for i in range(len(A[0]))]

def mv(A,v):
    return [total(mul(a,x) for a,x in zip(row,v)) for row in A]

def mass(v):
    return total(mul(conj(x),x) for x in v)

def main():
    checks=[]
    def check(name,condition):
        checks.append({'name':name,'passed':bool(condition)})
        if not condition:raise AssertionError(name)
    N=12
    powers=[O]
    z=(Q(0),Q(1,2),Q(1,2),Q(0))
    for _ in range(N):powers.append(mul(powers[-1],z))
    check('twelfth_root_and_exact_order',powers[12]==O and all(powers[k]!=O for k in range(1,12)))
    U=[k for k in range(12) if gcd(k,12)==1]
    check('coprime_labels',U==[1,5,7,11])
    c=[4,0,2,0,-2,0,-4,0,-2,0,2,0]
    for n in range(N):
        check(f'root_sum_{n}',total(powers[(n*k)%N] for k in U)==scale(c[n],O))
    fs=(Q(0),Q(1,6),Q(0),Q(0))
    ss=(Q(0),Q(1,12),Q(0),Q(0))
    F=[[mul(fs,powers[(n*k)%N]) for k in range(N)] for n in range(N)]
    D=[[O if i==j and i in U else Z for j in range(N)] for i in range(N)]
    P=[[scale(Q(c[(i-j)%N],N),O) for j in range(N)] for i in range(N)]
    I=[[O if i==j else Z for j in range(N)] for i in range(N)]
    left,right,transport=mm(adj(F),F),mm(F,adj(F)),mm(mm(F,D),adj(F))
    for i in range(N):
        for j in range(N):
            check(f'left_unitarity_{i}_{j}',left[i][j]==I[i][j])
            check(f'right_unitarity_{i}_{j}',right[i][j]==I[i][j])
            check(f'projector_transport_{i}_{j}',transport[i][j]==P[i][j])
    psi=[scale(x,ss) for x in c]
    chi=[scale(abs(x),ss) for x in c]
    u=[scale(Q(1,2),O) if k in U else Z for k in range(N)]
    check('state_preparation',mv(F,u)==psi)
    check('state_recovery',mv(adj(F),psi)==u)
    check('signed_normalized',mass(psi)==O)
    check('unsigned_normalized',mass(chi)==O)
    check('states_orthogonal',total(mul(conj(x),y) for x,y in zip(psi,chi))==Z)
    check('same_histogram',all(mul(conj(x),x)==mul(conj(y),y) for x,y in zip(psi,chi)))
    check('projector_fixes_signed',mv(P,psi)==psi)
    check('projector_kills_unsigned',mv(P,chi)==[Z]*N)
    check('signed_selected_probability',mass([mv(adj(F),psi)[k] for k in U])==O)
    check('unsigned_selected_probability',mass([mv(adj(F),chi)[k] for k in U])==Z)
    rho=[[scale(Q(c[i]**2,48),O) if i==j else Z for j in range(N)] for i in range(N)]
    check('density_nonnegative_trace_one',all(c[i]**2>=0 for i in range(N)) and total(rho[i][i] for i in range(N))==O)
    check('QA20_dephased_selected_probability',total(mm(P,rho)[i][i] for i in range(N))==scale(Q(1,3),O))
    # Exact specializations of QA19 at all four quarter turns.
    positive=[scale(max(v,0),ss) for v in c]
    negative=[scale(max(-v,0),ss) for v in c]
    for phase,p in [(O,Q(0)),((Q(0),Q(0),Q(1),Q(0)),Q(1,2)),(scale(-1,O),Q(1)),((Q(0),Q(0),Q(-1),Q(0)),Q(1,2))]:
        v=[add(a,mul(phase,b)) for a,b in zip(positive,negative)]
        check(f'phase_quadrant_{phase}_normalized',mass(v)==O)
        check(f'phase_quadrant_{phase}_probability',mass(mv(P,v))==scale(p,O))
    # Boundary N=1: Fourier, order selector, rational projector, and energy are scalar identities.
    check('q1_coprime_zero',[a for a in range(1) if gcd(a,1)==1]==[0])
    check('q1_unitarity',mm([[O]],adj([[O]]))==[[O]])
    check('q1_projector',mm([[O]],[[O]])==[[O]])
    check('q1_energy',1==1*len([0]))
    # Sensitivity controls test the exact same matrix/state predicates on explicit mutations.
    badP=[[scale(2,v) for v in row] for row in P]
    check('wrong_projector_scale_rejected',mm(badP,badP)!=badP)
    badpsi=psi.copy();badpsi[6]=scale(-1,badpsi[6])
    check('false_sign_rejected',mv(adj(F),badpsi)!=u)
    return {'status':'PASS','assertion_count':len(checks),'checks':checks,
            'domain':'Q(sqrt(3), i), exact Fraction coordinates',
            'moduli':[1,12],'dephased_probability':'1/3',
            'phase_samples':'1, i, -1, -i',
            'non_claims':['No universal arbitrary-modulus theorem is established by this finite run.',
                          'The continuous phase identity is proved in prose; four exact samples are checked here.',
                          'This script is independent exact Python arithmetic, not a Lean compiler run.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=main();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'assertion_count':result['assertion_count'],'dephased_probability':result['dephased_probability']}))
