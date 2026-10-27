"""Exact observable quotients of finite mixed-cyclic modules.

Columns are source coordinates, rows destination coordinates. Every map must
respect source torsion. All arithmetic is integral. HNF/Smith proposals are
checked by exact matrix identities; this is not a formal Lean executable refinement.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import gcd, prod
from typing import Sequence
from sympy import Matrix, eye, diag, zeros, isprime
from sympy.matrices.normalforms import hermite_normal_form
from presentation_engine import certified_smith, integer_matrix


def exponent(p: int, value: int) -> int:
    if value < 1:
        raise ValueError('Cardinality/modulus must be positive.')
    e = 0
    while value > 1 and value % p == 0:
        value //= p
        e += 1
    if value != 1:
        raise ValueError('Not a power of the given prime.')
    return e


def mat_rows(mat: Matrix) -> list[list[int]]:
    return [[int(x) for x in row] for row in mat.tolist()]


@dataclass
class ObservablePresentation:
    p: int
    r: int
    moduli: tuple[int, ...]
    matrices: tuple[Matrix, ...]
    output_row: Matrix
    observation_lattice: Matrix
    kernel_lattice: Matrix
    smith: Matrix
    left: Matrix
    right: Matrix
    left_inverse: Matrix
    active: tuple[int, ...]
    quotient_moduli: tuple[int, ...]
    quotient_matrices: tuple[Matrix, ...]
    quotient_output: Matrix
    growth_rounds: int
    quotient_exponents_by_round: list[int]
    kernel_smith_certificate: dict

    @classmethod
    def construct(cls, p: int, r: int, moduli: Sequence[int],
                  matrices: Sequence[Sequence[Sequence[int]] | Matrix],
                  output: Sequence[int]) -> 'ObservablePresentation':
        if not isinstance(p, int) or not isprime(p) or not isinstance(r, int) or r < 0:
            raise ValueError('Expected a prime and a nonnegative precision.')
        ds = tuple(int(d) for d in moduli); n = len(ds); m = p**r
        es = [exponent(p, d) for d in ds]
        if any(e > r for e in es) or len(output) != n:
            raise ValueError('Invalid coordinate modulus or output dimension.')
        Ts = tuple(integer_matrix(Matrix(n, n, list(t) if isinstance(t, Matrix)
                      else [z for row in t for z in row])) for t in matrices)
        # Validate shape before any zip/reduction can truncate data.
        for raw in matrices:
            if isinstance(raw, Matrix):
                if raw.shape != (n, n): raise ValueError('Wrong transition shape.')
            elif len(raw) != n or any(len(row) != n for row in raw):
                raise ValueError('Wrong transition shape.')
        lam = Matrix(1, n, [int(x) % m for x in output])
        if any(ds[i] * lam[0,i] % m for i in range(n)):
            raise ValueError('Output violates a source annihilator relation.')
        for T in Ts:
            if any(ds[i]*T[j,i] % ds[j] for j in range(n) for i in range(n)):
                raise ValueError('Transition violates a mixed-modulus source relation.')
        H = m*eye(n); bound = sum(es); trajectory = [0]
        for round_no in range(bound + 1):
            proposed = hermite_normal_form(Matrix.hstack(H, lam.T, *(T.T*H for T in Ts))) if n else eye(0)
            if proposed == H:
                break
            if round_no == bound:
                raise AssertionError('Observation module exceeded p-cardinality round bound.')
            H = proposed
            e = exponent(p, m**n // abs(int(H.det())))
            if e <= trajectory[-1] or e > bound:
                raise AssertionError('Strict cardinality progress failed.')
            trajectory.append(e)
        else:
            raise AssertionError('No fixed point.')
        # H columns encode a basis of observation ROWS. H^T x = 0 (mod m).
        D, U, V = certified_smith(H.T)
        kperiods = [m//gcd(m, int(D[i,i])) for i in range(n)]
        K = hermite_normal_form(V*diag(*kperiods)) if n else eye(0)
        Ki = K.inv() if n else eye(0)
        relations = diag(*ds) if n else eye(0)
        integer_matrix(Ki*relations)  # Original coordinate relations are inside the kernel.
        integer_matrix((H.T*K)/m)  # Every proposed kernel generator has all observations zero.
        integer_matrix((lam*K)/m)
        for T in Ts: integer_matrix(Ki*T*K)  # Kernel invariance, over integer lattices.
        qD, qU, qV = certified_smith(K)
        qUi = integer_matrix(qU.inv()) if n else eye(0)
        active = tuple(i for i in range(n) if qD[i,i] > 1)
        qs = tuple(int(qD[i,i]) for i in active)
        if prod(ds) % prod(qs): raise AssertionError('Quotient cardinality must divide source cardinality.')
        transformed = []
        for T in Ts:
            mat = integer_matrix(qU*T*qUi)
            qT = Matrix(len(active), len(active), lambda j,i: int(mat[active[j],active[i]]) % qs[j])
            if any(qs[i]*qT[j,i] % qs[j] for j in range(len(qs)) for i in range(len(qs))):
                raise AssertionError('Quotient transition violated cyclic relations.')
            transformed.append(qT)
        qlamfull = lam*qUi
        qlam = Matrix(1, len(active), [int(qlamfull[i]) % m for i in active])
        if any(qs[i]*qlam[i] % m for i in range(len(qs))):
            raise AssertionError('Quotient output violated cyclic relations.')
        return cls(p,r,ds,Ts,lam,H,K,qD,qU,qV,qUi,active,qs,tuple(transformed),qlam,
                   len(trajectory)-1,trajectory,
                   {'D':mat_rows(D),'U':mat_rows(U),'V':mat_rows(V),'periods':kperiods})

    @property
    def modulus(self) -> int: return self.p**self.r
    @property
    def cardinality(self) -> int: return prod(self.quotient_moduli)
    @property
    def kernel_cardinality(self) -> int: return prod(self.moduli)//self.cardinality
    @property
    def signature(self) -> tuple[int,...]:
        return tuple(exponent(self.p,d) for d in self.quotient_moduli)

    def _input(self, x: Sequence[int], moduli: tuple[int,...]) -> Matrix:
        if len(x) != len(moduli): raise ValueError('Incorrect coordinate count.')
        return Matrix(len(moduli),1,[int(a)%d for a,d in zip(x,moduli)])

    def in_kernel(self, x: Sequence[int]) -> bool:
        y = self.observation_lattice.T*self._input(x,self.moduli)
        return all(int(a)%self.modulus == 0 for a in y)

    def encode(self, x: Sequence[int]) -> tuple[int,...]:
        y=self.left*self._input(x,self.moduli)
        return tuple(int(y[i])%d for i,d in zip(self.active,self.quotient_moduli))

    def representative(self, y: Sequence[int]) -> tuple[int,...]:
        v=self._input(y,self.quotient_moduli); z=zeros(len(self.moduli),1)
        for i,a in zip(self.active,v): z[i]=a
        x=self.left_inverse*z
        return tuple(int(a)%d for a,d in zip(x,self.moduli))

    def transition(self, digit: int, y: Sequence[int]) -> tuple[int,...]:
        if not 0 <= digit < len(self.quotient_matrices): raise ValueError('Invalid digit.')
        z=self.quotient_matrices[digit]*self._input(y,self.quotient_moduli)
        return tuple(int(a)%d for a,d in zip(z,self.quotient_moduli))

    def output(self, y: Sequence[int]) -> int:
        return int((self.quotient_output*self._input(y,self.quotient_moduli))[0])%self.modulus

    def iterate(self, digits: Sequence[int], y: Sequence[int]) -> tuple[int,...]:
        v=tuple(int(a) for a in self._input(y,self.quotient_moduli))
        for d in digits: v=self.transition(d,v)
        return v

    def certificate(self) -> dict:
        return {'p':self.p,'r':self.r,'source_moduli':self.moduli,
                'quotient_moduli':self.quotient_moduli,'signature':self.signature,
                'source_cardinality':prod(self.moduli),'kernel_cardinality':self.kernel_cardinality,
                'quotient_cardinality':self.cardinality,'growth_rounds':self.growth_rounds,
                'quotient_exponents_by_round':self.quotient_exponents_by_round,
                'observation_lattice':mat_rows(self.observation_lattice),'kernel_lattice':mat_rows(self.kernel_lattice),
                'kernel_smith_certificate':self.kernel_smith_certificate,
                'quotient_smith':{'D':mat_rows(self.smith),'U':mat_rows(self.left),'V':mat_rows(self.right)},
                'quotient_matrices':[mat_rows(t) for t in self.quotient_matrices],
                'quotient_output':[int(a) for a in self.quotient_output]}
