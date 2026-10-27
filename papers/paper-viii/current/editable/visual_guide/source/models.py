"""Exact worked models for the Paper VIII reader appendix.

All algebraic examples use SymPy rational/complex-exact arithmetic. Integer
operation counts and toy timing constants are models, not device measurements.
No algorithm in this module is claimed to be extracted from Lean.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import product
import sympy as s
M=s.Matrix
Q=s.Rational

def bdlr():
    block=M([[3,1],[1,3]])
    D=s.diag(block,block,block)
    u=s.ones(6,1); x=M([1,-1,2,0,-2,3])
    return D,u,u.copy(),D+u*u.T,x

def product_model():
    DA,ua,va,A,x=bdlr()
    DB=s.diag(1,2,3,4,5,6)
    ub=M([1,0,1,0,1,0]);vb=M([0,1,0,1,0,1])
    B=DB+ub*vb.T
    UC=(DA*ub+ua*(va.T*ub)).row_join(ua)
    VC=vb.row_join(DB.T*va)
    return DA,DB,ua,va,ub,vb,A,B,UC,VC

def circulant(c):
    n=len(c)
    return M(n,n,lambda i,j:c[(i-j)%n])

def fourier4():
    c=M([2,1,0,-1]); F=M(4,4,lambda j,k:s.I**(-j*k)/2)
    C=circulant(c);lam=2*F*c;x=M([1,2,-1,0])
    return c,F,C,lam,x

def toeplitz_model():
    T=M([[2,-1,5],[3,2,-1],[4,3,2]])
    g=M([2,3,4,0,5,-1]); x=M([1,2,-1])
    return T,g,circulant(g),x

def vec(X):return M([X[i,j] for j in range(X.cols) for i in range(X.rows)])

def kron_model():return M([[1,s.I],[2,-1]]),M([[2,1],[0,3]]),M([[1,2],[3,4]])

def walsh(n):
    if n<1 or n&(n-1):raise ValueError('Walsh size must be a positive power of two')
    H=s.ones(1)
    while H.rows<n:H=H.row_join(H).col_join(H.row_join(-H))
    return H

def walsh_stages(x):
    a=list(x); n=len(a)
    if not n or n&(n-1):raise ValueError('Walsh size must be a positive power of two')
    stages=[a.copy()];h=1
    while h<n:
        for j in range(0,n,2*h):
            for k in range(j,j+h):
                p,q=a[k],a[k+h];a[k]=p+q;a[k+h]=p-q
        stages.append(a.copy());h*=2
    return stages

def compact_model():
    QL=M([[Q(3,5),0],[Q(4,5),0],[0,1],[0,0]])
    RL=M([[1,0,1],[0,1,0]])
    RR=M([[3,0,2],[0,2,0],[1,0,-1]])
    L=QL*RL;R=RR;G=RL*RR.T
    return QL,RL,RR,L,R,G,L*R.T

def diamond():
    K=s.zeros(4)
    for i,j,v in [(1,0,1),(2,0,1),(3,1,1),(3,2,-1)]:K[i,j]=v
    return K

DAG_EDGES=((0,2),(1,2),(1,3),(2,4),(3,4),(3,5),(4,6),(5,6))
def dag_model():
    n=7;K=s.zeros(n)
    for a,b in DAG_EDGES:K[b,a]=-1
    D=2*s.eye(n);A=D+K;b=s.ones(n,1)
    levels=[];done=set()
    while len(done)<n:
        ready=[v for v in range(n) if v not in done and all(a in done for a,z in DAG_EDGES if z==v)]
        if not ready:raise ValueError('cycle')
        levels.append(ready);done.update(ready)
    return A,b,A.inv()*b,levels

def schur_model(cancellation=False):
    off=Q(1,2) if cancellation else 0
    A=M([[2,off,1],[off,2,1],[1,1,2]])
    D=A[:2,:2];U=A[:2,2:];V=A[2:,:2];H=A[2:,2:]
    return A,D-U*H.inv()*V

def preconditioner():
    A=M([[4,1],[1,1]]);D=s.diag(4,1);B=s.diag(Q(1,2),1)
    return A,D,B,B*A*B

def error_model():
    e=Q(1,100);A=s.eye(4)+e*(s.ones(4)-s.eye(4))
    return A,A-s.eye(4)

OPTIONS=(((0,7),(2,3),(4,1)),((0,6),(1,4),(3,1)),((0,9),(2,5),(5,1)))
def assignments():
    return [(sum(OPTIONS[i][a][0] for i,a in enumerate(c)),sum(OPTIONS[i][a][1] for i,a in enumerate(c)),c) for c in product(range(3),repeat=3)]

def precision_dp():
    tables=[{0:(0,())}]
    for opts in OPTIONS:
        table={}
        for w,(cost,selection) in tables[-1].items():
            for k,(wk,ck) in enumerate(opts):
                key=w+wk;candidate=(cost+ck,selection+(k,))
                if key not in table or candidate<table[key]:table[key]=candidate
        tables.append(table)
    return tables

@dataclass(frozen=True)
class Node:
    name:str
    cost:int
    error:int
    overhead:int=0
    children:tuple['Node',...]=()

def tree_model():
    return Node('r',1,6,1,(Node('a',3,2,0,(Node('a0',2,0),Node('a1',2,0))),Node('b',3,2,0,(Node('b0',2,0),Node('b1',3,0)))))

def prunings(node):
    rows=[(node.cost,node.error,(node.name,))]
    if node.children:
        for terms in product(*(prunings(c) for c in node.children)):
            rows.append((node.overhead+sum(t[0] for t in terms),sum(t[1] for t in terms),tuple(a for t in terms for a in t[2])))
    return rows

def tree_lagrange(node,lam):
    keep=(node.cost+lam*node.error,(node.name,))
    if not node.children:return keep
    children=[tree_lagrange(c,lam) for c in node.children]
    split=(node.overhead+sum(c[0] for c in children),tuple(v for c in children for v in c[1]))
    return min(keep,split)

def tree_budget(node):
    table={node.error:(node.cost,(node.name,))}
    if node.children:
        split={0:(node.overhead,())}
        for c in node.children:
            new={}
            for w,(cost,labels) in split.items():
                for z,(cc,ll) in tree_budget(c).items():
                    cand=(cost+cc,labels+ll)
                    if w+z not in new or cand<new[w+z]:new[w+z]=cand
            split=new
        for w,cand in split.items():
            if w not in table or cand<table[w]:table[w]=cand
    return table

def node_values(n,lam):
    out={n.name:tree_lagrange(n,lam)[0]}
    for c in n.children:out.update(node_values(c,lam))
    return out

def changed_leaf(n,name,cost):
    return replace(n,cost=cost) if n.name==name else replace(n,children=tuple(changed_leaf(c,name,cost) for c in n.children))

def modeled_bytes(sizes,edges,q,scalar_bytes=8):
    return scalar_bytes*sum(sizes[b]*sizes[a]+sizes[a]*q+2*sizes[b]*q for b,a in edges)
