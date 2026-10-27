from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np

from .types import ActionCandidate, FloatArray, FramePackets, TransitionRecord


@dataclass
class RoleStatistics:
    count: int = 0
    reward_sum: float = 0.0
    progress_sum: float = 0.0
    wins: int = 0
    losses: int = 0
    changes: int = 0

    def update(self, record: TransitionRecord) -> None:
        self.count += 1
        self.reward_sum += float(record.reward)
        self.progress_sum += float(record.level_delta)
        self.wins += int(record.terminal_win)
        self.losses += int(record.terminal_loss)
        self.changes += int(record.changed)

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
class TransitionMemory:
    maximum_records: int = 512
    records: list[TransitionRecord] = field(default_factory=list)
    committed_coarse: list[FloatArray] = field(default_factory=list)
    committed_fine: list[FloatArray] = field(default_factory=list)
    signatures: Counter[str] = field(default_factory=Counter)
    role_statistics: dict[tuple[object, ...], RoleStatistics] = field(
        default_factory=lambda: defaultdict(RoleStatistics)
    )

    def initialize(self, packets: FramePackets) -> None:
        if not self.committed_coarse:
            self.committed_coarse.append(np.asarray(packets.coarse, dtype=float).copy())
            self.committed_fine.append(np.asarray(packets.fine, dtype=float).copy())
            self.signatures[packets.signature] += 1

    @staticmethod
    def _power_memory(states: Sequence[FloatArray], exponent: float = 0.72, horizon: int = 24) -> FloatArray | None:
        if len(states) <= 1:
            return None
        history = np.asarray(states[max(0, len(states) - horizon - 1) : -1][::-1], dtype=float)
        if history.size == 0:
            return None
        lags = np.arange(1, history.shape[0] + 1, dtype=float)
        weights = lags ** (-exponent)
        weights /= weights.sum()
        return weights @ history

    @staticmethod
    def _exponential_memory(states: Sequence[FloatArray], decay: float = 0.78, horizon: int = 32) -> FloatArray | None:
        if len(states) <= 1:
            return None
        history = np.asarray(states[max(0, len(states) - horizon - 1) : -1][::-1], dtype=float)
        if history.size == 0:
            return None
        weights = decay ** np.arange(history.shape[0], dtype=float)
        weights /= weights.sum()
        return weights @ history

    def context(self, resolution: str) -> tuple[FloatArray | None, FloatArray | None, FloatArray | None]:
        states = self.committed_coarse if resolution == "coarse" else self.committed_fine
        previous = None if len(states) < 2 else np.asarray(states[-2], dtype=float)
        return previous, self._power_memory(states), self._exponential_memory(states)

    def make_record(
        self,
        *,
        before: FramePackets,
        after: FramePackets,
        action_features: FloatArray,
        candidate: ActionCandidate,
        reward: float,
        level_delta: int,
        terminal_win: bool,
        terminal_loss: bool,
        step_index: int,
        source: str,
    ) -> TransitionRecord:
        previous_coarse, power_coarse, exponential_coarse = self.context("coarse")
        previous_fine, power_fine, exponential_fine = self.context("fine")
        return TransitionRecord(
            before_coarse=np.asarray(before.coarse, dtype=float).copy(),
            before_fine=np.asarray(before.fine, dtype=float).copy(),
            after_coarse=np.asarray(after.coarse, dtype=float).copy(),
            after_fine=np.asarray(after.fine, dtype=float).copy(),
            action_features=np.asarray(action_features, dtype=float).copy(),
            action_id=int(candidate.action_id),
            role=tuple(candidate.role),
            reward=float(reward),
            level_delta=int(level_delta),
            changed=before.signature != after.signature,
            terminal_win=bool(terminal_win),
            terminal_loss=bool(terminal_loss),
            step_index=int(step_index),
            source=str(source),
            previous_coarse=None if previous_coarse is None else previous_coarse.copy(),
            previous_fine=None if previous_fine is None else previous_fine.copy(),
            power_memory_coarse=None if power_coarse is None else power_coarse.copy(),
            power_memory_fine=None if power_fine is None else power_fine.copy(),
            exponential_memory_coarse=None if exponential_coarse is None else exponential_coarse.copy(),
            exponential_memory_fine=None if exponential_fine is None else exponential_fine.copy(),
        )

    def add(self, record: TransitionRecord, *, after_packets: FramePackets | None = None) -> None:
        self.records.append(record)
        if len(self.records) > self.maximum_records:
            del self.records[: len(self.records) - self.maximum_records]
        self.role_statistics[record.role].update(record)
        if record.source == "committed" and after_packets is not None:
            self.committed_coarse.append(np.asarray(after_packets.coarse, dtype=float).copy())
            self.committed_fine.append(np.asarray(after_packets.fine, dtype=float).copy())
            self.signatures[after_packets.signature] += 1
            if len(self.committed_coarse) > self.maximum_records + 1:
                del self.committed_coarse[: len(self.committed_coarse) - self.maximum_records - 1]
                del self.committed_fine[: len(self.committed_fine) - self.maximum_records - 1]

    def role_score(self, role: tuple[object, ...]) -> float:
        stats = self.role_statistics.get(role)
        if stats is None:
            return 0.0
        return (
            120.0 * stats.success_rate
            + 12.0 * stats.mean_reward
            + 2.0 * stats.change_rate
            - 20.0 * stats.losses / max(1, stats.count)
        )

    def novelty(self, signature: str) -> float:
        return 1.0 / (1.0 + float(self.signatures[signature]))

    def recent_roles(self, count: int = 12) -> tuple[tuple[object, ...], ...]:
        return tuple(record.role for record in self.records[-count:] if record.source == "committed")

    def state_history(self, resolution: str) -> list[FloatArray]:
        return list(self.committed_coarse if resolution == "coarse" else self.committed_fine)
