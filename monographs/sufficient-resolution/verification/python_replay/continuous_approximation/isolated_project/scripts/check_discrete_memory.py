#!/usr/bin/env python3
"""Deterministic exact-rational checks of the discrete-memory formalization.

This tests finite matrix instances, including zero-dimensional hidden state.
Universal quantifiers are certified by Lean, not inferred from these tests.
No third-party Python dependencies are required.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
import json
import random

@dataclass(frozen=True)
class Mat:
    rows: int
    cols: int
    entries: tuple[tuple[Q, ...], ...]

    def __post_init__(self) -> None:
        if self.rows < 0 or self.cols < 0 or len(self.entries) != self.rows:
            raise ValueError('Invalid matrix shape')
        if any(len(row) != self.cols for row in self.entries):
            raise ValueError('Ragged matrix')

    @staticmethod
    def zero(r: int, c: int) -> Mat:
        return Mat(r, c, tuple(tuple(Q(0) for _ in range(c)) for _ in range(r)))

    @staticmethod
    def eye(n: int) -> Mat:
        return Mat(n, n, tuple(tuple(Q(i == j) for j in range(n)) for i in range(n)))

    @staticmethod
    def of(rows: list[list[int]]) -> Mat:
        return Mat(len(rows), len(rows[0]) if rows else 0,
                   tuple(tuple(Q(x) for x in row) for row in rows))

    def __add__(self, other: Mat) -> Mat:
        if (self.rows, self.cols) != (other.rows, other.cols):
            raise ValueError('Addition shape mismatch')
        return Mat(self.rows, self.cols, tuple(tuple(self.entries[i][j] + other.entries[i][j]
                   for j in range(self.cols)) for i in range(self.rows)))

    def __neg__(self) -> Mat:
        return Mat(self.rows, self.cols, tuple(tuple(-x for x in row) for row in self.entries))

    def __sub__(self, other: Mat) -> Mat:
        return self + (-other)

    def __matmul__(self, other: Mat) -> Mat:
        if self.cols != other.rows:
            raise ValueError('Multiplication shape mismatch')
        return Mat(self.rows, other.cols, tuple(tuple(sum(
            (self.entries[i][k] * other.entries[k][j] for k in range(self.cols)), Q(0))
            for j in range(other.cols)) for i in range(self.rows)))

    def power(self, n: int) -> Mat:
        if self.rows != self.cols or n < 0:
            raise ValueError('Power requires square matrix and nonnegative exponent')
        out = Mat.eye(self.rows)
        for _ in range(n):
            out = self @ out
        return out

    def sub(self, r0: int, r1: int, c0: int, c1: int) -> Mat:
        if not (0 <= r0 <= r1 <= self.rows and 0 <= c0 <= c1 <= self.cols):
            raise ValueError('Submatrix bounds invalid')
        return Mat(r1-r0, c1-c0, tuple(tuple(self.entries[i][j] for j in range(c0,c1))
                   for i in range(r0,r1)))


def total(terms: list[Mat], r: int, c: int) -> Mat:
    out = Mat.zero(r,c)
    for t in terms:
        out = out + t
    return out


def blocks(A: Mat, B: Mat, G: Mat, D: Mat) -> Mat:
    p,d = A.rows,D.rows
    if (A.cols,B.rows,B.cols,G.rows,G.cols,D.cols) != (p,p,d,d,p,d):
        raise ValueError('Invalid four-block dimensions')
    entries = tuple(A.entries[i]+B.entries[i] for i in range(p)) + \
              tuple(G.entries[i]+D.entries[i] for i in range(d))
    return Mat(p+d,p+d,entries)


def run() -> dict:
    rng = random.Random(20260913)
    checks = 0
    systems = 0
    max_depth = 9

    def eq(a: Mat, b: Mat, label: str) -> None:
        nonlocal checks
        checks += 1
        if a != b:
            raise AssertionError(label)

    def rand(r: int,c: int) -> Mat:
        return Mat(r,c,tuple(tuple(Q(rng.randint(-2,2)) for _ in range(c)) for _ in range(r)))

    def inspect(A: Mat,B: Mat,G: Mat,D: Mat,label: str) -> None:
        nonlocal systems,checks
        systems += 1
        p,d=A.rows,D.rows
        L=blocks(A,B,G,D)
        E=lambda n: L.power(n).sub(0,p,0,p)
        M=lambda k: B @ D.power(k) @ G
        y0,z0=rand(p,1),rand(d,1)
        x0=Mat(p+d,1,y0.entries+z0.entries)
        Y=lambda n: (L.power(n) @ x0).sub(0,p,0,1)
        Z=lambda n: (L.power(n) @ x0).sub(p,p+d,0,1)
        for n in range(max_depth):
            eq(Z(n),D.power(n) @ z0 + total([
                D.power(n-1-j) @ G @ Y(j) for j in range(n)],d,1),label+' hidden elimination')
            eq(Y(n+1),A @ Y(n) + B @ D.power(n) @ z0 + total([
                M(n-1-j) @ Y(j) for j in range(n)],p,1),label+' state memory')
            eq(E(n+1),A @ E(n)+total([M(n-1-j) @ E(j) for j in range(n)],p,p),
               label+' operator renewal')
        for m in range(5):
            for n in range(5):
                hidden_return=L.power(m).sub(0,p,p,p+d) @ L.power(n).sub(p,p+d,0,p)
                eq(E(m+n)-E(m) @ E(n),hidden_return,label+' power defect')
        for N in range(5):
            prefix=all(M(k)==Mat.zero(p,p) for k in range(N))
            horizon=all(E(n)==A.power(n) for n in range(N+2))
            checks += 1
            if prefix != horizon: raise AssertionError(label+' finite-prefix equivalence')
        finite=all(M(k)==Mat.zero(p,p) for k in range(d))
        checks += 1
        if finite != all(E(n)==A.power(n) for n in range(d+2)):
            raise AssertionError(label+' dimension certificate horizon')
        if finite:
            for n in range(max_depth+1):
                eq(E(n),A.power(n),label+' certificate consequences')
                eq(M(n),Mat.zero(p,p),label+' certificate feedback consequences')

    for p in (1,2):
        for d in (0,1,2,3):
            for trial in range(2):
                inspect(rand(p,p),rand(p,d),rand(d,p),rand(d,d),f'random-{p}-{d}-{trial}')

    A=Mat.zero(1,1);B=Mat.of([[1,0]]);G=Mat.of([[0],[1]]);D=Mat.of([[0,1],[0,0]])
    inspect(A,B,G,D,'delayed-cycle')
    eq(B @ G,Mat.zero(1,1),'zero immediate feedback')
    eq(B @ D @ G,Mat.eye(1),'nonzero delayed feedback')
    L=blocks(A,B,G,D)
    assert L.power(3).sub(0,1,0,1) != A.power(3)
    checks += 1
    wrong_shallow_rule_detected=True

    inspect(Mat.eye(1),B,G,Mat.eye(2),'invisible-excursion')
    assert B != Mat.zero(1,2) and G != Mat.zero(2,1)
    checks += 1
    assert B @ Mat.of([[1],[0]]) != Mat.zero(1,1)
    checks += 1
    prepared_vs_all_state_distinguished=True

    # Exact nonorthogonal analysis/synthesis. C=[1,1], R=[1,0]^T.
    S=Mat.of([[1,-1],[0,1]]);Sinv=Mat.of([[1,1],[0,1]])
    C=Mat.of([[1,1]]);R=Mat.of([[1],[0]])
    eq(S @ Sinv,Mat.eye(2),'nonorthogonal inverse')
    eq(C @ R,Mat.eye(1),'split identity')
    for K in (Mat.of([[2,1],[0,3]]),Mat.of([[2,1],[1,3]])):
        T=S @ K @ Sinv
        for n in range(max_depth+1):
            eq(C @ T.power(n) @ R,K.power(n).sub(0,1,0,1),'canonical hidden realization')
        inspect(K.sub(0,1,0,1),K.sub(0,1,1,2),K.sub(1,2,0,1),K.sub(1,2,1,2),'canonical')

    return {'passed':True,'arithmetic':'fractions.Fraction (exact rational)',
            'seed':20260913,'systems':systems,'individual_assertions':checks,
            'max_evolution_depth':max_depth,'power_defect_m_n_max':4,
            'hidden_dimensions':[0,1,2,3],'visible_dimensions':[1,2],
            'wrong_shallow_rule_detected':wrong_shallow_rule_detected,
            'prepared_vs_all_state_distinguished':prepared_vs_all_state_distinguished,
            'boundary':'Finite implementation controls only; universal theorems are the Lean declarations.'}

if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
