from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Hashable, Iterable


@dataclass
class DirectedGraph:
    adjacency: dict[Hashable, set[Hashable]] = field(default_factory=dict)

    def add_vertex(self, vertex: Hashable) -> None:
        self.adjacency.setdefault(vertex, set())

    def add_edge(self, source: Hashable, target: Hashable) -> None:
        self.add_vertex(source)
        self.add_vertex(target)
        self.adjacency[source].add(target)

    @property
    def vertices(self) -> list[Hashable]:
        return list(self.adjacency)

    def reverse(self) -> "DirectedGraph":
        out = DirectedGraph()
        for v in self.vertices:
            out.add_vertex(v)
        for u, targets in self.adjacency.items():
            for v in targets:
                out.add_edge(v, u)
        return out


def _finish_order(graph: DirectedGraph) -> list[Hashable]:
    seen: set[Hashable] = set()
    order: list[Hashable] = []

    def visit(v: Hashable) -> None:
        seen.add(v)
        for w in graph.adjacency.get(v, set()):
            if w not in seen:
                visit(w)
        order.append(v)

    for v in graph.vertices:
        if v not in seen:
            visit(v)
    return order


def strongly_connected_components(graph: DirectedGraph) -> list[set[Hashable]]:
    order = _finish_order(graph)
    reversed_graph = graph.reverse()
    seen: set[Hashable] = set()
    components: list[set[Hashable]] = []

    def collect(v: Hashable, component: set[Hashable]) -> None:
        seen.add(v)
        component.add(v)
        for w in reversed_graph.adjacency.get(v, set()):
            if w not in seen:
                collect(w, component)

    for v in reversed(order):
        if v not in seen:
            component: set[Hashable] = set()
            collect(v, component)
            components.append(component)
    return components


def source_components(graph: DirectedGraph) -> list[set[Hashable]]:
    components = strongly_connected_components(graph)
    index = {v: i for i, comp in enumerate(components) for v in comp}
    indegree = [0] * len(components)
    for u, targets in graph.adjacency.items():
        for v in targets:
            i, j = index[u], index[v]
            if i != j:
                indegree[j] += 1
    return [components[i] for i, degree in enumerate(indegree) if degree == 0]


def transport_closure(graph: DirectedGraph, seeds: Iterable[Hashable]) -> set[Hashable]:
    reached = set(seeds)
    stack = list(reached)
    while stack:
        u = stack.pop()
        for v in graph.adjacency.get(u, set()):
            if v not in reached:
                reached.add(v)
                stack.append(v)
    return reached


def minimum_seed_representatives(graph: DirectedGraph) -> list[Hashable]:
    return [sorted(comp, key=str)[0] for comp in source_components(graph)]


def brute_force_minimum_seed_count(graph: DirectedGraph) -> int:
    vertices = graph.vertices
    for size in range(len(vertices) + 1):
        for subset in combinations(vertices, size):
            if transport_closure(graph, subset) == set(vertices):
                return size
    raise ArithmeticError("finite graph should be reachable from all vertices as seeds")
