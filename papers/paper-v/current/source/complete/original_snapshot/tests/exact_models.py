"""Paper V exact finite reference models, authored for the first Lean work block.

These models are not the original companion implementation and are not a proof
checker. They use Fraction, never floating-point tolerances.
Author: Komorebi P.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import prod
from typing import Iterable, Mapping

Q = Fraction
Address = tuple[int, ...]
Signal = dict[int, Q]


def rational(x: int | Q) -> Q:
    if not isinstance(x, (int, Fraction)):
        raise TypeError("Exact models accept int or Fraction, not floats.")
    return Q(x)


def clean_signal(x: Mapping[int, int | Q]) -> Signal:
    if any(not isinstance(k, int) for k in x):
        raise TypeError("Signal addresses must be integers.")
    return {k: rational(v) for k, v in x.items() if rational(v) != 0}


def analyze(x: Mapping[int, int | Q], n: int) -> tuple[Signal, ...]:
    if not isinstance(n, int) or n < 1:
        raise ValueError("The phase count must be a positive integer.")
    channels: tuple[Signal, ...] = tuple({} for _ in range(n))
    for address, value in clean_signal(x).items():
        q, r = divmod(address, n)
        channels[r][q] = value
    return channels


def synthesize(channels: tuple[Mapping[int, int | Q], ...]) -> Signal:
    n = len(channels)
    if n == 0:
        raise ValueError("At least one channel is required.")
    return {n * q + r: v for r, c in enumerate(channels)
            for q, v in clean_signal(c).items()}


def convolve(h: Mapping[int, int | Q], x: Mapping[int, int | Q]) -> Signal:
    out: Signal = {}
    for k, a in clean_signal(h).items():
        for i, b in clean_signal(x).items():
            out[i + k] = out.get(i + k, Q(0)) + a * b
    return clean_signal(out)


def transfer_kernels(h: Mapping[int, int | Q], n: int) -> tuple[tuple[Signal, ...], ...]:
    if not isinstance(n, int) or n < 1:
        raise ValueError("The phase count must be positive.")
    h = clean_signal(h)
    return tuple(tuple({(tap - k + s) // n: value
                        for tap, value in h.items() if (tap - k + s) % n == 0}
                       for s in range(n)) for k in range(n))


def polyphase_convolve(h: Mapping[int, int | Q], x: Mapping[int, int | Q], n: int) -> Signal:
    channels = analyze(x, n)
    kernels = transfer_kernels(h, n)
    out: list[Signal] = []
    for k in range(n):
        y: Signal = {}
        for s in range(n):
            for q, value in convolve(kernels[k][s], channels[s]).items():
                y[q] = y.get(q, Q(0)) + value
        out.append(clean_signal(y))
    return synthesize(tuple(out))


def sample_delay_routes(n: int, delay: int) -> tuple[tuple[int, int], ...]:
    """Rows (input phase, channel delay) for an original-sample delay.

    E.g. n=2, delay=1 returns ((1, 1), (0, 0)), namely
    [[0, z^-1], [1, 0]], not the scalar channel delay z^-1 I.
    """
    if not isinstance(n, int) or n < 1 or not isinstance(delay, int):
        raise ValueError("Positive integer phase count and integer delay required.")
    rows = []
    for r in range(n):
        carry, s = divmod(r - delay, n)
        rows.append((s, -carry))
    return tuple(rows)


def apply_delay_routes(channels: tuple[Mapping[int, int | Q], ...], delay: int) -> tuple[Signal, ...]:
    return tuple({q + d: v for q, v in clean_signal(channels[s]).items()}
                 for s, d in sample_delay_routes(len(channels), delay))


def lifting_analysis(e: int | Q, o: int | Q) -> tuple[Q, Q]:
    e, o = rational(e), rational(o)
    d = o - e
    return e + d / 2, d


def lifting_synthesis(s: int | Q, d: int | Q) -> tuple[Q, Q]:
    s, d = rational(s), rational(d)
    e = s - d / 2
    return e, d + e


@dataclass(frozen=True)
class Tree:
    children: tuple[Tree, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.children, tuple) or any(not isinstance(c, Tree) for c in self.children):
            raise TypeError("Children must be a tuple of Tree objects.")


def nodes(t: Tree, a: Address = ()) -> Iterable[Address]:
    yield a
    for i, child in enumerate(t.children):
        yield from nodes(child, a + (i,))


def leaves(t: Tree, a: Address = ()) -> Iterable[Address]:
    if not t.children:
        yield a
    for i, child in enumerate(t.children):
        yield from leaves(child, a + (i,))


def pruning_count(t: Tree) -> int:
    return 1 if not t.children else 1 + prod(pruning_count(c) for c in t.children)


def complete_prunings(t: Tree, a: Address = (), *, limit: int = 1_000_000) -> tuple[tuple[Address, ...], ...]:
    if pruning_count(t) > limit:
        raise ValueError("Enumeration limit exceeded; use dynamic programming.")
    out: list[tuple[Address, ...]] = [(a,)]
    if t.children:
        children = [complete_prunings(c, a + (i,), limit=limit) for i, c in enumerate(t.children)]
        out.extend(tuple(address for subcut in combination for address in subcut)
                   for combination in product(*children))
    return tuple(out)


def is_complete_pruning(t: Tree, cut: tuple[Address, ...]) -> bool:
    universe = set(nodes(t))
    if not cut or len(set(cut)) != len(cut) or not set(cut) <= universe:
        return False
    return all(sum(leaf[:len(a)] == a for a in cut) == 1 for leaf in leaves(t))


def checked_costs(t: Tree, c: Mapping[Address, int | Q]) -> dict[Address, Q]:
    if set(c) != set(nodes(t)):
        raise ValueError("A cost is required for every node and no other address.")
    return {a: rational(v) for a, v in c.items()}


@dataclass(frozen=True)
class Selection:
    value: Q
    cut: tuple[Address, ...]
    internal_comparisons: int


def optimal_cut(t: Tree, costs: Mapping[Address, int | Q]) -> Selection:
    """Two linear traversals after costs are available, stopping on ties.

    Arithmetic operation count is O(number of nodes); exact rational bit cost is
    not asserted to be constant. No exhaustive enumeration is used here.
    """
    c = checked_costs(t, costs)
    stop: dict[Address, bool] = {}
    comparisons = 0

    def solve(node: Tree, a: Address) -> Q:
        nonlocal comparisons
        if not node.children:
            stop[a] = True
            return c[a]
        refined = sum((solve(child, a + (i,)) for i, child in enumerate(node.children)), Q(0))
        comparisons += 1
        stop[a] = c[a] <= refined
        return c[a] if stop[a] else refined

    value = solve(t, ())
    selected: list[Address] = []

    def collect(node: Tree, a: Address) -> None:
        if stop[a]:
            selected.append(a)
        else:
            for i, child in enumerate(node.children):
                collect(child, a + (i,))

    collect(t, ())
    return Selection(value, tuple(selected), comparisons)


def perturbation_envelope(t: Tree, errors: Mapping[Address, int | Q]) -> Q:
    e = checked_costs(t, errors)
    if any(v < 0 for v in e.values()):
        raise ValueError("Local perturbation envelopes cannot be negative.")

    def visit(node: Tree, a: Address) -> Q:
        return e[a] if not node.children else max(
            e[a], sum((visit(ch, a + (i,)) for i, ch in enumerate(node.children)), Q(0)))

    return visit(t, ())


@dataclass(frozen=True)
class GapReport:
    unique: bool
    gap: Q | None  # None means there are no competing cuts, not a zero gap.
    optimum: Q


def selection_gap(t: Tree, costs: Mapping[Address, int | Q]) -> GapReport:
    c = checked_costs(t, costs)
    values = sorted(sum((c[a] for a in cut), Q(0)) for cut in complete_prunings(t))
    if len(values) == 1:
        return GapReport(True, None, values[0])
    return GapReport(values[0] < values[1], values[1] - values[0], values[0])


def gap_certifies_stability(report: GapReport, envelope: int | Q) -> bool:
    e = rational(envelope)
    if e < 0:
        raise ValueError("Envelope must be nonnegative.")
    return report.unique and (report.gap is None or 2 * e < report.gap)
