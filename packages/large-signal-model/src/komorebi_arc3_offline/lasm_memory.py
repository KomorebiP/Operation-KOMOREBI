from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np

from .lasm_types import LASMFramePackets, LASMTransition
from .types import ActionCandidate, FloatArray


@dataclass
class LASMRoleStatistics:
    count: int = 0
    reward_sum: float = 0.0
    progress_sum: float = 0.0
    wins: int = 0
    losses: int = 0
    changes: int = 0

    def update(self, transition: LASMTransition) -> None:
        self.count += 1
        self.reward_sum += transition.reward
        self.progress_sum += transition.level_delta
        self.wins += int(transition.terminal_win)
        self.losses += int(transition.terminal_loss)
        self.changes += int(transition.changed)

    @property
    def mean_reward(self) -> float:
        return self.reward_sum / max(1, self.count)

    @property
    def success_rate(self) -> float:
        return self.wins / max(1, self.count)

    @property
    def change_rate(self) -> float:
        return self.changes / max(1, self.count)


@dataclass
class LASMMemory:
    maximum_records: int = 768
    records: list[LASMTransition] = field(default_factory=list)
    committed: dict[str, list[FloatArray]] = field(
        default_factory=lambda: {"macro": [], "meso": [], "micro": []}
    )
    signatures: Counter[str] = field(default_factory=Counter)
    role_statistics: dict[tuple[object, ...], LASMRoleStatistics] = field(
        default_factory=lambda: defaultdict(LASMRoleStatistics)
    )

    def initialize(self, packets: LASMFramePackets) -> None:
        if self.committed["macro"]:
            return
        for resolution in self.committed:
            self.committed[resolution].append(packets.state(resolution).copy())
        self.signatures[packets.signature] += 1

    @staticmethod
    def power_memory(states: Sequence[FloatArray], exponent: float = 0.68, horizon: int = 32) -> FloatArray | None:
        if len(states) <= 1:
            return None
        history = np.asarray(states[max(0, len(states) - horizon - 1) : -1][::-1], dtype=float)
        if history.size == 0:
            return None
        lag = np.arange(1, history.shape[0] + 1, dtype=float)
        weights = lag ** (-exponent)
        weights /= weights.sum()
        return weights @ history

    @staticmethod
    def exponential_memory(states: Sequence[FloatArray], decay: float = 0.82, horizon: int = 40) -> FloatArray | None:
        if len(states) <= 1:
            return None
        history = np.asarray(states[max(0, len(states) - horizon - 1) : -1][::-1], dtype=float)
        if history.size == 0:
            return None
        weights = decay ** np.arange(history.shape[0], dtype=float)
        weights /= weights.sum()
        return weights @ history

    def context(self, resolution: str) -> tuple[FloatArray | None, FloatArray | None, FloatArray | None]:
        states = self.committed[resolution]
        previous = None if len(states) < 2 else states[-2]
        return previous, self.power_memory(states), self.exponential_memory(states)

    def make_transition(
        self,
        *,
        before: LASMFramePackets,
        after: LASMFramePackets,
        action: ActionCandidate,
        action_features: FloatArray,
        reward: float,
        level_delta: int,
        terminal_win: bool,
        terminal_loss: bool,
        step_index: int,
    ) -> LASMTransition:
        previous: dict[str, FloatArray] = {}
        power: dict[str, FloatArray] = {}
        exponential: dict[str, FloatArray] = {}
        for resolution in self.committed:
            lag, long_memory, short_memory = self.context(resolution)
            if lag is not None:
                previous[resolution] = lag.copy()
            if long_memory is not None:
                power[resolution] = long_memory.copy()
            if short_memory is not None:
                exponential[resolution] = short_memory.copy()
        return LASMTransition(
            before=before,
            after=after,
            action=action,
            action_features=np.asarray(action_features, dtype=float).copy(),
            reward=float(reward),
            level_delta=int(level_delta),
            terminal_win=bool(terminal_win),
            terminal_loss=bool(terminal_loss),
            step_index=int(step_index),
            previous_states=previous,
            power_memory=power,
            exponential_memory=exponential,
        )

    def add(self, transition: LASMTransition, after_packets: LASMFramePackets | None = None) -> None:
        self.records.append(transition)
        if len(self.records) > self.maximum_records:
            del self.records[: len(self.records) - self.maximum_records]
        self.role_statistics[transition.action.role].update(transition)
        if after_packets is not None:
            for resolution in self.committed:
                self.committed[resolution].append(after_packets.state(resolution).copy())
                if len(self.committed[resolution]) > self.maximum_records + 1:
                    del self.committed[resolution][0]
            self.signatures[after_packets.signature] += 1

    def novelty(self, signature: str) -> float:
        return 1.0 / (1.0 + float(self.signatures[signature]))

    def role_score(self, role: tuple[object, ...]) -> float:
        stats = self.role_statistics.get(role)
        if stats is None:
            return 0.0
        return (
            160.0 * stats.success_rate
            + 10.0 * stats.mean_reward
            + 3.0 * stats.change_rate
            - 28.0 * stats.losses / max(1, stats.count)
        )


__all__ = ["LASMMemory", "LASMRoleStatistics"]
