"""Exact finite-state search algorithms and certificate reconstruction."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Callable, Generic, Hashable, Iterable, Mapping, Sequence, TypeVar

State = TypeVar("State", bound=Hashable)


@dataclass(frozen=True)
class NamedGenerator(Generic[State]):
    name: str
    element: State
    cost: int = 1


def breadth_first_distances(
    identity: State,
    generators: Sequence[NamedGenerator[State]],
    multiply: Callable[[State, State], State],
) -> dict[State, int]:
    distances: dict[State, int] = {identity: 0}
    queue: deque[State] = deque([identity])
    while queue:
        state = queue.popleft()
        next_distance = distances[state] + 1
        for generator in generators:
            candidate = multiply(generator.element, state)
            if candidate not in distances:
                distances[candidate] = next_distance
                queue.append(candidate)
    return distances


def breadth_first_with_parents(
    identity: State,
    generators: Sequence[NamedGenerator[State]],
    multiply: Callable[[State, State], State],
) -> tuple[dict[State, int], dict[State, tuple[State, str] | None]]:
    distances: dict[State, int] = {identity: 0}
    parents: dict[State, tuple[State, str] | None] = {identity: None}
    queue: deque[State] = deque([identity])
    while queue:
        state = queue.popleft()
        next_distance = distances[state] + 1
        for generator in generators:
            candidate = multiply(generator.element, state)
            if candidate not in distances:
                distances[candidate] = next_distance
                parents[candidate] = (state, generator.name)
                queue.append(candidate)
    return distances, parents


def zero_one_distances(
    identity: State,
    generators: Sequence[NamedGenerator[State]],
    multiply: Callable[[State, State], State],
) -> dict[State, int]:
    if any(generator.cost not in (0, 1) for generator in generators):
        raise ValueError("zero_one_distances requires costs 0 or 1")
    infinity = 10**18
    distances: dict[State, int] = {identity: 0}
    queue: deque[State] = deque([identity])
    while queue:
        state = queue.popleft()
        current = distances[state]
        for generator in generators:
            candidate = multiply(generator.element, state)
            proposed = current + generator.cost
            if proposed < distances.get(candidate, infinity):
                distances[candidate] = proposed
                if generator.cost == 0:
                    queue.appendleft(candidate)
                else:
                    queue.append(candidate)
    return distances


def zero_one_with_parents(
    identity: State,
    generators: Sequence[NamedGenerator[State]],
    multiply: Callable[[State, State], State],
) -> tuple[dict[State, int], dict[State, tuple[State, str, int] | None]]:
    if any(generator.cost not in (0, 1) for generator in generators):
        raise ValueError("zero_one_with_parents requires costs 0 or 1")
    infinity = 10**18
    distances: dict[State, int] = {identity: 0}
    parents: dict[State, tuple[State, str, int] | None] = {identity: None}
    queue: deque[State] = deque([identity])
    while queue:
        state = queue.popleft()
        current = distances[state]
        for generator in generators:
            candidate = multiply(generator.element, state)
            proposed = current + generator.cost
            if proposed < distances.get(candidate, infinity):
                distances[candidate] = proposed
                parents[candidate] = (state, generator.name, generator.cost)
                if generator.cost == 0:
                    queue.appendleft(candidate)
                else:
                    queue.append(candidate)
    return distances, parents


def dijkstra_distances(
    identity: State,
    generators: Sequence[NamedGenerator[State]],
    multiply: Callable[[State, State], State],
) -> dict[State, int]:
    if any(generator.cost < 0 for generator in generators):
        raise ValueError("costs must be nonnegative")
    distances: dict[State, int] = {identity: 0}
    heap: list[tuple[int, State]] = [(0, identity)]
    while heap:
        distance, state = heappop(heap)
        if distance != distances[state]:
            continue
        for generator in generators:
            candidate = multiply(generator.element, state)
            proposed = distance + generator.cost
            if proposed < distances.get(candidate, 10**18):
                distances[candidate] = proposed
                heappush(heap, (proposed, candidate))
    return distances


def reconstruct_path(
    target: State,
    parents: Mapping[State, tuple | None],
) -> list[str]:
    path: list[str] = []
    state = target
    while parents[state] is not None:
        record = parents[state]
        assert record is not None
        state = record[0]
        path.append(record[1])
    path.reverse()
    return path


def defect_distribution(
    restricted: Mapping[State, int],
    ambient: Mapping[State, int],
) -> dict[tuple[int, int], int]:
    distribution: dict[tuple[int, int], int] = {}
    for state, restricted_distance in restricted.items():
        ambient_distance = ambient[state]
        if restricted_distance > ambient_distance:
            key = (restricted_distance, ambient_distance)
            distribution[key] = distribution.get(key, 0) + 1
    return dict(sorted(distribution.items()))
