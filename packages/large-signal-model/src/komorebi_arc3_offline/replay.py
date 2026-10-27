from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .packetizer import FramePacketizer
from .types import ActionCandidate, ArcObservation, EnvironmentFactory, FramePackets


@dataclass(frozen=True)
class ReplayResult:
    environment: object
    observation: ArcObservation
    packets: FramePackets
    matched_signature: bool


def replay_history(
    factory: EnvironmentFactory,
    history: Sequence[ActionCandidate],
    packetizer: FramePacketizer,
    *,
    expected_signature: str | None = None,
) -> ReplayResult:
    environment = factory.create()
    observation = environment.reset()
    previous_frame = None
    packets = packetizer.resolve(observation.frame, previous_frame)
    previous_frame = observation.frame
    for action in history:
        observation = environment.step(action)
        packets = packetizer.resolve(observation.frame, previous_frame)
        previous_frame = observation.frame
        if observation.terminal:
            break
    matched = expected_signature is None or packets.signature == expected_signature
    return ReplayResult(environment, observation, packets, matched)
