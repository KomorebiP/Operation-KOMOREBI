from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from typing import Iterable, Sequence

import numpy as np

from .types import ActionCandidate, ArcObservation, FloatArray, FramePackets


@dataclass(frozen=True)
class CandidateConfig:
    maximum_candidates: int = 48
    complex_action_ids: tuple[int, ...] = (6,)
    action_id_count: int = 8
    role_hash_dimension: int = 4


class ActionCandidateGenerator:
    def __init__(self, config: CandidateConfig | None = None) -> None:
        self.config = config or CandidateConfig()

    @staticmethod
    def _role_source(source: str) -> str:
        if source.startswith("component"):
            return "component"
        if source.startswith("change"):
            return "change"
        if source.startswith("phase"):
            return "polyphase"
        if source == "center":
            return "center"
        return "boundary"

    def generate(
        self,
        observation: ArcObservation,
        packets: FramePackets,
        *,
        action_space: Sequence[object] | None = None,
    ) -> list[ActionCandidate]:
        ids = set(int(value) for value in observation.available_actions)
        if action_space is not None:
            for action in action_space:
                ids.add(int(getattr(action, "value", action)))
        ids.discard(0)
        candidates: list[ActionCandidate] = []
        complex_ids = set(self.config.complex_action_ids)
        for action_id in sorted(ids):
            if action_id not in complex_ids:
                candidates.append(
                    ActionCandidate(
                        action_id=action_id,
                        role=("simple", action_id),
                        description=f"action {action_id}",
                        source="action_space",
                    )
                )
                continue
            for x, y, source in packets.salient_points:
                role_source = self._role_source(source)
                candidates.append(
                    ActionCandidate(
                        action_id=action_id,
                        data={"x": int(x), "y": int(y)},
                        role=(
                            "point",
                            action_id,
                            role_source,
                            int(x) // 16,
                            int(y) // 16,
                        ),
                        description=f"action {action_id} at ({x},{y}) from {source}",
                        source=source,
                    )
                )
        unique: dict[tuple[object, ...], ActionCandidate] = {}
        for candidate in candidates:
            unique.setdefault(candidate.identity(), candidate)
        ordered = list(unique.values())
        ordered.sort(
            key=lambda candidate: (
                0 if candidate.role and candidate.role[0] == "simple" else 1,
                0 if candidate.source.startswith("component") else 1,
                0 if candidate.source.startswith("change") else 1,
                candidate.action_id,
                int(candidate.data.get("y", -1)),
                int(candidate.data.get("x", -1)),
            )
        )
        return ordered[: self.config.maximum_candidates]

    def features(self, candidate: ActionCandidate) -> FloatArray:
        size = self.config.action_id_count + 5 + self.config.role_hash_dimension
        vector = np.zeros(size, dtype=np.float64)
        action_index = int(np.clip(candidate.action_id, 0, self.config.action_id_count - 1))
        vector[action_index] = 1.0
        x = float(candidate.data.get("x", 31.5)) / 63.0
        y = float(candidate.data.get("y", 31.5)) / 63.0
        offset = self.config.action_id_count
        vector[offset : offset + 5] = [x, y, x * x, y * y, x * y]
        digest = blake2b(repr(candidate.role).encode("utf-8"), digest_size=8).digest()
        role_offset = offset + 5
        for index in range(self.config.role_hash_dimension):
            byte = digest[index]
            vector[role_offset + index] = (float(byte) / 127.5) - 1.0
        return vector

    def diverse_subset(
        self,
        candidates: Sequence[ActionCandidate],
        count: int,
        *,
        seen_roles: Iterable[tuple[object, ...]] = (),
    ) -> list[ActionCandidate]:
        seen = set(seen_roles)
        selected: list[ActionCandidate] = []
        used_prefixes: set[tuple[object, ...]] = set()
        for candidate in candidates:
            prefix = candidate.role if candidate.role and candidate.role[0] == "point" else candidate.role[:3]
            if candidate.role in seen:
                continue
            if prefix in used_prefixes:
                continue
            selected.append(candidate)
            used_prefixes.add(prefix)
            if len(selected) >= count:
                return selected
        for candidate in candidates:
            if candidate in selected or candidate.role in seen:
                continue
            selected.append(candidate)
            if len(selected) >= count:
                break
        return selected
