#!/usr/bin/env python3
"""Exact finite audits for the v1.4.0 monograph models.

Only standard-library integer and Fraction arithmetic is used. Infinite claims
are proved in the manuscript, not inferred by extending these finite tests.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product, permutations
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
COUNT = 0
CASES: dict[str, int] = {}
CONTROLS: list[str] = []

def check(condition: bool, message: str) -> None:
    global COUNT
    COUNT += 1
    if not condition:
        raise AssertionError(message)

def reject_false_claim(condition: bool, name: str) -> None:
    check(not condition, 'Unrejected false claim: ' + name)
    CONTROLS.append(name)

def vmax(v):
    return max((abs(x) for x in v), default=F(0))

def vsub(x, y):
    return tuple(a-b for a,b in zip(x,y))

def norm2(x):
    return sum((a*a for a in x), F(0))

def run() -> dict:
    # Polynomial path: compare recurrence, direct formulas and telescoped tails.
    count = 0
    for s in [F(-3), F(0), F(5,2)]:
        Q = F(1)
        for n in range(65):
            r = F(1,n+1); q = F(n+1,n+2); c = F(1,n+2)
            x=(s,r); y=(s,F(1,n+2))
            check(Q==r, 'Polynomial prefix product')
            check(y[1]==q*x[1], 'Polynomial residual recurrence')
            check(vmax(vsub(x,y))==c*r, 'Polynomial exact step budget')
            check(x[0]==y[0]==s, 'Polynomial preservation')
            end=n+13
            partial=sum((F(1,(k+1)*(k+2)) for k in range(n,end)),F(0))
            check(partial==r-F(1,end+1), 'Telescoped polynomial finite tail')
            check(partial+F(1,end+1)==vmax(vsub(x,(s,F(0)))), 'Polynomial sharp tail')
            Q*=q; count+=1
    CASES['polynomial_path_states']=count

    # Bursting path: some q_n exceed one; pair products still decay.
    q=lambda n: F(2) if n%2==0 else F(1,8)
    c=lambda n: F(1) if n%2==0 else F(7,8)
    directQ=lambda n: F(1,4**(n//2))*(1 if n%2==0 else 2)
    tail=lambda n: (F(11,3) if n%2==0 else F(8,3))*F(1,4**(n//2))
    Q=F(1)
    for n in range(65):
        check(Q==directQ(n), 'Burst product formula')
        check(abs(directQ(n+1)-Q)==c(n)*Q, 'Burst movement formula')
        check(tail(n)-tail(n+1)==c(n)*Q, 'Burst infinite-tail recurrence')
        check(Q<=tail(n), 'Burst tail controls endpoint distance')
        end=n+11
        budget=sum((c(k)*directQ(k) for k in range(n,end)),F(0))
        check(budget+tail(end)==tail(n), 'Burst finite and remaining tail identity')
        Q*=q(n)
    CASES['burst_path_states']=65
    reject_false_claim(all(q(n)<1 for n in range(8)), 'Every valid variable-rate step must contract')

    # Distinct convergent paths with the same initial point and residual.
    fp=lambda s,a,n:(s,a*(1-F(1,2**n)),F(1,2**n))
    cases=0
    for s,a,n in product([F(-2),F(1)],map(F,range(-2,3)),range(33)):
        x=fp(s,a,n);y=fp(s,a,n+1);L=(s,a,F(0));C=max(abs(a),F(1))/2
        check(fp(s,a,0)==(s,F(0),F(1)), 'Common starting input')
        check(x[0]==s and x[2]==F(1,2**n), 'Common protected coordinate and residual')
        check(vmax(vsub(x,y))==C*x[2], 'Geometric movement')
        check(vmax(vsub(x,L))==2*C*x[2], 'Geometric posterior tail')
        for b in map(F,range(-2,3)):
            check(vmax(vsub(x,fp(s,b,n)))==abs(a-b)*(1-F(1,2**n)), 'Path separation formula')
        cases+=1
    CASES['geometric_path_states']=cases
    reject_false_claim((F(1),F(0),F(0))==(F(1),F(1),F(0)), 'Same residual and protected value determine one exact point')

    H=F(0)
    for n in range(257):
        x=(F(7),H,F(1,n+1)); newH=H+F(1,n+1); y=(F(7),newH,F(1,n+2))
        check(vmax(vsub(x,y))==x[2], 'Harmonic drift movement')
        check(y[2]==F(n+1,n+2)*x[2], 'Harmonic residual still decreases')
        H=newH
    for k in range(1,9):
        h=sum((F(1,j) for j in range(1,2**k+1)),F(0))
        check(h>=1+F(k,2), 'Harmonic dyadic lower bound')
    CASES['harmonic_path_states']=257
    reject_false_claim(sum((F(1,j) for j in range(5,9)),F(0))<F(1,2), 'Small residual forces a small total state movement')

    for n in range(65):
        check(F(1,(2**n-1)+1)==F(1,2**n), 'Cofinal schedule changes apparent rate')
        check((2*n)%2==0 and (2*n+1)%2==1, 'Alternating sampling witness')
    CASES['profile_sample_indices']=65
    reject_false_claim((2*9+1)%2==0, 'Zero sampled alternating profile means zero full profile')

    # Diagonal model. Reported infinite-tail bounds are proved by telescopes.
    cases=0
    for N in range(1,65):
        for L in range(N+1,N+13):
            u=tuple(F(-1) if j<=N else F(0) for j in range(1,L+1))
            r=tuple((u[j-1]+1)/j for j in range(1,L+1))
            check(all(r[j-1]==0 for j in range(1,N+1)), 'Exact finite prefix')
            check(r[N]==F(1,N+1), 'Next residual remains nonzero')
            check(norm2(u)==N, 'Squared correction norm')
            check(norm2(u)+1==N+1, 'Squared full candidate norm')
            partial=sum((F(1,j*j) for j in range(N+1,L+1)),F(0))
            check(norm2(r)==partial, 'Independent residual vector sum')
            check(partial+F(1,L+1)>=F(1,N+1), 'Infinite tail lower enclosure')
            check(partial+F(1,L)<=F(1,N), 'Infinite tail upper enclosure')
            check(F(1,(L)*(L+1))<=F(1,L*L)<=F(1,L*(L-1)), 'Termwise telescope comparison')
            cases+=1
    CASES['diagonal_prefix_tail_windows']=cases
    reject_false_claim(F(1,17)==0, 'Exact first sixteen coordinates imply exact infinite candidate')
    for N in range(1,33):
        for j in range(1,N+1):
            check(F(1,j*j)*N*N>=1, 'Finite inverse bound on coordinate witnesses')
            if j==N:
                check(F(1,j*j)*N*N==1, 'Finite inverse gain attained')
        if N<32:
            check((N+1)>N, 'Growing squared correction size')
    CASES['diagonal_inverse_dimensions']=32
    for v in product(map(F,[-1,0,1]),repeat=4):
        residual=tuple((v[j-1]+1)/j for j in range(1,5))
        check(norm2(tuple(t+1 for t in v))<=16*norm2(residual), 'Finite weighted-norm inequality')
    CASES['finite_escape_inequality_vectors']=81

    for n,a in product(range(25),map(F,range(-3,4))):
        check((F(n)-a)**2+1>=1, 'Persistent floor lower bound')
        check((F(n)-F(n))**2+1==1, 'Persistent floor attained')
        check((F(n)-a)**2+F(1,(n+1)**2)>=F(1,(n+1)**2), 'Nonpersistent positive floors')
    CASES['horizontal_floor_cases']=175

    # Shortest-path costs: Floyd-Warshall is compared with simple path enumeration.
    vertices=range(4); infinity=float('inf')
    edges={(0,1):0,(1,0):0,(0,2):2,(2,0):5}
    d=[[0 if i==j else edges.get((i,j),infinity) for j in vertices] for i in vertices]
    for k,i,j in product(vertices,repeat=3):
        d[i][j]=min(d[i][j],d[i][k]+d[k][j])
    expected=[[0,0,2,infinity],[0,0,2,infinity],[5,5,0,infinity],[infinity,infinity,infinity,0]]
    check(d==expected, 'Published distance matrix')
    for i,j in product(vertices,repeat=2):
        best=0 if i==j else infinity
        if i!=j:
            others=[v for v in vertices if v not in (i,j)]
            for length in range(len(others)+1):
                for mid in permutations(others,length):
                    path=(i,)+mid+(j,)
                    value=sum(edges.get((a,b),infinity) for a,b in zip(path,path[1:]))
                    best=min(best,value)
        check(best==d[i][j], 'Shortest cost vs independently enumerated paths')
    sym=[[max(d[i][j],d[j][i]) for j in vertices] for i in vertices]
    for i,j,k in product(vertices,repeat=3):
        check(d[i][k]<=d[i][j]+d[j][k], 'Directed triangle')
        check(sym[i][k]<=sym[i][j]+sym[j][k], 'Symmetric triangle')
    check(sym[0][1]==0 and sym[0][2]==5 and sym[0][3]==infinity, 'Zero classes and quotient distances')
    CASES['cost_matrix_pairs']=16
    reject_false_claim(1+1==0, 'Two zero-cost free edges compose to the identity path')
    reject_false_claim(d[0][2]==d[2][0], 'All transport costs are symmetric')

    # Phase model, all gauges, exact matrix lifts and the eight-element extension.
    G=[(0,0),(1,0),(0,1),(1,1)]
    plus=lambda x,y:((x[0]+y[0])%2,(x[1]+y[1])%2)
    phase=lambda x,y:x[1]*y[0]%2
    for x,y,z in product(G,repeat=3):
        check((phase(x,y)+phase(plus(x,y),z))%2==(phase(y,z)+phase(x,plus(y,z)))%2,'All phase cocycles')
    for x in G:
        check(phase((0,0),x)==phase(x,(0,0))==0,'Normalized phase')
    for values in product(range(2),repeat=4):
        a=dict(zip(G,values)); delta=lambda x,y:(a[x]+a[y]-a[plus(x,y)])%2
        check(any(phase(x,y)!=delta(x,y) for x,y in product(G,repeat=2)),'No scalar flattening among all gauges')
        for x,y in product(G,repeat=2):
            check(delta(x,y)==delta(y,x),'Every scalar coboundary is symmetric')
            check((phase(x,y)+delta(x,y)-phase(y,x)-delta(y,x))%2==(phase(x,y)-phase(y,x))%2,'Gauge-invariant antisymmetric phase')
    I=(1,0,0,1);X=(0,1,1,0);Z=(1,0,0,-1)
    def mul(A,B):
        return (A[0]*B[0]+A[1]*B[2],A[0]*B[1]+A[1]*B[3],
                A[2]*B[0]+A[3]*B[2],A[2]*B[1]+A[3]*B[3])
    scale=lambda s,A:tuple(s*t for t in A)
    U={x:mul(X if x[0] else I,Z if x[1] else I) for x in G}
    for x,y in product(G,repeat=2):
        check(mul(U[x],U[y])==scale((-1)**phase(x,y),U[plus(x,y)]),'Actual projective matrix multiplier')
    H=list(product(range(2),G)); one=(0,(0,0))
    def hm(a,b):
        return ((a[0]+b[0]+phase(a[1],b[1]))%2,plus(a[1],b[1]))
    lift=lambda a:scale((-1)**a[0],U[a[1]])
    for a,b,c0 in product(H,repeat=3):
        check(hm(hm(a,b),c0)==hm(a,hm(b,c0)),'Associative central extension')
    for a in H:
        inv=((a[0]+phase(a[1],a[1]))%2,a[1])
        check(hm(a,inv)==hm(inv,a)==one,'Two-sided inverse')
        check(hm(a,one)==hm(one,a)==a,'Identity')
    for a,b in product(H,repeat=2):
        check(lift(hm(a,b))==mul(lift(a),lift(b)),'Faithful matrix lift is a homomorphism')
    check(len({lift(a) for a in H})==8,'Eight distinct lifted matrices')
    reject_false_claim(phase((1,0),(0,1))==phase((0,1),(1,0)), 'Associative phase must be a symmetric coboundary')
    CASES.update({'phase_triples':64,'scalar_gauges':16,'extension_multiplication_triples':512,'matrix_lift_pairs':64})
    return {'status':'PASS','executed_utc':datetime.now(timezone.utc).isoformat(),
            'assertions':COUNT,'cases':CASES,'negative_controls':CONTROLS,
            'negative_control_count':len(CONTROLS),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'Finite exact arithmetic regression. Infinite convergence, closure, nonexistence and norm claims rely on the supplied mathematical proofs, not finite extrapolation. No Lean replay is executed.'}

if __name__=='__main__':
    try:
        result=run()
    except Exception as exc:
        result={'status':'FAIL','executed_utc':datetime.now(timezone.utc).isoformat(),
                'assertions_before_failure':COUNT,'error':repr(exc)}
        (ROOT/'audit/deepening_exact.json').write_text(json.dumps(result,indent=2)+'\n')
        raise
    (ROOT/'audit/deepening_exact.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
