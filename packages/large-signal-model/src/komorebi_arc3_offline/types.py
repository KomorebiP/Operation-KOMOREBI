from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IntFrame = NDArray[np.int16]


class EpisodeState(str, Enum):
    NOT_PLAYED = "NOT_PLAYED"
    NOT_FINISHED = "NOT_FINISHED"
    WIN = "WIN"
    GAME_OVER = "GAME_OVER"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_value(cls, value: Any) -> "EpisodeState":
        text = getattr(value, "value", value)
        text = str(text).split(".")[-1].upper()
        aliases = {
            "NOT_PLAYED": cls.NOT_PLAYED,
            "NOT_FINISHED": cls.NOT_FINISHED,
            "WIN": cls.WIN,
            "GAME_OVER": cls.GAME_OVER,
        }
        return aliases.get(text, cls.UNKNOWN)


@dataclass(frozen=True)
class ArcObservation:
    game_id: str
    frame: IntFrame
    state: EpisodeState
    levels_completed: int
    win_levels: int
    available_actions: tuple[int, ...]
    action_count: int = 0

    @property
    def terminal(self) -> bool:
        return self.state in {EpisodeState.WIN, EpisodeState.GAME_OVER}


@dataclass(frozen=True)
class ActionCandidate:
    action_id: int
    data: Mapping[str, int] = field(default_factory=dict)
    role: tuple[Any, ...] = field(default_factory=tuple)
    description: str = ""
    source: str = "action_space"

    def identity(self) -> tuple[int, tuple[tuple[str, int], ...], tuple[Any, ...]]:
        return self.action_id, tuple(sorted((str(k), int(v)) for k, v in self.data.items())), self.role


@dataclass(frozen=True)
class FrameComponent:
    color: int
    area: int
    bbox: tuple[int, int, int, int]
    centroid: tuple[float, float]
    compactness: float
    touches_border: bool

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0] + 1

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1] + 1

    @property
    def center_pixel(self) -> tuple[int, int]:
        return int(round(self.centroid[0])), int(round(self.centroid[1]))


@dataclass(frozen=True)
class FramePackets:
    coarse: FloatArray
    fine: FloatArray
    raw: FloatArray
    signature: str
    background: int
    components: tuple[FrameComponent, ...]
    salient_points: tuple[tuple[int, int, str], ...]
    change_fraction: float
    non_background_fraction: float
    phase2_energy: tuple[float, ...]
    phase4_energy: tuple[float, ...]

    def state(self, resolution: str) -> FloatArray:
        if resolution == "coarse":
            return self.coarse
        if resolution == "fine":
            return self.fine
        raise KeyError(f"unknown resolution {resolution!r}")


@dataclass(frozen=True)
class TransitionRecord:
    before_coarse: FloatArray
    before_fine: FloatArray
    after_coarse: FloatArray
    after_fine: FloatArray
    action_features: FloatArray
    action_id: int
    role: tuple[Any, ...]
    reward: float
    level_delta: int
    changed: bool
    terminal_win: bool
    terminal_loss: bool
    step_index: int
    source: str = "committed"
    previous_coarse: FloatArray | None = None
    previous_fine: FloatArray | None = None
    power_memory_coarse: FloatArray | None = None
    power_memory_fine: FloatArray | None = None
    exponential_memory_coarse: FloatArray | None = None
    exponential_memory_fine: FloatArray | None = None

    def state_before(self, resolution: str) -> FloatArray:
        return self.before_coarse if resolution == "coarse" else self.before_fine

    def state_after(self, resolution: str) -> FloatArray:
        return self.after_coarse if resolution == "coarse" else self.after_fine


@dataclass(frozen=True)
class Prediction:
    mean: FloatArray
    variance: FloatArray
    model_entropy: float
    family_probabilities: Mapping[str, float]
    resolution_probabilities: Mapping[str, float]


@dataclass(frozen=True)
class ActionScore:
    candidate: ActionCandidate
    predicted_reward: float
    progress_score: float
    novelty_score: float
    information_score: float
    uncertainty_penalty: float
    loop_penalty: float
    loss_risk: float
    total: float
    exact_probe: bool = False
    probe_observation: ArcObservation | None = None
    probe_packets: FramePackets | None = None


@dataclass(frozen=True)
class RunResult:
    game_id: str
    solved: bool
    final_state: str
    levels_completed: int
    win_levels: int
    committed_actions: int
    probe_actions: int
    resets: int
    elapsed_seconds: float
    model_updates: int
    output_dir: str
    notes: tuple[str, ...] = ()


class OfflineEnvironment(Protocol):
    game_id: str
    action_space: Sequence[Any]

    def reset(self) -> ArcObservation: ...

    def step(self, action: ActionCandidate) -> ArcObservation: ...


class EnvironmentFactory(Protocol):
    game_id: str

    def create(self) -> OfflineEnvironment: ...
