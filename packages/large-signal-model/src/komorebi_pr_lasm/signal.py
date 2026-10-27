"""Finite real-valued signal coordinates, explicit polyphase FIR blocks, and streaming.

Conventions: x_s[q] = x[N*q+s], h[k] = 0 outside 0 <= k < L.
The transfer blocks are E[r,s,m] = h[N*m+r-s].  FIR application uses
zero extension and returns full convolution, not a circular FFT filter.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

import numpy as np

from komorebi_arc3_offline._validation import dyadic_depth, integer, readonly, real_array
from komorebi_arc3_offline.lasm_refinement import PacketTree


def polyphase_analyze(values: object, modulus: int) -> dict[int, np.ndarray]:
    x = real_array(values, "signal", ndim=1)
    order = integer(modulus, "modulus", minimum=1)
    return {phase: x[phase::order].copy() for phase in range(order)}


def polyphase_synthesize(channels: Mapping[int, object], length: int, modulus: int) -> np.ndarray:
    length = integer(length, "length", minimum=1)
    order = integer(modulus, "modulus", minimum=1)
    if set(channels) != set(range(order)):
        raise ValueError("a complete residue-channel family is required")
    output = np.empty(length, dtype=np.float64)
    for phase in range(order):
        values = real_array(channels[phase], "channel", ndim=1, empty=True)
        if values.shape != output[phase::order].shape:
            raise ValueError(f"incorrect length for phase {phase}")
        output[phase::order] = values
    return output


@dataclass(frozen=True)
class SignalAnalysis1D:
    """Coordinate snapshot. No compressed state is substituted for the signal."""

    spatial: np.ndarray
    fourier: np.ndarray
    polyphase: Mapping[int, np.ndarray]
    packets: PacketTree
    modulus: int

    @property
    def length(self) -> int:
        return int(self.spatial.size)

    @property
    def effective_depth(self) -> int:
        return self.packets.maximum_depth

    def reconstruct(self, atlas: str = "spatial") -> np.ndarray:
        if atlas == "spatial":
            return self.spatial.copy()
        if atlas == "fourier":
            return np.fft.ifft(self.fourier, norm="ortho").real
        if atlas == "polyphase":
            return polyphase_synthesize(self.polyphase, self.length, self.modulus)
        if atlas == "packets":
            leaves = tuple(path for path in self.packets.coefficients if len(path) == self.effective_depth)
            return self.packets.synthesize(leaves)
        raise KeyError(atlas)

    def reconstruction_residuals(self) -> dict[str, float]:
        return {name: float(np.max(np.abs(self.reconstruct(name) - self.spatial)))
                for name in ("spatial", "fourier", "polyphase", "packets")}


def analyze_signal(values: object, *, modulus: int = 4, maximum_depth: int = 6) -> SignalAnalysis1D:
    """Analyze any nonempty finite real vector without padding, clipping or resizing.

    The effective Haar packet depth is the smaller of maximum_depth and the
    power of two dividing the length. At odd length the packet tree is the root.
    """
    x = real_array(values, "signal", ndim=1)
    depth = min(integer(maximum_depth, "maximum_depth"), dyadic_depth((x.size,)))
    order = integer(modulus, "modulus", minimum=1)
    return SignalAnalysis1D(
        spatial=readonly(x), fourier=readonly(np.fft.fft(x, norm="ortho")),
        polyphase=MappingProxyType({p: readonly(v) for p, v in polyphase_analyze(x, order).items()}),
        packets=PacketTree.analyze(x, depth), modulus=order,
    )


class PolyphaseFIR:
    """An explicit, finite N-by-N matrix of causal FIR transfer blocks.

    ``blocks[r,s,m]`` equals h[N*m+r-s] with out-of-support taps set to zero.
    This is an independently executable reference decomposition, not a claim
    of acceleration over NumPy's direct convolution.
    """

    def __init__(self, taps: object, modulus: int = 4) -> None:
        self._taps = readonly(real_array(taps, "taps", ndim=1))
        self._modulus = integer(modulus, "modulus", minimum=1)
        order = self._modulus
        lag_count = (self._taps.size + order - 2) // order + 1
        block = np.zeros((order, order, lag_count), dtype=np.float64)
        for r in range(order):
            for s in range(order):
                for m in range(lag_count):
                    index = order * m + r - s
                    if 0 <= index < self._taps.size:
                        block[r, s, m] = self._taps[index]
        self._blocks = readonly(block)

    @property
    def taps(self) -> np.ndarray:
        return self._taps

    @property
    def modulus(self) -> int:
        return self._modulus

    @property
    def blocks(self) -> np.ndarray:
        return self._blocks

    def apply(self, values: object) -> np.ndarray:
        x = real_array(values, "signal", ndim=1)
        channels = polyphase_analyze(x, self.modulus)
        output = np.zeros(x.size + self.taps.size - 1, dtype=np.float64)
        for r in range(self.modulus):
            lane = output[r::self.modulus]
            for s in range(self.modulus):
                if channels[s].size == 0:
                    continue
                contribution = np.convolve(channels[s], self.blocks[r, s], mode="full")
                count = min(lane.size, contribution.size)
                lane[:count] += contribution[:count]
        if not np.isfinite(output).all():
            raise FloatingPointError("FIR output overflowed float64")
        return output

    def compose(self, earlier: "PolyphaseFIR") -> "PolyphaseFIR":
        """Apply earlier first, then this operator, using the same residue order."""
        if not isinstance(earlier, PolyphaseFIR) or earlier.modulus != self.modulus:
            raise ValueError("composition requires a PolyphaseFIR with the same modulus")
        return PolyphaseFIR(np.convolve(self.taps, earlier.taps), self.modulus)


class StreamingFIR:
    """Chunk-independent causal FIR with an explicit finite tail and reset.

    process(chunk) returns one output per input sample. flush() returns the
    remaining L-1 samples exactly once. Processing after flush requires reset().
    No future sample is used to produce the current output.
    """

    def __init__(self, taps: object) -> None:
        self._taps = readonly(real_array(taps, "taps", ndim=1))
        self.reset()

    @property
    def taps(self) -> np.ndarray:
        return self._taps

    def reset(self) -> None:
        self._history = np.zeros(self.taps.size - 1, dtype=np.float64)
        self._closed = False
        self._seen = False

    def process(self, values: object) -> np.ndarray:
        if self._closed:
            raise ValueError("stream is flushed; reset before processing more samples")
        x = real_array(values, "chunk", ndim=1, empty=True)
        if x.size == 0:
            return np.empty(0, dtype=np.float64)
        joined = np.concatenate([self._history, x])
        offset = self.taps.size - 1
        output = np.convolve(joined, self.taps)[offset:offset + x.size]
        if not np.isfinite(output).all():
            raise FloatingPointError("stream output overflowed float64")
        if offset:
            self._history = joined[-offset:].copy()
        self._seen = True
        return output

    def flush(self) -> np.ndarray:
        if self._closed:
            return np.empty(0, dtype=np.float64)
        if self._seen and self.taps.size > 1:
            tail = self.process(np.zeros(self.taps.size - 1, dtype=np.float64))
        else:
            tail = np.empty(0, dtype=np.float64)
        self._closed = True
        return tail


__all__ = ["SignalAnalysis1D", "analyze_signal", "polyphase_analyze", "polyphase_synthesize",
           "PolyphaseFIR", "StreamingFIR"]
