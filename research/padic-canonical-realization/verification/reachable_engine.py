"""Exact reachable-module closure over Z/(p**r), using integer column lattices.

Reference implementation only: no claimed compiled-Lean refinement. Matrices are
indexed by destination row/source column. Hermite normal form represents the
preimage lattice of the residue submodule, including modulus*Z**n.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import prod
from typing import Sequence
from sympy import Matrix, eye, zeros
from sympy.matrices.normalforms import hermite_normal_form
from ideal_engine import IdealMachine

@dataclass
class ReachableModule:
    machine: IdealMachine
    basis: Matrix
    growth_rounds: int
    round_exponents: list[int]
    capacity_bound: int

    @property
    def cardinality(self) -> int:
        det = prod(int(self.basis[i,i]) for i in range(self.machine.n))
        full = self.machine.modulus**self.machine.n
        if det <= 0 or full % det:
            raise ArithmeticError('Lattice index does not divide the ambient cardinality.')
        return full // det

    @property
    def exponent(self) -> int:
        q,e = self.cardinality,0
        while q > 1 and q % self.machine.p == 0:
            q //= self.machine.p; e += 1
        if q != 1: raise ArithmeticError('The result is not a p-power.')
        return e

    def contains(self, vector: Sequence[int]) -> bool:
        if len(vector) != self.machine.n:
            raise ValueError('Wrong vector dimension.')
        residual = [int(x) for x in vector]
        for j in reversed(range(self.machine.n)):
            pivot = int(self.basis[j,j])
            if pivot <= 0 or residual[j] % pivot:
                return False
            q = residual[j] // pivot
            for i in range(j+1): residual[i] -= q*int(self.basis[i,j])
        return not any(residual)

    def generator(self, j: int) -> tuple[int,...]:
        return tuple(int(self.basis[i,j]) % self.machine.modulus for i in range(self.machine.n))

    def transition(self, d: int, vector: Sequence[int]) -> tuple[int,...]:
        if not self.contains(vector): raise ValueError('State is not in the reachable module.')
        result=self.machine.transition_full(d,vector)
        if not self.contains(result): raise AssertionError('Transition escaped the module.')
        return result


def lattice_step(model: IdealMachine, basis: Matrix) -> Matrix:
    if model.n == 0: return zeros(0,0)
    seed=Matrix(model.n,1,list(model.initial))
    columns=[basis,seed]
    for t in model.matrices:
        image=(Matrix(t)*basis).applyfunc(lambda x: int(x)%model.modulus)
        columns.append(image)
    return hermite_normal_form(Matrix.hstack(*columns))


def reachable_module(model: IdealMachine) -> ReachableModule:
    cap=sum(model.least_profile())
    basis=model.modulus*eye(model.n)
    out=ReachableModule(model,basis,0,[0],cap)
    for round_number in range(cap+1):
        candidate=lattice_step(model,basis)
        if candidate == basis:
            if not out.contains(model.initial): raise AssertionError('Initial vector missing.')
            for d in range(len(model.matrices)):
                for j in range(model.n):
                    if not out.contains(model.transition_full(d,out.generator(j))):
                        raise AssertionError('Generator invariance failed.')
            return out
        if round_number == cap:
            raise AssertionError('Proved p-adic digit round bound exceeded.')
        old_exp=out.exponent
        basis=candidate
        out=ReachableModule(model,basis,round_number+1,out.round_exponents[:],cap)
        if out.exponent <= old_exp or out.exponent > cap:
            raise AssertionError('Strict growth or ideal bound violated.')
        out.round_exponents.append(out.exponent)
    raise AssertionError('Unreachable loop exit.')
