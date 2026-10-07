"""Exact cyclic presentation of a finite residue submodule from its integer lattice.

Reference implementation, not a formally refined Lean program. Source convention:
columns are generators; destination rows/source columns for transition matrices.
SymPy proposes a Smith decomposition; exact unimodularity and identity checks
validate its certificate before any coordinates are used.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import prod
from typing import Sequence
from sympy import Matrix, eye, zeros, ZZ
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.normalforms import smith_normal_decomp
from reachable_engine import ReachableModule


def integer_matrix(a: Matrix) -> Matrix:
    if any(x.q != 1 for x in a):
        raise ArithmeticError('Expected an integral matrix, not a rational relaxation.')
    return a.applyfunc(int)


def certified_smith(a: Matrix) -> tuple[Matrix, Matrix, Matrix]:
    if a.rows != a.cols:
        raise ValueError('This quotient presentation requires a square relation matrix.')
    if a.rows == 0:
        return zeros(0,0), eye(0), eye(0)
    D,U,V = (x.to_Matrix() for x in smith_normal_decomp(DomainMatrix.from_Matrix(a).convert_to(ZZ)))
    validate_smith(a,D,U,V)
    return D,U,V


def validate_smith(a: Matrix, D: Matrix, U: Matrix, V: Matrix) -> None:
    """Reject malformed, nonunimodular, or incorrectly diagonalized certificates."""
    n=a.rows
    if a.cols!=n or any(x.shape!=(n,n) for x in (D,U,V)):
        raise ValueError('All Smith certificate matrices must have the same square shape.')
    for x in (a,D,U,V):integer_matrix(x)
    if U*a*V != D or abs(U.det()) != 1 or abs(V.det()) != 1:
        raise ArithmeticError('Invalid Smith decomposition certificate.')
    diag = [int(D[i,i]) for i in range(a.rows)]
    if any(x <= 0 for x in diag) or any(D[i,j] for i in range(a.rows) for j in range(a.cols) if i != j):
        raise ArithmeticError('Expected positive full-rank diagonal Smith form.')
    if any(b%a for a,b in zip(diag,diag[1:])):
        raise ArithmeticError('Smith diagonal divisibility chain failed.')


@dataclass
class CyclicPresentation:
    reachable: ReachableModule
    relations: Matrix
    diagonal: Matrix
    left: Matrix
    right: Matrix
    left_inverse: Matrix
    lattice_inverse: Matrix
    active: tuple[int,...]
    moduli: tuple[int,...]
    exponents: tuple[int,...]
    matrices: tuple[tuple[tuple[int,...],...],...]

    @classmethod
    def construct(cls, reachable: ReachableModule) -> 'CyclicPresentation':
        H=reachable.basis; model=reachable.machine; n=model.n; m=model.modulus
        Hi=H.inv() if n else zeros(0,0)
        K=integer_matrix(Hi*(m*eye(n)))
        D,U,V=certified_smith(K)
        Ui=integer_matrix(U.inv()) if n else eye(0)
        active=tuple(i for i in range(n) if int(D[i,i])>1)
        moduli=tuple(int(D[i,i]) for i in active)
        exponents=[]
        for modulus in moduli:
            x,e=modulus,0
            while x>1 and x%model.p==0:x//=model.p;e+=1
            if x != 1 or not 0 < e <= model.r:
                raise ArithmeticError('Cyclic factor is not an allowed positive p-power.')
            exponents.append(e)
        if prod(moduli) != reachable.cardinality:
            raise ArithmeticError('Cyclic cardinality differs from the lattice quotient.')
        matrices=[]
        for T in model.matrices:
            transformed=integer_matrix(U*Hi*Matrix(n,n,lambda i,j:T[i][j])*H*Ui)
            C=tuple(tuple(int(transformed[j,i])%int(D[j,j]) for i in active) for j in active)
            for j,dj in enumerate(moduli):
                for i,di in enumerate(moduli):
                    if (C[j][i]*di)%dj:
                        raise ArithmeticError('Transition does not respect cyclic relations.')
            matrices.append(C)
        return cls(reachable,K,D,U,V,Ui,Hi,active,moduli,tuple(exponents),tuple(matrices))

    @property
    def cardinality(self) -> int:
        return prod(self.moduli)

    def encode(self, vector: Sequence[int]) -> tuple[int,...]:
        n=self.reachable.machine.n
        if len(vector)!=n or not self.reachable.contains(vector):
            raise ValueError('Vector must belong to the reachable residue module.')
        coordinates=integer_matrix(self.lattice_inverse*Matrix(n,1,list(vector)))
        y=self.left*coordinates
        return tuple(int(y[i])%d for i,d in zip(self.active,self.moduli))

    def decode(self, vector: Sequence[int]) -> tuple[int,...]:
        if len(vector)!=len(self.active):
            raise ValueError('Incorrect number of cyclic coordinates.')
        n=self.reachable.machine.n;y=zeros(n,1)
        for i,d,z in zip(self.active,self.moduli,vector):
            y[i]=int(z)%d
        x=self.reachable.basis*self.left_inverse*y
        return tuple(int(a)%self.reachable.machine.modulus for a in x)

    def transition(self, digit: int, vector: Sequence[int]) -> tuple[int,...]:
        if len(vector)!=len(self.active):raise ValueError('Incorrect coordinate dimension.')
        if not 0<=digit<len(self.matrices):raise ValueError('Digit outside the transition alphabet.')
        C=self.matrices[digit]
        return tuple(sum(row[i]*(int(vector[i])%self.moduli[i]) for i in range(len(self.active)))%d
                     for row,d in zip(C,self.moduli))

    def iterate(self, digits: Sequence[int], vector: Sequence[int]) -> tuple[int,...]:
        if len(vector)!=len(self.active):raise ValueError('Incorrect coordinate dimension.')
        x=tuple(int(a)%d for a,d in zip(vector,self.moduli))
        for digit in digits:x=self.transition(int(digit),x)
        return x

    def certificate(self) -> dict:
        integer_rows=lambda mat:[[int(v) for v in row] for row in mat.tolist()]
        return {'prime':self.reachable.machine.p,'precision':self.reachable.machine.r,
          'signature':list(self.exponents),'moduli':list(self.moduli),
          'cardinality':self.cardinality,'lattice_basis':integer_rows(self.reachable.basis),
          'relation_matrix':integer_rows(self.relations),'smith_diagonal':integer_rows(self.diagonal),
          'left_transform':integer_rows(self.left),'right_transform':integer_rows(self.right),
          'transition_matrices':self.matrices}
