from __future__ import annotations

import numpy as np

from komorebi_arc3_offline.actions import ActionCandidateGenerator
from komorebi_arc3_offline.packetizer import FramePacketizer
from komorebi_arc3_offline.types import ArcObservation, EpisodeState


def test_action_candidates_include_simple_and_spatial_actions() -> None:
    frame = np.zeros((64, 64), dtype=np.int16)
    frame[20:32, 30:45] = 3
    observation = ArcObservation("test", frame, EpisodeState.NOT_FINISHED, 0, 1, (1, 2, 6))
    packets = FramePacketizer().resolve(frame)
    generator = ActionCandidateGenerator()
    candidates = generator.generate(observation, packets)
    assert {candidate.action_id for candidate in candidates} == {1, 2, 6}
    assert any(candidate.action_id == 6 and "x" in candidate.data for candidate in candidates)
    assert generator.features(candidates[0]).shape == (17,)
