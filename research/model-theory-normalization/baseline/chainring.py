"""Exact chain-ring Smith engine, adapted from the preserved Block03 implementation.
No Cartier or partition code is imported. This engine is NOT the certificate checker.
"""
from dataclasses import dataclass
from typing import Sequence

def is_prime(p):
    return type(p) is int and p >= 2 and all(p % k for k in range(2, __import__('math').isqrt(p)+1))

def identity(n):
    return [[int(i==j) for j in range(n)] for i in range(n)]


def vector_matrix(x,M,m):
    if not M: return []
    return [sum(x[i]*M[i][j] for i in range(len(x)))%m for j in range(len(M[0]))]


def valuation(x,p,r):
    if x==0: return r
    v=0
    while x%p==0:
        x//=p;v+=1
    return min(v,r)


@dataclass
class ModuleForm:
    p: int
    r: int
    ambient_dimension: int
    valuations: tuple[int,...]
    U: list[list[int]]
    V: list[list[int]]
    V_inverse: list[list[int]]

    @property
    def count(self): return len(self.valuations)

    @property
    def length(self): return sum(self.r-s for s in self.valuations)

    def coordinates(self,x: Sequence[int]):
        if len(x)!=self.ambient_dimension: raise ValueError('ambient size mismatch')
        y=vector_matrix(x,self.V,self.p**self.r)
        t=self.count
        if any(y[t:]): return None
        c=[]
        for yy,s in zip(y,self.valuations):
            if yy % self.p**s: return None
            c.append(yy//self.p**s)
        return tuple(c)


def module_form(G: Sequence[Sequence[int]],p: int,r: int) -> ModuleForm:
    """Exact Smith reduction over a finite chain ring; no division by nonunits."""
    if not isinstance(p,int) or not is_prime(p) or not isinstance(r,int) or r<1:
        raise ValueError('p must be prime and r positive')
    if not G or not G[0]: raise ValueError('nonempty generator matrix required')
    n,N=len(G),len(G[0]);m=p**r
    if any(len(row)!=N for row in G): raise ValueError('ragged matrix')
    X=[[x%m for x in row] for row in G]
    U=identity(n);V=identity(N);W=identity(N)
    ss=[]
    for k in range(min(n,N)):
        candidates=[(valuation(X[i][j],p,r),i,j) for i in range(k,n) for j in range(k,N) if X[i][j]]
        if not candidates: break
        s,ii,jj=min(candidates)
        X[k],X[ii]=X[ii],X[k];U[k],U[ii]=U[ii],U[k]
        if jj!=k:
            for mat in (X,V):
                for row in mat: row[k],row[jj]=row[jj],row[k]
            W[k],W[jj]=W[jj],W[k]
        pivot=p**s
        inv=pow(X[k][k]//pivot,-1,m)
        X[k]=[(x*inv)%m for x in X[k]]
        U[k]=[(x*inv)%m for x in U[k]]
        assert X[k][k]==pivot
        for i in range(k+1,n):
            assert X[i][k]%pivot==0
            c=X[i][k]//pivot
            if c:
                X[i]=[(x-c*y)%m for x,y in zip(X[i],X[k])]
                U[i]=[(x-c*y)%m for x,y in zip(U[i],U[k])]
        for j in range(k+1,N):
            assert X[k][j]%pivot==0
            c=X[k][j]//pivot
            if c:
                for mat in (X,V):
                    for row in mat: row[j]=(row[j]-c*row[k])%m
                W[k]=[(x+c*y)%m for x,y in zip(W[k],W[j])]
        ss.append(s)
    for i,row in enumerate(X):
        for j,x in enumerate(row):
            assert x==(p**ss[i] if i==j and i<len(ss) else 0)
    return ModuleForm(p,r,N,tuple(ss),U,V,W)

