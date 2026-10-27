"""Exact worked models for Paper V. All algebraic data uses SymPy exact arithmetic.

Signal conventions: N=16 periodic in Haar/smoothing examples; finitely supported
zero-extended sequences for FIR tests. Curves in the plates only sample explicit
formulas; no sampled curve is used as an acceptance certificate.
"""
from __future__ import annotations
from functools import lru_cache
from itertools import product
import sympy as s
Q=s.Rational
D,t,w,v=s.symbols('D t w v')
SMOOTH=s.Matrix([Q(a,4) for a in [0,1,2,1,0,-1,-2,-1]*2])
MASK=tuple(6<=i<12 for i in range(16))
JUMP=s.Matrix([3 if b else 0 for b in MASK])
SIGNAL=SMOOTH+JUMP
FIR={0:Q(1),1:Q(2),2:Q(-1),3:Q(1)}
J=s.Matrix([[0,D],[1,0]])
H=s.eye(2)+2*J-J**2+J**3
H2=s.Matrix([[1,1],[1,-1]])/s.sqrt(2)
LIFT=s.Matrix([[Q(1,2),Q(1,2)],[-1,1]])
COSTS={'':20,'0':5,'1':8,'00':1,'01':2,'10':7,'11':4,
       '000':1,'001':2,'010':2,'011':3,'100':1,'101':1,'110':2,'111':3}

def eq(a,b)->bool:
    if isinstance(a,s.MatrixBase) or isinstance(b,s.MatrixBase):
        a,b=s.Matrix(a),s.Matrix(b)
        return a.shape==b.shape and all(s.simplify(x-y)==0 for x,y in zip(a,b))
    return s.simplify(a-b)==0

def energy(a): return s.simplify(sum(s.conjugate(v)*v for v in a))
def phases(x,N:int): return [list(x[r::N]) for r in range(N)]
def analyze_dict(x:dict,N:int):
    if N<1:raise ValueError('N must be positive')
    return tuple({n//N:a for n,a in x.items() if n%N==r and a!=0} for r in range(N))
def synthesize_dict(ch):return {len(ch)*n+r:a for r,c in enumerate(ch) for n,a in c.items() if a!=0}
def convolve(h:dict,x:dict):
    out={}
    for k,a in h.items():
        for n,b in x.items():out[n+k]=out.get(n+k,0)+a*b
    return {n:s.simplify(a) for n,a in out.items() if a!=0}
def polyphase_convolve(h:dict,x:dict,N:int):
    ch=analyze_dict(x,N);out=[{} for _ in range(N)]
    for k in range(N):
        for tap,a in h.items():
            j=(k-tap)%N;delay=(tap-k+j)//N
            for n,b in ch[j].items():out[k][n+delay]=out[k].get(n+delay,0)+a*b
    return synthesize_dict(out)
def fir_polyphase_matrix(h:dict,N:int):
    return s.Matrix(N,N,lambda k,j:sum(a*D**((q-k+j)//N) for q,a in h.items() if (q-k+j)%N==0))
def smooth_periodic(x):
    n=len(x);return s.Matrix([s.simplify((x[(i-1)%n]+2*x[i]+x[(i+1)%n])/4) for i in range(n)])
@lru_cache(None)
def one_level(n:int,bit:int):
    if n<=0 or n%2 or bit not in (0,1):raise ValueError('even n and binary branch required')
    a=s.zeros(n//2,n)
    for i in range(n//2):a[i,2*i]=1/s.sqrt(2);a[i,2*i+1]=(1 if bit==0 else -1)/s.sqrt(2)
    return a
@lru_cache(None)
def packet(n:int,address:str):
    a=s.eye(n);size=n
    for b in address:
        a=one_level(size,int(b))*a;size//=2
    return a.applyfunc(s.simplify)
def addresses(depth:int):return tuple(''.join(b) for b in product('01',repeat=depth))
def packet_coefficients(depth=2):return {a:packet(16,a)*SIGNAL for a in addresses(depth)}
def packet_projector(n,a):
    w=packet(n,a);return (w.T*w).applyfunc(s.simplify)
@lru_cache(None)
def prunings(node='',depth=3):
    if len(node)==depth:return ((node,),)
    return ((node,),)+tuple(a+b for a in prunings(node+'0',depth) for b in prunings(node+'1',depth))
def complete(cut,depth=3):
    return len(set(cut))==len(cut) and all(sum(leaf.startswith(a) for a in cut)==1 for leaf in addresses(depth))
def cost(cut,costs=None):
    costs=COSTS if costs is None else costs
    return sum(costs[a] for a in cut)
def optimum(node='',depth=3,costs=None):
    costs=COSTS if costs is None else costs
    if len(node)==depth:return costs[node],(node,)
    a,ca=optimum(node+'0',depth,costs);b,cb=optimum(node+'1',depth,costs)
    return (costs[node],(node,)) if costs[node]<=a+b else (a+b,ca+cb)
def envelope(node='',depth=3,eps=None):
    eps={a:Q(1,32) for a in COSTS} if eps is None else eps
    if len(node)==depth:return eps[node]
    return max(eps[node],envelope(node+'0',depth,eps)+envelope(node+'1',depth,eps))
def ranked_prunings():return sorted((cost(c),c) for c in prunings())
def best_coefficients(k:int):
    coeff=packet_coefficients();entries=[(a,i,s.simplify(c)) for a,cs in coeff.items() for i,c in enumerate(cs)]
    entries.sort(key=lambda q:(-q[2]**2,q[0],q[1]))
    chosen=entries[:k];reconstructed=s.zeros(16,1)
    for a,i,c in chosen:reconstructed+=packet(16,a).T[:,i]*c
    return chosen,reconstructed.applyfunc(s.simplify),s.simplify(sum(c*c for _,_,c in entries[k:]))
def masked_polynomial(p,N,k):
    return s.expand(sum(co*t**int(mon[0]) for mon,co in s.Poly(p,t).terms() if mon[0]%N==k))
def gamma(z):
    z=s.sympify(z);return s.simplify((z-1)/(z+1))
def impedance(g):
    g=s.sympify(g);return s.simplify((1+g)/(1-g))
def action(a):return s.Matrix([[1+a,1-a],[1-a,1+a]])/2
def homogeneous_equal(x,y):return s.simplify(x[0]*y[1]-x[1]*y[0])==0 and x!=s.zeros(2,1) and y!=s.zeros(2,1)
def circle_masks():
    a={(i,j) for i in range(8) for j in range(8) if (i-3)**2+(j-3)**2<=5}
    b={(i+1,j) for i,j in a}
    return a,b
