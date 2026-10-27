from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .offline_guard import assert_offline_guard, install_offline_guard
from .types import ActionCandidate, ArcObservation, EpisodeState, OfflineEnvironment


def _latest_frame(observation: Any) -> np.ndarray:
    if observation is None:
        return np.zeros((64, 64), dtype=np.int16)
    frames = getattr(observation, "frame", None)
    if frames is None:
        return np.zeros((64, 64), dtype=np.int16)
    if isinstance(frames, np.ndarray):
        if frames.ndim == 2:
            return frames.astype(np.int16, copy=False)
        if frames.ndim >= 3:
            return np.asarray(frames[-1], dtype=np.int16)
    try:
        if len(frames):
            return np.asarray(frames[-1], dtype=np.int16)
    except Exception:
        pass
    return np.zeros((64, 64), dtype=np.int16)


class OfficialOfflineEnvironment:
    def __init__(self, wrapper: Any, game_id: str) -> None:
        self._wrapper = wrapper
        self.game_id = game_id
        self._last: ArcObservation | None = None

    @property
    def action_space(self) -> Sequence[Any]:
        value = getattr(self._wrapper, "action_space", ())
        try:
            return tuple(value)
        except Exception:
            return ()

    def _convert(self, raw: Any) -> ArcObservation:
        available = getattr(raw, "available_actions", ()) if raw is not None else ()
        return ArcObservation(
            game_id=self.game_id,
            frame=_latest_frame(raw),
            state=EpisodeState.from_value(getattr(raw, "state", EpisodeState.UNKNOWN)),
            levels_completed=int(getattr(raw, "levels_completed", 0) or 0),
            win_levels=int(getattr(raw, "win_levels", 0) or 0),
            available_actions=tuple(int(getattr(action, "value", action)) for action in available),
            action_count=int(getattr(raw, "action_count", 0) or 0),
        )

    def reset(self) -> ArcObservation:
        raw = self._wrapper.reset()
        self._last = self._convert(raw)
        return self._last

    def step(self, action: ActionCandidate) -> ArcObservation:
        from arcengine import GameAction

        game_action = GameAction.from_id(int(action.action_id))
        reasoning = {
            "offline": True,
            "role": [str(value) for value in action.role],
            "source": action.source,
        }
        raw = self._wrapper.step(game_action, data=dict(action.data), reasoning=reasoning)
        self._last = self._convert(raw)
        return self._last


@dataclass
class OfficialOfflineFactory:
    game_id: str
    environments_dir: Path
    seed: int = 0
    recordings_dir: Path | None = None
    save_recording: bool = True
    logger: logging.Logger | None = None

    def __post_init__(self) -> None:
        install_offline_guard(strict=True)
        assert_offline_guard()
        self.environments_dir = Path(self.environments_dir).expanduser().resolve()
        if not self.environments_dir.exists():
            raise FileNotFoundError(
                f"local ARC-AGI-3 environment directory does not exist: {self.environments_dir}"
            )
        if self.recordings_dir is None:
            self.recordings_dir = self.environments_dir.parent / "recordings"
        self.recordings_dir = Path(self.recordings_dir).expanduser().resolve()
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        try:
            from arc_agi import Arcade, OperationMode
        except Exception as exc:
            raise RuntimeError(
                "arc-agi 0.9.9 and arcengine 0.9.3 are required. "
                "Run Setup_Conda_OnlineOnce.ps1 or install from a prepared wheelhouse."
            ) from exc
        self._arcade = Arcade(
            arc_api_key="",
            operation_mode=OperationMode.OFFLINE,
            environments_dir=str(self.environments_dir),
            recordings_dir=str(self.recordings_dir),
            logger=self.logger,
        )
        if getattr(self._arcade, "operation_mode", None) != OperationMode.OFFLINE:
            raise RuntimeError("official toolkit did not remain in OFFLINE mode")

    def create(self) -> OfficialOfflineEnvironment:
        wrapper = self._arcade.make(
            self.game_id,
            seed=int(self.seed),
            save_recording=bool(self.save_recording),
            include_frame_data=True,
            render_mode=None,
        )
        if wrapper is None:
            available = sorted(
                str(getattr(item, "game_id", ""))
                for item in self._arcade.get_environments()
            )
            raise RuntimeError(
                f"could not create local game {self.game_id!r}; available local games: {available}"
            )
        return OfficialOfflineEnvironment(wrapper, self.game_id)

    def list_games(self) -> list[dict[str, Any]]:
        output = []
        for item in self._arcade.get_environments():
            output.append(
                {
                    "game_id": str(getattr(item, "game_id", "")),
                    "title": str(getattr(item, "title", "") or ""),
                    "baseline_actions": list(getattr(item, "baseline_actions", []) or []),
                    "local_dir": str(getattr(item, "local_dir", "") or ""),
                }
            )
        return sorted(output, key=lambda row: row["game_id"])
