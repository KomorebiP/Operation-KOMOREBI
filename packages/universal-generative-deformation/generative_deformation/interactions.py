from __future__ import annotations

from itertools import combinations_with_replacement
from typing import Any, Iterable, Sequence

from .model import InteractionRule, InteractionSystem, ValidationResult


def generate_interactions(
    states: Sequence[Any],
    rules: Iterable[InteractionRule],
    system: InteractionSystem,
    *,
    limit: int = 1000,
) -> list[tuple[InteractionRule, tuple[int, ...], Any]]:
    """Generate a finite prefix of the multi-input perturbation hyperforest."""
    if limit < 1:
        raise ValueError("limit must be positive")
    output: list[tuple[InteractionRule, tuple[int, ...], Any]] = []
    for rule in rules:
        for indices in combinations_with_replacement(range(len(states)), rule.arity):
            selected = [states[index] for index in indices]
            if system.admissible(rule, selected):
                output.append((rule, indices, system.apply_interaction(rule, selected)))
                if len(output) >= limit:
                    return output
    return output
