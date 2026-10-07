"""Exact coordinate-ideal closure and heterogeneous cyclic coordinates.

This is a reference implementation, not a proved refinement of compiled Lean.
Matrices are destination-row/source-column and must already include branch sums.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import gcd, isqrt, prod
from typing import Iterable, Sequence


def is_prime(p: int) -> bool:
    return isinstance(p, int) and not isinstance(p, bool) and p >= 2 and all(p % d for d in range(2, isqrt(p) + 1))


@dataclass(frozen=True)
class IdealMachine:
    p: int
    r: int
    initial: tuple[int, ...]
    matrices: tuple[tuple[tuple[int, ...], ...], ...]

    def __post_init__(self) -> None:
        if not is_prime(self.p) or not isinstance(self.r, int) or isinstance(self.r, bool) or self.r < 0:
            raise ValueError("Require prime p and nonnegative integer r.")
        n, m = len(self.initial), self.modulus
        if any(len(t) != n or any(len(row) != n for row in t) for t in self.matrices):
            raise ValueError("Every matrix must be square with the initial vector's dimension.")
        if any(not isinstance(x, int) or isinstance(x, bool) for x in self.initial):
            raise TypeError("Initial coefficients must be integers.")
        if any(not isinstance(x, int) or isinstance(x, bool) for t in self.matrices for row in t for x in row):
            raise TypeError("Matrix entries must be integers.")
        object.__setattr__(self, 'initial', tuple(x % m for x in self.initial))
        object.__setattr__(self, 'matrices', tuple(tuple(tuple(x % m for x in row) for row in t) for t in self.matrices))

    @property
    def modulus(self) -> int:
        return self.p ** self.r

    @property
    def n(self) -> int:
        return len(self.initial)

    def order(self, x: int) -> int:
        x %= self.modulus
        if x == 0:
            return self.r
        a = 0
        while x % self.p == 0:
            x //= self.p
            a += 1
        return a

    def step_profile(self, c: Sequence[int]) -> tuple[int, ...]:
        self.check_profile(c)
        return tuple(max([c[j], self.r - self.order(self.initial[j])] +
                         [max(0, c[i] - self.order(t[j][i])) for t in self.matrices for i in range(self.n)])
                     for j in range(self.n))

    def least_profile(self) -> tuple[int, ...]:
        c = (0,) * self.n
        for _ in range(self.n * self.r):
            d = self.step_profile(c)
            if d == c:
                return c
            c = d
        if self.step_profile(c) != c:
            raise AssertionError("The finite stabilization bound was violated.")
        return c

    def check_profile(self, c: Sequence[int]) -> None:
        if len(c) != self.n or any(type(x) is not int or not 0 <= x <= self.r for x in c):
            raise ValueError("A capacity profile has one integer in [0,r] per coordinate.")

    def generators(self, c: Sequence[int]) -> tuple[int, ...]:
        self.check_profile(c)
        return tuple(self.p ** (self.r - a) for a in c)

    def closed_direct(self, c: Sequence[int]) -> bool:
        """Independent membership test by integer divisibility, without valuations."""
        g = self.generators(c)
        return (all(x % q == 0 for x, q in zip(self.initial, g)) and
                all((t[j][i] * g[i]) % g[j] == 0
                    for t in self.matrices for i in range(self.n) for j in range(self.n)))

    def least_gcd_generators(self) -> tuple[int, ...]:
        """Independent ideal-sum closure: gcd of integer principal generators."""
        g = (self.modulus,) * self.n
        while True:
            d = tuple(gcd(g[j], self.initial[j],
                          *[t[j][i] * g[i] for t in self.matrices for i in range(self.n)])
                      for j in range(self.n))
            if d == g:
                return g
            g = d

    def embed(self, c: Sequence[int], y: Sequence[int]) -> tuple[int, ...]:
        g = self.generators(c)
        if len(y) != self.n:
            raise ValueError("Wrong coordinate count.")
        return tuple(q * (x % (self.p ** a)) % self.modulus for q, x, a in zip(g, y, c))

    def decode(self, c: Sequence[int], x: Sequence[int]) -> tuple[int, ...]:
        g = self.generators(c)
        if len(x) != self.n:
            raise ValueError("Wrong coordinate count.")
        x = tuple(v % self.modulus for v in x)
        if any(v % q for v, q in zip(x, g)):
            raise ValueError("Input does not belong to the certified ideal product.")
        return tuple(v // q for v, q in zip(x, g))

    def transition_full(self, d: int, x: Sequence[int]) -> tuple[int, ...]:
        if not 0 <= d < len(self.matrices) or len(x) != self.n:
            raise ValueError("Invalid digit or vector dimension.")
        return tuple(sum(a * b for a, b in zip(row, x)) % self.modulus for row in self.matrices[d])

    def transition_cyclic(self, c: Sequence[int], d: int, y: Sequence[int]) -> tuple[int, ...]:
        return self.decode(c, self.transition_full(d, self.embed(c, y)))

    def support(self) -> tuple[int, ...]:
        s = {i for i, x in enumerate(self.initial) if x != 0}
        while True:
            t = s | {j for m in self.matrices for i in s for j in range(self.n) if m[j][i] != 0}
            if t == s:
                return tuple(sorted(s))
            s = t

    def state_count(self, c: Sequence[int]) -> int:
        self.check_profile(c)
        return self.p ** sum(c)
