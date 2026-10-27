"""Exact finite models for Paper VII's visual appendix.

Matrices use column state vectors and composition acts right to left.
Computational tensor order is the displayed left-to-right bit order.  All finite
identities below use SymPy rationals/algebraic expressions; plot sampling is
separate. Nothing in this module invokes Lean or asserts a continuum theorem.
"""
from __future__ import annotations
from functools import lru_cache
import sympy as s
R=s.Rational
M=s.Matrix
I=s.I

def basis(n:int,j:int)->s.Matrix:
    if n<1 or not 0<=j<n:raise ValueError('invalid basis address')
    return s.eye(n)[:,j]
def outer(v):return v*v.conjugate().T
def kron(*xs):
    out=M([[1]])
    for x in xs:out=s.kronecker_product(out,x)
    return out

def paulis():
    return M([[0,1],[1,0]]),M([[0,-I],[I,0]]),s.diag(1,-1)

def clean(a):
    if isinstance(a,s.MatrixBase):return a.applyfunc(lambda x:s.simplify(s.expand_complex(x)))
    return s.simplify(a)

@lru_cache(None)
def cyclic4():
    S=s.zeros(4)
    for j in range(4):S[(j+1)%4,j]=1
    Ps=[s.simplify(sum([I**(-j*r)*S**r for r in range(4)],s.zeros(4))/4) for j in range(4)]
    vecs=[M([I**(-j*k)/2 for k in range(4)]) for j in range(4)]
    L=2*s.eye(4)-S-S.T
    return S,Ps,vecs,L

@lru_cache(None)
def parity(n:int=3):
    if n<0:raise ValueError('qubit count must be nonnegative')
    d=2**n
    fine=[outer(basis(d,j)) for j in range(d)]
    groups=[[j for j in range(d) if j.bit_count()%2==a] for a in range(2)]
    coarse=[sum([fine[j] for j in g],s.zeros(d)) for g in groups]
    return fine,groups,coarse

@lru_cache(None)
def bell():
    X,Y,Z=paulis();h=M([[1,1],[1,-1]])/s.sqrt(2)
    cnot=M([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
    v0=basis(4,0);middle=kron(h,s.eye(2))*v0;v=cnot*middle
    return h,cnot,middle,v,outer(v)

@lru_cache(None)
def symmetry():
    X,Y,Z=paulis();H=kron(X,X)+R(3,8)*(kron(Z,s.eye(2))+kron(s.eye(2),Z))
    order=[0,3,1,2];B=s.eye(4)[:,order]
    return H,B,B.T*H*B

def rotation(t):return M([[s.cos(t),-s.sin(t)],[s.sin(t),s.cos(t)]])

def rotating_projector(t):
    U=rotation(t);P=U*s.diag(1,0)*U.T
    return U,P,s.eye(2)-P

def bloch(theta,phi):
    X,Y,Z=paulis()
    return (s.eye(2)+s.sin(theta)*s.cos(phi)*X+s.sin(theta)*s.sin(phi)*Y+s.cos(theta)*Z)/2

def dephase(rho,projectors):return sum([p*rho*p for p in projectors],s.zeros(rho.rows))

def channel(rho,Ks):return sum([k*rho*k.conjugate().T for k in Ks],s.zeros(rho.rows))

@lru_cache(None)
def damping():
    Ks=[s.diag(1,R(4,5)),M([[0,R(3,5)],[0,0]])]
    rho=M([[1,1],[1,1]])/2
    return Ks,rho,channel(rho,Ks)

def partial_transpose_second(a,da:int=2,db:int=2):
    return M(da*db,da*db,lambda r,c:a[(r//db)*db+c%db,(c//db)*db+r%db])

@lru_cache(None)
def code():
    X,Y,Z=paulis();E=[s.eye(8)]+[kron(*[X if j==k else s.eye(2) for j in range(3)]) for k in range(3)]
    V=M.hstack(basis(8,0),basis(8,7));P=V*V.T;Q=[a*P*a.T for a in E]
    psi=V*M([R(3,5),R(4,5)]);rho=outer(psi)
    weights=[R(1,10),R(2,10),R(3,10),R(4,10)]
    corrupted=sum([w*a*rho*a.T for w,a in zip(weights,E)],s.zeros(8))
    rec=[a.T*q for a,q in zip(E,Q)];recovered=channel(corrupted,rec)
    return E,V,P,Q,psi,rho,weights,corrupted,rec,recovered

@lru_cache(None)
def constraints():
    C1=s.diag(0,1,-1);C2=M([[0,0,0],[0,0,1],[0,1,0]]);P=s.diag(1,0,0)
    A=C1*C2-C2*C1
    return C1,C2,P,A

def sine_enclosure(x,n:int=8):
    """Alternating Taylor enclosure for 0 <= x <= 1, using rational arithmetic."""
    x=R(x)
    if not 0<=x<=1 or n<1:raise ValueError('0 <= x <= 1 and n >= 1 required')
    lo=sum([(-1)**j*x**(2*j+1)/s.factorial(2*j+1) for j in range(2*n)],s.S.Zero)
    hi=lo+x**(4*n+1)/s.factorial(4*n+1)
    return lo,hi

def dispersion_row(h):
    h=R(h);lo,hi=sine_enclosure(h/2,5)
    return {'h':h,'error_lower':1-4*hi**2/h**2,'error_upper':1-4*lo**2/h**2,'bound':h**2/12}

def exact_data():
    Ks,rho,output=damping();C1,C2,P,A=constraints()
    return {'damping_output':str(output),'damping_determinant':str(output.det()),
            'dispersion':[dict((k,str(v)) for k,v in dispersion_row(h).items()) for h in [R(1,4),R(1,8),R(1,16)]],
            'constraint_commutator':str(A),'conventions':'column vectors, right-to-left composition, bits left-to-right'}
