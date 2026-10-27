#!/usr/bin/env python3
"""Independent exact-rational diagnostics for packet energy and posterior certificates.

This checks sixteen constructed finite cases, not all matrices. It does not prove
Gaussian laws, optimal transport, numerical rounding correctness, or universality.
"""
from __future__ import annotations
from pathlib import Path
import datetime as dt
import hashlib
import json
import time
import sympy as sp


def energy(A: sp.MatrixBase) -> sp.Expr:
    return sum((x*x for x in A), sp.Rational(0))


def packets(n: int, offset: int) -> list[sp.Matrix]:
    v = sp.Matrix([sp.Rational(i + offset + 1) for i in range(n)])
    Q = sp.eye(n) - 2 * (v * v.T) / (v.dot(v))
    assert Q.T*Q == sp.eye(n)
    E = [Q[:,i] * Q[:,i].T for i in range(n)]
    assert sum(E, sp.zeros(n)) == sp.eye(n)
    for i in range(n):
        assert E[i].T == E[i] and E[i]*E[i] == E[i]
        for j in range(n):
            if i != j:
                assert E[i]*E[j] == sp.zeros(n)
    return E


def grouped(E: list[sp.Matrix]) -> list[sp.Matrix]:
    n = E[0].rows
    return [sum((P for i,P in enumerate(E) if i % 2 == a), sp.zeros(n)) for a in range(2)]


def model(n: int, m: int, tag: int) -> dict:
    L=sp.Matrix(n,n+1,lambda i,j: sp.Rational(((i+1)*(j+2+tag))%7-3, 2+j))
    if n > 1:
        L[n-1,:] = sp.zeros(1,n+1)  # singular prior is intentional
    N=(tag+1)*sp.eye(m)
    P=L*L.T; R=N*N.T
    H=sp.Matrix(m,n,lambda i,j: sp.Rational(((i+2)*(j+1+tag))%5-2, 1+i+j))
    mean=sp.Matrix([sp.Rational(i-tag,3) for i in range(n)])
    y=sp.Matrix([sp.Rational(2*i+tag+1,4) for i in range(m)])
    S=H*P*H.T+R
    K=P*H.T*S.inv(); G=sp.eye(n)-K*H
    a=mean+K*(y-H*mean)
    return dict(L=L,N=N,P=P,R=R,H=H,mean=mean,y=y,S=S,K=K,G=G,a=a,U=G*L,V=K*N)


def run() -> dict:
    t=time.monotonic(); started=dt.datetime.now(dt.timezone.utc).isoformat()
    cases=[]; parents=0
    for n in range(1,5):
        for m in range(1,5):
            E=packets(n,1); D=packets(m,2)
            A=sp.Matrix(n,m,lambda i,j:sp.Rational((i+2)*(j+3)-2*(i-j)**2,1+i+j))
            parts=[[energy(P*A*Q) for Q in D] for P in E]
            assert all(x>=0 for row in parts for x in row)
            assert sum(map(sum,parts)) == energy(A) == (A.T*A).trace()
            CE=grouped(E); CD=grouped(D)
            for a in range(2):
                for b in range(2):
                    eparent=energy(CE[a]*A*CD[b])
                    descendants=sum((parts[i][j] for i in range(n) for j in range(m)
                                     if i%2==a and j%2==b),sp.Rational(0))
                    assert eparent==descendants
                    zero_children=all(E[i]*A*D[j]==sp.zeros(n,m)
                         for i in range(n) for j in range(m) if i%2==a and j%2==b)
                    assert (eparent==0)==zero_children
                    parents+=1
            v=sp.Matrix([sp.Rational(i+2,i+1) for i in range(n)])
            assert sum(energy(P*v) for P in E)==energy(v)
            M=model(n,m,0); M0=model(n,m,1)
            QL=packets(n+1,3); QN=D
            da=M['a']-M0['a']; du=M['U']-M0['U']; dv=M['V']-M0['V']
            original=energy(da)+energy(du)+energy(dv)
            resolved=(sum(energy(P*da) for P in E)
                      +sum(energy(P*du*Q) for P in E for Q in QL)
                      +sum(energy(P*dv*Q) for P in E for Q in QN))
            assert original==resolved
            B=M['K']+sp.Matrix(n,m,lambda i,j:sp.Rational(1,10+i+j))
            F=M['P']*M['H'].T-B*M['S']
            innovation=M['y']-M['H']*M['mean']
            gap=M['K']-B; Sinv=M['S'].inv()
            cost=energy(gap*innovation)+(gap*M['S']*gap.T).trace()
            cost2=energy(F*Sinv*innovation)+(F*Sinv*F.T).trace()
            residualparts=sum(energy(P*F*Q) for P in E for Q in D)
            assert cost==cost2 and residualparts==energy(F)
            bound=residualparts*(1+energy(innovation))  # sigma=1 and R=I
            assert cost<=bound
            enclosed=residualparts+sp.Rational(n*m,100)
            assert bound<=enclosed*(1+energy(innovation))
            cases.append({'state_dimension':n,'observation_dimension':m,
                          'prior_factor_dimension':n+1,'prior_rank':M['P'].rank(),
                          'matrix_energy':str(energy(A)),
                          'factor_cost':str(original),'residual_cost':str(cost),
                          'packet_residual_majorant':str(bound),'passed':True})
    P=sp.Matrix([[1,1],[0,0]]); Q=sp.Matrix([[0,-1],[0,1]])
    assert P*P==P and Q*Q==Q and P*Q==Q*P==sp.zeros(2) and P+Q==sp.eye(2)
    assert energy(P)+energy(Q)==4 and energy(sp.eye(2))==2
    partial=sp.diag(1,0); missed=sp.diag(0,1)
    assert energy(partial*missed*partial)==0 and energy(missed)==1
    return {'status':'PASS','arithmetic':'exact rational matrices; no floating point',
            'sympy_version':sp.__version__,'started_at_utc':started,
            'elapsed_seconds':round(time.monotonic()-t,3),'constructed_cases':len(cases),
            'local_parent_identities':parents,'randomness_used':False,
            'non_self_adjoint_counterexample':{'partition_energy':4,'identity_energy':2},
            'incomplete_coverage_counterexample':{'reported_partial_energy':0,'actual_energy':1},
            'cases':cases,'non_claims':['Not exhaustive over matrices or dimensions.',
              'Not a Gaussian-law proof or a universal theorem.',
              'No optimal-transport, adaptive-improvement, or runtime-performance claim.'],
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}

if __name__=='__main__':
    result=run()
    out=Path(__file__).resolve().parent/'EXACT_PACKET_CHECKS.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
