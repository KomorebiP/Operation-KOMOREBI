"""Finite view systems for coherent proof-field annotations.

This is a finite graph-of-views layer, not a claim that every proof archive
comes equipped with a universal or canonical category of all proof paths.
Restrictions are explicit maps from target-view values to source-view values.
For a full category, the caller must also supply functorial restrictions and
verify their composition equations; this module checks declared edges only.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping, Sequence
from types import MappingProxyType


@dataclass(frozen=True)
class Restriction:
    source: str
    target: str
    values: Mapping[str, str]
    label: str = ""


class FiniteViewSystem:
    """Finite coherent assignments subject to declared edge restrictions."""

    def __init__(
        self,
        fibers: Mapping[str, Sequence[str]],
        restrictions: Sequence[Restriction],
    ) -> None:
        self.fibers = MappingProxyType({v: tuple(values) for v, values in fibers.items()})
        if any(not isinstance(v, str) or not v for v in self.fibers):
            raise ValueError("view identifiers must be nonempty")
        for v, values in self.fibers.items():
            if any(not isinstance(t, str) for t in values) or len(values) != len(set(values)):
                raise ValueError(f"fiber {v} must contain distinct string values")
        self.restrictions = tuple(Restriction(e.source, e.target, MappingProxyType(dict(e.values)), e.label)
                                  for e in restrictions)
        for edge in self.restrictions:
            if edge.source not in self.fibers or edge.target not in self.fibers:
                raise ValueError("restriction references an unknown view")
            if set(edge.values) != set(self.fibers[edge.target]):
                raise ValueError("restriction must be total on the target fiber")
            if not set(edge.values.values()).issubset(self.fibers[edge.source]):
                raise ValueError("restriction has values outside the source fiber")

    def is_coherent(self, assignment: Mapping[str, str]) -> bool:
        if set(assignment) != set(self.fibers):
            return False
        if any(assignment[v] not in self.fibers[v] for v in assignment):
            return False
        return all(
            edge.values[assignment[edge.target]] == assignment[edge.source]
            for edge in self.restrictions
        )

    def sections(self, *, max_raw_assignments: int = 1_000_000) -> tuple[dict[str, str], ...]:
        """Exact enumeration, guarded against accidental combinatorial explosion."""
        if type(max_raw_assignments) is not int or max_raw_assignments < 1:
            raise ValueError("max_raw_assignments must be a positive integer")
        total = 1
        for v in self.fibers:
            total *= len(self.fibers[v])
        if total > max_raw_assignments:
            raise ValueError("enumeration exceeds max_raw_assignments")
        views = tuple(self.fibers)
        return tuple(
            candidate
            for values in product(*(self.fibers[v] for v in views))
            if self.is_coherent(candidate := dict(zip(views, values)))
        )

    def covers_arrows(self, patches: Sequence[Sequence[str]]) -> bool:
        p = [set(patch) for patch in patches]
        return (
            all(view in set().union(*p) for view in self.fibers)
        ) and all(
            any({e.source, e.target}.issubset(patch) for patch in p)
            for e in self.restrictions
        )

    def glue(
        self,
        patches: Sequence[Mapping[str, str]],
    ) -> dict[str, str]:
        """Glue coherent matching local sections of an arrow-covering family.

        A failure of the arrow-cover hypothesis is not treated as proof that
        the data are globally inconsistent; it is a missing hypothesis.
        """
        if not self.covers_arrows([tuple(p) for p in patches]):
            raise ValueError("patches do not cover every view and restriction")
        assembled: dict[str, str] = {}
        for patch in patches:
            if any(v not in self.fibers for v in patch):
                raise ValueError("unknown view in patch")
            if any(value not in self.fibers[v] for v, value in patch.items()):
                raise ValueError("value outside a fiber")
            for v, value in patch.items():
                if v in assembled and assembled[v] != value:
                    raise ValueError(f"patches disagree at view {v}")
                assembled[v] = value
            for edge in self.restrictions:
                if edge.source in patch and edge.target in patch:
                    if edge.values[patch[edge.target]] != patch[edge.source]:
                        raise ValueError("local patch violates its restriction")
        if not self.is_coherent(assembled):
            raise AssertionError("unexpected failure of arrow-cover gluing")
        return assembled
