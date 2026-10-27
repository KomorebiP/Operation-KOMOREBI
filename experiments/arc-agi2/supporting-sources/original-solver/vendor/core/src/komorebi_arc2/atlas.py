from __future__ import annotations

"""Exact multi-atlas analysis and nested signal states for static ARC grids.

This module is the static-grid counterpart of the PR-LASM frame packetizer.  A
single ARC grid is retained simultaneously in spatial, color, Fourier, Haar,
polyphase, and object-relational coordinates.  Compact macro, meso, and micro
states are deterministic projections used for Bayesian program selection; they
are not substitutes for the exact coordinate archive.
"""

from collections import Counter, deque
from dataclasses import dataclass
from hashlib import blake2b
from functools import lru_cache
from math import ceil, log2, pi
from typing import Iterable, Mapping, Sequence

import numpy as np

Array = np.ndarray
FloatArray = np.ndarray

PALETTE_SIZE = 10
MAX_SIDE = 30


def sanitize_grid(grid: Array | Sequence[Sequence[int]]) -> Array:
    array = np.asarray(grid, dtype=np.int16)
    if array.ndim != 2 or array.size == 0:
        return np.zeros((1, 1), dtype=np.int16)
    height = max(1, min(MAX_SIDE, int(array.shape[0])))
    width = max(1, min(MAX_SIDE, int(array.shape[1])))
    array = array[:height, :width].copy()
    return np.where((0 <= array) & (array < PALETTE_SIZE), array, 0).astype(np.int16)


def infer_background(grid: Array) -> int:
    values, counts = np.unique(grid, return_counts=True)
    if 0 in values:
        return 0
    return int(values[int(np.argmax(counts))])


def _next_power_of_two(value: int) -> int:
    return 1 if value <= 1 else 1 << int(ceil(log2(value)))


def _pad_dyadic(array: FloatArray) -> tuple[FloatArray, tuple[int, int]]:
    height, width = array.shape
    padded_height = _next_power_of_two(height)
    padded_width = _next_power_of_two(width)
    padded = np.zeros((padded_height, padded_width), dtype=np.float64)
    padded[:height, :width] = array
    return padded, (height, width)


def haar2d_forward(array: FloatArray, levels: int) -> FloatArray:
    out = np.asarray(array, dtype=np.float64).copy()
    height, width = out.shape
    levels = max(0, min(levels, int(log2(min(height, width))) if min(height, width) > 0 else 0))
    scale = np.sqrt(2.0)
    current_h, current_w = height, width
    for _ in range(levels):
        rows = out[:current_h, :current_w]
        even = rows[:, 0:current_w:2]
        odd = rows[:, 1:current_w:2]
        horizontal = np.empty_like(rows)
        half_w = current_w // 2
        horizontal[:, :half_w] = (even + odd) / scale
        horizontal[:, half_w:current_w] = (even - odd) / scale
        even_rows = horizontal[0:current_h:2, :]
        odd_rows = horizontal[1:current_h:2, :]
        transformed = np.empty_like(horizontal)
        half_h = current_h // 2
        transformed[:half_h, :] = (even_rows + odd_rows) / scale
        transformed[half_h:current_h, :] = (even_rows - odd_rows) / scale
        out[:current_h, :current_w] = transformed
        current_h //= 2
        current_w //= 2
    return out


def haar2d_inverse(coefficients: FloatArray, levels: int) -> FloatArray:
    out = np.asarray(coefficients, dtype=np.float64).copy()
    height, width = out.shape
    levels = max(0, min(levels, int(log2(min(height, width))) if min(height, width) > 0 else 0))
    scale = np.sqrt(2.0)
    current_h = height // (2 ** max(levels - 1, 0))
    current_w = width // (2 ** max(levels - 1, 0))
    for _ in range(levels):
        block = out[:current_h, :current_w]
        half_h = current_h // 2
        half_w = current_w // 2
        low_rows = block[:half_h, :]
        high_rows = block[half_h:current_h, :]
        vertical = np.empty_like(block)
        vertical[0:current_h:2, :] = (low_rows + high_rows) / scale
        vertical[1:current_h:2, :] = (low_rows - high_rows) / scale
        low_cols = vertical[:, :half_w]
        high_cols = vertical[:, half_w:current_w]
        restored = np.empty_like(vertical)
        restored[:, 0:current_w:2] = (low_cols + high_cols) / scale
        restored[:, 1:current_w:2] = (low_cols - high_cols) / scale
        out[:current_h, :current_w] = restored
        current_h *= 2
        current_w *= 2
    return out


def polyphase_analyze(array: FloatArray, modulus: int) -> dict[tuple[int, int], FloatArray]:
    return {
        (row, column): np.asarray(array[row::modulus, column::modulus], dtype=np.float64).copy()
        for row in range(modulus)
        for column in range(modulus)
    }


def polyphase_synthesize(
    channels: Mapping[tuple[int, int], FloatArray], shape: tuple[int, int], modulus: int
) -> FloatArray:
    out = np.zeros(shape, dtype=np.float64)
    for (row, column), channel in channels.items():
        out[row::modulus, column::modulus] = channel
    return out


def color_one_hot(grid: Array) -> FloatArray:
    return np.eye(PALETTE_SIZE, dtype=np.float64)[grid].transpose(2, 0, 1)


def color_reconstruct(one_hot: FloatArray) -> FloatArray:
    return np.argmax(one_hot, axis=0).astype(np.float64)


def _pool(array: FloatArray, blocks: int) -> FloatArray:
    height, width = array.shape
    ys = np.linspace(0, height, blocks + 1, dtype=int)
    xs = np.linspace(0, width, blocks + 1, dtype=int)
    values: list[float] = []
    for row in range(blocks):
        for column in range(blocks):
            region = array[ys[row] : ys[row + 1], xs[column] : xs[column + 1]]
            values.append(float(region.mean()) if region.size else 0.0)
    return np.asarray(values, dtype=np.float64)


def _fixed(values: Iterable[float] | FloatArray, size: int) -> FloatArray:
    source = np.asarray(list(values) if not isinstance(values, np.ndarray) else values, dtype=np.float64).ravel()
    out = np.zeros(size, dtype=np.float64)
    count = min(size, source.size)
    out[:count] = source[:count]
    return out


def _mask_holes(mask: Array) -> int:
    mask = np.asarray(mask, dtype=bool)
    if mask.size == 0:
        return 0
    height, width = mask.shape
    exterior = np.zeros_like(mask, dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    for row in range(height):
        for column in (0, width - 1):
            if not mask[row, column] and not exterior[row, column]:
                exterior[row, column] = True
                queue.append((row, column))
    for column in range(width):
        for row in (0, height - 1):
            if not mask[row, column] and not exterior[row, column]:
                exterior[row, column] = True
                queue.append((row, column))
    while queue:
        row, column = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, column + dc
            if 0 <= nr < height and 0 <= nc < width and not mask[nr, nc] and not exterior[nr, nc]:
                exterior[nr, nc] = True
                queue.append((nr, nc))
    holes = (~mask) & (~exterior)
    seen = np.zeros_like(holes, dtype=bool)
    count = 0
    for row in range(height):
        for column in range(width):
            if not holes[row, column] or seen[row, column]:
                continue
            count += 1
            seen[row, column] = True
            queue.append((row, column))
            while queue:
                rr, cc = queue.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and holes[nr, nc] and not seen[nr, nc]:
                        seen[nr, nc] = True
                        queue.append((nr, nc))
    return count


@dataclass(frozen=True)
class AtlasObject:
    color: int
    cells: tuple[tuple[int, int], ...]
    bbox: tuple[int, int, int, int]
    centroid: tuple[float, float]
    holes: int
    density: float
    touches_border: tuple[bool, bool, bool, bool]
    symmetry: tuple[bool, bool, bool]

    @property
    def size(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.bbox[2] - self.bbox[0] + 1

    @property
    def width(self) -> int:
        return self.bbox[3] - self.bbox[1] + 1

    @property
    def normalized_mask(self) -> Array:
        mask = np.zeros((self.height, self.width), dtype=np.int8)
        row0, column0, _, _ = self.bbox
        for row, column in self.cells:
            mask[row - row0, column - column0] = 1
        return mask


def extract_objects(grid: Array, connectivity: int = 4, separate_colors: bool = True) -> tuple[AtlasObject, ...]:
    grid = sanitize_grid(grid)
    background = infer_background(grid)
    height, width = grid.shape
    seen = np.zeros((height, width), dtype=bool)
    steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
    if connectivity == 8:
        steps = steps + ((1, 1), (1, -1), (-1, 1), (-1, -1))
    objects: list[AtlasObject] = []
    for row in range(height):
        for column in range(width):
            if seen[row, column] or int(grid[row, column]) == background:
                continue
            seed_color = int(grid[row, column])
            queue: deque[tuple[int, int]] = deque([(row, column)])
            seen[row, column] = True
            cells: list[tuple[int, int]] = []
            while queue:
                rr, cc = queue.popleft()
                cells.append((rr, cc))
                for dr, dc in steps:
                    nr, nc = rr + dr, cc + dc
                    if not (0 <= nr < height and 0 <= nc < width) or seen[nr, nc]:
                        continue
                    value = int(grid[nr, nc])
                    admissible = value != background and (not separate_colors or value == seed_color)
                    if admissible:
                        seen[nr, nc] = True
                        queue.append((nr, nc))
            rows = [cell[0] for cell in cells]
            columns = [cell[1] for cell in cells]
            row0, row1 = min(rows), max(rows)
            column0, column1 = min(columns), max(columns)
            mask = np.zeros((row1 - row0 + 1, column1 - column0 + 1), dtype=bool)
            for rr, cc in cells:
                mask[rr - row0, cc - column0] = True
            density = float(mask.mean())
            symmetry = (
                bool(np.array_equal(mask, np.fliplr(mask))),
                bool(np.array_equal(mask, np.flipud(mask))),
                bool(mask.shape[0] == mask.shape[1] and np.array_equal(mask, mask.T)),
            )
            color = seed_color if separate_colors else int(Counter(int(grid[r, c]) for r, c in cells).most_common(1)[0][0])
            objects.append(
                AtlasObject(
                    color=color,
                    cells=tuple(cells),
                    bbox=(row0, column0, row1, column1),
                    centroid=(float(np.mean(rows)), float(np.mean(columns))),
                    holes=_mask_holes(mask),
                    density=density,
                    touches_border=(row0 == 0, column0 == 0, row1 == height - 1, column1 == width - 1),
                    symmetry=symmetry,
                )
            )
    return tuple(objects)


def _object_feature_vector(grid: Array, objects: Sequence[AtlasObject]) -> FloatArray:
    height, width = grid.shape
    area = max(1, height * width)
    ordered = sorted(objects, key=lambda obj: (-obj.size, obj.bbox, obj.color))
    values: list[float] = [
        len(objects) / 30.0,
        sum(obj.holes for obj in objects) / 20.0,
        sum(obj.size for obj in objects) / area,
        float(np.mean([obj.density for obj in objects])) if objects else 0.0,
        float(np.std([obj.size / area for obj in objects])) if objects else 0.0,
        len({obj.color for obj in objects}) / PALETTE_SIZE,
        sum(any(obj.touches_border) for obj in objects) / max(1, len(objects)),
        sum(any(obj.symmetry) for obj in objects) / max(1, len(objects)),
    ]
    for obj in ordered[:8]:
        row0, column0, row1, column1 = obj.bbox
        values.extend(
            [
                obj.color / 9.0,
                obj.size / area,
                obj.height / max(1, height),
                obj.width / max(1, width),
                obj.centroid[0] / max(1, height - 1),
                obj.centroid[1] / max(1, width - 1),
                min(obj.holes, 4) / 4.0,
                obj.density,
                float(sum(obj.symmetry)) / 3.0,
                float(sum(obj.touches_border)) / 4.0,
            ]
        )
    while len(values) < 88:
        values.append(0.0)

    relation = np.zeros(12, dtype=np.float64)
    pairs = 0
    for left_index, left in enumerate(ordered[:12]):
        for right in ordered[left_index + 1 : 12]:
            pairs += 1
            l0, c0, l1, c1 = left.bbox
            r0, d0, r1, d1 = right.bbox
            relation[0] += float(left.color == right.color)
            relation[1] += float(left.normalized_mask.shape == right.normalized_mask.shape and np.array_equal(left.normalized_mask, right.normalized_mask))
            relation[2] += float(l0 == r0 or l1 == r1 or left.centroid[0] == right.centroid[0])
            relation[3] += float(c0 == d0 or c1 == d1 or left.centroid[1] == right.centroid[1])
            relation[4] += float(l1 + 1 == r0 or r1 + 1 == l0)
            relation[5] += float(c1 + 1 == d0 or d1 + 1 == c0)
            relation[6] += float(l0 <= r0 <= r1 <= l1 and c0 <= d0 <= d1 <= c1)
            relation[7] += float(r0 <= l0 <= l1 <= r1 and d0 <= c0 <= c1 <= d1)
            relation[8] += abs(left.centroid[0] - right.centroid[0]) / max(1, height - 1)
            relation[9] += abs(left.centroid[1] - right.centroid[1]) / max(1, width - 1)
            relation[10] += float(left.size == right.size)
            relation[11] += float(left.holes == right.holes)
    if pairs:
        relation /= pairs
    return np.concatenate([np.asarray(values[:88], dtype=np.float64), relation])


def _spatial_features(spatial: FloatArray) -> FloatArray:
    normalized = spatial / 9.0
    height, width = spatial.shape
    values = [
        height / MAX_SIDE,
        width / MAX_SIDE,
        (height * width) / float(MAX_SIDE * MAX_SIDE),
        float(np.mean(normalized)),
        float(np.std(normalized)),
        float(np.mean(spatial != 0)),
    ]
    return np.concatenate([np.asarray(values), _pool(normalized, 2), _pool(normalized, 4), _pool(normalized, 6)])


def _color_features(one_hot: FloatArray) -> FloatArray:
    _, height, width = one_hot.shape
    masses = one_hot.mean(axis=(1, 2))
    y = np.linspace(-1.0, 1.0, height, dtype=np.float64)
    x = np.linspace(-1.0, 1.0, width, dtype=np.float64)
    row_mass = one_hot.mean(axis=2)
    column_mass = one_hot.mean(axis=1)
    y_moment = (row_mass @ y) / max(1, height)
    x_moment = (column_mass @ x) / max(1, width)
    return np.concatenate([masses, x_moment, y_moment]).astype(np.float64)


def _fourier_features(fourier: Array) -> FloatArray:
    height, width = fourier.shape
    energy = np.abs(fourier) ** 2
    fy = np.fft.fftfreq(height)
    fx = np.fft.fftfreq(width)
    yy, xx = np.meshgrid(fy, fx, indexing="ij")
    radius = np.sqrt(xx * xx + yy * yy)
    angle = np.mod(np.arctan2(yy, xx), 2.0 * pi)
    total = max(float(energy.sum()), 1e-12)
    radial_edges = np.linspace(0.0, float(radius.max()) + 1e-12, 9)
    angular_edges = np.linspace(0.0, 2.0 * pi + 1e-12, 9)
    radial = [float(energy[(radius >= radial_edges[i]) & (radius < radial_edges[i + 1])].sum() / total) for i in range(8)]
    angular = [float(energy[(angle >= angular_edges[i]) & (angle < angular_edges[i + 1])].sum() / total) for i in range(8)]
    low = np.zeros((4, 4), dtype=np.complex128)
    low[: min(4, height), : min(4, width)] = fourier[: min(4, height), : min(4, width)]
    scale = max(1.0, np.sqrt(height * width))
    return np.concatenate([np.asarray(radial), np.asarray(angular), low.real.ravel() / scale, low.imag.ravel() / scale])


def _haar_features(coefficients: FloatArray, levels: int) -> FloatArray:
    height, width = coefficients.shape
    total = max(float(np.sum(coefficients**2)), 1e-12)
    energies: list[float] = []
    current_h, current_w = height, width
    for _ in range(levels):
        half_h, half_w = current_h // 2, current_w // 2
        energies.extend(
            [
                float(np.sum(coefficients[:half_h, half_w:current_w] ** 2) / total),
                float(np.sum(coefficients[half_h:current_h, :half_w] ** 2) / total),
                float(np.sum(coefficients[half_h:current_h, half_w:current_w] ** 2) / total),
            ]
        )
        current_h, current_w = half_h, half_w
    energies.append(float(np.sum(coefficients[:current_h, :current_w] ** 2) / total))
    coarse = _fixed(coefficients[:current_h, :current_w].ravel() / max(1.0, np.sqrt(height * width)), 16)
    return np.concatenate([_fixed(np.asarray(energies), 13), coarse])


def _polyphase_features(channels: Mapping[tuple[int, int], FloatArray], normalization: float) -> FloatArray:
    values: list[float] = []
    for phase in sorted(channels):
        channel = channels[phase]
        if channel.size:
            values.extend(
                [
                    float(channel.mean() / normalization),
                    float(channel.std() / normalization),
                    float(np.mean(channel != 0.0)),
                    float(len(np.unique(channel)) / PALETTE_SIZE),
                ]
            )
        else:
            values.extend([0.0, 0.0, 0.0, 0.0])
    return np.asarray(values, dtype=np.float64)


@lru_cache(maxsize=16)
def _dct_matrix(length: int, dimension: int) -> FloatArray:
    indices = np.arange(length, dtype=np.float64) + 0.5
    frequencies = np.arange(dimension, dtype=np.float64)[:, None] + 1.0
    return (np.sqrt(2.0 / length) * np.cos(pi * frequencies * indices[None, :] / length)).astype(np.float64)


def _dct_projection(values: FloatArray, dimension: int) -> FloatArray:
    source = np.asarray(values, dtype=np.float64).ravel()
    if source.size == 0:
        return np.zeros(dimension, dtype=np.float64)
    return (_dct_matrix(source.size, dimension) @ source).astype(np.float64)


@dataclass(frozen=True)
class ARCAtlasState:
    spatial: FloatArray
    color: FloatArray
    fourier: Array
    haar: FloatArray
    polyphase2: Mapping[tuple[int, int], FloatArray]
    polyphase3: Mapping[tuple[int, int], FloatArray]
    polyphase4: Mapping[tuple[int, int], FloatArray]
    objects4: tuple[AtlasObject, ...]
    objects8: tuple[AtlasObject, ...]
    feature_groups: Mapping[str, FloatArray]
    macro: FloatArray
    meso: FloatArray
    micro: FloatArray
    raw: FloatArray
    signature: str
    background: int
    reconstruction_residuals: Mapping[str, float]

    def state(self, resolution: str) -> FloatArray:
        if resolution == "macro":
            return self.macro
        if resolution == "meso":
            return self.meso
        if resolution == "micro":
            return self.micro
        if resolution == "raw":
            return self.raw
        raise KeyError(resolution)


class ARCAtlasAnalyzer:
    """Build exact coordinate archives and nested statistical states."""

    def __init__(self, macro_dimension: int = 48, meso_dimension: int = 96, micro_dimension: int = 192) -> None:
        self.macro_dimension = macro_dimension
        self.meso_dimension = meso_dimension
        self.micro_dimension = micro_dimension
        self._cache: dict[str, ARCAtlasState] = {}
        self._group_cache: dict[str, Mapping[str, FloatArray]] = {}

    @staticmethod
    def signature(grid: Array) -> str:
        grid = sanitize_grid(grid)
        digest = blake2b(digest_size=16, person=b"PRLASM-ARC2-grid")
        digest.update(str(grid.shape).encode("ascii"))
        digest.update(grid.astype("<i2", copy=False).tobytes())
        return digest.hexdigest()

    def feature_groups(self, grid: Array | Sequence[Sequence[int]]) -> Mapping[str, FloatArray]:
        """Return fixed multi-atlas summaries without computing projected states."""
        normalized = sanitize_grid(grid)
        signature = self.signature(normalized)
        cached_state = self._cache.get(signature)
        if cached_state is not None:
            return cached_state.feature_groups
        cached = self._group_cache.get(signature)
        if cached is not None:
            return cached
        spatial = normalized.astype(np.float64)
        one_hot = color_one_hot(normalized)
        fourier = np.fft.fft2(spatial, norm="ortho")
        padded, _ = _pad_dyadic(spatial)
        levels = min(4, int(log2(min(padded.shape))) if min(padded.shape) > 1 else 0)
        haar = haar2d_forward(padded, levels)
        phase2 = polyphase_analyze(spatial, 2)
        phase3 = polyphase_analyze(spatial, 3)
        phase4 = polyphase_analyze(spatial, 4)
        objects4 = extract_objects(normalized, 4, True)
        normalization = max(1.0, float(np.max(np.abs(spatial))))
        groups = {
            "spatial": _fixed(_spatial_features(spatial), 64),
            "color": _fixed(_color_features(one_hot), 32),
            "fourier": _fixed(_fourier_features(fourier), 48),
            "haar": _fixed(_haar_features(haar, levels), 32),
            "polyphase2": _fixed(_polyphase_features(phase2, normalization), 16),
            "polyphase3": _fixed(_polyphase_features(phase3, normalization), 36),
            "polyphase4": _fixed(_polyphase_features(phase4, normalization), 64),
            "object": _fixed(_object_feature_vector(normalized, objects4), 100),
        }
        self._group_cache[signature] = groups
        return groups


    def analyze(self, grid: Array | Sequence[Sequence[int]]) -> ARCAtlasState:
        normalized = sanitize_grid(grid)
        signature = self.signature(normalized)
        cached = self._cache.get(signature)
        if cached is not None:
            return cached
        spatial = normalized.astype(np.float64)
        one_hot = color_one_hot(normalized)
        fourier = np.fft.fft2(spatial, norm="ortho")
        padded, original_shape = _pad_dyadic(spatial)
        levels = min(4, int(log2(min(padded.shape))) if min(padded.shape) > 1 else 0)
        haar = haar2d_forward(padded, levels)
        phase2 = polyphase_analyze(spatial, 2)
        phase3 = polyphase_analyze(spatial, 3)
        phase4 = polyphase_analyze(spatial, 4)
        objects4 = extract_objects(normalized, 4, True)
        objects8 = extract_objects(normalized, 8, False)
        normalization = max(1.0, float(np.max(np.abs(spatial))))
        groups = {
            "spatial": _fixed(_spatial_features(spatial), 64),
            "color": _fixed(_color_features(one_hot), 32),
            "fourier": _fixed(_fourier_features(fourier), 48),
            "haar": _fixed(_haar_features(haar, levels), 32),
            "polyphase2": _fixed(_polyphase_features(phase2, normalization), 16),
            "polyphase3": _fixed(_polyphase_features(phase3, normalization), 36),
            "polyphase4": _fixed(_polyphase_features(phase4, normalization), 64),
            "object": _fixed(_object_feature_vector(normalized, objects4), 100),
        }
        raw = np.concatenate([groups[name] for name in sorted(groups)]).astype(np.float64)
        restored_haar = haar2d_inverse(haar, levels)[: original_shape[0], : original_shape[1]]
        residuals = {
            "spatial": 0.0,
            "color": float(np.max(np.abs(color_reconstruct(one_hot) - spatial))),
            "fourier": float(np.max(np.abs(np.fft.ifft2(fourier, norm="ortho").real - spatial))),
            "haar": float(np.max(np.abs(restored_haar - spatial))),
            "polyphase2": float(np.max(np.abs(polyphase_synthesize(phase2, spatial.shape, 2) - spatial))),
            "polyphase3": float(np.max(np.abs(polyphase_synthesize(phase3, spatial.shape, 3) - spatial))),
            "polyphase4": float(np.max(np.abs(polyphase_synthesize(phase4, spatial.shape, 4) - spatial))),
        }
        state = ARCAtlasState(
            spatial=spatial,
            color=one_hot,
            fourier=fourier,
            haar=haar,
            polyphase2=phase2,
            polyphase3=phase3,
            polyphase4=phase4,
            objects4=objects4,
            objects8=objects8,
            feature_groups=groups,
            macro=_dct_projection(raw, self.macro_dimension),
            meso=_dct_projection(raw, self.meso_dimension),
            micro=_dct_projection(raw, self.micro_dimension),
            raw=raw,
            signature=signature,
            background=infer_background(normalized),
            reconstruction_residuals=residuals,
        )
        self._cache[signature] = state
        return state


ROUTE_NAMES = (
    "identity_like",
    "recolor",
    "geometry",
    "crop_extract",
    "expand",
    "compress",
    "draw_add",
    "erase_remove",
    "translate",
    "panel",
    "periodic",
    "object_relational",
    "mixed",
)

ATLAS_NAMES = ("spatial", "color", "fourier", "haar", "polyphase2", "polyphase3", "polyphase4", "object")
RESOLUTION_NAMES = ("macro", "meso", "micro")


def _separator_count(grid: Array) -> int:
    count = 0
    for row in range(grid.shape[0]):
        if np.all(grid[row] == grid[row, 0]):
            count += 1
    for column in range(grid.shape[1]):
        if np.all(grid[:, column] == grid[0, column]):
            count += 1
    return count


def _periodicity_score(grid: Array) -> float:
    scores: list[float] = []
    for axis in (0, 1):
        length = grid.shape[axis]
        for period in range(1, min(6, length)):
            left = np.take(grid, np.arange(0, length - period), axis=axis)
            right = np.take(grid, np.arange(period, length), axis=axis)
            if left.size:
                scores.append(float(np.mean(left == right)))
    return max(scores, default=0.0)


@dataclass(frozen=True)
class TaskSignalState:
    input_states: tuple[ARCAtlasState, ...]
    output_states: tuple[ARCAtlasState, ...]
    route_probabilities: Mapping[str, float]
    atlas_probabilities: Mapping[str, float]
    resolution_probabilities: Mapping[str, float]
    primary_route: str
    summary_vector: FloatArray
    residual_group_norms: Mapping[str, float]


def analyze_task_signal(
    train: Sequence[tuple[Array, Array]], analyzer: ARCAtlasAnalyzer | None = None
) -> TaskSignalState:
    analyzer = analyzer or ARCAtlasAnalyzer()
    inputs = tuple(analyzer.analyze(x) for x, _ in train)
    outputs = tuple(analyzer.analyze(y) for _, y in train)
    route_scores = {name: 0.05 for name in ROUTE_NAMES}
    group_norms = {name: 0.0 for name in ATLAS_NAMES}
    summary_rows: list[FloatArray] = []
    for (x, y), input_state, output_state in zip(train, inputs, outputs, strict=True):
        x = sanitize_grid(x)
        y = sanitize_grid(y)
        same_shape = x.shape == y.shape
        x_bg, y_bg = infer_background(x), infer_background(y)
        x_support = x != x_bg
        y_support = y != y_bg
        if same_shape:
            added = float(np.mean((~x_support) & y_support))
            removed = float(np.mean(x_support & (~y_support)))
            changed = float(np.mean(x != y))
            overlap = x_support & y_support
            recolored = float(np.mean((x != y) & overlap))
            same_counts = Counter(int(v) for v in x.ravel()) == Counter(int(v) for v in y.ravel())
            if changed < 1e-12:
                route_scores["identity_like"] += 3.0
            if recolored > 0 and added < 0.01 and removed < 0.01:
                route_scores["recolor"] += 2.5 + 4.0 * recolored
            if added > max(removed, 0.01):
                route_scores["draw_add"] += 2.0 + 5.0 * added
            if removed > max(added, 0.01):
                route_scores["erase_remove"] += 2.0 + 5.0 * removed
            if same_counts and changed > 0.02:
                route_scores["translate"] += 2.5
                route_scores["geometry"] += 1.0
            if changed > 0.05:
                route_scores["mixed"] += 0.5
        else:
            area_ratio = (y.size / max(1, x.size))
            if area_ratio > 1.15:
                route_scores["expand"] += 2.0 + min(3.0, area_ratio - 1.0)
            elif area_ratio < 0.85:
                route_scores["compress"] += 2.0 + min(3.0, 1.0 / max(area_ratio, 1e-6) - 1.0)
                route_scores["crop_extract"] += 1.0
            route_scores["geometry"] += 1.0
        object_delta = len(output_state.objects4) - len(input_state.objects4)
        if object_delta != 0 or any(obj.holes for obj in input_state.objects4 + output_state.objects4):
            route_scores["object_relational"] += 1.5
        if _separator_count(x) >= 2:
            route_scores["panel"] += 2.0
        if max(_periodicity_score(x), _periodicity_score(y)) > 0.82:
            route_scores["periodic"] += 2.0
        for name in ATLAS_NAMES:
            left = input_state.feature_groups[name]
            right = output_state.feature_groups[name]
            norm = float(np.linalg.norm(right - left) / max(1.0, np.sqrt(left.size)))
            group_norms[name] += norm
        summary_rows.append(
            np.concatenate(
                [
                    input_state.macro[:16],
                    output_state.macro[:16] - input_state.macro[:16],
                    np.asarray(
                        [
                            x.shape[0] / MAX_SIDE,
                            x.shape[1] / MAX_SIDE,
                            y.shape[0] / MAX_SIDE,
                            y.shape[1] / MAX_SIDE,
                            len(input_state.objects4) / 30.0,
                            len(output_state.objects4) / 30.0,
                            len(np.unique(x)) / PALETTE_SIZE,
                            len(np.unique(y)) / PALETTE_SIZE,
                        ],
                        dtype=np.float64,
                    ),
                ]
            )
        )
    count = max(1, len(train))
    for name in group_norms:
        group_norms[name] /= count
    route_total = sum(route_scores.values())
    route_probabilities = {name: route_scores[name] / route_total for name in ROUTE_NAMES}
    primary_route = max(route_probabilities, key=route_probabilities.get)

    atlas_scores = {name: 0.15 + group_norms[name] for name in ATLAS_NAMES}
    route_atlas = {
        "identity_like": ("spatial",),
        "recolor": ("color", "object"),
        "geometry": ("spatial", "haar", "object"),
        "crop_extract": ("object", "spatial"),
        "expand": ("spatial", "polyphase2", "polyphase3", "polyphase4"),
        "compress": ("spatial", "haar", "object"),
        "draw_add": ("object", "spatial", "haar"),
        "erase_remove": ("object", "spatial"),
        "translate": ("object", "spatial", "fourier"),
        "panel": ("spatial", "object", "polyphase2"),
        "periodic": ("polyphase2", "polyphase3", "polyphase4", "fourier"),
        "object_relational": ("object", "spatial", "color"),
        "mixed": ATLAS_NAMES,
    }
    for route, probability in route_probabilities.items():
        for atlas in route_atlas[route]:
            atlas_scores[atlas] += 2.5 * probability
    atlas_total = sum(atlas_scores.values())
    atlas_probabilities = {name: atlas_scores[name] / atlas_total for name in ATLAS_NAMES}

    mean_change = float(np.mean(list(group_norms.values())))
    object_complexity = float(np.mean([len(state.objects4) for state in inputs])) if inputs else 0.0
    resolution_scores = {
        "macro": 0.7 + max(0.0, 0.5 - mean_change),
        "meso": 0.8 + min(1.0, mean_change) + min(1.0, object_complexity / 10.0),
        "micro": 0.4 + min(1.5, 2.0 * mean_change) + min(1.0, object_complexity / 6.0),
    }
    resolution_total = sum(resolution_scores.values())
    resolution_probabilities = {name: resolution_scores[name] / resolution_total for name in RESOLUTION_NAMES}

    mean_summary = np.mean(np.vstack(summary_rows), axis=0) if summary_rows else np.zeros(40, dtype=np.float64)
    route_vector = np.asarray([route_probabilities[name] for name in ROUTE_NAMES], dtype=np.float64)
    atlas_vector = np.asarray([atlas_probabilities[name] for name in ATLAS_NAMES], dtype=np.float64)
    resolution_vector = np.asarray([resolution_probabilities[name] for name in RESOLUTION_NAMES], dtype=np.float64)
    residual_vector = np.asarray([group_norms[name] for name in ATLAS_NAMES], dtype=np.float64)
    summary_vector = np.concatenate([mean_summary, route_vector, atlas_vector, resolution_vector, residual_vector])
    return TaskSignalState(
        input_states=inputs,
        output_states=outputs,
        route_probabilities=route_probabilities,
        atlas_probabilities=atlas_probabilities,
        resolution_probabilities=resolution_probabilities,
        primary_route=primary_route,
        summary_vector=summary_vector,
        residual_group_norms=group_norms,
    )


__all__ = [
    "ARCAtlasAnalyzer",
    "ARCAtlasState",
    "AtlasObject",
    "ATLAS_NAMES",
    "RESOLUTION_NAMES",
    "ROUTE_NAMES",
    "TaskSignalState",
    "analyze_task_signal",
    "color_one_hot",
    "extract_objects",
    "haar2d_forward",
    "haar2d_inverse",
    "infer_background",
    "polyphase_analyze",
    "polyphase_synthesize",
    "sanitize_grid",
]
