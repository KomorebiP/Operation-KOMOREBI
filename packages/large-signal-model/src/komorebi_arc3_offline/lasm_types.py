from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np

from .exact_atlas import AtlasAnalysis
from .types import ActionCandidate, ArcObservation, FloatArray, FrameComponent


@dataclass(frozen=True)
class LASMFramePackets:
    """Complete PR-LASM observation record.

    ``analysis`` contains the exact multi-atlas coordinates.  ``raw`` and the
    three projected states are statistical summaries used by the learned world
    model.  They are intentionally not described as exact reconstructions.
    """

    macro: FloatArray
    meso: FloatArray
    micro: FloatArray
    raw: FloatArray
    feature_groups: Mapping[str, FloatArray]
    analysis: AtlasAnalysis
    signature: str
    background: int
    components: tuple[FrameComponent, ...]
    salient_points: tuple[tuple[int, int, str], ...]
    change_fraction: float
    non_background_fraction: float
    reconstruction_residuals: Mapping[str, float]

    def state(self, resolution: str) -> FloatArray:
        if resolution == "macro":
            return self.macro
        if resolution == "meso":
            return self.meso
        if resolution == "micro":
            return self.micro
        if resolution == "raw":
            return self.raw
        raise KeyError(resolution)


@dataclass(frozen=True)
class LASMTransition:
    before: LASMFramePackets
    after: LASMFramePackets
    action: ActionCandidate
    action_features: FloatArray
    reward: float
    level_delta: int
    terminal_win: bool
    terminal_loss: bool
    step_index: int
    previous_states: Mapping[str, FloatArray] = field(default_factory=dict)
    power_memory: Mapping[str, FloatArray] = field(default_factory=dict)
    exponential_memory: Mapping[str, FloatArray] = field(default_factory=dict)

    @property
    def changed(self) -> bool:
        return self.before.signature != self.after.signature

    def target(self, resolution: str) -> FloatArray:
        before = self.before.state(resolution)
        after = self.after.state(resolution)
        scalar = np.asarray(
            [
                self.reward / 100.0,
                float(self.level_delta),
                float(self.terminal_win),
                float(self.terminal_loss),
                float(self.changed),
            ],
            dtype=np.float64,
        )
        return np.concatenate([after - before, scalar])


@dataclass(frozen=True)
class LASMPrediction:
    expected_reward: float
    expected_progress: float
    win_probability: float
    loss_probability: float
    change_probability: float
    expected_change_norm: float
    predictive_variance: float
    model_disagreement: float
    information_score: float
    family_probabilities: Mapping[str, float]
    atlas_probabilities: Mapping[str, float]
    resolution_probabilities: Mapping[str, float]
    program_probabilities: Mapping[str, float]


@dataclass(frozen=True)
class GraphEdge:
    source_signature: str
    action_identity: tuple[int, tuple[tuple[str, int], ...], tuple[Any, ...]]
    target_signature: str
    reward: float
    level_delta: int
    terminal_win: bool
    terminal_loss: bool
    visits: int = 1


@dataclass(frozen=True)
class LASMRunTrace:
    observation: ArcObservation
    packets: LASMFramePackets
    action: ActionCandidate | None = None


__all__ = [
    "GraphEdge",
    "LASMFramePackets",
    "LASMPrediction",
    "LASMRunTrace",
    "LASMTransition",
]
