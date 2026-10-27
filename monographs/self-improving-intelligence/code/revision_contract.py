"""Finite certificate applicability and resource accounting for the first edition.

This module tracks declared dependencies; it does NOT discover all semantic
assumptions, authenticate an issuer, or turn a Python callback into a proof kernel.
No networking, dynamic code execution, or external-system integration is used.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
from collections.abc import Callable, Mapping, Sequence
import hashlib
import json
from typing import Any


def canonical(value: Any) -> bytes:
    """Exact JSON snapshot. Rationals must be encoded explicitly as strings/pairs."""
    def check(x: Any) -> None:
        if x is None or type(x) in (bool, int, str):
            return
        if type(x) in (list, tuple):
            for y in x:
                check(y)
            return
        if type(x) is dict and all(type(k) is str for k in x):
            for y in x.values():
                check(y)
            return
        raise ValueError('Snapshot accepts only finite JSON values with exact integers.')
    check(value)
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


@dataclass(frozen=True)
class Obligation:
    name: str
    dependencies: tuple[str, ...]
    parents: tuple[str, ...] = ()


@dataclass(frozen=True)
class Certificate:
    name: str
    bindings: tuple[tuple[str, bytes], ...]
    parent_seals: tuple[tuple[str, str], ...]
    witness: bytes

    def seal(self) -> str:
        # A content identifier, not a signature or an origin/validity assertion.
        record = [self.name, [(k, v.decode('ascii')) for k, v in self.bindings],
                  self.parent_seals, self.witness.decode('ascii')]
        return hashlib.sha256(canonical(record)).hexdigest()


Checker = Callable[[Mapping[str, Any], Any], None]


def topological_order(specs: Sequence[Obligation]) -> tuple[str, ...]:
    indexed = {s.name: s for s in specs}
    if len(indexed) != len(specs) or any(not s.name for s in specs):
        raise ValueError('Obligation names must be nonempty and unique.')
    for s in specs:
        if len(set(s.dependencies)) != len(s.dependencies):
            raise ValueError('Duplicate component dependency.')
        if len(set(s.parents)) != len(s.parents) or not set(s.parents) <= indexed.keys():
            raise ValueError('Duplicate or unavailable parent obligation.')
    visiting: set[str] = set()
    done: set[str] = set()
    order: list[str] = []
    def visit(n: str) -> None:
        if n in visiting:
            raise ValueError('Circular certificate dependencies require a separate rule.')
        if n in done:
            return
        visiting.add(n)
        for p in indexed[n].parents:
            visit(p)
        visiting.remove(n)
        done.add(n)
        order.append(n)
    for n in indexed:
        visit(n)
    return tuple(order)


def issue(spec: Obligation, state: Mapping[str, Any], witness: Any,
          parents: Mapping[str, Certificate], checker: Checker) -> Certificate:
    """Check local evidence before recording a snapshot of all required inputs.

    Parent soundness is established by check_bundle, not by merely supplying
    certificate objects to this constructor.
    """
    if not set(spec.dependencies) <= state.keys() or not set(spec.parents) <= parents.keys():
        raise ValueError('An input or parent required by the contract is unavailable.')
    view = {k: state[k] for k in spec.dependencies}
    checker(view, witness)
    return Certificate(spec.name,
        tuple((k, canonical(view[k])) for k in sorted(spec.dependencies)),
        tuple((k, parents[k].seal()) for k in sorted(spec.parents)), canonical(witness))


def check_bundle(specs: Sequence[Obligation], state: Mapping[str, Any],
                 certificates: Mapping[str, Certificate],
                 checkers: Mapping[str, Checker]) -> dict[str, dict[str, Any]]:
    """Fail closed on missing, changed, cyclic, or rejected obligations.

    Every applicable local checker is actually replayed. Bindings compare the
    complete declared JSON payload, not just a version name or a digest.
    """
    order = topological_order(specs)
    indexed = {s.name: s for s in specs}
    out: dict[str, dict[str, Any]] = {}
    for n in order:
        s = indexed[n]
        c = certificates.get(n)
        status, reason = 'VALID', 'local evidence replayed on matching declared inputs'
        if c is None or c.name != n:
            status, reason = 'MISSING', 'certificate unavailable or misnamed'
        elif n not in checkers:
            status, reason = 'REJECTED', 'no installed local checker'
        elif not set(s.dependencies) <= state.keys():
            status, reason = 'STALE', 'a required input is unavailable'
        elif tuple(k for k, _ in c.bindings) != tuple(sorted(s.dependencies)):
            status, reason = 'REJECTED', 'the binding omits or adds contract dependencies'
        elif any(canonical(state[k]) != value for k, value in c.bindings):
            status, reason = 'STALE', 'a declared input changed'
        elif tuple(k for k, _ in c.parent_seals) != tuple(sorted(s.parents)):
            status, reason = 'REJECTED', 'the parent binding differs from the contract'
        elif any(out[p]['status'] != 'VALID' for p in s.parents):
            status, reason = 'BLOCKED', 'a parent obligation is unavailable'
        elif any(certificates[p].seal() != seal for p, seal in c.parent_seals):
            status, reason = 'BLOCKED', 'the supplied parent evidence differs'
        else:
            try:
                witness = json.loads(c.witness)
                if canonical(witness) != c.witness:
                    raise ValueError('Noncanonical witness.')
                checkers[n]({k: state[k] for k in s.dependencies}, witness)
            except (ValueError, KeyError, TypeError, AssertionError, IndexError) as e:
                status, reason = 'REJECTED', f'{type(e).__name__}: {e}'
        out[n] = {'status': status, 'reason': reason}
    return out


def invalidation_closure(specs: Sequence[Obligation], changed: set[str]) -> frozenset[str]:
    order = topological_order(specs)
    indexed = {s.name: s for s in specs}
    invalid: set[str] = set()
    for n in order:
        s = indexed[n]
        if changed.intersection(s.dependencies) or invalid.intersection(s.parents):
            invalid.add(n)
    return frozenset(invalid)


def net_saving(setup: Sequence[Q], savings: Sequence[Sequence[Q]],
               multiplicities: Sequence[int]) -> tuple[Q, ...]:
    """Event-count ledger for an additive workload, in named units kept separate."""
    if not setup or any(Q(v) < 0 for v in setup):
        raise ValueError('Setup must be a nonempty nonnegative vector.')
    if len(savings) != len(multiplicities):
        raise ValueError('Each workload type needs one multiplicity.')
    if any(type(n) is not int or n < 0 for n in multiplicities):
        raise ValueError('Workload counts must be nonnegative integers.')
    d = len(setup)
    if any(len(row) != d for row in savings):
        raise ValueError('Resource dimensions differ.')
    return tuple(sum((n * Q(row[j]) for n, row in zip(multiplicities, savings)), Q(0))
                 - Q(setup[j]) for j in range(d))


def priced_saving(delta: Sequence[Q], prices: Sequence[Q]) -> Q:
    if not delta or len(delta) != len(prices) or any(Q(p) < 0 for p in prices):
        raise ValueError('Use a nonempty matching vector of nonnegative prices.')
    return sum((Q(x) * Q(w) for x, w in zip(delta, prices)), Q(0))


def price_polytope_margin(delta: Sequence[Q], vertices: Sequence[Sequence[Q]]) -> Q:
    if not vertices:
        raise ValueError('At least one price vertex is required.')
    return min(priced_saving(delta, w) for w in vertices)
