from __future__ import annotations

import numpy as np

from komorebi_arc3_offline.packetizer import FramePacketizer


def test_packetizer_is_deterministic_and_nested() -> None:
    frame = np.zeros((64, 64), dtype=np.int16)
    frame[10:20, 12:28] = 2
    frame[40:55, 45:60] = 4
    previous = frame.copy()
    previous[40:55, 45:60] = 0
    packetizer = FramePacketizer()
    first = packetizer.resolve(frame, previous)
    second = packetizer.resolve(frame, previous)
    assert first.coarse.shape == (24,)
    assert first.fine.shape == (48,)
    assert np.allclose(first.coarse, second.coarse)
    assert np.allclose(first.fine, second.fine)
    assert first.signature == second.signature
    assert len(first.components) == 2
    assert first.change_fraction > 0
    assert len(first.phase2_energy) == 4
    assert len(first.phase4_energy) == 16
