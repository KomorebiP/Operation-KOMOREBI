from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

from .types import ActionCandidate

ActionIdentity = tuple[int, tuple[tuple[str, int], ...], tuple[object, ...]]


@dataclass
class TransitionStats:
    source: str
    action: ActionIdentity
    target: str
    reward_sum: float = 0.0
    level_delta_sum: int = 0
    wins: int = 0
    losses: int = 0
    visits: int = 0

    def update(self, reward: float, level_delta: int, terminal_win: bool, terminal_loss: bool) -> None:
        self.reward_sum += float(reward)
        self.level_delta_sum += int(level_delta)
        self.wins += int(terminal_win)
        self.losses += int(terminal_loss)
        self.visits += 1

    @property
    def mean_reward(self) -> float:
        return self.reward_sum / max(1, self.visits)

    @property
    def mean_progress(self) -> float:
        return self.level_delta_sum / max(1, self.visits)


@dataclass
class StateTransitionGraph:
    """Exact deterministic transition memory with frontier queries."""

    nodes: set[str] = field(default_factory=set)
    edges: dict[tuple[str, ActionIdentity], TransitionStats] = field(default_factory=dict)
    incoming: dict[str, set[tuple[str, ActionIdentity]]] = field(
        default_factory=lambda: defaultdict(set)
    )
    candidate_actions: dict[str, set[ActionIdentity]] = field(
        default_factory=lambda: defaultdict(set)
    )

    def register_state(self, signature: str, candidates: Iterable[ActionCandidate] = ()) -> None:
        self.nodes.add(signature)
        self.candidate_actions[signature].update(candidate.identity() for candidate in candidates)

    def record(
        self,
        source: str,
        action: ActionCandidate,
        target: str,
        *,
        reward: float,
        level_delta: int,
        terminal_win: bool,
        terminal_loss: bool,
    ) -> TransitionStats:
        self.nodes.update([source, target])
        identity = action.identity()
        key = (source, identity)
        existing = self.edges.get(key)
        if existing is None:
            existing = TransitionStats(source, identity, target)
            self.edges[key] = existing
            self.incoming[target].add(key)
        elif existing.target != target:
            # The model can still represent stochasticity, but a replay planner
            # must not treat this action as a deterministic edge.
            self.incoming[existing.target].discard(key)
            existing.target = "<nondeterministic>"
        existing.update(reward, level_delta, terminal_win, terminal_loss)
        return existing

    def known_outcome(self, source: str, action: ActionCandidate) -> TransitionStats | None:
        value = self.edges.get((source, action.identity()))
        if value is None or value.target == "<nondeterministic>":
            return None
        return value

    def untried_actions(self, signature: str, candidates: Sequence[ActionCandidate]) -> list[ActionCandidate]:
        tried = {identity for state, identity in self.edges if state == signature}
        return [candidate for candidate in candidates if candidate.identity() not in tried]

    def adjacency(self) -> dict[str, list[tuple[str, ActionIdentity]]]:
        result: dict[str, list[tuple[str, ActionIdentity]]] = defaultdict(list)
        for (source, action), stats in self.edges.items():
            if stats.target != "<nondeterministic>" and not stats.losses:
                result[source].append((stats.target, action))
        return result

    def shortest_path(self, source: str, targets: set[str]) -> list[ActionIdentity] | None:
        if source in targets:
            return []
        adjacency = self.adjacency()
        queue = deque([source])
        parent: dict[str, tuple[str, ActionIdentity]] = {}
        seen = {source}
        while queue:
            state = queue.popleft()
            for target, action in adjacency.get(state, []):
                if target in seen:
                    continue
                parent[target] = (state, action)
                if target in targets:
                    path: list[ActionIdentity] = []
                    cursor = target
                    while cursor != source:
                        previous, edge_action = parent[cursor]
                        path.append(edge_action)
                        cursor = previous
                    return list(reversed(path))
                seen.add(target)
                queue.append(target)
        return None

    def frontier_states(self) -> set[str]:
        return {
            state
            for state in self.nodes
            if self.candidate_actions.get(state, set())
            - {identity for source, identity in self.edges if source == state}
        }

    def path_to_frontier(self, source: str) -> list[ActionIdentity] | None:
        return self.shortest_path(source, self.frontier_states())

    def winning_action(self, source: str) -> ActionIdentity | None:
        candidates = [
            stats
            for (state, _), stats in self.edges.items()
            if state == source and stats.wins == stats.visits and stats.visits > 0
            and not stats.losses and stats.target != "<nondeterministic>"
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda value: (value.wins, value.mean_reward)).action

    def progressing_action(self, source: str) -> ActionIdentity | None:
        candidates = [
            stats
            for (state, _), stats in self.edges.items()
            if state == source and stats.level_delta_sum > 0 and not stats.losses
            and stats.target != "<nondeterministic>"
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda value: (value.mean_progress, value.mean_reward)).action

    def summary(self) -> dict[str, int]:
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "frontier_states": len(self.frontier_states()),
            "nondeterministic_edges": sum(value.target == "<nondeterministic>" for value in self.edges.values()),
        }


__all__ = ["ActionIdentity", "StateTransitionGraph", "TransitionStats"]
