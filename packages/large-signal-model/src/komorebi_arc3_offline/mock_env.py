from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .types import ActionCandidate, ArcObservation, EpisodeState


class MockAction:
    def __init__(self, value: int, complex_action: bool = False) -> None:
        self.value = int(value)
        self._complex = bool(complex_action)

    def is_complex(self) -> bool:
        return self._complex


class OfflineMockEnvironment:
    """Small deterministic environment used only for package smoke tests.

    The red marker must be moved right twice and then clicked.  It exercises
    simple actions, a complex coordinate action, level progress, replay, and
    the offline agent loop without exposing any ARC-AGI-3 benchmark source.
    """

    game_id = "km00-local-smoke"

    def __init__(self) -> None:
        self.position = 1
        self.levels = 0
        self.state = EpisodeState.NOT_PLAYED
        self.actions = 0
        self.action_space: Sequence[MockAction] = (
            MockAction(1),
            MockAction(2),
            MockAction(6, True),
        )

    def _frame(self) -> np.ndarray:
        frame = np.zeros((64, 64), dtype=np.int16)
        frame[24:40, 8:56] = 1
        x = 12 + 16 * self.position
        frame[28:36, x : x + 8] = 2
        frame[4:12, 4:12] = 3 if self.levels == 0 else 4
        return frame

    def _observation(self) -> ArcObservation:
        return ArcObservation(
            game_id=self.game_id,
            frame=self._frame(),
            state=self.state,
            levels_completed=self.levels,
            win_levels=2,
            available_actions=(1, 2, 6),
            action_count=self.actions,
        )

    def reset(self) -> ArcObservation:
        self.position = 1
        self.levels = 0
        self.state = EpisodeState.NOT_FINISHED
        self.actions = 0
        return self._observation()

    def step(self, action: ActionCandidate) -> ArcObservation:
        self.actions += 1
        if action.action_id == 1:
            self.position = max(0, self.position - 1)
        elif action.action_id == 2:
            old_position = self.position
            self.position = min(2, self.position + 1)
            if old_position < 2 and self.position == 2:
                self.levels = max(self.levels, 1)
        elif action.action_id == 6:
            x = int(action.data.get("x", -1))
            y = int(action.data.get("y", -1))
            target_x = 12 + 16 * self.position + 4
            if self.position == 2 and abs(x - target_x) <= 8 and 24 <= y <= 40:
                self.levels = 2
                self.state = EpisodeState.WIN
            elif abs(x - target_x) > 20:
                self.state = EpisodeState.GAME_OVER
        return self._observation()


@dataclass
class OfflineMockFactory:
    game_id: str = OfflineMockEnvironment.game_id

    def create(self) -> OfflineMockEnvironment:
        return OfflineMockEnvironment()
