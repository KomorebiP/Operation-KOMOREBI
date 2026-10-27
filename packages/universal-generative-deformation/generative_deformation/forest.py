from __future__ import annotations

import csv
import heapq
import json
from collections import Counter, defaultdict, deque
from dataclasses import asdict
from pathlib import Path
from typing import Any, Hashable, Iterable

from .model import (
    DeformationSystem,
    Direction,
    ExplorationConfig,
    ForestEdge,
    ForestNode,
    PathRecord,
)


class PerturbationForest:
    """Finite explored prefix of an infinite state-dependent perturbation tree.

    Every admissible path is represented by a :class:`PathRecord`.  Endpoints
    are deduplicated through ``system.canonical_key`` and stored as quotient
    nodes.  This simultaneously records the raw tree and the relation quotient.
    """

    def __init__(self, system: DeformationSystem, seeds: Iterable[Any]) -> None:
        self.system = system
        self.nodes: dict[int, ForestNode] = {}
        self.node_by_key: dict[Hashable, int] = {}
        self.edges: dict[tuple[int, int, str], ForestEdge] = {}
        self.paths: dict[int, PathRecord] = {}
        self.paths_by_depth: Counter[int] = Counter()
        self.invalid_attempts: list[dict[str, Any]] = []
        self._next_node_id = 0
        self._next_path_id = 0
        self.root_path_ids: list[int] = []
        for seed in seeds:
            path_id = self._add_root(seed)
            self.root_path_ids.append(path_id)
        if not self.root_path_ids:
            raise ValueError("at least one seed is required")

    def _safe_key(self, state: Any) -> Hashable:
        key = self.system.canonical_key(state)
        try:
            hash(key)
        except TypeError:
            key = repr(key)
        return key

    def _new_path(
        self,
        *,
        node_id: int,
        depth: int,
        parent_path_id: int | None,
        direction: Direction | None,
        cost: float,
        labels: tuple[str, ...],
    ) -> int:
        path_id = self._next_path_id
        self._next_path_id += 1
        self.paths[path_id] = PathRecord(
            id=path_id,
            node_id=node_id,
            depth=depth,
            parent_path_id=parent_path_id,
            direction=direction,
            cost=cost,
            labels=labels,
        )
        self.paths_by_depth[depth] += 1
        return path_id

    def _add_root(self, state: Any) -> int:
        validation = self.system.validate(state)
        if not validation.valid:
            raise ValueError(f"invalid seed: {validation.reason}")
        key = self._safe_key(state)
        if key in self.node_by_key:
            node_id = self.node_by_key[key]
        else:
            node_id = self._next_node_id
            self._next_node_id += 1
            path_id_preview = self._next_path_id
            self.nodes[node_id] = ForestNode(
                id=node_id,
                key=key,
                state=state,
                min_depth=0,
                first_parent=None,
                first_direction=None,
                first_path_id=path_id_preview,
                path_cost=0.0,
                invariants=dict(self.system.invariants(state)),
            )
            self.node_by_key[key] = node_id
        return self._new_path(
            node_id=node_id,
            depth=0,
            parent_path_id=None,
            direction=None,
            cost=0.0,
            labels=(),
        )

    def explore(self, config: ExplorationConfig = ExplorationConfig()) -> "PerturbationForest":
        if config.strategy == "breadth_first":
            frontier: Any = deque(self.root_path_ids)
            pop = frontier.popleft
            push = frontier.append
        else:
            frontier = [(self.paths[path_id].cost, path_id) for path_id in self.root_path_ids]
            heapq.heapify(frontier)

            def pop() -> int:
                return heapq.heappop(frontier)[1]

            def push(path_id: int) -> None:
                heapq.heappush(frontier, (self.paths[path_id].cost, path_id))

        while frontier:
            if len(self.paths) >= config.max_paths:
                break
            path_id = pop()
            path = self.paths[path_id]
            if path.depth >= config.max_depth:
                continue
            node = self.nodes[path.node_id]
            directions = list(self.system.directions(node.state, path.depth))
            if config.per_path_direction_limit is not None:
                directions = directions[: config.per_path_direction_limit]
            for direction in directions:
                if len(self.paths) >= config.max_paths or len(self.edges) >= config.max_edges:
                    break
                try:
                    child_state = self.system.apply(node.state, direction)
                except Exception as exc:  # explicit audit trail rather than silent loss
                    self.invalid_attempts.append(
                        {
                            "path_id": path_id,
                            "node_id": node.id,
                            "direction": direction.label(),
                            "reason": f"exception: {type(exc).__name__}: {exc}",
                        }
                    )
                    continue
                validation = self.system.validate(child_state)
                if not validation.valid:
                    self.invalid_attempts.append(
                        {
                            "path_id": path_id,
                            "node_id": node.id,
                            "direction": direction.label(),
                            "reason": validation.reason,
                        }
                    )
                    if not config.keep_invalid:
                        continue
                child_key = self._safe_key(child_state)
                next_depth = path.depth + 1
                next_cost = path.cost + float(direction.cost)
                if child_key in self.node_by_key:
                    child_id = self.node_by_key[child_key]
                    existing = self.nodes[child_id]
                    if next_depth < existing.min_depth or (
                        next_depth == existing.min_depth and next_cost < existing.path_cost
                    ):
                        existing.min_depth = next_depth
                        existing.first_parent = node.id
                        existing.first_direction = direction
                        existing.path_cost = next_cost
                else:
                    if len(self.nodes) >= config.max_nodes:
                        continue
                    child_id = self._next_node_id
                    self._next_node_id += 1
                    self.node_by_key[child_key] = child_id
                    self.nodes[child_id] = ForestNode(
                        id=child_id,
                        key=child_key,
                        state=child_state,
                        min_depth=next_depth,
                        first_parent=node.id,
                        first_direction=direction,
                        first_path_id=self._next_path_id,
                        path_cost=next_cost,
                        invariants=dict(self.system.invariants(child_state)),
                    )
                edge_key = (node.id, child_id, direction.label())
                if edge_key in self.edges:
                    self.edges[edge_key].multiplicity += 1
                else:
                    self.edges[edge_key] = ForestEdge(
                        source=node.id,
                        target=child_id,
                        direction=direction,
                        first_depth=next_depth,
                    )
                child_path_id = self._new_path(
                    node_id=child_id,
                    depth=next_depth,
                    parent_path_id=path_id,
                    direction=direction,
                    cost=next_cost,
                    labels=path.labels + (direction.label(),),
                )
                push(child_path_id)
        return self

    def raw_counts(self) -> dict[int, int]:
        return dict(sorted(self.paths_by_depth.items()))

    def quotient_counts(self, *, exact_depth: bool = True) -> dict[int, int]:
        """Count distinct relation classes represented at each explored depth.

        With ``exact_depth=True``, a class is counted whenever at least one raw
        path of exactly that depth reaches it.  This is the natural comparison
        with raw path growth.  With ``exact_depth=False``, the count is
        cumulative over all paths up to the requested depth.
        """
        by_depth: dict[int, set[int]] = defaultdict(set)
        for path in self.paths.values():
            by_depth[path.depth].add(path.node_id)
        if exact_depth:
            return {depth: len(ids) for depth, ids in sorted(by_depth.items())}
        cumulative: set[int] = set()
        counts: dict[int, int] = {}
        for depth in sorted(by_depth):
            cumulative.update(by_depth[depth])
            counts[depth] = len(cumulative)
        return counts

    def new_node_counts(self) -> dict[int, int]:
        counts: Counter[int] = Counter(node.min_depth for node in self.nodes.values())
        return dict(sorted(counts.items()))

    def first_path(self, node_id: int) -> tuple[str, ...]:
        node = self.nodes[node_id]
        return self.paths[node.first_path_id].labels

    def shortest_path_labels(self, node_id: int) -> tuple[str, ...]:
        # The first path is shortest under breadth first exploration.  For other
        # strategies, reconstruct through first-parent links.
        node = self.nodes[node_id]
        if node.first_parent is None:
            return ()
        labels: list[str] = []
        current = node
        seen: set[int] = set()
        while current.first_parent is not None:
            if current.id in seen:
                break
            seen.add(current.id)
            if current.first_direction is not None:
                labels.append(current.first_direction.label())
            current = self.nodes[current.first_parent]
        labels.reverse()
        return tuple(labels)

    def summary(self) -> dict[str, Any]:
        return {
            "system": self.system.name,
            "roots": len(self.root_path_ids),
            "raw_paths": len(self.paths),
            "quotient_nodes": len(self.nodes),
            "quotient_edges": len(self.edges),
            "invalid_attempts": len(self.invalid_attempts),
            "raw_counts": self.raw_counts(),
            "quotient_counts": self.quotient_counts(),
            "new_node_counts": self.new_node_counts(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary(),
            "nodes": [
                {
                    "id": node.id,
                    "key": repr(node.key),
                    "state": self.system.serialize_state(node.state),
                    "min_depth": node.min_depth,
                    "first_parent": node.first_parent,
                    "first_direction": node.first_direction.label() if node.first_direction else None,
                    "path_cost": node.path_cost,
                    "invariants": dict(node.invariants),
                    "shortest_path": list(self.shortest_path_labels(node.id)),
                }
                for node in sorted(self.nodes.values(), key=lambda item: item.id)
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "direction": edge.direction.label(),
                    "first_depth": edge.first_depth,
                    "multiplicity": edge.multiplicity,
                    "cost": edge.direction.cost,
                }
                for edge in sorted(
                    self.edges.values(), key=lambda item: (item.first_depth, item.source, item.target)
                )
            ],
            "invalid_attempts": self.invalid_attempts,
        }

    def export(self, directory: str | Path) -> None:
        out = Path(directory)
        out.mkdir(parents=True, exist_ok=True)
        (out / "forest.json").write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        with (out / "nodes.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "id",
                    "min_depth",
                    "first_parent",
                    "first_direction",
                    "path_cost",
                    "state",
                    "invariants",
                    "shortest_path",
                ],
            )
            writer.writeheader()
            for node in sorted(self.nodes.values(), key=lambda item: item.id):
                writer.writerow(
                    {
                        "id": node.id,
                        "min_depth": node.min_depth,
                        "first_parent": node.first_parent,
                        "first_direction": node.first_direction.label() if node.first_direction else "",
                        "path_cost": node.path_cost,
                        "state": json.dumps(self.system.serialize_state(node.state)),
                        "invariants": json.dumps(dict(node.invariants), sort_keys=True),
                        "shortest_path": " -> ".join(self.shortest_path_labels(node.id)),
                    }
                )
        with (out / "edges.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["source", "target", "direction", "first_depth", "multiplicity", "cost"],
            )
            writer.writeheader()
            for edge in sorted(
                self.edges.values(), key=lambda item: (item.first_depth, item.source, item.target)
            ):
                writer.writerow(
                    {
                        "source": edge.source,
                        "target": edge.target,
                        "direction": edge.direction.label(),
                        "first_depth": edge.first_depth,
                        "multiplicity": edge.multiplicity,
                        "cost": edge.direction.cost,
                    }
                )


def reconstruct_path(paths: dict[int, PathRecord], path_id: int) -> tuple[str, ...]:
    labels: list[str] = []
    current = paths[path_id]
    while current.parent_path_id is not None:
        if current.direction is not None:
            labels.append(current.direction.label())
        current = paths[current.parent_path_id]
    labels.reverse()
    return tuple(labels)
