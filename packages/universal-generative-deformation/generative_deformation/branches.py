from __future__ import annotations

from typing import Any, Callable, Sequence

from .model import DeformationSystem, Direction


def follow_branch(
    system: DeformationSystem,
    seed: Any,
    selector: Callable[[Any, int, Sequence[Direction]], Direction],
    depth: int,
) -> tuple[list[Any], list[Direction]]:
    if depth < 0:
        raise ValueError("depth must be nonnegative")
    states = [seed]
    directions_used: list[Direction] = []
    state = seed
    for level in range(depth):
        directions = list(system.directions(state, level))
        if not directions:
            break
        direction = selector(state, level, directions)
        if direction not in directions:
            raise ValueError("selector returned a direction outside the available set")
        state = system.apply(state, direction)
        states.append(state)
        directions_used.append(direction)
    return states, directions_used


def first_direction_selector(state: Any, depth: int, directions: Sequence[Direction]) -> Direction:
    return directions[0]
