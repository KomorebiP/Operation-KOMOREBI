"""Exact finite arithmetic for the dense lift group G_A.

The mathematical group has underlying set Q x direct_sum_p F_p.  Its addition
uses the finite cocycle in the accompanying proof.  A bit oracle specifies A.
The executable examples use computable masks only, never a pretend halting oracle.
Python 3.10+; standard library only. No floating-point arithmetic is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Callable, Iterable, Mapping

BitOracle = Callable[[int], bool]
Sparse = tuple[tuple[int, int], ...]


@lru_cache(maxsize=None)
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


@lru_cache(maxsize=None)
def prime(index: int) -> int:
    if index < 0:
        raise ValueError("A prime index must be nonnegative.")
    n, seen = 2, 0
    while True:
        if is_prime(n):
            if seen == index:
                return n
            seen += 1
        n += 1


@lru_cache(maxsize=None)
def prime_index(p: int) -> int:
    if not is_prime(p):
        raise ValueError(f"{p} is not a prime.")
    n = 0
    while prime(n) != p:
        n += 1
    return n


@lru_cache(maxsize=None)
def prime_divisors(n: int) -> tuple[int, ...]:
    n = abs(n)
    if n == 0:
        raise ValueError("Zero has no finite set of prime divisors.")
    result: list[int] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            result.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        result.append(n)
    return tuple(result)


def normalize(values: Mapping[int, int] | Iterable[tuple[int, int]] = ()) -> Sparse:
    items = values.items() if isinstance(values, Mapping) else values
    result: dict[int, int] = {}
    for p, value in items:
        if not is_prime(p):
            raise ValueError(f"Support label {p} is not a prime.")
        result[p] = (result.get(p, 0) + int(value)) % p
    return tuple(sorted((p, value) for p, value in result.items() if value))


def sparse_add(*vectors: Sparse) -> Sparse:
    return normalize(item for vector in vectors for item in vector)


def sparse_scale(n: int, vector: Sparse) -> Sparse:
    return normalize((p, n * a) for p, a in vector)


@dataclass(frozen=True)
class Element:
    rational: Fraction
    torsion: Sparse = ()

    @staticmethod
    def make(rational: Fraction | int = 0,
             torsion: Mapping[int, int] | Iterable[tuple[int, int]] = ()) -> Element:
        return Element(Fraction(rational), normalize(torsion))


@dataclass(frozen=True)
class RootResult:
    root: Element | None
    obstructing_prime: int | None


class DenseLiftGroup:
    """G_A with oracle A and one selected prime per consecutive pair."""

    def __init__(self, bit: BitOracle):
        self.bit = bit

    def selected(self, p: int) -> bool:
        i = prime_index(p)
        return i % 2 == int(bool(self.bit(i // 2)))

    def section_value(self, r: Fraction, p: int) -> int:
        """The p-coordinate of s_A(r), with zero at denominator primes."""
        r = Fraction(r)
        if not self.selected(p) or r.denominator % p == 0:
            return 0
        return (r.numerator * pow(r.denominator, -1, p)) % p

    def coordinate(self, x: Element, p: int) -> int:
        return (self.section_value(x.rational, p) + dict(x.torsion).get(p, 0)) % p

    def cocycle(self, r: Fraction, s: Fraction) -> Sparse:
        r, s = Fraction(r), Fraction(s)
        support = set(prime_divisors(r.denominator)) | set(prime_divisors(s.denominator))
        return normalize((p, self.section_value(r, p) + self.section_value(s, p)
                          - self.section_value(r + s, p)) for p in support)

    def add(self, x: Element, y: Element) -> Element:
        return Element(x.rational + y.rational,
                       sparse_add(x.torsion, y.torsion,
                                  self.cocycle(x.rational, y.rational)))

    def neg(self, x: Element) -> Element:
        return Element(-x.rational, sparse_scale(-1, x.torsion))

    def sub(self, x: Element, y: Element) -> Element:
        return self.add(x, self.neg(y))

    def scale(self, n: int, x: Element) -> Element:
        """Integer multiplication, independently implemented by doubling."""
        if n < 0:
            return self.scale(-n, self.neg(x))
        answer = Element.make()
        while n:
            if n & 1:
                answer = self.add(answer, x)
            n //= 2
            if n:
                x = self.add(x, x)
        return answer

    def root(self, x: Element, m: int) -> RootResult:
        """Produce an m-root or a prime-coordinate obstruction, for m >= 1.

        This is effective relative to the bit oracle. It is NOT a procedure for
        finding arbitrary noncomputable masks from finite observations.
        """
        if m < 1:
            raise ValueError("The root multiplier must be positive.")
        for p in prime_divisors(m):
            if self.coordinate(x, p):
                return RootResult(None, p)
        q = x.rational / m
        support = (set(dict(x.torsion))
                   | set(prime_divisors(x.rational.denominator))
                   | set(prime_divisors(q.denominator)))
        d = dict(x.torsion)
        e: dict[int, int] = {}
        for p in support:
            h = (self.section_value(x.rational, p) + d.get(p, 0)
                 - m * self.section_value(q, p)) % p
            if m % p == 0:
                if h:
                    raise AssertionError("The necessary coordinate test was inconsistent.")
            elif h:
                e[p] = h * pow(m, -1, p) % p
        return RootResult(Element.make(q, e), None)

    def finite_change_transport(self, x: Element, other: DenseLiftGroup,
                                changed_indices: Iterable[int]) -> Element:
        """Same ambient element in another mask's coordinates.

        PRECONDITION: the two masks differ ONLY at changed_indices. A finite
        test cannot establish this global precondition for arbitrary oracles.
        """
        ps = {prime(2*n + b) for n in changed_indices for b in (0, 1)}
        delta = normalize((p, self.section_value(x.rational, p)
                           - other.section_value(x.rational, p)) for p in ps)
        return Element(x.rational, sparse_add(x.torsion, delta))


def element_json(x: Element) -> dict:
    return {"rational": str(x.rational), "torsion": [list(a) for a in x.torsion]}


if __name__ == "__main__":
    import json
    group = DenseLiftGroup(lambda n: False)  # Select p_0, p_2, p_4, ...
    u, half = Element.make(1), Element.make(Fraction(1, 2))
    result = {
        "mask": "A is empty: select the even-indexed prime from each pair",
        "u": element_json(u),
        "twice_half": element_json(group.scale(2, half)),
        "two_root_of_u": {"exists": group.root(u, 2).root is not None,
                          "obstructing_prime": group.root(u, 2).obstructing_prime},
        "three_root_of_u": element_json(group.root(u, 3).root),
        "warning": "Finite example only; infinite claims are proved in the manuscript."
    }
    print(json.dumps(result, indent=2))
