"""Finite information realizations, v0.2. Standard library, Python >= 3.10.

States are indices. Observations and task values may be any hashable objects.
Weights are exact nonnegative integers, normalized internally. Structural
statements include zero-weight states; probabilistic statements ignore their
mass. No external data, network access, or training is used.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import isqrt, lcm, log2
from typing import Hashable, Iterable, Sequence

Q = Fraction
Label = Hashable


def fixed_width_bits(alphabet_size: int) -> int:
    """Exact ceil(log2(k)) without floating point. The alphabet is nonempty."""
    if type(alphabet_size) is not int or alphabet_size < 1:
        raise ValueError("alphabet_size must be a positive integer")
    return (alphabet_size - 1).bit_length()


def canonical_partition(labels: Iterable[Label]) -> tuple[int, ...]:
    seen: dict[Label, int] = {}
    out = []
    for value in labels:
        hash(value)
        if value not in seen:
            seen[value] = len(seen)
        out.append(seen[value])
    return tuple(out)


@lru_cache(maxsize=None)
def partitions(n: int) -> tuple[tuple[int, ...], ...]:
    """All partitions in restricted-growth notation, one per relabeling orbit.

    Intended for small exhaustive verification, not large partition search.
    """
    if type(n) is not int or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if n == 0:
        return ((),)
    if n == 1:
        return ((0,),)
    return tuple(p + (j,) for p in partitions(n - 1)
                 for j in range(max(p) + 2))


def refines(fine: Sequence[Label], coarse: Sequence[Label]) -> bool:
    if len(fine) != len(coarse):
        raise ValueError("partitions must have equal lengths")
    mapping = {}
    for a, b in zip(fine, coarse):
        if a in mapping and mapping[a] != b:
            return False
        mapping[a] = b
    return True


@dataclass(frozen=True)
class EntropyCertificate:
    """Exact identity: H = log2(ratio)/total.

    Comparing entropies with the same total is an exact rational comparison.
    Adding entropies with the same total multiplies their ratios.
    Decimal conversion is for display, not the inequality certificate.
    """
    ratio: Fraction
    total: int

    def decimal(self, precision: int = 60) -> Decimal:
        if precision < 16:
            raise ValueError("precision must be at least 16")
        with localcontext() as ctx:
            ctx.prec = precision
            if self.ratio == 1:
                return Decimal(0)
            return ((Decimal(self.ratio.numerator).ln()
                     - Decimal(self.ratio.denominator).ln())
                    / Decimal(2).ln() / Decimal(self.total))


@dataclass(frozen=True)
class FiniteModel:
    observations: tuple[Label, ...]
    targets: tuple[Label, ...]
    weights: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        observations, targets = tuple(self.observations), tuple(self.targets)
        weights = ((1,) * len(observations) if self.weights is None
                   else tuple(self.weights))
        if not observations:
            raise ValueError("the structural state space must be nonempty")
        if len(targets) != len(observations) or len(weights) != len(observations):
            raise ValueError("observations, targets and weights must have equal lengths")
        if any(type(w) is not int or w < 0 for w in weights):
            raise ValueError("weights must be nonnegative integers (not floats/bools)")
        if sum(weights) == 0:
            raise ValueError("at least one state must have positive weight")
        for value in observations + targets:
            hash(value)
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "targets", targets)
        object.__setattr__(self, "weights", weights)

    @classmethod
    def from_probabilities(cls, observations: Sequence[Label],
                           targets: Sequence[Label],
                           probabilities: Sequence[Fraction | int]) -> FiniteModel:
        """Use exact rational probabilities; reject inexact float inputs."""
        probabilities = tuple(probabilities)
        if any(type(p) not in (int, Fraction) for p in probabilities):
            raise ValueError("probabilities must be exact int/Fraction values")
        if any(p < 0 for p in probabilities) or sum(probabilities) != 1:
            raise ValueError("probabilities must be nonnegative and sum exactly to 1")
        denominator = lcm(*(Q(p).denominator for p in probabilities))
        weights = tuple(int(Q(p) * denominator) for p in probabilities)
        return cls(tuple(observations), tuple(targets), weights)

    @property
    def n(self) -> int:
        return len(self.observations)

    @property
    def total(self) -> int:
        return sum(self.weights)

    def fibers(self, *, support_only: bool = False) -> dict[Label, set[Label]]:
        cells = defaultdict(set)
        for r, f, w in zip(self.observations, self.targets, self.weights):
            if not support_only or w:
                cells[r].add(f)
        return dict(cells)

    def kappa(self, *, support_only: bool = False) -> int:
        return max(map(len, self.fibers(support_only=support_only).values()))

    def repair_bits(self, *, support_only: bool = False) -> int:
        return fixed_width_bits(self.kappa(support_only=support_only))

    def obstruction(self, *, support_only: bool = False) -> tuple[int, int] | None:
        """A pair of state indices that certifies insufficient observations."""
        seen = {}
        for i, (r, f, w) in enumerate(zip(self.observations, self.targets, self.weights)):
            if support_only and not w:
                continue
            if r in seen:
                j = seen[r]
                if self.targets[j] != f:
                    return j, i
            else:
                seen[r] = i
        return None

    def answer_masses(self) -> dict[Label, dict[Label, int]]:
        cells = defaultdict(lambda: defaultdict(int))
        for r, f, w in zip(self.observations, self.targets, self.weights):
            if w:
                cells[r][f] += w
        return {r: dict(cell) for r, cell in cells.items()}

    def bayes_error(self) -> Fraction:
        correct = sum(max(cell.values()) for cell in self.answer_masses().values())
        return Q(self.total - correct, self.total)

    def entropy(self) -> float:
        """Floating-point display value. Exact comparisons use entropy_certificate."""
        h = 0.0
        for cell in self.answer_masses().values():
            subtotal = sum(cell.values())
            for w in cell.values():
                h += (w / self.total) * (log2(subtotal) - log2(w))
        return h

    def entropy_certificate(self, max_total: int = 100_000) -> EntropyCertificate:
        """H(F|R) = log2(prod W_r^W_r / prod W_rf^W_rf) / W.

        Zero masses are omitted. A resource guard prevents accidental creation
        of enormous exact integers. Scaling weights changes the certificate but
        not its represented entropy.
        """
        if self.total > max_total:
            raise ValueError("exact entropy certificate exceeds max_total resource guard")
        numerator, denominator = 1, 1
        for cell in self.answer_masses().values():
            subtotal = sum(cell.values())
            numerator *= subtotal ** subtotal
            for w in cell.values():
                denominator *= w ** w
        return EntropyCertificate(Q(numerator, denominator), self.total)

    def categorical_residual(self) -> Fraction:
        """Bayes multiclass Brier risk, with the unhalved one-hot convention.

        V_R(F) = E||e_F - P(F=.|R)||^2. Invariant under target relabeling,
        unlike scalar MSE after an arbitrary numeric encoding of task labels.
        """
        collision = sum((Q(sum(w*w for w in cell.values()), sum(cell.values()))
                         for cell in self.answer_masses().values()), Q(0)) / self.total
        return 1 - collision

    def categorical_projection_distance(self, other: FiniteModel) -> Fraction:
        """Squared L2 distance between conditional task-distribution vectors."""
        if self.weights != other.weights or self.targets != other.targets:
            raise ValueError("models must have identical state weights and task labels")
        def posteriors(model):
            return {r: {f: Q(w, sum(cell.values())) for f, w in cell.items()}
                    for r, cell in model.answer_masses().items()}
        a, b = posteriors(self), posteriors(other)
        labels = set(self.targets)
        total = Q(0)
        for r, s, w in zip(self.observations, other.observations, self.weights):
            if w:
                total += w * sum((a[r].get(f, Q(0)) - b[s].get(f, Q(0))) ** 2 for f in labels)
        return total / self.total

    def bayes_decoder(self) -> dict[Label, Label]:
        return {r: max(cell, key=cell.get) for r, cell in self.answer_masses().items()}

    def exact_repair(self) -> tuple[tuple[int, ...], dict[tuple[Label, int], Label]]:
        """Construct a minimal state-aware code plus its exact decoder.

        The encoder is allowed to know both observation and target (hence
        access to the underlying state suffices). This is not a decoder-only
        reconstruction of missing data.
        """
        labels: dict[Label, dict[Label, int]] = {}
        decoder = {}
        code = []
        for r, f in zip(self.observations, self.targets):
            mapping = labels.setdefault(r, {})
            if f not in mapping:
                mapping[f] = len(mapping)
            c = mapping[f]
            code.append(c)
            decoder[r, c] = f
        return tuple(code), decoder

    def optimal_success(self, alphabet_size: int) -> Fraction:
        """Maximum exact-answer probability with a state-aware m-symbol repair."""
        fixed_width_bits(alphabet_size)  # validate
        correct = sum(sum(sorted(cell.values(), reverse=True)[:alphabet_size])
                      for cell in self.answer_masses().values())
        return Q(correct, self.total)

    def budget_repair(self, alphabet_size: int) -> tuple[tuple[int, ...],
                                                       dict[tuple[Label, int], Label]]:
        """Construct an m-symbol repair attaining optimal_success(m)."""
        fixed_width_bits(alphabet_size)
        # Include null cells/answers so every structural state receives a code.
        cells = self.answer_masses()
        mappings, decoder = {}, {}
        for r, answers in self.fibers().items():
            # Stable order follows first appearance, including tie cases.
            ordered = list(dict.fromkeys(f for rr, f in zip(self.observations, self.targets)
                                         if rr == r))
            ordered.sort(key=lambda f: cells.get(r, {}).get(f, 0), reverse=True)
            selected = ordered[:alphabet_size]
            mappings[r] = {f: c for c, f in enumerate(selected)}
            for c, f in enumerate(selected):
                decoder[r, c] = f
        code = tuple(mappings[r].get(f, 0) for r, f in zip(self.observations, self.targets))
        return code, decoder

    def conditional_means(self, values: Sequence[Fraction | int]) -> dict[Label, Fraction]:
        values = self._numeric_values(values)
        total, weighted_sum = defaultdict(int), defaultdict(Fraction)
        for r, y, w in zip(self.observations, values, self.weights):
            if w:
                total[r] += w
                weighted_sum[r] += w * y
        return {r: weighted_sum[r] / total[r] for r in total}

    def projected_values(self, values: Sequence[Fraction | int]) -> tuple[Fraction, ...]:
        """A version of conditional expectation, set arbitrarily to 0 on null cells."""
        means = self.conditional_means(values)
        return tuple(means.get(r, Q(0)) for r in self.observations)

    def mse(self, values: Sequence[Fraction | int]) -> Fraction:
        values = self._numeric_values(values)
        projected = self.projected_values(values)
        return sum((w * (y - p) ** 2 for w, y, p in zip(self.weights, values, projected)
                    if w), Q(0)) / self.total

    def projection_distance(self, other: FiniteModel,
                            values: Sequence[Fraction | int]) -> Fraction:
        """Compute ||E[Y|R]-E[Y|S]||². Does not assert nesting/Markovity."""
        if self.weights != other.weights or self.n != other.n:
            raise ValueError("models must describe the same weighted state enumeration")
        a, b = self.projected_values(values), other.projected_values(values)
        return sum((w * (u - v) ** 2 for w, u, v in zip(self.weights, a, b) if w), Q(0)) / self.total

    def _numeric_values(self, values: Sequence[Fraction | int]) -> tuple[Fraction, ...]:
        values = tuple(values)
        if len(values) != self.n or any(type(v) not in (int, Fraction) for v in values):
            raise ValueError("numeric targets must be same-length exact int/Fraction values")
        return tuple(Q(v) for v in values)

    def profile(self) -> dict:
        return {"states": self.n, "positive_mass_states": sum(w > 0 for w in self.weights),
                "classes": len(set(self.observations)), "kappa": self.kappa(),
                "repair_bits": self.repair_bits(), "entropy_bits": self.entropy(),
                "bayes_error": str(self.bayes_error()), "categorical_residual": str(self.categorical_residual())}


def predictive_refinement(observations: Sequence[Label],
                          actions: Sequence[Sequence[int]]) -> tuple[tuple[int, ...],
                                                                    tuple[tuple[int, ...], ...]]:
    """Coarsest exact finite-state refinement stable under all listed actions.

    The history contains only strict refinements, preceded by the initial
    partition. Action words of all finite lengths are covered at stabilization.
    """
    observations, actions = tuple(observations), tuple(tuple(t) for t in actions)
    n = len(observations)
    if n == 0 or any(len(t) != n or any(type(j) is not int or not 0 <= j < n for j in t)
                     for t in actions):
        raise ValueError("actions must be total endomaps on a nonempty indexed state space")
    p = canonical_partition(observations)
    history = [p]
    while True:
        nxt = canonical_partition((p[i],) + tuple(p[t[i]] for t in actions) for i in range(n))
        if nxt == p:
            return p, tuple(history)
        if len(set(nxt)) <= len(set(p)):
            raise RuntimeError("partition refinement failed its strict-growth invariant")
        p = nxt
        history.append(p)


def _prime(p: int) -> bool:
    return type(p) is int and p >= 2 and all(p % d for d in range(2, isqrt(p) + 1))


def rank_mod(matrix: Sequence[Sequence[int]], prime: int, ncols: int | None = None) -> int:
    """Exact rank over a prime field. Composite moduli are rejected."""
    if not _prime(prime):
        raise ValueError("prime-field arithmetic requires a prime modulus")
    a = [list(row) for row in matrix]
    if ncols is None:
        ncols = len(a[0]) if a else 0
    if type(ncols) is not int or ncols < 0 or any(len(row) != ncols for row in a):
        raise ValueError("matrix dimensions are inconsistent")
    if any(type(v) is not int for row in a for v in row):
        raise ValueError("matrix entries must be integers")
    a = [[v % prime for v in row] for row in a]
    pivot = 0
    for col in range(ncols):
        i = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if i is None:
            continue
        a[pivot], a[i] = a[i], a[pivot]
        inv = pow(a[pivot][col], -1, prime)
        a[pivot] = [(v * inv) % prime for v in a[pivot]]
        for i in range(len(a)):
            if i != pivot and a[i][col]:
                c = a[i][col]
                a[i] = [(x - c * y) % prime for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def matvec(matrix: Sequence[Sequence[int]], x: Sequence[int], prime: int) -> tuple[int, ...]:
    """Matrix action; rank_mod validates field/dimensions at construction time."""
    if any(len(row) != len(x) for row in matrix):
        raise ValueError("matrix and vector dimensions disagree")
    return tuple(sum(a * b for a, b in zip(row, x)) % prime for row in matrix)


def linear_repair_rows(observation: Sequence[Sequence[int]],
                       target: Sequence[Sequence[int]], prime: int,
                       ncols: int) -> tuple[tuple[int, ...], ...]:
    """Extend the row space of R by d independent task rows. Minimal linear repair."""
    rows = [tuple(row) for row in observation]
    rank = rank_mod(rows, prime, ncols)
    # Validate all task rows even if observation already has full rank.
    rank_mod(target, prime, ncols)
    repair = []
    for row in target:
        new_rank = rank_mod(rows + [tuple(row)], prime, ncols)
        if new_rank > rank:
            rows.append(tuple(row))
            repair.append(tuple(row))
            rank = new_rank
    return tuple(repair)
