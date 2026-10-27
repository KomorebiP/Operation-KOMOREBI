#!/usr/bin/env python3
"""Exact-rational audit of finite-dimensional orthogonal holonomy repair.

Norms: Euclidean on each fiber, maximum over vertices/directed edges.
The finite computation audits independently implemented matrices. It does not
replace Lean's universal finite-dimensional existence and optimal-gain proofs.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import argparse, datetime as dt, hashlib, json, platform, time

assertions=0
def check(b: bool, label: str) -> None:
    global assertions
    assertions+=1
    if not b: raise AssertionError(label)
def eye(n): return [[Q(int(i==j)) for j in range(n)] for i in range(n)]
def zeros(m,n): return [[Q(0) for _ in range(n)] for _ in range(m)]
def transpose(A): return list(map(list,zip(*A)))
def add(A,B): return [[a+b for a,b in zip(r,s)] for r,s in zip(A,B)]
def sub(A,B): return [[a-b for a,b in zip(r,s)] for r,s in zip(A,B)]
def scale(c,A):return [[c*a for a in r] for r in A]
def mm(A,B):
    BT=transpose(B)
    return [[sum((a*b for a,b in zip(r,c)),Q(0)) for c in BT] for r in A]
def mv(A,v): return [sum((a*b for a,b in zip(r,v)),Q(0)) for r in A]
def vs(u,v):return [a-b for a,b in zip(u,v)]
def sq(v):return sum((a*a for a in v),Q(0))
def maxsq(xs):return max(map(sq,xs),default=Q(0))
def rref(A):
    B=[r[:] for r in A]; piv=[];k=0
    if not B:return B,piv
    for j in range(len(B[0])):
        p=next((i for i in range(k,len(B)) if B[i][j]),None)
        if p is None:continue
        B[k],B[p]=B[p],B[k]
        a=B[k][j];B[k]=[b/a for b in B[k]]
        for i in range(len(B)):
            if i!=k:
                a=B[i][j]
                B[i]=[b-a*c for b,c in zip(B[i],B[k])]
        piv.append(j);k+=1
        if k==len(B):break
    return B,piv
def inverse(A):
    n=len(A);B,p=rref([a+b for a,b in zip(A,eye(n))])
    if p[:n]!=list(range(n)):raise ValueError('singular matrix')
    if [r[:n] for r in B]!=eye(n):raise ValueError('invalid inverse reduction')
    return [r[n:] for r in B]
def null_basis(A,n):
    B,p=rref(A);out=[]
    for j in range(n):
        if j in p:continue
        v=[Q(0)]*n;v[j]=Q(1)
        for i,k in enumerate(p):v[k]=-B[i][j]
        out.append(v)
    return out
def proj_span(vectors,n):
    if not vectors:return zeros(n,n)
    B=transpose(vectors)
    return mm(mm(B,inverse(mm(transpose(B),B))),transpose(B))
def ldl_positive(A):
    """Exact symmetric LDL certificate. None means strict positive-definiteness fails."""
    n=len(A)
    if transpose(A)!=A:return None
    L=eye(n);D=[]
    for i in range(n):
        d=A[i][i]-sum((L[i][k]**2*D[k] for k in range(i)),Q(0))
        if d<=0:return None
        D.append(d)
        for j in range(i+1,n):
            L[j][i]=(A[j][i]-sum((L[j][k]*L[i][k]*D[k] for k in range(i)),Q(0)))/d
    diag=zeros(n,n)
    for i,d in enumerate(D):diag[i][i]=d
    check(mm(mm(L,diag),transpose(L))==A,'LDL reconstruction')
    return D
def cayley(t):
    den=t*t+1
    return [[(t*t-1)/den,-2*t/den],[2*t/den,(t*t-1)/den]]
def embedded(n,t,offset=0):
    if n==1:return [[Q(-1)]]
    A=eye(n);i=offset%(n-1);B=cayley(t)
    for r in range(2):
        for c in range(2):A[i+r][i+c]=B[r][c]
    return A

def run(output: Path):
    start=time.monotonic();when=dt.datetime.now(dt.timezone.utc).isoformat()
    cases=0;candidates=0;certificates=[];ranks=set()
    for n in range(1,5):
      for mode in range(6):
       for loops in range(1,4):
        vertices=loops+2;I=eye(n);tau={}
        for j in range(1,vertices):tau[0,j]=I;tau[j,0]=I
        for j in range(1,loops+1):
            A=I if mode==0 else embedded(n,Q([0,0,1,3,7,11][mode]),j+mode)
            if mode==5 and n>1 and j==loops:
                A=eye(n);A[-1][-1]=Q(-1)
            tau[j,j+1]=A;tau[j+1,j]=transpose(A)
        edges=sorted(tau);m=len(edges)
        for a in edges:
            check(mm(tau[a],transpose(tau[a]))==I,'isometric connection')
            check(tau[a[::-1]]==transpose(tau[a]),'inverse-consistent reverse transport')
        D=[r for a in edges for r in sub(tau[a],I)]
        N=null_basis(D,n);P=proj_span(N,n)
        B0,piv=rref(D);rows=B0[:len(piv)];ranks.add(len(N))
        complement=proj_span(rows,n)
        check(P==sub(I,complement),'independent kernel and row-space projectors agree')
        check(mm(P,P)==P,'projection idempotence')
        check(transpose(P)==P,'projection self-adjointness')
        check(mm(D,P)==zeros(len(D),n),'actual rooted defect killed')
        DG=[]
        for i,j in edges:
            for k in range(n):
                row=[Q(0)]*(vertices*n)
                row[i*n+k]-=1
                for l in range(n):row[j*n+l]+=tau[i,j][k][l]
                DG.append(row)
        _,gp=rref(DG)
        check(vertices*n-len(gp)==len(N),'independent global kernel agrees with holonomy kernel')
        lam=Q(1);ldl=[]
        if rows:
            B=transpose(rows);DB=mm(D,B);M=mm(transpose(DB),DB);Gram=mm(transpose(B),B)
            for _ in range(128):
                ldl=ldl_positive(sub(M,scale(lam,Gram)))
                if ldl is not None:break
                lam/=2
            else:raise RuntimeError('gap-certificate resource cap reached')
            # An integer/rational upper bound avoids introducing sqrt approximations.
            C=max(Q(1),Q(m)/lam)
            check(C*C*lam>=m,'certified conversion from squared sum to edge maximum')
        else:C=Q(0)
        for f in range(6):
            x=[[Q(((f+1)*(i+2)*(j+3))%19-9,1+(f+j)%3) for j in range(n)] for i in range(vertices)]
            z=x[0];qz=mv(P,z);h=[mv(sub(tau[a],I),z) for a in edges]
            check(sq(vs(z,qz))<=C*C*maxsq(h),'certified anchor error bound')
            check(sq(qz)<=sq(z),'anchor projection contraction')
            dx=[vs(mv(tau[i,j],x[j]),x[i]) for i,j in edges]
            y=[qz[:] for _ in range(vertices)]
            check(all(vs(mv(tau[i,j],y[j]),y[i])==[Q(0)]*n for i,j in edges),'exact reconstructed section')
            check(mv(P,y[0])==qz,'protected feasible anchor component')
            check(maxsq(y)<=maxsq(x),'global repair contraction')
            check(maxsq(vs(a,b) for a,b in zip(x,y))<=(1+3*C)**2*maxsq(dx),'global routed error bound')
            for w in [z,[Q(i-f) for i in range(n)]]:
                w0=mv(P,w)
                check(sq(vs(z,qz))<=sq(vs(z,w0)),'anchor best approximation')
            candidates+=1
        certificates.append({'fiber_dimension':n,'mode':mode,'loops':loops,
            'directed_edges':m,'fixed_dimension':len(N),'lambda':str(lam),
            'LDL_pivots':list(map(str,ldl)) if ldl else [],'certified_anchor_constant':str(C)})
        cases+=1
    cayley_cases=0
    for t in map(Q,[-1000,-100,-7,-1,0,1,2,5,10,100,1000]):
        K=cayley(t);D=sub(K,eye(2));gain_sq=(t*t+1)/4
        check(mm(K,transpose(K))==eye(2),'Cayley rotation orthogonal')
        check(len(null_basis(D,2))==0,'Cayley fixed space zero')
        for z in [[Q(1),Q(0)],[Q(0),Q(1)],[Q(7),Q(-3)],[Q(2,3),Q(-5,4)]]:
            check(sq(z)==gain_sq*sq(mv(D,z)),'exact squared sharp gain identity')
            cayley_cases+=1
    controls=[]
    def reject(name,predicate):
        check(not predicate,'negative control '+name)
        controls.append({'claim':name,'rejected':True})
    reject('uniform_gain_one_for_all_isometric_loop_systems',Q(1)<=sq(mv(sub(cayley(Q(5)),eye(2)),[Q(1),Q(0)])))
    reject('all_anchor_components_can_be_preserved',mv(zeros(2,2),[Q(1),Q(0)])==[Q(1),Q(0)])
    reject('nontrivial_holonomy_forces_zero_core',len(null_basis(sub(embedded(3,Q(3)),eye(3)),3))==0)
    reject('Euclidean_stacked_gain_equals_max_norm_gain',Q(1)<=Q(1,8)*4)
    reject('nonpositive_gap_is_a_valid_LDL_certificate',ldl_positive([[Q(-1)]]) is not None)
    result={'status':'PASS','coefficient_domain':'fractions.Fraction; exact rational real matrices',
      'norm_conventions':'Euclidean fiber norms; maximum vertex/edge norms; all comparisons squared exactly',
      'cases':{'connection_systems':cases,'candidate_families':candidates,'Cayley_vectors':cayley_cases},
      'fixed_dimensions':sorted(ranks),'assertions':assertions,'negative_controls':controls,
      'certificates':certificates,'randomness':{'used':False},
      'bounds':{'fiber_dimensions':[1,2,3,4],'vertices':[3,4,5],
        'loop_counts':[1,2,3],'fixture_modes':6,'candidates_per_system':6,'gap_halving_cap':128},
      'non_claims':['Finite fixtures are not an exhaustive enumeration or a universal proof.',
        'The finite auditor does not compute or validate a floating-point singular value.',
        'Optimality and arbitrary finite-dimensional existence are proved by Lean, not inferred from these checks.'],
      'started_at_utc':when,'runtime_seconds':time.monotonic()-start,'python':platform.python_version(),
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',result['cases'],'assertions',assertions,'seconds',round(result['runtime_seconds'],3))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
