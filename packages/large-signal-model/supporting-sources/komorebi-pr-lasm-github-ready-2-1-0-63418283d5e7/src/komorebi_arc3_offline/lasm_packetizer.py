from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b

import numpy as np
from numpy.typing import NDArray

from .exact_atlas import MultiAtlasAnalyzer, MultiAtlasConfig
from .lasm_types import LASMFramePackets
from .packetizer import FramePacketizer, PacketizerConfig
from .types import FloatArray, IntFrame


@dataclass(frozen=True)
class LASMPacketizerConfig:
    macro_dimension: int = 48
    meso_dimension: int = 96
    micro_dimension: int = 192
    projection_seed: int = 20260729
    multi_atlas: MultiAtlasConfig = MultiAtlasConfig()


class UltimateLASMPacketizer:
    """Resolve each frame into exact coordinates plus nested learned states."""

    def __init__(self, config: LASMPacketizerConfig | None = None) -> None:
        self.config = config or LASMPacketizerConfig()
        self.base = FramePacketizer(
            PacketizerConfig(
                palette_size=self.config.multi_atlas.palette_size,
                maximum_components=12,
                coarse_dimension=32,
                fine_dimension=64,
                projection_seed=self.config.projection_seed + 1,
            )
        )
        self.atlas = MultiAtlasAnalyzer(self.config.multi_atlas)
        self._projection: FloatArray | None = None

    def _ensure_projection(self, raw_dimension: int) -> None:
        if self._projection is not None and self._projection.shape[1] == raw_dimension:
            return
        maximum = max(
            self.config.macro_dimension,
            self.config.meso_dimension,
            self.config.micro_dimension,
        )
        if maximum > raw_dimension:
            raise ValueError(
                f"micro dimension {maximum} exceeds raw feature dimension {raw_dimension}"
            )
        rng = np.random.default_rng(self.config.projection_seed + raw_dimension)
        matrix = rng.normal(size=(raw_dimension, maximum))
        q, _ = np.linalg.qr(matrix, mode="reduced")
        self._projection = q.T.astype(np.float64)

    def _project(self, raw: FloatArray, dimension: int) -> FloatArray:
        self._ensure_projection(raw.size)
        assert self._projection is not None
        return np.asarray(self._projection[:dimension] @ raw, dtype=np.float64)

    @staticmethod
    def _signature(frame: IntFrame) -> str:
        digest = blake2b(digest_size=16, person=b"PR-LASM-frame")
        digest.update(str(frame.shape).encode("ascii"))
        digest.update(frame.astype("<i2", copy=False).tobytes())
        return digest.hexdigest()

    def resolve(
        self,
        frame: NDArray[np.integer],
        previous_frame: NDArray[np.integer] | None = None,
    ) -> LASMFramePackets:
        normalized = self.base._normalize_frame(np.asarray(frame))
        previous = None if previous_frame is None else self.base._normalize_frame(np.asarray(previous_frame))
        base_packets = self.base.resolve(normalized, previous)
        exact = self.atlas.analyze(normalized)
        groups = self.atlas.feature_groups(exact)
        group_vector = np.concatenate([groups[name] for name in sorted(groups)])
        # The previous packetizer already includes connected objects, change,
        # spatial pools, and low-frequency summaries.  Keeping both is an
        # intentional representation portfolio, not accidental duplication.
        raw = np.concatenate([base_packets.raw, group_vector]).astype(np.float64)
        residuals = exact.reconstruction_residuals()
        return LASMFramePackets(
            macro=self._project(raw, self.config.macro_dimension),
            meso=self._project(raw, self.config.meso_dimension),
            micro=self._project(raw, self.config.micro_dimension),
            raw=raw,
            feature_groups=groups,
            analysis=exact,
            signature=self._signature(normalized),
            background=base_packets.background,
            components=base_packets.components,
            salient_points=base_packets.salient_points,
            change_fraction=base_packets.change_fraction,
            non_background_fraction=base_packets.non_background_fraction,
            reconstruction_residuals=residuals,
        )


__all__ = ["LASMPacketizerConfig", "UltimateLASMPacketizer"]
