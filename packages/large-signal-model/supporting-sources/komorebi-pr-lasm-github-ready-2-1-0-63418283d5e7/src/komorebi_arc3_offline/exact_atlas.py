from __future__ import annotations

"""Exact multi-atlas analysis used by PR-LASM.

The module deliberately separates two objects:

* a complete, exactly invertible coordinate record; and
* a compact feature vector used by the statistical world model.

The compact vector is allowed to lose information.  The coordinate record is
not.  This keeps model compression from being confused with reconstruction.
"""

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


def _as_float_image(image: NDArray[np.number]) -> FloatArray:
    array = np.asarray(image, dtype=np.float64)
    if array.ndim != 2:
        raise ValueError(f"expected a two-dimensional image, received {array.shape}")
    return array


def _require_dyadic_shape(image: FloatArray, levels: int) -> None:
    divisor = 2**levels
    if image.shape[0] % divisor or image.shape[1] % divisor:
        raise ValueError(f"shape {image.shape} is not divisible by 2**{levels}")


def haar2d_forward(image: NDArray[np.number], levels: int | None = None) -> FloatArray:
    """Return an orthonormal separable Haar transform in packed layout."""
    array = _as_float_image(image).copy()
    maximum = int(np.floor(np.log2(min(array.shape))))
    depth = maximum if levels is None else int(levels)
    if depth < 0 or depth > maximum:
        raise ValueError("invalid Haar depth")
    _require_dyadic_shape(array, depth)
    height, width = array.shape
    root2 = np.sqrt(2.0)
    for _ in range(depth):
        region = array[:height, :width].copy()
        even_columns = region[:, 0:width:2]
        odd_columns = region[:, 1:width:2]
        horizontal = np.empty_like(region)
        horizontal[:, : width // 2] = (even_columns + odd_columns) / root2
        horizontal[:, width // 2 : width] = (even_columns - odd_columns) / root2

        even_rows = horizontal[0:height:2, :]
        odd_rows = horizontal[1:height:2, :]
        transformed = np.empty_like(horizontal)
        transformed[: height // 2, :] = (even_rows + odd_rows) / root2
        transformed[height // 2 : height, :] = (even_rows - odd_rows) / root2
        array[:height, :width] = transformed
        height //= 2
        width //= 2
    return array


def haar2d_inverse(coefficients: NDArray[np.number], levels: int | None = None) -> FloatArray:
    """Invert :func:`haar2d_forward` exactly up to floating-point roundoff."""
    array = _as_float_image(coefficients).copy()
    maximum = int(np.floor(np.log2(min(array.shape))))
    depth = maximum if levels is None else int(levels)
    if depth < 0 or depth > maximum:
        raise ValueError("invalid Haar depth")
    _require_dyadic_shape(array, depth)
    full_height, full_width = array.shape
    height = full_height // (2 ** max(depth - 1, 0))
    width = full_width // (2 ** max(depth - 1, 0))
    root2 = np.sqrt(2.0)
    for _ in range(depth):
        region = array[:height, :width].copy()
        upper = region[: height // 2, :]
        lower = region[height // 2 : height, :]
        horizontal = np.empty_like(region)
        horizontal[0:height:2, :] = (upper + lower) / root2
        horizontal[1:height:2, :] = (upper - lower) / root2

        left = horizontal[:, : width // 2]
        right = horizontal[:, width // 2 : width]
        reconstructed = np.empty_like(horizontal)
        reconstructed[:, 0:width:2] = (left + right) / root2
        reconstructed[:, 1:width:2] = (left - right) / root2
        array[:height, :width] = reconstructed
        height *= 2
        width *= 2
    return array


def polyphase2d_analyze(image: NDArray[np.number], modulus: int) -> dict[tuple[int, int], FloatArray]:
    """Extract every two-dimensional residue channel."""
    array = _as_float_image(image)
    order = int(modulus)
    if order < 1:
        raise ValueError("modulus must be positive")
    return {
        (row, column): array[row::order, column::order].copy()
        for row in range(order)
        for column in range(order)
    }


def polyphase2d_synthesize(
    channels: Mapping[tuple[int, int], NDArray[np.number]],
    shape: tuple[int, int],
    modulus: int,
) -> FloatArray:
    """Interleave a complete two-dimensional polyphase family."""
    order = int(modulus)
    output = np.zeros(shape, dtype=np.float64)
    expected = {(row, column) for row in range(order) for column in range(order)}
    if set(channels) != expected:
        missing = sorted(expected - set(channels))
        extra = sorted(set(channels) - expected)
        raise ValueError(f"polyphase family is incomplete: missing={missing}, extra={extra}")
    for (row, column), values in channels.items():
        target = output[row::order, column::order]
        source = np.asarray(values, dtype=np.float64)
        if source.shape != target.shape:
            raise ValueError(f"channel {(row, column)} has shape {source.shape}, expected {target.shape}")
        target[...] = source
    return output


def color_one_hot(frame: NDArray[np.integer], palette_size: int = 16) -> FloatArray:
    values = np.asarray(frame, dtype=np.int64)
    if values.ndim != 2:
        raise ValueError("frame must be two-dimensional")
    clipped = np.clip(values, 0, palette_size - 1)
    return np.moveaxis(np.eye(palette_size, dtype=np.float64)[clipped], -1, 0)


def reconstruct_color(one_hot: NDArray[np.number]) -> NDArray[np.int16]:
    array = np.asarray(one_hot, dtype=np.float64)
    if array.ndim != 3:
        raise ValueError("one-hot coordinates must have shape (palette, height, width)")
    return np.argmax(array, axis=0).astype(np.int16)


def fourier_band_masks(shape: tuple[int, int], radial_edges: Sequence[float]) -> tuple[FloatArray, ...]:
    """Create a disjoint complete radial partition in unitary FFT coordinates."""
    fy = np.fft.fftfreq(shape[0])
    fx = np.fft.fftfreq(shape[1])
    yy, xx = np.meshgrid(fy, fx, indexing="ij")
    radius = np.sqrt(xx * xx + yy * yy)
    edges = np.asarray(radial_edges, dtype=float)
    if edges.ndim != 1 or edges.size < 2 or not np.all(np.diff(edges) > 0):
        raise ValueError("radial edges must be a strictly increasing one-dimensional sequence")
    if edges[0] > 0 or edges[-1] < float(radius.max()) - 1e-12:
        raise ValueError("radial edges must cover the complete FFT grid")
    masks: list[FloatArray] = []
    for index, (left, right) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
        if index == len(edges) - 2:
            mask = (radius >= left) & (radius <= right + 1e-15)
        else:
            mask = (radius >= left) & (radius < right)
        masks.append(mask.astype(np.float64))
    if not np.array_equal(np.sum(masks, axis=0), np.ones(shape)):
        raise RuntimeError("Fourier masks do not form an exact partition")
    return tuple(masks)


def fourier_project(image: NDArray[np.number], mask: NDArray[np.number]) -> FloatArray:
    array = _as_float_image(image)
    selector = np.asarray(mask, dtype=np.float64)
    if selector.shape != array.shape:
        raise ValueError("Fourier selector shape mismatch")
    transformed = np.fft.fft2(array, norm="ortho")
    projected = np.fft.ifft2(transformed * selector, norm="ortho")
    return np.real_if_close(projected, tol=1000).real.astype(np.float64)


def polyphase_project(image: NDArray[np.number], modulus: int, phase: tuple[int, int]) -> FloatArray:
    array = _as_float_image(image)
    row, column = phase
    output = np.zeros_like(array)
    output[row::modulus, column::modulus] = array[row::modulus, column::modulus]
    return output


def wavelet_subband_slices(shape: tuple[int, int], levels: int) -> dict[str, tuple[slice, slice]]:
    """Return packed Haar subband slices for energy and projector queries."""
    height, width = shape
    _require_dyadic_shape(np.zeros(shape), levels)
    output: dict[str, tuple[slice, slice]] = {}
    current_h, current_w = height, width
    for level in range(1, levels + 1):
        half_h, half_w = current_h // 2, current_w // 2
        output[f"L{level}-LH"] = (slice(0, half_h), slice(half_w, current_w))
        output[f"L{level}-HL"] = (slice(half_h, current_h), slice(0, half_w))
        output[f"L{level}-HH"] = (slice(half_h, current_h), slice(half_w, current_w))
        current_h, current_w = half_h, half_w
    output[f"L{levels}-LL"] = (slice(0, current_h), slice(0, current_w))
    return output


def wavelet_project(
    image: NDArray[np.number],
    levels: int,
    labels: Sequence[str],
) -> FloatArray:
    coefficients = haar2d_forward(image, levels)
    retained = np.zeros_like(coefficients)
    slices = wavelet_subband_slices(coefficients.shape, levels)
    for label in labels:
        if label not in slices:
            raise KeyError(label)
        retained[slices[label]] = coefficients[slices[label]]
    return haar2d_inverse(retained, levels)


@dataclass(frozen=True)
class AtlasAnalysis:
    """Complete coordinates for one frame in several exact atlases."""

    spatial: FloatArray
    fourier: ComplexArray
    haar: FloatArray
    polyphase2: Mapping[tuple[int, int], FloatArray]
    polyphase4: Mapping[tuple[int, int], FloatArray]
    color: FloatArray
    haar_levels: int

    @property
    def shape(self) -> tuple[int, int]:
        return self.spatial.shape

    def reconstruct(self, atlas: str) -> FloatArray:
        if atlas == "spatial":
            return self.spatial.copy()
        if atlas == "fourier":
            return np.fft.ifft2(self.fourier, norm="ortho").real.astype(np.float64)
        if atlas == "haar":
            return haar2d_inverse(self.haar, self.haar_levels)
        if atlas == "polyphase2":
            return polyphase2d_synthesize(self.polyphase2, self.shape, 2)
        if atlas == "polyphase4":
            return polyphase2d_synthesize(self.polyphase4, self.shape, 4)
        if atlas == "color":
            return reconstruct_color(self.color).astype(np.float64)
        raise KeyError(atlas)

    def reconstruction_residuals(self) -> dict[str, float]:
        return {
            name: float(np.max(np.abs(self.reconstruct(name) - self.spatial)))
            for name in ("spatial", "fourier", "haar", "polyphase2", "polyphase4", "color")
        }

    def tight_frame_synthesis(self, weights: Mapping[str, float] | None = None) -> FloatArray:
        """Synthesize the normalized redundant multi-atlas tight frame.

        Each coordinate family reconstructs the same object.  Weighted analysis
        followed by the canonical dual therefore returns the weighted average of
        identical reconstructions and is exactly the identity.
        """
        names = ("spatial", "fourier", "haar", "polyphase2", "polyphase4")
        chosen = {name: 1.0 for name in names} if weights is None else {name: float(weights[name]) for name in names}
        denominator = sum(value * value for value in chosen.values())
        if denominator <= 0:
            raise ValueError("at least one atlas weight must be positive")
        output = np.zeros_like(self.spatial)
        for name, value in chosen.items():
            output += value * value * self.reconstruct(name)
        return output / denominator


@dataclass(frozen=True)
class MultiAtlasConfig:
    palette_size: int = 16
    haar_levels: int = 4
    radial_bins: int = 8
    angular_bins: int = 8
    pool_sizes: tuple[int, ...] = (2, 4, 8)


class MultiAtlasAnalyzer:
    """Build exact coordinates and compact multi-atlas statistics."""

    def __init__(self, config: MultiAtlasConfig | None = None) -> None:
        self.config = config or MultiAtlasConfig()

    def analyze(self, frame: NDArray[np.integer | np.floating]) -> AtlasAnalysis:
        spatial = _as_float_image(np.asarray(frame))
        levels = min(self.config.haar_levels, int(np.floor(np.log2(min(spatial.shape)))))
        return AtlasAnalysis(
            spatial=spatial.copy(),
            fourier=np.fft.fft2(spatial, norm="ortho").astype(np.complex128),
            haar=haar2d_forward(spatial, levels),
            polyphase2=polyphase2d_analyze(spatial, 2),
            polyphase4=polyphase2d_analyze(spatial, 4),
            color=color_one_hot(np.rint(spatial).astype(np.int16), self.config.palette_size),
            haar_levels=levels,
        )

    @staticmethod
    def _pool(array: FloatArray, blocks: int) -> FloatArray:
        height, width = array.shape
        ys = np.linspace(0, height, blocks + 1, dtype=int)
        xs = np.linspace(0, width, blocks + 1, dtype=int)
        return np.asarray(
            [
                float(np.mean(array[ys[row] : ys[row + 1], xs[column] : xs[column + 1]]))
                for row in range(blocks)
                for column in range(blocks)
            ],
            dtype=np.float64,
        )

    def spatial_features(self, analysis: AtlasAnalysis) -> FloatArray:
        scaled = analysis.spatial / max(1.0, float(self.config.palette_size - 1))
        values = [self._pool(scaled, blocks) for blocks in self.config.pool_sizes]
        return np.concatenate(values)

    def color_features(self, analysis: AtlasAnalysis) -> FloatArray:
        mass = analysis.color.mean(axis=(1, 2))
        # Row and column moments preserve rough object location for each color.
        y = np.linspace(-1.0, 1.0, analysis.shape[0])
        x = np.linspace(-1.0, 1.0, analysis.shape[1])
        row_mass = analysis.color.mean(axis=2)
        column_mass = analysis.color.mean(axis=1)
        y_moment = row_mass @ y / max(1, analysis.shape[0])
        x_moment = column_mass @ x / max(1, analysis.shape[1])
        return np.concatenate([mass, x_moment, y_moment]).astype(np.float64)

    def fourier_features(self, analysis: AtlasAnalysis) -> FloatArray:
        energy = np.abs(analysis.fourier) ** 2
        fy = np.fft.fftfreq(analysis.shape[0])
        fx = np.fft.fftfreq(analysis.shape[1])
        yy, xx = np.meshgrid(fy, fx, indexing="ij")
        radius = np.sqrt(xx * xx + yy * yy)
        angle = np.mod(np.arctan2(yy, xx), 2.0 * np.pi)
        radial_edges = np.linspace(0.0, float(radius.max()) + 1e-12, self.config.radial_bins + 1)
        angular_edges = np.linspace(0.0, 2.0 * np.pi + 1e-12, self.config.angular_bins + 1)
        radial = []
        angular = []
        total = max(float(energy.sum()), 1e-12)
        for index in range(self.config.radial_bins):
            mask = (radius >= radial_edges[index]) & (radius < radial_edges[index + 1])
            radial.append(float(energy[mask].sum() / total))
        for index in range(self.config.angular_bins):
            mask = (angle >= angular_edges[index]) & (angle < angular_edges[index + 1])
            angular.append(float(energy[mask].sum() / total))
        low = analysis.fourier[:4, :4]
        low_features = np.concatenate([low.real.ravel(), low.imag.ravel()]) / max(1.0, np.sqrt(np.prod(analysis.shape)))
        return np.concatenate([radial, angular, low_features]).astype(np.float64)

    def haar_features(self, analysis: AtlasAnalysis) -> FloatArray:
        slices = wavelet_subband_slices(analysis.shape, analysis.haar_levels)
        total = max(float(np.sum(analysis.haar**2)), 1e-12)
        energies = [float(np.sum(analysis.haar[region] ** 2) / total) for _, region in sorted(slices.items())]
        # Coarsest LL coefficients give a compact signed low-resolution state.
        ll = slices[f"L{analysis.haar_levels}-LL"]
        coarse = analysis.haar[ll].ravel() / max(1.0, np.sqrt(np.prod(analysis.shape)))
        return np.concatenate([np.asarray(energies), coarse]).astype(np.float64)

    @staticmethod
    def polyphase_features(analysis: AtlasAnalysis, modulus: int) -> FloatArray:
        channels = analysis.polyphase2 if modulus == 2 else analysis.polyphase4
        values: list[float] = []
        normalization = max(1.0, float(np.max(np.abs(analysis.spatial))))
        for phase in sorted(channels):
            channel = np.asarray(channels[phase], dtype=float)
            values.extend(
                [
                    float(channel.mean() / normalization),
                    float(channel.std() / normalization),
                    float(np.mean(channel != 0.0)),
                ]
            )
        return np.asarray(values, dtype=np.float64)

    def feature_groups(self, analysis: AtlasAnalysis) -> dict[str, FloatArray]:
        return {
            "spatial": self.spatial_features(analysis),
            "color": self.color_features(analysis),
            "fourier": self.fourier_features(analysis),
            "haar": self.haar_features(analysis),
            "polyphase2": self.polyphase_features(analysis, 2),
            "polyphase4": self.polyphase_features(analysis, 4),
        }

    def feature_vector(self, analysis: AtlasAnalysis) -> FloatArray:
        groups = self.feature_groups(analysis)
        return np.concatenate([groups[name] for name in sorted(groups)])


__all__ = [
    "AtlasAnalysis",
    "MultiAtlasAnalyzer",
    "MultiAtlasConfig",
    "color_one_hot",
    "fourier_band_masks",
    "fourier_project",
    "haar2d_forward",
    "haar2d_inverse",
    "polyphase2d_analyze",
    "polyphase2d_synthesize",
    "polyphase_project",
    "reconstruct_color",
    "wavelet_project",
    "wavelet_subband_slices",
]
