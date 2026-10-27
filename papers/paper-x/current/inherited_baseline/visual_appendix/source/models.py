"""Exact worked models for Paper X. No general Galois/automorphy existence algorithm.

All arithmetic in the evidence models is integer, rational, finite-field, or symbolic.
The drawings may convert exact values to decimal positions, never to decide a check.
"""
from __future__ import annotations
from itertools import product, combinations
from math import gcd, ceil, isqrt
import sympy as s

T = s.Symbol('T')

def roots_mod(p: int, depth: int, f=lambda x: x*x+1) -> tuple[int,...]:
    if p < 2 or depth < 1: raise ValueError('Require p >= 2 and positive depth.')
    modulus = p**depth
    return tuple(x for x in range(modulus) if f(x) % modulus == 0)

def root_lift(p: int, depth: int, a: int) -> tuple[int,...]:
    return tuple(a + j*p**depth for j in range(p) if ((a+j*p**depth)**2+1) % (p**(depth+1)) == 0)

def quarter_branch(length=6):
    return [pow(4,-1,5**m) for m in range(1,length+1)]

def decode_digits(p: int, residues):
    previous=0; digits=[]
    for m,x in enumerate(residues,1):
        if not 0<=x<p**m or x % p**(m-1) != previous:
            raise ValueError('Not a normalized compatible residue stream.')
        digits.append((x-previous)//p**(m-1));previous=x
    return digits

def smooth_count(q: int,d: int,m: int):return q**(d*(m-1))
def weighted_count(q: int,weights,m: int):return q**sum(max(m-w,0) for w in weights)
def weighted_zeta(q: int,weights):
    W=sum(weights);last=max(weights,default=0);d=len(weights)
    if not weights:return T/(1-T)
    return s.cancel(sum(weighted_count(q,weights,m)*T**m for m in range(1,last+1)) + s.Rational(1,q**W)*(q**d*T)**(last+1)/(1-q**d*T))
def singular_count(q: int,e: int,m: int):return q**(m-(m+e-1)//e)
def singular_zeta(q: int,e: int):return sum(q**(r-1)*T**r for r in range(1,e+1))/(1-q**(e-1)*T**e)

def rank_mod(A,p):
    a=[[int(x)%p for x in row] for row in s.Matrix(A).tolist()];m=len(a);n=len(a[0]) if m else 0;r=0
    for c in range(n):
        pivot=next((i for i in range(r,m) if a[i][c]),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r];iv=pow(a[r][c],-1,p);a[r]=[(v*iv)%p for v in a[r]]
        for i in range(m):
            if i!=r:
                factor=a[i][c];a[i]=[(u-factor*v)%p for u,v in zip(a[i],a[r])]
        r+=1
        if r==m:break
    return r

def complex_model():
    d0=s.Matrix([[1,0],[0,0],[0,0],[0,0]])
    d1=s.Matrix([[0,1,0,0],[0,0,0,0]])
    projectors=[s.diag(1,0),s.diag(1,1,0,0),s.diag(1,0)]
    return d0,d1,projectors

def finite_image(A,p):
    A=s.Matrix(A)
    return {tuple(int(v)%p for v in A*s.Matrix(x)) for x in product(range(p),repeat=A.cols)}
def finite_kernel(A,p):
    A=s.Matrix(A)
    return {tuple(x) for x in product(range(p),repeat=A.cols) if all(int(v)%p==0 for v in A*s.Matrix(x))}

VERTICES=tuple('ABCDEFG')
EDGES=(('A','B'),('B','A'),('B','C'),('C','F'),('D','E'),('E','D'),('E','F'),('G','F'))
def reachable(seeds,edges=EDGES):
    found=set(seeds)
    while True:
        new=found|{v for u,v in edges if u in found}
        if new==found:return found
        found=new

def sccs(vertices=VERTICES,edges=EDGES):
    unseen=set(vertices);out=[]
    while unseen:
        u=min(unseen);r=reachable([u],edges)
        component={v for v in unseen if v in r and u in reachable([v],edges)}
        unseen-=component;out.append(tuple(sorted(component)))
    return out

def minimum_seed_sets(vertices=VERTICES,edges=EDGES):
    for k in range(len(vertices)+1):
        ans=[list(c) for c in combinations(vertices,k) if reachable(c,edges)==set(vertices)]
        if ans:return k,ans
    raise AssertionError('Finite graph must have a generating vertex set.')

def s3_data():
    C=s.Matrix([[1,1,2],[1,-1,0],[1,1,-1]])
    multiplicities=s.Matrix([2,0,1]);capacities=(2,1,1)
    return C,multiplicities,C*multiplicities,capacities

def recover_multiplicities(C,b,capacities):
    C=s.Matrix(C);b=s.Matrix(b)
    if C.rank()!=C.cols:raise ValueError('Insufficient separating rank.')
    m=list(C.inv()*b)
    if any(x.q!=1 for x in m):raise ValueError('Nonintegral multiplicity.')
    if any(x<0 for x in m):raise ValueError('Negative multiplicity.')
    if any(x>c for x,c in zip(m,capacities)):raise ValueError('Carrier capacity exceeded.')
    return tuple(int(x) for x in m)

def occupancy_data():
    labels=((0,0,0),(0,0,1),(0,1,0),(1,0,1),(1,1,0),(1,1,1))
    operators=[s.diag(*(x[j] for x in labels)) for j in range(3)]
    return labels,operators

def joint_projector(target):
    labels,ops=occupancy_data();E=s.eye(len(labels))
    for t,op in zip(target,ops):E=E*((s.eye(len(labels))-op) if t==0 else op)
    return E

F25=tuple(product(range(5),repeat=2))
def f25_mul(z,w):
    a,b=z;c,d=w;return ((a*c+2*b*d)%5,(a*d+b*c)%5)
def f25_norm(z):
    a,b=z;return (a*a-2*b*b)%5
def f25_matrix(z):
    a,b=z;return s.Matrix([[a,2*b],[b,a]])
def f25_pow(z,n):
    y=(1,0)
    for _ in range(n):y=f25_mul(y,z)
    return y

def chi5(a):return {0:0,1:1,2:-1,3:-1,4:1}[a%5]
def chi4(a):return {0:s.Integer(0),1:s.Integer(1),2:s.I,3:-s.I,4:s.Integer(-1)}[a%5]
def character(a,k):return s.Integer(0) if a%5==0 else s.expand(chi4(a)**k)
def scalar_witness(k,d):return any(character(pow(a,d,5),k)!=1 for a in range(1,5))
def unit_orbits(v=(0,2)):
    todo=set(F25)-{(0,0)};out=[]
    while todo:
        z=min(todo);orbit=[];w=z
        while not orbit or w!=z:orbit.append(w);w=f25_mul(v,w)
        todo-=set(orbit);out.append(orbit)
    return out

def lattice_sum(L):return sum(chi5(f25_norm((a%5,b%5))) for a in range(L) for b in range(L))
def crt_three():return next(x for x in range(30) if x%2==1 and x%3==2 and x%5==4)
def primes_to(n):
    return [p for p in range(2,n+1) if all(p%d for d in range(2,isqrt(p)+1))]

def f9_mul(z,w):
    a,b=z;c,d=w;return ((a*c-b*d)%3,(a*d+b*c)%3)
