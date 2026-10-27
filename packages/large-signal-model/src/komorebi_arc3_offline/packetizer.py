from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from typing import Iterable

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage

from .types import FloatArray, FrameComponent, FramePackets, IntFrame


@dataclass(frozen=True)
class PacketizerConfig:
    palette_size: int = 16
    maximum_components: int = 8
    coarse_dimension: int = 24
    fine_dimension: int = 48
    projection_seed: int = 731029


class FramePacketizer:
    """Convert a 64x64 ARC frame into nested coarse and fine packet states.

    The raw representation keeps interpretable packets: color mass, spatial
    occupancy, connected objects, polyphase occupancy, low-frequency spectral
    energy, and frame-to-frame change.  Fixed orthogonal projections then give
    compact coarse and fine states for Bayesian operator selection.
    """

    def __init__(self, config: PacketizerConfig | None = None) -> None:
        self.config = config or PacketizerConfig()
        self._coarse_projection: FloatArray | None = None
        self._fine_projection: FloatArray | None = None

    @staticmethod
    def _normalize_frame(frame: NDArray[np.integer]) -> IntFrame:
        array = np.asarray(frame, dtype=np.int16)
        if array.ndim == 3:
            array = array[-1]
        if array.ndim != 2:
            raise ValueError(f"frame must be two-dimensional, got {array.shape}")
        if array.shape != (64, 64):
            zoom = (64.0 / array.shape[0], 64.0 / array.shape[1])
            array = ndimage.zoom(array, zoom, order=0)
            array = np.asarray(array[:64, :64], dtype=np.int16)
            if array.shape != (64, 64):
                padded = np.zeros((64, 64), dtype=np.int16)
                padded[: array.shape[0], : array.shape[1]] = array
                array = padded
        return array

    def infer_background(self, frame: IntFrame) -> int:
        values, counts = np.unique(frame, return_counts=True)
        if values.size == 0:
            return 0
        border = np.concatenate([frame[0], frame[-1], frame[:, 0], frame[:, -1]])
        border_values, border_counts = np.unique(border, return_counts=True)
        border_mode = int(border_values[np.argmax(border_counts)])
        global_mode = int(values[np.argmax(counts)])
        # Border evidence is usually more reliable in interactive games; fall
        # back to global mass when the border is highly mixed.
        if border_counts.max() >= 0.35 * border.size:
            return border_mode
        return global_mode

    def _components(self, frame: IntFrame, background: int) -> tuple[FrameComponent, ...]:
        components: list[FrameComponent] = []
        for color in np.unique(frame):
            color_int = int(color)
            if color_int == background:
                continue
            mask = frame == color_int
            labels, count = ndimage.label(mask)
            if count == 0:
                continue
            objects = ndimage.find_objects(labels)
            for label_index, slices in enumerate(objects, start=1):
                if slices is None:
                    continue
                ys, xs = slices
                object_mask = labels[ys, xs] == label_index
                area = int(object_mask.sum())
                if area <= 0:
                    continue
                y0, y1 = int(ys.start), int(ys.stop - 1)
                x0, x1 = int(xs.start), int(xs.stop - 1)
                cy, cx = ndimage.center_of_mass(mask, labels, label_index)
                width, height = x1 - x0 + 1, y1 - y0 + 1
                compactness = float(area / max(1, width * height))
                touches = x0 == 0 or y0 == 0 or x1 == 63 or y1 == 63
                components.append(
                    FrameComponent(
                        color=color_int,
                        area=area,
                        bbox=(x0, y0, x1, y1),
                        centroid=(float(cx), float(cy)),
                        compactness=compactness,
                        touches_border=touches,
                    )
                )
        components.sort(key=lambda item: (-item.area, item.color, item.centroid[1], item.centroid[0]))
        return tuple(components[: self.config.maximum_components])

    @staticmethod
    def _spatial_pool(frame: IntFrame, background: int, blocks: int) -> list[float]:
        output: list[float] = []
        size = 64 // blocks
        for by in range(blocks):
            for bx in range(blocks):
                cell = frame[by * size : (by + 1) * size, bx * size : (bx + 1) * size]
                non_background = cell != background
                output.append(float(non_background.mean()))
                if np.any(non_background):
                    output.append(float(cell[non_background].mean() / 15.0))
                else:
                    output.append(0.0)
        return output

    @staticmethod
    def _phase_energy(frame: IntFrame, background: int, modulus: int) -> tuple[float, ...]:
        foreground = (frame != background).astype(float)
        result: list[float] = []
        for ry in range(modulus):
            for rx in range(modulus):
                result.append(float(foreground[ry::modulus, rx::modulus].mean()))
        return tuple(result)

    @staticmethod
    def _spectral_features(frame: IntFrame, background: int) -> list[float]:
        foreground = (frame != background).astype(float)
        spectrum = np.abs(np.fft.rfft2(foreground)) / foreground.size
        patch = spectrum[:4, :4]
        return np.log1p(40.0 * patch).ravel().astype(float).tolist()

    def _component_features(self, components: tuple[FrameComponent, ...]) -> list[float]:
        rows: list[float] = []
        for index in range(self.config.maximum_components):
            if index < len(components):
                component = components[index]
                x0, y0, x1, y1 = component.bbox
                rows.extend(
                    [
                        component.color / 15.0,
                        component.area / 4096.0,
                        component.centroid[0] / 63.0,
                        component.centroid[1] / 63.0,
                        component.width / 64.0,
                        component.height / 64.0,
                        component.compactness,
                        float(component.touches_border),
                    ]
                )
            else:
                rows.extend([0.0] * 8)
        return rows

    @staticmethod
    def _change_features(frame: IntFrame, previous_frame: IntFrame | None) -> tuple[list[float], float, list[tuple[int, int, str]]]:
        if previous_frame is None:
            return [0.0] * 10, 0.0, []
        previous = np.asarray(previous_frame, dtype=np.int16)
        changed = frame != previous
        fraction = float(changed.mean())
        if not np.any(changed):
            return [0.0] * 10, 0.0, []
        ys, xs = np.nonzero(changed)
        x0, x1 = int(xs.min()), int(xs.max())
        y0, y1 = int(ys.min()), int(ys.max())
        centroid_x = float(xs.mean()) / 63.0
        centroid_y = float(ys.mean()) / 63.0
        features = [
            fraction,
            centroid_x,
            centroid_y,
            x0 / 63.0,
            y0 / 63.0,
            x1 / 63.0,
            y1 / 63.0,
            float(np.mean(np.abs(frame.astype(float) - previous.astype(float))) / 15.0),
            float(np.mean(changed[::2, ::2])),
            float(np.mean(changed[1::2, 1::2])),
        ]
        points = [
            (int(round(xs.mean())), int(round(ys.mean())), "change-centroid"),
            (x0, y0, "change-corner"),
            (x1, y1, "change-corner"),
        ]
        return features, fraction, points

    def _build_raw(self, frame: IntFrame, previous_frame: IntFrame | None) -> tuple[FloatArray, tuple[FrameComponent, ...], int, float, tuple[float, ...], tuple[float, ...], list[tuple[int, int, str]]]:
        background = self.infer_background(frame)
        components = self._components(frame, background)
        histogram = np.bincount(
            np.clip(frame.ravel(), 0, self.config.palette_size - 1),
            minlength=self.config.palette_size,
        ).astype(float)
        histogram /= max(1.0, histogram.sum())
        foreground = frame != background
        non_background_fraction = float(foreground.mean())
        if np.any(foreground):
            ys, xs = np.nonzero(foreground)
            bbox = [xs.min() / 63.0, ys.min() / 63.0, xs.max() / 63.0, ys.max() / 63.0]
        else:
            bbox = [0.0, 0.0, 0.0, 0.0]
        horizontal = float(np.mean(frame[:, 1:] != frame[:, :-1]))
        vertical = float(np.mean(frame[1:, :] != frame[:-1, :]))
        phase2 = self._phase_energy(frame, background, 2)
        phase4 = self._phase_energy(frame, background, 4)
        change, change_fraction, change_points = self._change_features(frame, previous_frame)
        raw_values: list[float] = []
        raw_values.extend(histogram.tolist())
        raw_values.extend([non_background_fraction, horizontal, vertical, len(components) / self.config.maximum_components])
        raw_values.extend(bbox)
        raw_values.extend(self._spatial_pool(frame, background, 2))
        raw_values.extend(self._spatial_pool(frame, background, 4))
        raw_values.extend(phase2)
        raw_values.extend(phase4)
        raw_values.extend(self._spectral_features(frame, background))
        raw_values.extend(self._component_features(components))
        raw_values.extend(change)

        salient: list[tuple[int, int, str]] = []
        for index, component in enumerate(components):
            x, y = component.center_pixel
            salient.append((x, y, f"component-{index}"))
            x0, y0, x1, y1 = component.bbox
            salient.extend(
                [
                    (x0, y0, f"component-{index}-corner"),
                    (x1, y0, f"component-{index}-corner"),
                    (x0, y1, f"component-{index}-corner"),
                    (x1, y1, f"component-{index}-corner"),
                ]
            )
        salient.extend(change_points)
        return (
            np.asarray(raw_values, dtype=np.float64),
            components,
            background,
            change_fraction,
            phase2,
            phase4,
            salient,
        )

    def _projection(self, raw_dimension: int, output_dimension: int, salt: int) -> FloatArray:
        rng = np.random.default_rng(self.config.projection_seed + salt + raw_dimension * 101)
        matrix = rng.normal(size=(raw_dimension, output_dimension))
        q, _ = np.linalg.qr(matrix)
        if q.shape[1] < output_dimension:
            raise ValueError("raw feature dimension is too small for requested projection")
        return q[:, :output_dimension].T.astype(np.float64)

    @staticmethod
    def _standardize(raw: FloatArray) -> FloatArray:
        array = np.asarray(raw, dtype=np.float64)
        # Raw features are mostly in [0,1].  A smooth signed remapping prevents
        # high-count packets from dominating while keeping zero meaningful.
        return np.tanh(2.5 * array)

    @staticmethod
    def _signature(frame: IntFrame) -> str:
        digest = blake2b(frame.tobytes(), digest_size=12)
        return digest.hexdigest()

    def resolve(self, frame: NDArray[np.integer], previous_frame: NDArray[np.integer] | None = None) -> FramePackets:
        normalized = self._normalize_frame(frame)
        previous = None if previous_frame is None else self._normalize_frame(previous_frame)
        raw, components, background, change_fraction, phase2, phase4, salient = self._build_raw(normalized, previous)
        standardized = self._standardize(raw)
        if self._coarse_projection is None or self._coarse_projection.shape[1] != standardized.size:
            self._coarse_projection = self._projection(standardized.size, self.config.coarse_dimension, 17)
            self._fine_projection = self._projection(standardized.size, self.config.fine_dimension, 53)
        coarse = self._coarse_projection @ standardized
        fine = self._fine_projection @ standardized
        coarse /= max(1.0, np.linalg.norm(coarse))
        fine /= max(1.0, np.linalg.norm(fine))

        # Add deterministic grid probes after object points.  They serve as a
        # polyphase fallback when no connected component supplies a click target.
        grid = [8, 24, 40, 56]
        salient.extend((x, y, "phase4-grid") for y in grid for x in grid)
        salient.extend([(32, 32, "center"), (4, 4, "corner"), (59, 4, "corner"), (4, 59, "corner"), (59, 59, "corner")])
        unique: dict[tuple[int, int], tuple[int, int, str]] = {}
        for x, y, source in salient:
            key = (int(np.clip(x, 0, 63)), int(np.clip(y, 0, 63)))
            unique.setdefault(key, (key[0], key[1], source))

        return FramePackets(
            coarse=np.asarray(coarse, dtype=np.float64),
            fine=np.asarray(fine, dtype=np.float64),
            raw=raw,
            signature=self._signature(normalized),
            background=background,
            components=components,
            salient_points=tuple(unique.values()),
            change_fraction=change_fraction,
            non_background_fraction=float(np.mean(normalized != background)),
            phase2_energy=phase2,
            phase4_energy=phase4,
        )
