#!/usr/bin/env python3
from __future__ import annotations
from fractions import Fraction
from sympy import Matrix, eye, zeros

def _q(x):
    if isinstance(x,(int,Fraction)): return x
    if isinstance(x,str) and '/' in x:
        a,b=x.split('/',1); return Fraction(int(a),int(b))
    if isinstance(x,str): return Fraction(x)
    return x

def matrix(x): return Matrix([[_q(v) for v in row] for row in x])
def vector(x): return Matrix([_q(v) for v in x])
def enc_scalar(x):
    try:
        n,d=x.as_numer_denom();
        return str(n) if d==1 else f"{n}/{d}"
    except Exception: return str(x)
def enc_matrix(M): return [[enc_scalar(M[i,j]) for j in range(M.cols)] for i in range(M.rows)]

def validate_packet_system(projectors):
    P=[matrix(x) for x in projectors]; n=P[0].rows
    idem=all(p*p==p for p in P)
    ann=all(i==j or p*q==zeros(n) for i,p in enumerate(P) for j,q in enumerate(P))
    comp=sum(P,zeros(n))==eye(n)
    return {'valid':idem and ann and comp,'idempotent':idem,'pairwise_annihilating':ann,'complete':comp}

def analyze(projectors,v):
    P=[matrix(x) for x in projectors]; x=vector(v)
    return {'packets':[enc_matrix(p*x) for p in P],'reconstructs':sum((p*x for p in P),zeros(x.rows,1))==x}

def blockify(projectors,operator):
    P=[matrix(x) for x in projectors]; T=matrix(operator)
    return {'blocks':[[enc_matrix(pb*T*pa) for pa in P] for pb in P]}

def reconstruct(blocks):
    B=[[matrix(x) for x in row] for row in blocks]; n=B[0][0].rows
    T=sum((x for row in B for x in row),zeros(n))
    return {'operator':enc_matrix(T)}

def compose_blocks(projectors,S,T):
    P=[matrix(x) for x in projectors]; S=matrix(S);T=matrix(T);n=len(P);z=zeros(S.rows)
    SB=[[pb*S*pa for pa in P] for pb in P]; TB=[[pb*T*pa for pa in P] for pb in P]
    C=[[sum((SB[g][b]*TB[b][a] for b in range(n)),z) for a in range(n)] for g in range(n)]
    return {'blocks':[[enc_matrix(x) for x in row] for row in C],'equals_direct':C==[[pb*(S*T)*pa for pa in P] for pb in P]}

def lower_intertwiner(P,Q,T,S,U):
    P=[matrix(x) for x in P]; Q=[matrix(x) for x in Q];T=matrix(T);S=matrix(S);U=matrix(U)
    local=[]; ok=True
    for g,qg in enumerate(Q):
      for a,pa in enumerate(P):
        lhs=sum((qg*U*pb*(pb*T*pa) for pb in P),zeros(U.rows,U.cols))
        rhs=sum(((qg*S*qd)*(qd*U*pa) for qd in Q),zeros(U.rows,U.cols))
        res=lhs-rhs; eq=res==zeros(*res.shape);ok &= eq
        local.append({'target':g,'source':a,'lhs':enc_matrix(lhs),'rhs':enc_matrix(rhs),'residual':enc_matrix(res),'holds':eq})
    return {'global_holds':U*T==S*U,'all_local_hold':ok,'local_equations':local}
