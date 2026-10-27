#!/usr/bin/env python3
"""Executable magnitude/radius budgets for the checked dyadic evaluator.

All values are exact Fractions. A budget (m,k) proves |x| <= m and the
rounded radius <= k*2**(-p), uniformly for p >= 0. This predictor does not
form an exact posterior, gain, innovation inverse, or exact residual.
Python output is provisional until its exported Lean instance is checked.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
from typing import Iterable
from exact_certificate import Model, Matrix, eye, scale, shape, packet_valid

@dataclass(frozen=True)
class Budget:
    mag: Q
    coeff: Q
    def __post_init__(self) -> None:
        if self.mag < 0 or self.coeff < 0:
            raise ValueError('Budget components must be nonnegative.')
    @property
    def energy_coeff(self) -> Q:
        return 4*self.coeff*(self.mag+self.coeff)

BudgetMatrix = tuple[tuple[Budget, ...], ...]

def source(x: Q) -> Budget:
    return Budget(abs(x), Q(2))

def plus(a: Budget, b: Budget) -> Budget:
    return Budget(a.mag+b.mag, a.coeff+b.coeff+2)

def times(a: Budget, b: Budget) -> Budget:
    return Budget(a.mag*b.mag,
        a.mag*b.coeff+b.mag*a.coeff+3*a.coeff*b.coeff+2)

def total(bs: Iterable[Budget]) -> Budget:
    xs=tuple(bs)
    return Budget(sum((x.mag for x in xs),Q(0)),sum((x.coeff for x in xs),Q(0))+2)

def inp(a: Matrix) -> BudgetMatrix:
    return tuple(tuple(source(x) for x in row) for row in a)

def trans(a: BudgetMatrix) -> BudgetMatrix:
    return tuple(zip(*a))

def add(a: BudgetMatrix,b: BudgetMatrix) -> BudgetMatrix:
    if shape(a)!=shape(b): raise ValueError('Budget sum dimension mismatch.')
    return tuple(tuple(plus(x,y) for x,y in zip(ar,br)) for ar,br in zip(a,b))

def mul(a: BudgetMatrix,b: BudgetMatrix) -> BudgetMatrix:
    if len(a[0])!=len(b): raise ValueError('Budget product dimension mismatch.')
    return tuple(tuple(total(times(a[i][k],b[k][j]) for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))

def mv(a: BudgetMatrix,v: tuple[Budget,...]) -> tuple[Budget,...]:
    if len(a[0])!=len(v): raise ValueError('Budget vector dimension mismatch.')
    return tuple(total(times(x,y) for x,y in zip(row,v)) for row in a)

def matrix_coeff(a: BudgetMatrix) -> Q:
    return sum((x.energy_coeff for row in a for x in row),Q(0))

def matrix_magnitude(a: BudgetMatrix) -> Q:
    return sum((x.mag*x.mag for row in a for x in row),Q(0))

def graph(m: Model, gain: Matrix) -> dict[str,BudgetMatrix]:
    n,k=len(m.H[0]),len(m.H)
    if shape(gain)!=(n,k): raise ValueError('Gain dimensions do not match.')
    if max(n,k,len(m.L[0]),len(m.N[0]),len(m.outputs),len(m.inputs))>8:
        raise ValueError('Producer dimension/packet cap is 8.')
    if m.sigma<=0 or not packet_valid(m.outputs,n) or not packet_valid(m.inputs,k):
        raise ValueError('Invalid noise floor or packet geometry.')
    h,l,z,b=inp(m.H),inp(m.L),inp(m.N),inp(gain)
    prior=mul(l,trans(l))
    noise=add(mul(z,trans(z)),inp(scale(m.sigma,eye(k))))
    innovation=add(mul(mul(h,prior),trans(h)),noise)
    # Subtraction uses addition of magnitudes, not subtraction of error budgets.
    residual=add(mul(prior,trans(h)),mul(b,innovation))
    vec=tuple(plus(x,y) for x,y in zip(tuple(source(x) for x in m.observation),
        mv(h,tuple(source(x) for x in m.mean))))
    nodes={'prior':prior,'noise':noise,'innovation':innovation,'residual':residual,
           'innovation_vector':tuple((x,) for x in vec)}
    for i,pa in enumerate(m.outputs):
        for j,pb in enumerate(m.inputs):
            nodes[f'packet_{i}_{j}']=mul(mul(inp(pa),residual),inp(pb))
    return nodes

def score_coefficient(m: Model,gain: Matrix) -> tuple[Q,dict[str,Q],dict[str,BudgetMatrix]]:
    nodes=graph(m,gain)
    packets=[v for k,v in nodes.items() if k.startswith('packet_')]
    a=sum((matrix_coeff(x) for x in packets),Q(0))
    mu=sum((matrix_magnitude(x) for x in packets),Q(0))
    b=matrix_coeff(nodes['innovation_vector']);nu=matrix_magnitude(nodes['innovation_vector'])
    c=(a*(m.sigma+nu)+mu*b+a*b)/(m.sigma*m.sigma)
    return c,dict(residual_coefficient=a,innovation_coefficient=b,
                  residual_magnitude=mu,innovation_magnitude=nu),nodes

def precision_for(coefficient: Q,slack: Q) -> int:
    if slack<=0: raise ValueError('Strictly positive score slack is required.')
    ratio=coefficient/slack
    ceil=max(0,-((-ratio.numerator)//ratio.denominator))
    # Nat.log 2 ceil + 1; Nat.log 2 0 = 0.
    return max(1,ceil.bit_length())

def sufficient_precision(m: Model,gain: Matrix,slack: Q) -> tuple[int,Q,dict[str,Q]]:
    c,parts,_=score_coefficient(m,gain)
    p=precision_for(c,slack)
    if c/Q(1<<p)>slack: raise ArithmeticError('Bit predictor invariant failed.')
    return p,c,parts
