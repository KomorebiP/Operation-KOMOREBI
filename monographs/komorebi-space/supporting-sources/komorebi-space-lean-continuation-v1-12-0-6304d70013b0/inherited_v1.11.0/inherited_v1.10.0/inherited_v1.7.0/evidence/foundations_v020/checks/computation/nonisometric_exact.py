#!/usr/bin/env python3
"""Exact bounded audit of known invertible nonisometric connection fixtures.
No finite check is a proof for arbitrary graphs. All matrix and vector
arithmetic is SymPy Rational. Squared Euclidean fiber norms and vertex/edge
maximum norms are compared without floating-point approximations.
"""
from __future__ import annotations
import argparse, json, time, sys, hashlib
from pathlib import Path
import sympy as s

COUNT=0

def check(p):
    global COUNT
    COUNT+=1
    if not bool(p):raise AssertionError(f'assertion {COUNT}')

def opbound(A):return sum(abs(a) for a in A) # conservative Euclidean operator bound

def vnorm2(v):return (v.T*v)[0]

def sup2(xs):return max([vnorm2(x) for x in xs],default=s.Integer(0))

def bound(v2,C,r2):check(v2 <= C*C*r2)

def fix_projection(H):
    basis=H.nullspace()
    if not basis:return s.zeros(H.cols),0
    N=s.Matrix.hstack(*basis)
    return N*(N.T*N).inv()*N.T,len(basis)

def fixture(n,d,kind,t):
    E=s.eye(d)
    frames=[]
    for i in range(n):
        F=s.diag(*[s.Rational(2)**((i+k+t)%3-1) for k in range(d)])
        if d>1:F[0,d-1]+=s.Rational(i+t,2)
        frames.append(F)
    pairs={(i,i+1) for i in range(n-1)}
    if kind=='cycle':pairs.add((0,n-1))
    if kind=='complete':pairs={(i,j) for i in range(n) for j in range(i+1,n)}
    T={}
    for i,j in sorted(pairs):
        M=E.copy()
        if j>i+1 and t:
            if t%2:M[d-1,d-1]=-1
            elif d>1:M[0,d-1]=s.Rational(1,2)
            else:M[0,0]=2
        T[i,j]=frames[i]*M*frames[j].inv()
        T[j,i]=T[i,j].inv()
    # BFS routes and forward products; transport maps last vertex to first.
    routes={0:[0]};work=[0]
    for i in work:
        for j in range(n):
            if (i,j) in T and j not in routes:routes[j]=routes[i]+[j];work.append(j)
    check(len(routes)==n)
    root={};R={}
    def pathprod(path):
        out=E.copy()
        for i,j in zip(path,path[1:]):out=out*T[i,j]
        return out
    def gain(path):
        total=s.Integer(0);prefix=s.Integer(1)
        for i,j in zip(path,path[1:]):
            total+=prefix;prefix*=opbound(T[i,j])
        return total
    for i in range(n):
        root[i]=pathprod(routes[i]);R[i]=root[i].inv()
        check(pathprod(list(reversed(routes[i])))==R[i])
    edges=sorted(T)
    loop={e:root[e[0]]*T[e]*R[e[1]] for e in edges}
    H=s.Matrix.vstack(*[loop[e]-E for e in edges])
    Q,dim=fix_projection(H)
    check(Q*Q==Q);check(H*Q==s.zeros(H.rows,d));check(Q==Q.T)
    Hp=(H.T*H+Q).inv()*H.T
    check(Hp*H==E-Q)
    kappa=opbound(Hp)
    A=max(gain(list(reversed(routes[i]))) for i in range(n))
    B=max(opbound(R[i]) for i in range(n))
    N=max(opbound(root[i]) for i in range(n))
    D=1+max(opbound(T[e]) for e in edges)
    C=A+B*kappa*N*(D*A+1)
    # Independent global-kernel elimination.
    DG=s.zeros(len(edges)*d,n*d)
    for j,(u,v) in enumerate(edges):
        DG[j*d:(j+1)*d,u*d:(u+1)*d]=-E
        DG[j*d:(j+1)*d,v*d:(v+1)*d]=T[u,v]
    check(n*d-DG.rank()==dim)
    def defect(x):return [T[u,v]*x[v]-x[u] for u,v in edges]
    for seed in range(5):
        x=[s.Matrix([s.Rational(((i+2)*(k+3)+seed)%11-5,seed+1) for k in range(d)]) for i in range(n)]
        rr=defect(x);eps=sup2(rr);y=[R[i]*Q*x[0] for i in range(n)]
        check(all(a==s.zeros(d,1) for a in defect(y)))
        check([R[i]*Q*y[0] for i in range(n)]==y)
        check(Q*y[0]==Q*x[0])
        routex=[R[i]*x[0] for i in range(n)]
        bound(sup2([x[i]-routex[i] for i in range(n)]),A,eps)
        hh=[(loop[e]-E)*x[0] for e in edges]
        bound(sup2(hh),N*(D*A+1),eps)
        bound(vnorm2(x[0]-Q*x[0]),kappa,sup2(hh))
        bound(sup2([x[i]-y[i] for i in range(n)]),C,eps)
        bound(sup2(y),B,sup2(x))
        # Exact transported telescoping on every route, not just its bound.
        for i in range(n):
            path=routes[i];total=s.zeros(d,1);pref=E.copy()
            for u,v in zip(path,path[1:]):
                total+=pref*(T[u,v]*x[v]-x[u]);pref=pref*T[u,v]
            check(total==root[i]*x[i]-x[0])
    return {'vertices':n,'dimension':d,'shape':kind,'fixture':t,'fixed_dimension':dim,'gain_bound':str(C)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    start=time.perf_counter();rows=[]
    for n in (3,4):
      for d in (1,2,3):
       for kind in ('path','cycle','complete'):
        for t in (0,1,2):rows.append(fixture(n,d,kind,t))
    # Exact all-positive-depth fixtures for the geometric chain formula.
    for n in range(1,41):
        x=[8*2**i-1 for i in range(n+1)];y=[7*2**i for i in range(n+1)]
        check(x[0]==7);check(max(abs(x[i]-y[i]) for i in range(n+1))==2**n-1)
        check(all(s.Rational(x[i+1],2)-x[i]==s.Rational(1,2) for i in range(n)))
        check(all(2*x[i]-x[i+1]==-1 for i in range(n)))
    negative=[
      {'claim':'route length suffices without isometry','rejected':2**3-1>3},
      {'claim':'anchor-preserving repair stays nonexpansive','rejected':14>7},
      {'claim':'omit inverse frame when restoring endpoint','rejected':s.Rational(1,2)*7!=2*7},
    ]
    for n in negative:check(n['rejected'])
    out={'status':'PASS','arithmetic':'exact SymPy Rational; squared Euclidean fiber / vertex-edge maximum norms',
         'cases':{'connections':len(rows),'candidates':len(rows)*5,'scalar_chain_lengths':40},
         'assertions':COUNT,'negative_controls':negative,'fixtures':rows,
         'non_claims':['Fixtures are not exhaustive.','Finite checks are not universal proofs.','Rational operator bounds are conservative, not optimal.'],
         'python':sys.version,'sympy':s.__version__,'runtime_seconds':time.perf_counter()-start,
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','cases','assertions','negative_controls','runtime_seconds')},indent=2))
if __name__=='__main__':main()
