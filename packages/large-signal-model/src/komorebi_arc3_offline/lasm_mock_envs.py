from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .types import ActionCandidate, ArcObservation, EpisodeState


class _BaseSyntheticEnvironment:
    game_id = "lasm-base"
    action_space: tuple[int, ...] = (1, 2, 3, 4)

    def __init__(self) -> None:
        self.action_count = 0
        self.state = EpisodeState.NOT_FINISHED
        self.levels_completed = 0
        self.win_levels = 1

    def frame(self) -> np.ndarray:
        return np.zeros((64, 64), dtype=np.int16)

    def observation(self) -> ArcObservation:
        return ArcObservation(
            self.game_id,
            self.frame(),
            self.state,
            self.levels_completed,
            self.win_levels,
            self.action_space,
            self.action_count,
        )

    def reset(self) -> ArcObservation:
        self.__init__()
        return self.observation()


class SequenceEnvironment(_BaseSyntheticEnvironment):
    game_id = "lasm-sequence"
    sequence = (2, 4, 1, 3, 2)

    def __init__(self) -> None:
        super().__init__()
        self.index = 0

    def frame(self) -> np.ndarray:
        frame = np.zeros((64, 64), dtype=np.int16)
        for index, action in enumerate(self.sequence):
            color = 2 + action
            x0 = 5 + index * 11
            frame[8:18, x0 : x0 + 8] = color
            if index < self.index:
                frame[22:30, x0 : x0 + 8] = 9
        frame[44:54, 6 + self.index * 10 : 12 + self.index * 10] = 12
        return frame

    def step(self, action: ActionCandidate) -> ArcObservation:
        if self.state is EpisodeState.WIN:
            return self.observation()
        self.action_count += 1
        if int(action.action_id) == self.sequence[self.index]:
            self.index += 1
            self.levels_completed = self.index
            self.win_levels = len(self.sequence)
            if self.index == len(self.sequence):
                self.state = EpisodeState.WIN
        return self.observation()


class ClickTargetEnvironment(_BaseSyntheticEnvironment):
    game_id = "lasm-click-target"
    action_space = (6,)

    def __init__(self) -> None:
        super().__init__()
        self.target = (43, 19)

    def frame(self) -> np.ndarray:
        frame = np.zeros((64, 64), dtype=np.int16)
        x, y = self.target
        frame[y - 5 : y + 6, x - 5 : x + 6] = 6
        frame[2:6, 2:62] = 3
        return frame

    def step(self, action: ActionCandidate) -> ArcObservation:
        self.action_count += 1
        x = int(action.data.get("x", -100))
        y = int(action.data.get("y", -100))
        if int(action.action_id) == 6 and abs(x - self.target[0]) <= 6 and abs(y - self.target[1]) <= 6:
            self.levels_completed = 1
            self.state = EpisodeState.WIN
        return self.observation()


class GridNavigationEnvironment(_BaseSyntheticEnvironment):
    game_id = "lasm-grid-navigation"

    def __init__(self) -> None:
        super().__init__()
        self.position = [1, 1]
        self.target = (5, 4)
        self.walls = {(3, 1), (3, 2), (3, 3), (1, 4), (2, 4)}

    def frame(self) -> np.ndarray:
        frame = np.zeros((64, 64), dtype=np.int16)
        for cell_x, cell_y in self.walls:
            frame[6 + cell_y * 9 : 13 + cell_y * 9, 6 + cell_x * 9 : 13 + cell_x * 9] = 7
        tx, ty = self.target
        frame[6 + ty * 9 : 13 + ty * 9, 6 + tx * 9 : 13 + tx * 9] = 5
        px, py = self.position
        frame[7 + py * 9 : 12 + py * 9, 7 + px * 9 : 12 + px * 9] = 12
        return frame

    def step(self, action: ActionCandidate) -> ArcObservation:
        self.action_count += 1
        delta = {1: (0, -1), 2: (1, 0), 3: (0, 1), 4: (-1, 0)}.get(int(action.action_id), (0, 0))
        candidate = (self.position[0] + delta[0], self.position[1] + delta[1])
        if 0 <= candidate[0] <= 5 and 0 <= candidate[1] <= 5 and candidate not in self.walls:
            self.position[:] = candidate
        if tuple(self.position) == self.target:
            self.levels_completed = 1
            self.state = EpisodeState.WIN
        return self.observation()


class PhaseSwitchEnvironment(_BaseSyntheticEnvironment):
    game_id = "lasm-phase-switch"
    sequence = (1, 2, 1, 2, 1, 2)

    def __init__(self) -> None:
        super().__init__()
        self.phase = 0
        self.win_levels = len(self.sequence)

    def frame(self) -> np.ndarray:
        frame = np.zeros((64, 64), dtype=np.int16)
        frame[10:54, 10:30] = 3 if self.phase % 2 == 0 else 8
        frame[10:54, 34:54] = 8 if self.phase % 2 == 0 else 3
        frame[56:60, 4 : 4 + min(self.phase, 6) * 9] = 12
        return frame

    def step(self, action: ActionCandidate) -> ArcObservation:
        self.action_count += 1
        if int(action.action_id) == self.sequence[self.phase]:
            self.phase += 1
            self.levels_completed = self.phase
            if self.phase == len(self.sequence):
                self.state = EpisodeState.WIN
        return self.observation()


@dataclass(frozen=True)
class SyntheticFactory:
    environment_type: type[_BaseSyntheticEnvironment]

    @property
    def game_id(self) -> str:
        return self.environment_type.game_id

    def create(self) -> _BaseSyntheticEnvironment:
        return self.environment_type()


def benchmark_factories() -> tuple[SyntheticFactory, ...]:
    return tuple(
        SyntheticFactory(environment)
        for environment in (
            SequenceEnvironment,
            ClickTargetEnvironment,
            GridNavigationEnvironment,
            PhaseSwitchEnvironment,
        )
    )


__all__ = [
    "ClickTargetEnvironment",
    "GridNavigationEnvironment",
    "PhaseSwitchEnvironment",
    "SequenceEnvironment",
    "SyntheticFactory",
    "benchmark_factories",
]
