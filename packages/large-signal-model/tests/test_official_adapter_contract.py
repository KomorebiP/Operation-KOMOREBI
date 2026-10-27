from __future__ import annotations

import sys
import types
from enum import Enum
from pathlib import Path

import numpy as np

from komorebi_arc3_offline.official_adapter import OfficialOfflineFactory
from komorebi_arc3_offline.types import ActionCandidate, EpisodeState


class FakeOperationMode(str, Enum):
    NORMAL = "normal"
    OFFLINE = "offline"


class FakeGameAction(Enum):
    RESET = 0
    ACTION1 = 1
    ACTION6 = 6

    @classmethod
    def from_id(cls, action_id: int) -> "FakeGameAction":
        return cls(action_id)


class FakeRaw:
    def __init__(self, action_count: int = 0) -> None:
        self.frame = [np.zeros((64, 64), dtype=np.int16)]
        self.state = "NOT_FINISHED"
        self.levels_completed = 0
        self.win_levels = 1
        self.available_actions = [1, 6]
        self.action_count = action_count


class FakeWrapper:
    action_space = (FakeGameAction.ACTION1, FakeGameAction.ACTION6)

    def __init__(self) -> None:
        self.calls: list[tuple[object, dict[str, int], dict[str, object]]] = []

    def reset(self) -> FakeRaw:
        return FakeRaw(0)

    def step(self, action, data=None, reasoning=None) -> FakeRaw:
        self.calls.append((action, dict(data or {}), dict(reasoning or {})))
        return FakeRaw(len(self.calls))


class FakeEnvironmentInfo:
    game_id = "zz00-local"
    title = "contract"
    baseline_actions = [4]
    local_dir = "local"


class FakeArcade:
    last_kwargs = None

    def __init__(self, **kwargs) -> None:
        type(self).last_kwargs = kwargs
        self.operation_mode = kwargs["operation_mode"]
        self.wrapper = FakeWrapper()

    def make(self, game_id: str, **kwargs):
        assert game_id == "zz00-local"
        assert kwargs["include_frame_data"] is True
        assert kwargs["render_mode"] is None
        return self.wrapper

    def get_environments(self):
        return [FakeEnvironmentInfo()]


def test_official_adapter_forces_offline_mode_and_public_actions(monkeypatch, tmp_path: Path) -> None:
    arc_agi = types.ModuleType("arc_agi")
    arc_agi.Arcade = FakeArcade
    arc_agi.OperationMode = FakeOperationMode
    arcengine = types.ModuleType("arcengine")
    arcengine.GameAction = FakeGameAction
    monkeypatch.setitem(sys.modules, "arc_agi", arc_agi)
    monkeypatch.setitem(sys.modules, "arcengine", arcengine)

    factory = OfficialOfflineFactory(
        "zz00-local",
        tmp_path,
        recordings_dir=tmp_path / "recordings",
        save_recording=True,
    )
    assert FakeArcade.last_kwargs["operation_mode"] is FakeOperationMode.OFFLINE
    assert FakeArcade.last_kwargs["arc_api_key"] == ""

    environment = factory.create()
    initial = environment.reset()
    assert initial.state is EpisodeState.NOT_FINISHED
    assert initial.available_actions == (1, 6)

    after = environment.step(
        ActionCandidate(6, data={"x": 17, "y": 23}, role=("point", 6), source="test")
    )
    assert after.action_count == 1
    action, data, reasoning = factory._arcade.wrapper.calls[-1]
    assert action is FakeGameAction.ACTION6
    assert data == {"x": 17, "y": 23}
    assert reasoning["offline"] is True
