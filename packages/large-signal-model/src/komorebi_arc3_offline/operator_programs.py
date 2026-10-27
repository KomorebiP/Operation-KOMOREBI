from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from .types import FloatArray, TransitionRecord


@dataclass(frozen=True)
class OperatorProgram:
    name: str
    family: str
    resolution: str
    complexity_weight: float
    quadratic_rank: int = 6
    phase_modulus: int = 1

    @property
    def mechanism_count(self) -> int:
        return {
            "linear": 0,
            "quadratic": 1,
            "delay": 1,
            "fractional": 1,
            "volterra": 1,
            "phase": 1,
            "hybrid": 3,
        }.get(self.family, 1)

    def _state(self, record: TransitionRecord) -> FloatArray:
        return record.state_before(self.resolution)

    def _previous(self, record: TransitionRecord) -> FloatArray:
        value = record.previous_coarse if self.resolution == "coarse" else record.previous_fine
        return np.zeros_like(self._state(record)) if value is None else np.asarray(value, dtype=float)

    def _power_memory(self, record: TransitionRecord) -> FloatArray:
        value = record.power_memory_coarse if self.resolution == "coarse" else record.power_memory_fine
        return np.zeros_like(self._state(record)) if value is None else np.asarray(value, dtype=float)

    def _exponential_memory(self, record: TransitionRecord) -> FloatArray:
        value = record.exponential_memory_coarse if self.resolution == "coarse" else record.exponential_memory_fine
        return np.zeros_like(self._state(record)) if value is None else np.asarray(value, dtype=float)

    @staticmethod
    def _quadratic(values: FloatArray, rank: int) -> FloatArray:
        q = np.asarray(values[: min(rank, values.size)], dtype=float)
        terms = [q[i] * q[j] for i in range(q.size) for j in range(i, q.size)]
        return np.asarray(terms, dtype=float)

    def design_row(
        self,
        *,
        state: FloatArray,
        action_features: FloatArray,
        step_index: int,
        previous: FloatArray | None = None,
        power_memory: FloatArray | None = None,
        exponential_memory: FloatArray | None = None,
    ) -> FloatArray:
        current = np.asarray(state, dtype=float)
        action = np.asarray(action_features, dtype=float)
        features: list[float] = [1.0]
        features.extend(current.tolist())
        features.extend(action.tolist())

        if self.family in {"quadratic", "hybrid"}:
            features.extend(self._quadratic(current, self.quadratic_rank).tolist())
            # Interactions with the spatial coordinate part of the action make
            # click-dependent effects explicit without creating a huge tensor.
            coordinate = action[8:10] if action.size >= 10 else action[:2]
            for value in current[: self.quadratic_rank]:
                features.extend((value * coordinate).tolist())

        if self.family in {"delay", "hybrid"}:
            lag = np.zeros_like(current) if previous is None else np.asarray(previous, dtype=float)
            features.extend(lag.tolist())
            if self.family == "hybrid":
                features.extend((current[: self.quadratic_rank] * lag[: self.quadratic_rank]).tolist())

        if self.family in {"fractional", "hybrid"}:
            memory = np.zeros_like(current) if power_memory is None else np.asarray(power_memory, dtype=float)
            features.extend(memory.tolist())

        if self.family == "volterra":
            memory = np.zeros_like(current) if exponential_memory is None else np.asarray(exponential_memory, dtype=float)
            features.extend(memory.tolist())

        if self.family == "phase":
            modulus = max(2, self.phase_modulus)
            phase = int(step_index) % modulus
            one_hot = np.eye(modulus, dtype=float)[phase]
            features.extend(one_hot.tolist())
            for value in current[: self.quadratic_rank]:
                features.extend((value * one_hot).tolist())

        return np.asarray(features, dtype=np.float64)

    def design_record(self, record: TransitionRecord) -> FloatArray:
        return self.design_row(
            state=self._state(record),
            action_features=record.action_features,
            step_index=record.step_index,
            previous=self._previous(record),
            power_memory=self._power_memory(record),
            exponential_memory=self._exponential_memory(record),
        )

    def targets(self, record: TransitionRecord) -> FloatArray:
        before = record.state_before(self.resolution)
        after = record.state_after(self.resolution)
        delta = after - before
        scalars = np.asarray(
            [
                record.reward / 100.0,
                float(record.level_delta),
                float(record.terminal_win),
                float(record.terminal_loss),
                float(record.changed),
            ],
            dtype=float,
        )
        return np.concatenate([delta, scalars])

    def complexity(self, feature_count: int, output_count: int) -> float:
        return float(self.complexity_weight * feature_count * output_count)


def default_operator_programs() -> tuple[OperatorProgram, ...]:
    programs: list[OperatorProgram] = []
    for resolution in ("coarse", "fine"):
        programs.extend(
            [
                OperatorProgram(f"linear-{resolution}", "linear", resolution, 1.0),
                OperatorProgram(f"quadratic-{resolution}", "quadratic", resolution, 1.05),
                OperatorProgram(f"delay-{resolution}", "delay", resolution, 1.0),
                OperatorProgram(f"fractional-{resolution}", "fractional", resolution, 1.0),
                OperatorProgram(f"volterra-{resolution}", "volterra", resolution, 1.0),
                OperatorProgram(f"phase2-{resolution}", "phase", resolution, 1.0, phase_modulus=2),
                OperatorProgram(f"phase4-{resolution}", "phase", resolution, 1.0, phase_modulus=4),
            ]
        )
    programs.append(OperatorProgram("hybrid-fine", "hybrid", "fine", 1.15))
    return tuple(programs)
