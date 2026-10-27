from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from .lasm_memory import LASMMemory
from .lasm_types import LASMFramePackets, LASMTransition
from .types import FloatArray


@dataclass(frozen=True)
class LASMProgram:
    name: str
    family: str
    resolution: str
    atlas: str
    complexity_weight: float = 1.0
    state_rank: int = 72
    atlas_rank: int = 24
    interaction_rank: int = 8
    phase_modulus: int = 1

    @property
    def mechanism_count(self) -> int:
        return {
            "linear": 0,
            "quadratic": 1,
            "bilinear": 1,
            "delay": 1,
            "fractional": 1,
            "volterra": 1,
            "phase": 1,
            "gated": 2,
            "hybrid": 4,
        }.get(self.family, 1)

    @staticmethod
    def _fixed_prefix(values: FloatArray, length: int) -> FloatArray:
        source = np.asarray(values, dtype=np.float64).ravel()
        output = np.zeros(length, dtype=np.float64)
        count = min(length, source.size)
        output[:count] = source[:count]
        return output

    def state(self, packets: LASMFramePackets) -> FloatArray:
        return self._fixed_prefix(packets.state(self.resolution), self.state_rank)

    def atlas_features(self, packets: LASMFramePackets) -> FloatArray:
        if self.atlas == "portfolio":
            values = np.concatenate([packets.feature_groups[name] for name in sorted(packets.feature_groups)])
        else:
            values = packets.feature_groups[self.atlas]
        return self._fixed_prefix(values, self.atlas_rank)

    @staticmethod
    def _quadratic(values: FloatArray, rank: int) -> FloatArray:
        q = np.asarray(values[: min(rank, values.size)], dtype=np.float64)
        return np.asarray([q[i] * q[j] for i in range(q.size) for j in range(i, q.size)], dtype=np.float64)

    def design_row(
        self,
        packets: LASMFramePackets,
        action_features: FloatArray,
        *,
        step_index: int,
        previous: FloatArray | None = None,
        power_memory: FloatArray | None = None,
        exponential_memory: FloatArray | None = None,
    ) -> FloatArray:
        state = self.state(packets)
        atlas = self.atlas_features(packets)
        action = np.asarray(action_features, dtype=np.float64)
        features: list[float] = [1.0]
        features.extend(state.tolist())
        features.extend(atlas.tolist())
        features.extend(action.tolist())

        rank = min(self.interaction_rank, state.size)
        action_coordinates = action[8:10] if action.size >= 10 else action[:2]

        if self.family in {"quadratic", "hybrid"}:
            features.extend(self._quadratic(state, rank).tolist())
            features.extend(self._quadratic(atlas, min(rank, atlas.size)).tolist())

        if self.family in {"bilinear", "gated", "hybrid"}:
            for value in state[:rank]:
                features.extend((value * action_coordinates).tolist())
            for value in atlas[:rank]:
                features.extend((value * action_coordinates).tolist())

        if self.family in {"delay", "hybrid"}:
            lag = np.zeros_like(state) if previous is None else self._fixed_prefix(previous, self.state_rank)
            features.extend(lag.tolist())
            if self.family == "hybrid":
                features.extend((state[:rank] * lag[:rank]).tolist())

        if self.family in {"fractional", "hybrid"}:
            memory = np.zeros_like(state) if power_memory is None else self._fixed_prefix(power_memory, self.state_rank)
            features.extend(memory.tolist())

        if self.family in {"volterra", "hybrid"}:
            memory = np.zeros_like(state) if exponential_memory is None else self._fixed_prefix(exponential_memory, self.state_rank)
            features.extend(memory.tolist())
            if self.family == "hybrid":
                features.extend((state[:rank] * memory[:rank]).tolist())

        if self.family == "phase":
            modulus = max(2, self.phase_modulus)
            phase = np.eye(modulus, dtype=float)[int(step_index) % modulus]
            features.extend(phase.tolist())
            for value in state[:rank]:
                features.extend((value * phase).tolist())

        if self.family == "gated":
            # A smooth gate allows different linear regimes without using a
            # discontinuous target-dependent rule.
            gate_argument = float(np.mean(atlas[: max(1, min(8, atlas.size))]))
            gate = 1.0 / (1.0 + np.exp(-4.0 * gate_argument))
            features.append(gate)
            features.extend((gate * state).tolist())
            features.extend(((1.0 - gate) * state).tolist())

        return np.asarray(features, dtype=np.float64)

    def design_transition(self, transition: LASMTransition) -> FloatArray:
        return self.design_row(
            transition.before,
            transition.action_features,
            step_index=transition.step_index,
            previous=transition.previous_states.get(self.resolution),
            power_memory=transition.power_memory.get(self.resolution),
            exponential_memory=transition.exponential_memory.get(self.resolution),
        )

    def targets(self, transition: LASMTransition) -> FloatArray:
        # The learned target is the same fixed-rank state used by the program,
        # not the full exact coordinate archive.
        before = self.state(transition.before)
        after = self.state(transition.after)
        scalar = np.asarray(
            [
                transition.reward / 100.0,
                float(transition.level_delta),
                float(transition.terminal_win),
                float(transition.terminal_loss),
                float(transition.changed),
            ],
            dtype=np.float64,
        )
        return np.concatenate([after - before, scalar])

    def complexity(self, feature_count: int, output_count: int) -> float:
        return float(self.complexity_weight * feature_count * np.sqrt(max(1, output_count)))


def default_lasm_programs() -> tuple[LASMProgram, ...]:
    programs: list[LASMProgram] = []
    # Atlas-matched linear experts: the posterior can select the coordinate
    # system in which the transition is most economical.
    for atlas in ("spatial", "color", "fourier", "haar", "polyphase2", "polyphase4", "portfolio"):
        programs.append(
            LASMProgram(
                name=f"linear-macro-{atlas}",
                family="linear",
                resolution="macro",
                atlas=atlas,
                state_rank=48,
                atlas_rank=24,
            )
        )
        programs.append(
            LASMProgram(
                name=f"linear-meso-{atlas}",
                family="linear",
                resolution="meso",
                atlas=atlas,
                state_rank=72,
                atlas_rank=32,
                complexity_weight=1.05,
            )
        )

    programs.extend(
        [
            LASMProgram("quadratic-spatial", "quadratic", "meso", "spatial", 1.08, 72, 32, 8),
            LASMProgram("quadratic-haar", "quadratic", "meso", "haar", 1.06, 72, 29, 8),
            LASMProgram("bilinear-color-action", "bilinear", "macro", "color", 1.02, 48, 32, 10),
            LASMProgram("bilinear-spatial-action", "bilinear", "meso", "spatial", 1.05, 72, 32, 10),
            LASMProgram("delay-portfolio", "delay", "macro", "portfolio", 1.02, 48, 32, 8),
            LASMProgram("fractional-fourier", "fractional", "macro", "fourier", 1.04, 48, 32, 8),
            LASMProgram("fractional-portfolio", "fractional", "meso", "portfolio", 1.08, 72, 32, 8),
            LASMProgram("volterra-portfolio", "volterra", "macro", "portfolio", 1.04, 48, 32, 8),
            LASMProgram("phase2-polyphase", "phase", "macro", "polyphase2", 1.01, 48, 12, 8, 2),
            LASMProgram("phase4-polyphase", "phase", "macro", "polyphase4", 1.02, 48, 32, 8, 4),
            LASMProgram("gated-color", "gated", "macro", "color", 1.10, 48, 32, 8),
            LASMProgram("hybrid-portfolio", "hybrid", "meso", "portfolio", 1.18, 72, 32, 6),
        ]
    )
    return tuple(programs)


__all__ = ["LASMProgram", "default_lasm_programs"]
