"""The finite proof-field to coherent-view bridge.

A valuation says which nodes belong to a closed set under the declared certified
rules. It is NOT a truth assignment to the mathematical sentences in node labels.
Whole AND-rule supports must be covered. Alternative justifications remain
separate implications, preserving the field's AND/OR distinction.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Iterable, Mapping, Sequence

from .ambient import FiniteViewSystem, Restriction
from .model import ProofField


@dataclass(frozen=True)
class RuleConstraint:
    id: str
    premises: frozenset[str]
    conclusion: str

    @property
    def support(self) -> frozenset[str]:
        return self.premises | {self.conclusion}


class ProofFieldViews:
    """A constraint snapshot of a finite declared proof field."""

    def __init__(self, field: ProofField) -> None:
        self.nodes = frozenset(field.nodes)
        self.leaves = frozenset(v for v in self.nodes if field.is_admissible_leaf(v))
        self.rules = tuple(
            RuleConstraint(j.id, frozenset(j.premises), j.conclusion)
            for j in sorted(field.justifications.values(), key=lambda j: j.id)
            if j.certified
        )

    def _patch(self, patch: Iterable[str]) -> frozenset[str]:
        result = frozenset(patch)
        if not result <= self.nodes:
            raise ValueError("patch references unknown nodes")
        return result

    def is_local_model(self, patch: Iterable[str], true_nodes: Iterable[str]) -> bool:
        u = self._patch(patch)
        t = frozenset(true_nodes)
        if not t <= u or not (self.leaves & u) <= t:
            return False
        return all(
            not (r.support <= u and r.premises <= t) or r.conclusion in t
            for r in self.rules
        )

    def local_models(self, patch: Iterable[str], *, max_assignments: int = 1_000_000
                     ) -> tuple[frozenset[str], ...]:
        u = self._patch(patch)
        if type(max_assignments) is not int or max_assignments < 1:
            raise ValueError("max_assignments must be a positive integer")
        ordered = sorted(u)
        if 2 ** len(ordered) > max_assignments:
            raise ValueError("local enumeration exceeds max_assignments")
        return tuple(
            t for bits in product((0, 1), repeat=len(ordered))
            if self.is_local_model(u, t := frozenset(v for v, b in zip(ordered, bits) if b))
        )

    def restrict(self, larger: Iterable[str], smaller: Iterable[str],
                 true_nodes: Iterable[str]) -> frozenset[str]:
        v, u, t = self._patch(larger), self._patch(smaller), frozenset(true_nodes)
        if not u <= v or not self.is_local_model(v, t):
            raise ValueError("restriction requires inclusion and a valid local model")
        return t & u

    def covers_supports(self, patches: Sequence[Iterable[str]]) -> bool:
        ps = tuple(self._patch(p) for p in patches)
        return frozenset().union(*ps) == self.nodes and all(
            any(r.support <= p for p in ps) for r in self.rules
        )

    def glue(self, patches: Sequence[Iterable[str]],
             true_sets: Sequence[Iterable[str]]) -> frozenset[str]:
        if len(patches) != len(true_sets):
            raise ValueError("one local valuation is required per patch")
        ps = tuple(self._patch(p) for p in patches)
        ts = tuple(frozenset(t) for t in true_sets)
        if not self.covers_supports(ps):
            raise ValueError("cover omits a node or a whole certified rule support")
        if any(not self.is_local_model(p, t) for p, t in zip(ps, ts)):
            raise ValueError("an assignment is not a local model")
        for i, j in combinations(range(len(ps)), 2):
            overlap = ps[i] & ps[j]
            if ts[i] & overlap != ts[j] & overlap:
                raise ValueError("local valuations disagree on an overlap")
        answer = frozenset().union(*ts)
        if not self.is_local_model(self.nodes, answer):
            raise AssertionError("support-cover gluing invariant failed")
        return answer

    def least_model(self) -> frozenset[str]:
        """Forward closure, with a finite stopping argument independent of a DAG order."""
        current = set(self.leaves)
        while True:
            previous = len(current)
            for rule in self.rules:
                if rule.premises <= current:
                    current.add(rule.conclusion)
            if len(current) == previous:
                return frozenset(current)

    def countermodel(self, target: str) -> frozenset[str] | None:
        """A declared-rule countermodel, not a counterexample to a theorem's semantics."""
        if target not in self.nodes:
            raise ValueError("unknown target")
        model = self.least_model()
        return None if target in model else model

    def to_view_system(self, patches: Sequence[Iterable[str]], *,
                       max_patches: int = 256, max_local_assignments: int = 1_000_000
                       ) -> tuple[FiniteViewSystem, Mapping[str, tuple[str, ...]]]:
        """Add intersections, enumerate local fibers, and use literal coordinate restriction.

        This does not require support coverage merely to build a diagram. Without
        coverage its coherent families need not satisfy all original field rules.
        """
        if type(max_patches) is not int or max_patches < 1:
            raise ValueError("max_patches must be a positive integer")
        sets = {self._patch(p) for p in patches}
        if len(sets) > max_patches:
            raise ValueError("too many patches")
        while True:
            added = {a & b for a, b in combinations(sets, 2)} - sets
            if not added:
                break
            sets.update(added)
            if len(sets) > max_patches:
                raise ValueError("intersection closure exceeds max_patches")
        ps = sorted(sets, key=lambda u: (len(u), tuple(sorted(u))))
        mapping = {f"p{i}": tuple(sorted(u)) for i, u in enumerate(ps)}
        def encode(t: frozenset[str], ordered: tuple[str, ...]) -> str:
            return ''.join('1' if v in t else '0' for v in ordered)
        fibers = {
            key: tuple(encode(t, ordered) for t in self.local_models(
                ordered, max_assignments=max_local_assignments))
            for key, ordered in mapping.items()
        }
        edges = []
        for small, u in mapping.items():
            for large, v in mapping.items():
                if small == large or not set(u) <= set(v):
                    continue
                positions = tuple(v.index(x) for x in u)
                edges.append(Restriction(small, large,
                    {bits: ''.join(bits[i] for i in positions) for bits in fibers[large]},
                    "coordinate restriction"))
        return FiniteViewSystem(fibers, edges), mapping
