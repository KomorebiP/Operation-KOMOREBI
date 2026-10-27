from __future__ import annotations

from komorebi_arc3_offline.mock_env import OfflineMockFactory
from komorebi_arc3_offline.packetizer import FramePacketizer
from komorebi_arc3_offline.replay import replay_history
from komorebi_arc3_offline.types import ActionCandidate


def test_replay_reconstructs_deterministic_state() -> None:
    factory = OfflineMockFactory()
    packetizer = FramePacketizer()
    history = [ActionCandidate(2, role=("simple", 2))]
    first = replay_history(factory, history, packetizer)
    second = replay_history(factory, history, packetizer, expected_signature=first.packets.signature)
    assert second.matched_signature
    assert first.observation.levels_completed == 1
    assert first.packets.signature == second.packets.signature
