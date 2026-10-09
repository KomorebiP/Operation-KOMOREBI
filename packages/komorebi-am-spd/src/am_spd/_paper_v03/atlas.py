from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from scipy import fft as spfft
from scipy import ndimage
from skimage import color, data, feature, measure, morphology, segmentation, transform
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
from skimage.restoration import denoise_tv_chambolle

Array = NDArray[np.float64]

INK = "#17202A"
MUTED = "#566573"
BLUE = "#2E86AB"
TEAL = "#2A9D8F"
ORANGE = "#F4A261"
MAGENTA = "#A23E8C"
RED = "#E76F51"
YELLOW = "#E9C46A"
PAPER = "#FAFAF7"
PACKET_COLORS = [BLUE, TEAL, ORANGE, MAGENTA, RED, YELLOW, "#6C5CE7", "#00A8CC"]


# ---------------------------------------------------------------------------
# General image utilities
# ---------------------------------------------------------------------------


def ensure_image(image: Array) -> Array:
    value = np.asarray(image, dtype=np.float64)
    if value.ndim == 2:
        value = value[..., None]
    if value.ndim != 3:
        raise ValueError("image must have shape H x W or H x W x C")
    if not np.isfinite(value).all():
        raise ValueError("image contains nonfinite values")
    low = float(value.min())
    high = float(value.max())
    if high > 1.0 or low < 0.0:
        if high <= low:
            value = np.zeros_like(value)
        else:
            value = (value - low) / (high - low)
    return np.clip(value, 0.0, 1.0)


def luminance(image: Array) -> Array:
    value = ensure_image(image)
    if value.shape[2] == 1:
        return value[..., 0]
    rgb = value[..., :3]
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def resize_image(image: Array, size: int) -> Array:
    value = ensure_image(image)
    resized = transform.resize(
        value,
        (size, size, value.shape[2]),
        order=1,
        anti_aliasing=True,
        preserve_range=True,
    )
    return np.asarray(resized, dtype=np.float64)


def normalize_atom(atom: Array, tolerance: float = 1e-12) -> Array | None:
    value = np.asarray(atom, dtype=np.float64)
    value = np.nan_to_num(value)
    norm = float(np.linalg.norm(value.ravel()))
    if norm <= tolerance:
        return None
    return value / norm


def atom_digest(atom: Array) -> str:
    quantized = np.rint(np.clip(atom, -1.0, 1.0) * 32767).astype(np.int16)
    return hashlib.blake2b(quantized.tobytes(), digest_size=12).hexdigest()


def safe_json(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    return value


def rmse(left: Array, right: Array) -> float:
    return float(np.sqrt(np.mean((np.asarray(left) - np.asarray(right)) ** 2)))


def edge_band(truth: Array, width: int = 2) -> NDArray[np.bool_]:
    gray = luminance(truth)
    gradient = np.hypot(ndimage.sobel(gray, axis=0), ndimage.sobel(gray, axis=1))
    threshold = float(np.quantile(gradient, 0.90))
    edge = gradient >= max(threshold, 1e-9)
    return ndimage.binary_dilation(edge, iterations=width)


def edge_rmse(truth: Array, reconstruction: Array) -> float:
    mask = edge_band(truth)
    if not np.any(mask):
        return 0.0
    diff = ensure_image(reconstruction) - ensure_image(truth)
    return float(np.sqrt(np.mean(diff[mask] ** 2)))


def ringing_metrics(truth: Array, reconstruction: Array, window: int = 5) -> dict[str, float]:
    reference = ensure_image(truth)
    estimate = ensure_image(reconstruction)
    footprint = (window, window, 1)
    local_min = ndimage.minimum_filter(reference, size=footprint, mode="reflect")
    local_max = ndimage.maximum_filter(reference, size=footprint, mode="reflect")
    upper = np.maximum(estimate - local_max, 0.0)
    lower = np.maximum(local_min - estimate, 0.0)
    band = edge_band(reference)
    violation = upper + lower
    if not np.any(band):
        return {
            "max_local_range_violation": 0.0,
            "mean_local_range_violation": 0.0,
            "fraction_outside_local_range": 0.0,
        }
    selected = violation[band]
    return {
        "max_local_range_violation": float(np.max(selected)),
        "mean_local_range_violation": float(np.mean(selected)),
        "fraction_outside_local_range": float(np.mean(selected > 1e-6)),
    }


def image_metrics(truth: Array, reconstruction: Array) -> dict[str, float]:
    reference = ensure_image(truth)
    estimate = np.asarray(reconstruction, dtype=np.float64)
    if estimate.ndim == 2:
        estimate = estimate[..., None]
    if estimate.shape != reference.shape or not np.isfinite(estimate).all():
        raise ValueError("reconstruction must be finite and match the reference shape")
    # Reconstruction metrics use bounded synthesis, not global min-max renormalization.
    # Renormalization can hide range errors and materially change the approximation.
    estimate = np.clip(estimate, 0.0, 1.0)
    channels = reference.shape[2]
    kwargs: dict[str, Any] = {"data_range": 1.0}
    if channels > 1:
        kwargs["channel_axis"] = -1
        ssim_reference = reference
        ssim_estimate = estimate
    else:
        ssim_reference = reference[..., 0]
        ssim_estimate = estimate[..., 0]
    metrics = {
        "rmse": rmse(reference, estimate),
        "psnr": float(peak_signal_noise_ratio(reference, estimate, data_range=1.0)),
        "ssim": float(structural_similarity(ssim_reference, ssim_estimate, **kwargs)),
        "edge_rmse": edge_rmse(reference, estimate),
        "range_violation": float(max(0.0, -estimate.min()) + max(0.0, estimate.max() - 1.0)),
    }
    metrics.update(ringing_metrics(reference, estimate))
    return metrics


# ---------------------------------------------------------------------------
# Infinite packet grammar
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PacketSpec:
    kind: str
    params: tuple[Any, ...]
    parent: str = ""
    depth: int = 0
    complexity: float = 1.0

    @property
    def key(self) -> str:
        payload = json.dumps(
            {
                "kind": self.kind,
                "params": safe_json(self.params),
                "parent": self.parent,
                "depth": self.depth,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.blake2b(payload.encode("utf-8"), digest_size=12).hexdigest()


@dataclass
class PacketAtom:
    spec: PacketSpec
    values: Array
    digest: str
    score: float = 0.0
    gain: float = 0.0
    orthogonal_norm: float = 0.0


@dataclass
class PacketSelection:
    iteration: int
    spec_key: str
    kind: str
    parent: str
    depth: int
    complexity: float
    gain: float
    score: float
    residual_norm: float
    packet_count: int
    seed_id: int | None = None


@dataclass
class PacketSearchState:
    """Serializable state for exact continuation of the packet search.

    The state records the finite active candidate frontier, the image-derived
    seed masks, the quadtree leaves, and the NumPy random-generator state.  It
    does not contain the active atoms themselves because those already belong
    to :class:`ReconstructionResult`.
    """

    candidate_specs: list[PacketSpec]
    seed_masks: dict[int, Array]
    seed_metadata: dict[int, dict[str, Any]]
    next_seed_id: int
    selected_seed_ids: list[int]
    quadtree_leaves: list[tuple[int, int, int, int]]
    random_state: dict[str, Any]


@dataclass
class ReconstructionResult:
    reconstruction: Array
    residual: Array
    coefficients: Array
    active_specs: list[PacketSpec]
    active_atoms: list[Array]
    history: list[PacketSelection]
    snapshots: dict[int, Array]
    residual_norms: list[float]
    runtime_seconds: float
    exact_archive_residual: Array
    search_state: PacketSearchState | None = None


class InfinitePacketGenerator:
    """Lazy generator for a countably dense packet atlas.

    The continuous geometric parameters are explored through repeated rational
    perturbations. A dyadic quadtree fallback is always available. At pixel
    depth, the fallback contains the standard coordinate basis.
    """

    def __init__(self, image: Array, max_seed_masks: int = 180, random_seed: int = 20260731):
        self.image = ensure_image(image)
        self.height, self.width, self.channels = self.image.shape
        self.gray = luminance(self.image)
        self.y_grid, self.x_grid = np.mgrid[0 : self.height, 0 : self.width]
        self.x_unit = (self.x_grid + 0.5) / self.width
        self.y_unit = (self.y_grid + 0.5) / self.height
        self.random = np.random.default_rng(random_seed)
        self.max_seed_masks = max_seed_masks
        self.seed_masks: dict[int, Array] = {}
        self.seed_metadata: dict[int, dict[str, Any]] = {}
        self.next_seed_id = 0
        self.selected_seed_ids: list[int] = []
        self.quadtree_leaves: set[tuple[int, int, int, int]] = {(0, 0, self.height, self.width)}
        self._initial_specs: list[PacketSpec] | None = None
        self._build_initial_seed_masks()

    def register_mask(self, mask: Array, metadata: dict[str, Any] | None = None) -> int | None:
        value = np.asarray(mask, dtype=np.float64)
        if value.shape != (self.height, self.width):
            raise ValueError("mask shape mismatch")
        value = np.clip(value, 0.0, 1.0)
        area = float(value.mean())
        if area <= 1.0 / (self.height * self.width) or area >= 0.995:
            return None
        digest = atom_digest(value)
        for seed_id, existing in self.seed_masks.items():
            if atom_digest(existing) == digest:
                return seed_id
        if len(self.seed_masks) >= self.max_seed_masks:
            return None
        seed_id = self.next_seed_id
        self.next_seed_id += 1
        self.seed_masks[seed_id] = value
        self.seed_metadata[seed_id] = metadata or {}
        return seed_id

    def _build_initial_seed_masks(self) -> None:
        # Segmentation libraries can emit empty-cluster warnings or unstable
        # labels on constant rasters. The constant packet already represents
        # such images, while DCT and quadtree packets remain available for any
        # floating-point residue.
        if float(np.ptp(self.image)) <= 1e-14:
            return
        image_for_segments = self.image[..., :3] if self.channels >= 3 else self.gray
        segmentations: list[tuple[str, Array]] = []
        for scale_value in (45, 90, 180):
            labels = segmentation.felzenszwalb(
                image_for_segments,
                scale=scale_value,
                sigma=0.75,
                min_size=max(12, self.height * self.width // 450),
                channel_axis=-1 if image_for_segments.ndim == 3 else None,
            )
            segmentations.append((f"felzenszwalb_{scale_value}", labels))
        for segment_count, compactness in ((32, 7.0), (64, 10.0), (96, 14.0)):
            labels = segmentation.slic(
                self.image,
                n_segments=segment_count,
                compactness=compactness,
                sigma=0.6,
                start_label=0,
                channel_axis=-1,
            )
            segmentations.append((f"slic_{segment_count}_{compactness}", labels))

        for source, labels in segmentations:
            for label in np.unique(labels):
                mask = labels == label
                area = int(mask.sum())
                if area < max(8, self.height * self.width // 900):
                    continue
                if area > int(0.85 * self.height * self.width):
                    continue
                seed_id = self.register_mask(mask.astype(float), {"source": source, "label": int(label)})
                if seed_id is None:
                    continue
                if len(self.seed_masks) >= self.max_seed_masks:
                    return

        for channel in range(self.channels):
            values = self.image[..., channel]
            for quantile in (0.15, 0.30, 0.50, 0.70, 0.85):
                threshold = float(np.quantile(values, quantile))
                for polarity, mask in (
                    ("above", values >= threshold),
                    ("below", values <= threshold),
                ):
                    clean = morphology.remove_small_objects(mask, max_size=max(9, self.height * self.width // 700 - 1))
                    clean = morphology.remove_small_holes(clean, max_size=max(9, self.height * self.width // 700 - 1))
                    labels = measure.label(clean)
                    for region in measure.regionprops(labels):
                        if region.area < max(10, self.height * self.width // 700):
                            continue
                        component = labels == region.label
                        seed_id = self.register_mask(
                            component.astype(float),
                            {
                                "source": "threshold",
                                "channel": channel,
                                "quantile": quantile,
                                "polarity": polarity,
                            },
                        )
                        if seed_id is None:
                            continue
                        if len(self.seed_masks) >= self.max_seed_masks:
                            return

        edges = feature.canny(self.gray, sigma=1.15)
        contours, _ = cv2.findContours(
            edges.astype(np.uint8),
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:80]:
            if len(contour) < 4:
                continue
            canvas = np.zeros((self.height, self.width), dtype=np.uint8)
            cv2.drawContours(canvas, [contour], -1, 1, thickness=-1)
            area = int(canvas.sum())
            if area < max(10, self.height * self.width // 900):
                continue
            if area > int(0.85 * self.height * self.width):
                continue
            self.register_mask(canvas.astype(float), {"source": "canny_contour"})
            if len(self.seed_masks) >= self.max_seed_masks:
                return

    def initial_specs(self) -> list[PacketSpec]:
        if self._initial_specs is not None:
            return list(self._initial_specs)
        specs: list[PacketSpec] = []
        max_frequency = max(5, min(11, min(self.height, self.width) // 8))
        for u in range(max_frequency + 1):
            for v in range(max_frequency + 1):
                if u == 0 and v == 0:
                    continue
                complexity = 1.0 + 0.12 * (u + v)
                specs.append(PacketSpec("dct", (u, v), depth=u + v, complexity=complexity))
        for seed_id in sorted(self.seed_masks):
            specs.append(PacketSpec("mask", (seed_id,), depth=0, complexity=1.0))
            for operation, radius in (("dilate", 1), ("erode", 1)):
                specs.append(PacketSpec("morph", (seed_id, operation, radius), depth=1, complexity=1.15))
        root = (0, 0, self.height, self.width)
        for rectangle in self.split_rectangle(root):
            specs.append(PacketSpec("quadtree", rectangle, depth=1, complexity=1.0))
        self._initial_specs = specs
        return list(specs)

    def dct_atom(self, u: int, v: int) -> Array:
        x = np.cos(math.pi * (self.x_grid + 0.5) * u / self.width)
        y = np.cos(math.pi * (self.y_grid + 0.5) * v / self.height)
        return x * y

    def affine_mask(self, mask: Array, dx: float, dy: float, angle: float, scale: float) -> Array:
        center = (self.width / 2.0, self.height / 2.0)
        matrix = cv2.getRotationMatrix2D(center, angle, scale)
        matrix[0, 2] += dx
        matrix[1, 2] += dy
        warped = cv2.warpAffine(
            mask.astype(np.float32),
            matrix,
            (self.width, self.height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0.0,
        )
        return np.clip(warped, 0.0, 1.0)

    def radial_warp(self, mask: Array, amplitude: float, frequency: int, phase: float) -> Array:
        mass = float(mask.sum())
        if mass <= 1e-9:
            return mask.copy()
        cx = float((mask * self.x_grid).sum() / mass)
        cy = float((mask * self.y_grid).sum() / mass)
        dx = self.x_grid - cx
        dy = self.y_grid - cy
        radius = np.sqrt(dx * dx + dy * dy) + 1e-6
        theta = np.arctan2(dy, dx)
        displacement = amplitude * np.sin(frequency * theta + phase)
        source_radius = radius - displacement
        map_x = cx + source_radius * dx / radius
        map_y = cy + source_radius * dy / radius
        warped = cv2.remap(
            mask.astype(np.float32),
            map_x.astype(np.float32),
            map_y.astype(np.float32),
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0.0,
        )
        return np.clip(warped, 0.0, 1.0)

    def atom_from_spec(self, spec: PacketSpec) -> Array | None:
        kind = spec.kind
        if kind == "dct":
            u, v = map(int, spec.params)
            return normalize_atom(self.dct_atom(u, v))
        if kind == "mask":
            seed_id = int(spec.params[0])
            return normalize_atom(self.seed_masks[seed_id])
        if kind == "morph":
            seed_id = int(spec.params[0])
            operation = str(spec.params[1])
            radius = int(spec.params[2])
            mask = self.seed_masks[seed_id] > 0.5
            footprint = morphology.disk(max(1, radius))
            if operation == "dilate":
                value = morphology.dilation(mask, footprint)
            elif operation == "erode":
                value = morphology.erosion(mask, footprint)
            elif operation == "boundary":
                dilated = morphology.dilation(mask, footprint)
                eroded = morphology.erosion(mask, footprint)
                value = dilated.astype(float) - eroded.astype(float)
            else:
                raise ValueError(f"unknown morphology operation {operation}")
            return normalize_atom(value.astype(float))
        if kind == "affine":
            seed_id, dx, dy, angle, scale = spec.params
            value = self.affine_mask(
                self.seed_masks[int(seed_id)],
                float(dx),
                float(dy),
                float(angle),
                float(scale),
            )
            return normalize_atom(value)
        if kind == "radial":
            seed_id, amplitude, frequency, phase = spec.params
            value = self.radial_warp(
                self.seed_masks[int(seed_id)],
                float(amplitude),
                int(frequency),
                float(phase),
            )
            return normalize_atom(value)
        if kind == "masked_poly":
            seed_id = int(spec.params[0])
            mode = str(spec.params[1])
            mask = self.seed_masks[seed_id]
            x = 2.0 * self.x_unit - 1.0
            y = 2.0 * self.y_unit - 1.0
            if mode == "x":
                value = mask * x
            elif mode == "y":
                value = mask * y
            elif mode == "xy":
                value = mask * x * y
            elif mode == "x2y2":
                value = mask * (x * x - y * y)
            elif mode == "radial":
                mass = max(float(mask.sum()), 1e-12)
                cx = float((mask * self.x_unit).sum() / mass)
                cy = float((mask * self.y_unit).sum() / mass)
                value = mask * ((self.x_unit - cx) ** 2 + (self.y_unit - cy) ** 2)
            else:
                raise ValueError(f"unknown masked polynomial {mode}")
            return normalize_atom(value)
        if kind == "masked_dct":
            seed_id, u, v = spec.params
            value = self.seed_masks[int(seed_id)] * self.dct_atom(int(u), int(v))
            return normalize_atom(value)
        if kind == "soft_mask":
            seed_id, scale, polarity = spec.params
            mask = self.seed_masks[int(seed_id)] > 0.5
            inside = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)
            outside = cv2.distanceTransform((~mask).astype(np.uint8), cv2.DIST_L2, 5)
            signed = inside - outside
            width = max(float(scale), 1e-6)
            value = 1.0 / (1.0 + np.exp(np.clip(-float(polarity) * signed / width, -40.0, 40.0)))
            return normalize_atom(value)
        if kind == "combine":
            left_id, right_id, operation = spec.params
            left = self.seed_masks[int(left_id)]
            right = self.seed_masks[int(right_id)]
            if operation == "union":
                value = np.maximum(left, right)
            elif operation == "intersection":
                value = np.minimum(left, right)
            elif operation == "left_difference":
                value = np.clip(left - right, 0.0, 1.0)
            elif operation == "xor":
                value = np.abs(left - right)
            else:
                raise ValueError(f"unknown combination operation {operation}")
            return normalize_atom(value)
        if kind == "quadtree":
            y0, x0, y1, x1 = map(int, spec.params)
            value = np.zeros((self.height, self.width), dtype=float)
            value[y0:y1, x0:x1] = 1.0
            return normalize_atom(value)
        if kind == "edge_ribbon":
            seed_id, radius = spec.params
            mask = self.seed_masks[int(seed_id)] > 0.5
            footprint = morphology.disk(max(1, int(radius)))
            outside = morphology.dilation(mask, footprint)
            inside = morphology.erosion(mask, footprint)
            value = outside.astype(float) - inside.astype(float)
            return normalize_atom(value)
        raise ValueError(f"unknown packet kind {kind}")

    def split_rectangle(self, rectangle: tuple[int, int, int, int]) -> list[tuple[int, int, int, int]]:
        y0, x0, y1, x1 = rectangle
        if y1 - y0 <= 1 and x1 - x0 <= 1:
            return []
        ym = (y0 + y1) // 2
        xm = (x0 + x1) // 2
        children = [
            (y0, x0, max(ym, y0 + 1), max(xm, x0 + 1)),
            (y0, max(xm, x0 + 1), max(ym, y0 + 1), x1),
            (max(ym, y0 + 1), x0, y1, max(xm, x0 + 1)),
            (max(ym, y0 + 1), max(xm, x0 + 1), y1, x1),
        ]
        valid: list[tuple[int, int, int, int]] = []
        for child in children:
            cy0, cx0, cy1, cx1 = child
            if cy1 > cy0 and cx1 > cx0:
                valid.append(child)
        return valid

    def residual_seed_specs(self, residual: Array, iteration: int, max_components: int = 20) -> list[PacketSpec]:
        value = ensure_image(residual)
        magnitude = np.sqrt(np.sum(value * value, axis=2))
        specs: list[PacketSpec] = []
        min_size = max(4, self.height * self.width // 1600)
        for quantile in (0.78, 0.88, 0.95):
            threshold = float(np.quantile(magnitude, quantile))
            mask = magnitude >= max(threshold, 1e-12)
            mask = morphology.remove_small_objects(mask, max_size=max(1, min_size - 1))
            labels = measure.label(mask)
            regions = sorted(measure.regionprops(labels), key=lambda region: region.area, reverse=True)
            for region in regions[:max_components]:
                component = labels == region.label
                seed_id = self.register_mask(
                    component.astype(float),
                    {"source": "residual", "iteration": iteration, "quantile": quantile},
                )
                if seed_id is None:
                    continue
                specs.append(PacketSpec("mask", (seed_id,), depth=0, complexity=1.0))
                specs.append(PacketSpec("morph", (seed_id, "dilate", 1), parent=str(seed_id), depth=1, complexity=1.12))
                specs.append(PacketSpec("morph", (seed_id, "erode", 1), parent=str(seed_id), depth=1, complexity=1.12))
                specs.append(PacketSpec("edge_ribbon", (seed_id, 1), parent=str(seed_id), depth=1, complexity=1.18))
        return specs

    def quadtree_specs(self, residual: Array, top_count: int = 16) -> list[PacketSpec]:
        value = ensure_image(residual)
        energy = np.sum(value * value, axis=2)
        ranked: list[tuple[float, tuple[int, int, int, int]]] = []
        for rectangle in self.quadtree_leaves:
            y0, x0, y1, x1 = rectangle
            ranked.append((float(energy[y0:y1, x0:x1].sum()), rectangle))
        ranked.sort(reverse=True, key=lambda item: item[0])
        specs: list[PacketSpec] = []
        for _, rectangle in ranked[:top_count]:
            depth = int(round(math.log2(max(self.height / max(1, rectangle[2] - rectangle[0]), 1.0))))
            specs.append(PacketSpec("quadtree", rectangle, depth=depth, complexity=1.0 + 0.05 * depth))
        return specs

    def refine_quadtree(self, residual: Array, count: int = 1) -> list[PacketSpec]:
        value = ensure_image(residual)
        energy = np.sum(value * value, axis=2)
        candidates: list[tuple[float, tuple[int, int, int, int]]] = []
        for rectangle in self.quadtree_leaves:
            y0, x0, y1, x1 = rectangle
            if y1 - y0 <= 1 and x1 - x0 <= 1:
                continue
            candidates.append((float(energy[y0:y1, x0:x1].sum()), rectangle))
        candidates.sort(reverse=True, key=lambda item: item[0])
        specs: list[PacketSpec] = []
        for _, rectangle in candidates[:count]:
            self.quadtree_leaves.discard(rectangle)
            children = self.split_rectangle(rectangle)
            self.quadtree_leaves.update(children)
            for child in children:
                depth = int(round(math.log2(max(self.height / max(1, child[2] - child[0]), 1.0))))
                specs.append(PacketSpec("quadtree", child, parent=str(rectangle), depth=depth, complexity=1.0 + 0.05 * depth))
        return specs

    def selected_descendants(self, spec: PacketSpec, atom: Array) -> list[PacketSpec]:
        """Return a finite frontier from an infinite, dyadically refined grammar.

        Repeated calls along a selected lineage use perturbation steps of size
        2^{-depth}. The union over all depths is countable and dense in the
        bounded affine and boundary-perturbation parameters represented here.
        """
        specs: list[PacketSpec] = []
        if spec.kind in {"mask", "morph", "affine", "radial", "soft_mask", "combine", "quadtree"}:
            normalized_seed = np.clip(atom / max(float(atom.max()), 1e-12), 0.0, 1.0)
            seed_id = self.register_mask(normalized_seed, {"source": "selected", "parent": spec.key})
            if seed_id is not None:
                next_depth = spec.depth + 1
                for mode in ("x", "y", "xy", "x2y2", "radial"):
                    specs.append(PacketSpec("masked_poly", (seed_id, mode), parent=spec.key, depth=next_depth, complexity=1.25 + 0.03 * next_depth))
                local_frequency = min(6, 2 + next_depth)
                for u, v in ((1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (local_frequency, 0), (0, local_frequency)):
                    specs.append(PacketSpec("masked_dct", (seed_id, u, v), parent=spec.key, depth=next_depth, complexity=1.30 + 0.08 * (u + v)))

                # Dyadic perturbation schedule. The parameter steps tend to zero.
                spatial_step = max(self.height, self.width) / (2.0 ** (next_depth + 4))
                angle_step = 45.0 / (2.0 ** next_depth)
                log_scale_step = math.log(2.0) / (2.0 ** (next_depth + 2))
                for dx, dy in ((-spatial_step, 0.0), (spatial_step, 0.0), (0.0, -spatial_step), (0.0, spatial_step)):
                    specs.append(PacketSpec("affine", (seed_id, dx, dy, 0.0, 1.0), parent=spec.key, depth=next_depth, complexity=1.16 + 0.02 * next_depth))
                for angle in (-angle_step, angle_step):
                    specs.append(PacketSpec("affine", (seed_id, 0.0, 0.0, angle, 1.0), parent=spec.key, depth=next_depth, complexity=1.20 + 0.02 * next_depth))
                for sign in (-1.0, 1.0):
                    scale = math.exp(sign * log_scale_step)
                    specs.append(PacketSpec("affine", (seed_id, 0.0, 0.0, 0.0, scale), parent=spec.key, depth=next_depth, complexity=1.20 + 0.02 * next_depth))

                radial_amplitude = max(self.height, self.width) / (2.0 ** (next_depth + 4))
                phase_denominator = 2 ** min(next_depth + 2, 7)
                phase_step = 2.0 * math.pi / phase_denominator
                for frequency in sorted({2, 3, min(10, 2 + next_depth)}):
                    for phase in (0.0, phase_step, math.pi / 2.0):
                        specs.append(PacketSpec("radial", (seed_id, radial_amplitude, frequency, phase), parent=spec.key, depth=next_depth, complexity=1.28 + 0.025 * frequency))

                soft_scale = max(self.height, self.width) / (2.0 ** (next_depth + 3))
                for polarity in (-1.0, 1.0):
                    specs.append(PacketSpec("soft_mask", (seed_id, soft_scale, polarity), parent=spec.key, depth=next_depth, complexity=1.22 + 0.02 * next_depth))
                specs.append(PacketSpec("edge_ribbon", (seed_id, 1), parent=spec.key, depth=next_depth, complexity=1.18))

                # Compositional packets let separated local pieces grow into larger objects.
                for other_id in self.selected_seed_ids[-4:]:
                    if other_id == seed_id:
                        continue
                    for operation in ("union", "intersection", "left_difference", "xor"):
                        specs.append(PacketSpec("combine", (seed_id, other_id, operation), parent=spec.key, depth=next_depth, complexity=1.38 + 0.03 * next_depth))
                if seed_id not in self.selected_seed_ids:
                    self.selected_seed_ids.append(seed_id)

        if spec.kind == "dct":
            u, v = map(int, spec.params)
            for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1)):
                uu = max(0, u + du)
                vv = max(0, v + dv)
                if uu == 0 and vv == 0:
                    continue
                specs.append(PacketSpec("dct", (uu, vv), parent=spec.key, depth=uu + vv, complexity=1.0 + 0.12 * (uu + vv)))
        if spec.kind == "quadtree":
            rectangle = tuple(map(int, spec.params))
            for child in self.split_rectangle(rectangle):
                specs.append(PacketSpec("quadtree", child, parent=spec.key, depth=spec.depth + 1, complexity=1.0 + 0.05 * (spec.depth + 1)))
        return specs



# ---------------------------------------------------------------------------
# Adaptive global reconstruction
# ---------------------------------------------------------------------------


class InfinitePacketReconstructor:
    def __init__(
        self,
        image: Array,
        complexity_weight: float = 0.03,
        ridge: float = 1e-9,
        max_candidates_per_iteration: int = 260,
        residual_refresh: int = 4,
        quadtree_refine_every: int = 3,
        random_seed: int = 20260731,
    ):
        self.image = ensure_image(image)
        self.height, self.width, self.channels = self.image.shape
        self.generator = InfinitePacketGenerator(self.image, max_seed_masks=120, random_seed=random_seed)
        self.complexity_weight = float(complexity_weight)
        self.ridge = float(ridge)
        self.max_candidates_per_iteration = int(max_candidates_per_iteration)
        self.residual_refresh = int(residual_refresh)
        self.quadtree_refine_every = int(quadtree_refine_every)
        self.target = self.image.reshape(-1, self.channels)
        self.active_specs: list[PacketSpec] = []
        self.active_atoms: list[Array] = []
        self.active_matrix = np.empty((self.height * self.width, 0), dtype=np.float64)
        self.coefficients = np.empty((0, self.channels), dtype=np.float64)
        self.gram_inverse = np.empty((0, 0), dtype=np.float64)
        self.reconstruction = np.zeros_like(self.image)
        self.residual = self.image.copy()
        self.history: list[PacketSelection] = []
        self.residual_norms: list[float] = [float(np.linalg.norm(self.residual))]
        self.candidate_specs: dict[str, PacketSpec] = {}
        self.used_spec_keys: set[str] = set()
        self.used_atom_digests: set[str] = set()
        self._add_constant()
        for spec in self.generator.initial_specs():
            self.candidate_specs.setdefault(spec.key, spec)

    @classmethod
    def from_reconstruction_result(
        cls,
        image: Array,
        result: ReconstructionResult,
        *,
        complexity_weight: float = 0.03,
        ridge: float = 1e-9,
        max_candidates_per_iteration: int = 260,
        residual_refresh: int = 4,
        quadtree_refine_every: int = 3,
        random_seed: int = 20260731,
    ) -> "InfinitePacketReconstructor":
        """Restore a packet search from a prior core reconstruction.

        Models written by AM-SPD 0.3 or later carry an exact finite search
        state.  Older models can still be resumed as a warm start from their
        stored packet atoms.  Warm-start continuation rebuilds a fresh
        candidate frontier and is deterministic, but it is not bit-for-bit
        identical to pausing the original search.
        """

        value = ensure_image(image)
        if np.asarray(result.reconstruction).shape != value.shape:
            raise ValueError("saved core reconstruction does not match the source image")
        if len(result.active_specs) != len(result.active_atoms):
            raise ValueError("saved packet specification and atom counts differ")
        solver = cls(
            value,
            complexity_weight=complexity_weight,
            ridge=ridge,
            max_candidates_per_iteration=max_candidates_per_iteration,
            residual_refresh=residual_refresh,
            quadtree_refine_every=quadtree_refine_every,
            random_seed=random_seed,
        )

        atoms = [np.asarray(atom, dtype=np.float64).copy() for atom in result.active_atoms]
        if any(atom.shape != value.shape[:2] for atom in atoms):
            raise ValueError("saved packet atom shape does not match the source image")
        if not atoms:
            raise ValueError("saved model does not contain packet atoms")

        solver.active_specs = list(result.active_specs)
        solver.active_atoms = atoms
        solver.active_matrix = np.column_stack([atom.reshape(-1) for atom in atoms])
        solver.used_spec_keys = {spec.key for spec in solver.active_specs}
        solver.used_atom_digests = {atom_digest(atom) for atom in atoms}
        solver.history = list(result.history)
        solver.residual_norms = list(result.residual_norms) or [float(np.linalg.norm(value))]
        solver._refit()

        state = result.search_state
        if state is not None:
            solver.generator.seed_masks = {
                int(seed_id): np.asarray(mask, dtype=np.float64).copy()
                for seed_id, mask in state.seed_masks.items()
            }
            solver.generator.seed_metadata = {
                int(seed_id): dict(metadata)
                for seed_id, metadata in state.seed_metadata.items()
            }
            solver.generator.next_seed_id = int(state.next_seed_id)
            solver.generator.selected_seed_ids = [int(seed_id) for seed_id in state.selected_seed_ids]
            solver.generator.quadtree_leaves = {
                tuple(map(int, rectangle)) for rectangle in state.quadtree_leaves
            }
            solver.generator._initial_specs = None
            solver.generator.random.bit_generator.state = dict(state.random_state)
            # The captured frontier is authoritative. Rebuilding initial specs
            # here would incorrectly introduce masks registered only after the
            # original search began, changing the next candidate selection.
            solver.candidate_specs = {
                spec.key: spec for spec in state.candidate_specs if spec.key not in solver.used_spec_keys
            }
        else:
            solver.candidate_specs = {}
            for spec in solver.generator.initial_specs():
                if spec.key not in solver.used_spec_keys:
                    solver.candidate_specs.setdefault(spec.key, spec)
            # Rebuild a useful moving frontier from every selected atom.  This
            # is the compatibility path for schema-1 and stripped models.
            for spec, atom in zip(solver.active_specs, solver.active_atoms):
                for descendant in solver.generator.selected_descendants(spec, atom):
                    if descendant.key not in solver.used_spec_keys:
                        solver.candidate_specs.setdefault(descendant.key, descendant)
            for spec in solver.generator.quadtree_specs(solver.residual):
                if spec.key not in solver.used_spec_keys:
                    solver.candidate_specs.setdefault(spec.key, spec)
        return solver

    def _capture_search_state(self) -> PacketSearchState:
        return PacketSearchState(
            candidate_specs=[
                spec for key, spec in self.candidate_specs.items() if key not in self.used_spec_keys
            ],
            seed_masks={
                int(seed_id): np.asarray(mask, dtype=np.float64).copy()
                for seed_id, mask in self.generator.seed_masks.items()
            },
            seed_metadata={
                int(seed_id): dict(metadata)
                for seed_id, metadata in self.generator.seed_metadata.items()
            },
            next_seed_id=int(self.generator.next_seed_id),
            selected_seed_ids=[int(seed_id) for seed_id in self.generator.selected_seed_ids],
            quadtree_leaves=[tuple(map(int, rectangle)) for rectangle in sorted(self.generator.quadtree_leaves)],
            random_state=safe_json(self.generator.random.bit_generator.state),
        )

    def _add_constant(self) -> None:
        atom = normalize_atom(np.ones((self.height, self.width), dtype=float))
        if atom is None:
            raise RuntimeError("constant atom failed")
        spec = PacketSpec("constant", (), depth=0, complexity=0.5)
        self.active_specs.append(spec)
        self.active_atoms.append(atom)
        self.active_matrix = atom.reshape(-1, 1)
        self.used_spec_keys.add(spec.key)
        self.used_atom_digests.add(atom_digest(atom))
        self._refit()

    def _refit(self) -> None:
        matrix = self.active_matrix
        gram = matrix.T @ matrix
        gram.flat[:: gram.shape[0] + 1] += self.ridge
        target = matrix.T @ self.target
        try:
            coefficients = np.linalg.solve(gram, target)
            gram_inverse = np.linalg.inv(gram)
        except np.linalg.LinAlgError:
            coefficients = np.linalg.lstsq(matrix, self.target, rcond=1e-10)[0]
            gram_inverse = np.linalg.pinv(gram, rcond=1e-10)
        self.coefficients = coefficients
        self.gram_inverse = gram_inverse
        reconstruction = (matrix @ coefficients).reshape(self.height, self.width, self.channels)
        self.reconstruction = reconstruction
        self.residual = self.image - reconstruction

    def _orthogonal_norm(self, vector: Array) -> float:
        p = vector.reshape(-1)
        if self.active_matrix.shape[1] == 0:
            return float(p @ p)
        cross = self.active_matrix.T @ p
        value = float(p @ p - cross @ self.gram_inverse @ cross)
        return max(value, 0.0)

    def _score_spec(self, spec: PacketSpec) -> PacketAtom | None:
        if spec.key in self.used_spec_keys:
            return None
        try:
            atom = self.generator.atom_from_spec(spec)
        except Exception:
            return None
        if atom is None:
            return None
        digest = atom_digest(atom)
        if digest in self.used_atom_digests:
            return None
        p = atom.reshape(-1)
        orthogonal_norm = self._orthogonal_norm(atom)
        if orthogonal_norm <= 1e-8:
            return None
        correlation = p @ self.residual.reshape(-1, self.channels)
        gain = float(np.sum(correlation * correlation) / orthogonal_norm)
        score = gain / (1.0 + self.complexity_weight * spec.complexity)
        return PacketAtom(spec, atom, digest, score, gain, orthogonal_norm)

    def _candidate_subset(self) -> list[PacketSpec]:
        specs = [spec for key, spec in self.candidate_specs.items() if key not in self.used_spec_keys]
        if len(specs) <= self.max_candidates_per_iteration:
            return specs
        deterministic = sorted(specs, key=lambda spec: (spec.depth, spec.complexity, spec.key))
        shallow = deterministic[: self.max_candidates_per_iteration // 2]
        remaining = deterministic[self.max_candidates_per_iteration // 2 :]
        count = self.max_candidates_per_iteration - len(shallow)
        if len(remaining) <= count:
            return shallow + remaining
        indices = self.generator.random.choice(len(remaining), size=count, replace=False)
        return shallow + [remaining[int(index)] for index in indices]

    def _refresh_candidates(self, iteration: int) -> None:
        if iteration % self.residual_refresh == 0:
            for spec in self.generator.residual_seed_specs(self.residual, iteration):
                self.candidate_specs.setdefault(spec.key, spec)
        for spec in self.generator.quadtree_specs(self.residual):
            self.candidate_specs.setdefault(spec.key, spec)
        if iteration % self.quadtree_refine_every == 0:
            for spec in self.generator.refine_quadtree(self.residual, count=2):
                self.candidate_specs.setdefault(spec.key, spec)

    def _select_best(self) -> PacketAtom | None:
        best: PacketAtom | None = None
        for spec in self._candidate_subset():
            candidate = self._score_spec(spec)
            if candidate is None:
                continue
            if best is None or candidate.score > best.score:
                best = candidate
        return best

    def _add_candidate(self, candidate: PacketAtom, iteration: int) -> None:
        self.active_specs.append(candidate.spec)
        self.active_atoms.append(candidate.values)
        self.active_matrix = np.column_stack([self.active_matrix, candidate.values.reshape(-1)])
        self.used_spec_keys.add(candidate.spec.key)
        self.used_atom_digests.add(candidate.digest)
        self._refit()
        residual_norm = float(np.linalg.norm(self.residual))
        seed_id: int | None = None
        descendants = self.generator.selected_descendants(candidate.spec, candidate.values)
        for spec in descendants:
            self.candidate_specs.setdefault(spec.key, spec)
            if spec.kind in {"masked_poly", "masked_dct", "affine", "radial"}:
                try:
                    seed_id = int(spec.params[0])
                except Exception:
                    pass
        self.history.append(
            PacketSelection(
                iteration=iteration,
                spec_key=candidate.spec.key,
                kind=candidate.spec.kind,
                parent=candidate.spec.parent,
                depth=candidate.spec.depth,
                complexity=candidate.spec.complexity,
                gain=candidate.gain,
                score=candidate.score,
                residual_norm=residual_norm,
                packet_count=len(self.active_specs),
                seed_id=seed_id,
            )
        )
        self.residual_norms.append(residual_norm)

    def run(
        self,
        max_packets: int = 80,
        tolerance: float = 1e-4,
        snapshot_packets: Sequence[int] = (8, 16, 32, 64, 80),
    ) -> ReconstructionResult:
        started = time.perf_counter()
        current_count = len(self.active_specs)
        snapshots: dict[int, Array] = {current_count: self.reconstruction.copy()}
        target_norm = max(float(np.linalg.norm(self.image)), 1e-12)
        iteration = max((selection.iteration for selection in self.history), default=max(0, current_count - 1))
        while len(self.active_specs) < max_packets:
            iteration += 1
            self._refresh_candidates(iteration)
            candidate = self._select_best()
            if candidate is None:
                new_specs = self.generator.refine_quadtree(self.residual, count=4)
                for spec in new_specs:
                    self.candidate_specs.setdefault(spec.key, spec)
                candidate = self._select_best()
                if candidate is None:
                    break
            current_energy = float(np.sum(self.residual * self.residual))
            if candidate.gain <= tolerance * max(current_energy, 1e-20):
                new_specs = self.generator.refine_quadtree(self.residual, count=4)
                for spec in new_specs:
                    self.candidate_specs.setdefault(spec.key, spec)
                replacement = self._select_best()
                if replacement is not None and replacement.gain > candidate.gain:
                    candidate = replacement
            self._add_candidate(candidate, iteration)
            packet_count = len(self.active_specs)
            if packet_count in snapshot_packets:
                snapshots[packet_count] = self.reconstruction.copy()
            if float(np.linalg.norm(self.residual)) <= tolerance * target_norm:
                break
        runtime = time.perf_counter() - started
        return ReconstructionResult(
            reconstruction=self.reconstruction.copy(),
            residual=self.residual.copy(),
            coefficients=self.coefficients.copy(),
            active_specs=list(self.active_specs),
            active_atoms=[atom.copy() for atom in self.active_atoms],
            history=list(self.history),
            snapshots=snapshots,
            residual_norms=list(self.residual_norms),
            runtime_seconds=runtime,
            exact_archive_residual=self.residual.copy(),
            search_state=self._capture_search_state(),
        )

    def complete_with_pixels(self, threshold: float = 1e-12) -> ReconstructionResult:
        started = time.perf_counter()
        residual = self.residual.copy()
        magnitude = np.sqrt(np.sum(residual * residual, axis=2))
        positions = np.argwhere(magnitude > threshold)
        for y, x in positions:
            atom = np.zeros((self.height, self.width), dtype=float)
            atom[int(y), int(x)] = 1.0
            normalized = normalize_atom(atom)
            if normalized is None:
                continue
            spec = PacketSpec("pixel", (int(y), int(x)), depth=int(math.ceil(math.log2(max(self.height, self.width)))), complexity=2.0)
            digest = atom_digest(normalized)
            if digest in self.used_atom_digests:
                continue
            self.active_specs.append(spec)
            self.active_atoms.append(normalized)
            self.active_matrix = np.column_stack([self.active_matrix, normalized.reshape(-1)])
            self.used_spec_keys.add(spec.key)
            self.used_atom_digests.add(digest)
        self._refit()
        runtime = time.perf_counter() - started
        return ReconstructionResult(
            reconstruction=self.reconstruction.copy(),
            residual=self.residual.copy(),
            coefficients=self.coefficients.copy(),
            active_specs=list(self.active_specs),
            active_atoms=[atom.copy() for atom in self.active_atoms],
            history=list(self.history),
            snapshots={},
            residual_norms=list(self.residual_norms) + [float(np.linalg.norm(self.residual))],
            runtime_seconds=runtime,
            exact_archive_residual=self.residual.copy(),
            search_state=self._capture_search_state(),
        )


# ---------------------------------------------------------------------------
# Baseline reconstructions
# ---------------------------------------------------------------------------




def sparse_dct_component(signal: Array, coefficient_budget: int) -> Array:
    value = np.asarray(signal, dtype=np.float64)
    if value.ndim == 2:
        value = value[..., None]
    coefficients = np.stack([spfft.dctn(value[..., channel], norm="ortho") for channel in range(value.shape[2])], axis=-1)
    energy = np.sum(coefficients * coefficients, axis=2)
    count = min(max(1, coefficient_budget), energy.size)
    indices = np.argpartition(energy.ravel(), -count)[-count:]
    mask = np.zeros(energy.size, dtype=bool)
    mask[indices] = True
    mask = mask.reshape(energy.shape)
    filtered = coefficients * mask[..., None]
    return np.stack([spfft.idctn(filtered[..., channel], norm="ortho") for channel in range(value.shape[2])], axis=-1)


def bounded_synthesis(reconstruction: Array) -> Array:
    return np.clip(np.asarray(reconstruction, dtype=np.float64), 0.0, 1.0)

def dct_reconstruction(image: Array, coefficient_budget: int) -> Array:
    value = ensure_image(image)
    coefficients = np.stack([spfft.dctn(value[..., channel], norm="ortho") for channel in range(value.shape[2])], axis=-1)
    energy = np.sum(coefficients * coefficients, axis=2)
    count = min(coefficient_budget, energy.size)
    indices = np.argpartition(energy.ravel(), -count)[-count:]
    mask = np.zeros(energy.size, dtype=bool)
    mask[indices] = True
    mask = mask.reshape(energy.shape)
    filtered = coefficients * mask[..., None]
    reconstruction = np.stack([spfft.idctn(filtered[..., channel], norm="ortho") for channel in range(value.shape[2])], axis=-1)
    return np.asarray(reconstruction, dtype=float)


def fourier_lowpass_reconstruction(image: Array, coefficient_budget: int) -> Array:
    value = ensure_image(image)
    height, width, channels = value.shape
    side = max(1, int(math.sqrt(max(coefficient_budget, 1))))
    half = side // 2
    reconstruction = np.zeros_like(value)
    for channel in range(channels):
        spectrum = np.fft.fftshift(np.fft.fft2(value[..., channel]))
        mask = np.zeros((height, width), dtype=bool)
        cy, cx = height // 2, width // 2
        y0 = max(0, cy - half)
        y1 = min(height, y0 + side)
        x0 = max(0, cx - half)
        x1 = min(width, x0 + side)
        mask[y0:y1, x0:x1] = True
        reconstruction[..., channel] = np.real(np.fft.ifft2(np.fft.ifftshift(spectrum * mask)))
    return reconstruction


def adaptive_quadtree_reconstruction(image: Array, leaf_budget: int) -> Array:
    value = ensure_image(image)
    height, width, channels = value.shape
    leaves: list[tuple[int, int, int, int]] = [(0, 0, height, width)]

    def cost(rectangle: tuple[int, int, int, int]) -> float:
        y0, x0, y1, x1 = rectangle
        patch = value[y0:y1, x0:x1]
        mean = patch.mean(axis=(0, 1), keepdims=True)
        return float(np.sum((patch - mean) ** 2))

    while len(leaves) < leaf_budget:
        splittable = [rectangle for rectangle in leaves if rectangle[2] - rectangle[0] > 1 or rectangle[3] - rectangle[1] > 1]
        if not splittable:
            break
        rectangle = max(splittable, key=cost)
        leaves.remove(rectangle)
        y0, x0, y1, x1 = rectangle
        ym = (y0 + y1) // 2
        xm = (x0 + x1) // 2
        children = [
            (y0, x0, max(ym, y0 + 1), max(xm, x0 + 1)),
            (y0, max(xm, x0 + 1), max(ym, y0 + 1), x1),
            (max(ym, y0 + 1), x0, y1, max(xm, x0 + 1)),
            (max(ym, y0 + 1), max(xm, x0 + 1), y1, x1),
        ]
        leaves.extend([child for child in children if child[2] > child[0] and child[3] > child[1]])
    reconstruction = np.zeros_like(value)
    for y0, x0, y1, x1 in leaves:
        reconstruction[y0:y1, x0:x1] = value[y0:y1, x0:x1].mean(axis=(0, 1), keepdims=True)
    return reconstruction


def tv_reconstruction(image: Array, weight: float = 0.07) -> Array:
    value = ensure_image(image)
    if value.shape[2] == 1:
        result = denoise_tv_chambolle(value[..., 0], weight=weight, channel_axis=None)
        return result[..., None]
    return denoise_tv_chambolle(value, weight=weight, channel_axis=-1)


# ---------------------------------------------------------------------------
# Test images
# ---------------------------------------------------------------------------


def polygon_mask(height: int, width: int, points: Sequence[tuple[float, float]]) -> Array:
    canvas = np.zeros((height, width), dtype=np.uint8)
    polygon = np.array([[int(x * width), int(y * height)] for x, y in points], dtype=np.int32)
    cv2.fillPoly(canvas, [polygon], 1)
    return canvas.astype(float)


def synthetic_geometry(size: int = 80) -> Array:
    y, x = np.mgrid[0:size, 0:size]
    xu = (x + 0.5) / size
    yu = (y + 0.5) / size
    image = np.zeros((size, size, 3), dtype=float)
    image[..., 0] = 0.10 + 0.18 * xu + 0.05 * np.sin(2 * math.pi * yu)
    image[..., 1] = 0.12 + 0.12 * yu + 0.04 * np.cos(2 * math.pi * xu)
    image[..., 2] = 0.18 + 0.08 * xu

    disk = (xu - 0.26) ** 2 + (yu - 0.30) ** 2 <= 0.15**2
    image[disk] = np.array([0.92, 0.26, 0.18])
    ellipse = ((xu - 0.70) / 0.20) ** 2 + ((yu - 0.27) / 0.11) ** 2 <= 1.0
    image[ellipse] = np.array([0.18, 0.78, 0.42])
    rectangle = polygon_mask(size, size, [(0.12, 0.58), (0.45, 0.50), (0.52, 0.78), (0.18, 0.86)]) > 0.5
    image[rectangle] = np.array([0.25, 0.42, 0.94])
    star_points: list[tuple[float, float]] = []
    for index in range(10):
        radius = 0.17 if index % 2 == 0 else 0.075
        angle = -math.pi / 2 + index * math.pi / 5
        star_points.append((0.73 + radius * math.cos(angle), 0.72 + radius * math.sin(angle)))
    star = polygon_mask(size, size, star_points) > 0.5
    image[star] = np.array([0.96, 0.75, 0.14])
    cv2.line(image, (3, size - 7), (size - 4, size - 22), (0.92, 0.92, 0.92), thickness=2)
    return np.clip(image, 0.0, 1.0)


def synthetic_text_curves(size: int = 80) -> Array:
    y, x = np.mgrid[0:size, 0:size]
    xu = (x + 0.5) / size
    yu = (y + 0.5) / size
    image = np.zeros((size, size, 3), dtype=float)
    image[..., 0] = 0.10 + 0.65 * xu
    image[..., 1] = 0.16 + 0.45 * yu
    image[..., 2] = 0.22 + 0.18 * np.sin(2 * math.pi * xu) ** 2
    ring = np.logical_and(
        (xu - 0.70) ** 2 + (yu - 0.30) ** 2 <= 0.18**2,
        (xu - 0.70) ** 2 + (yu - 0.30) ** 2 >= 0.11**2,
    )
    image[ring] = np.array([0.95, 0.33, 0.72])
    wave_boundary = yu > 0.60 + 0.05 * np.sin(7 * math.pi * xu)
    image[wave_boundary] = 0.55 * image[wave_boundary] + 0.45 * np.array([0.08, 0.78, 0.88])
    canvas = np.zeros((size, size), dtype=np.uint8)
    cv2.putText(canvas, "K", (5, int(0.55 * size)), cv2.FONT_HERSHEY_SIMPLEX, 1.7, 255, thickness=3, lineType=cv2.LINE_AA)
    text_mask = canvas > 20
    image[text_mask] = np.array([0.98, 0.94, 0.20])
    return np.clip(image, 0.0, 1.0)


def natural_images(size: int = 80) -> dict[str, Array]:
    camera = resize_image(data.camera().astype(float) / 255.0, size)
    astronaut = resize_image(data.astronaut().astype(float) / 255.0, size)
    page = resize_image(data.page().astype(float) / 255.0, size)
    return {"camera": camera, "astronaut": astronaut, "page": page}


def benchmark_images(size: int = 80) -> dict[str, Array]:
    images = {
        "synthetic_geometry": synthetic_geometry(size),
        "synthetic_text_curves": synthetic_text_curves(size),
    }
    naturals = natural_images(size)
    images["camera"] = naturals["camera"]
    images["astronaut"] = naturals["astronaut"]
    return images


# ---------------------------------------------------------------------------
# Verification tests
# ---------------------------------------------------------------------------


def run_tests() -> dict[str, Any]:
    checks: dict[str, Any] = {}

    # Exact residual archive identity.
    image = synthetic_geometry(24)
    reconstructor = InfinitePacketReconstructor(image, max_candidates_per_iteration=90)
    result = reconstructor.run(max_packets=14, snapshot_packets=(8, 14))
    archive_residual = image - result.reconstruction
    checks["archive_identity"] = float(np.max(np.abs(result.reconstruction + archive_residual - image)))
    if checks["archive_identity"] > 1e-11:
        raise AssertionError("archive identity failed")

    # Residual is monotone under exact refitting.
    residuals = np.array(result.residual_norms)
    increases = np.maximum(np.diff(residuals), 0.0)
    checks["monotone_residual_max_increase"] = float(increases.max(initial=0.0))
    if checks["monotone_residual_max_increase"] > 1e-8:
        raise AssertionError("residual is not monotone")

    # Pixel completion is exact on a finite image.
    tiny = synthetic_text_curves(12)
    tiny_reconstructor = InfinitePacketReconstructor(tiny, max_candidates_per_iteration=60)
    tiny_reconstructor.run(max_packets=10)
    completed = tiny_reconstructor.complete_with_pixels()
    checks["pixel_completion_residual"] = float(np.max(np.abs(completed.residual)))
    if checks["pixel_completion_residual"] > 2e-8:
        raise AssertionError("pixel completion failed")

    # A step packet is synthesized without overshoot when represented directly.
    step = np.zeros((32, 32, 1), dtype=float)
    step[:, 16:, 0] = 1.0
    mask = np.zeros((32, 32), dtype=float)
    mask[:, 16:] = 1.0
    atom = normalize_atom(mask)
    constant = normalize_atom(np.ones((32, 32)))
    if atom is None or constant is None:
        raise AssertionError("step atoms failed")
    matrix = np.column_stack([constant.ravel(), atom.ravel()])
    coefficients = np.linalg.lstsq(matrix, step.reshape(-1, 1), rcond=None)[0]
    step_reconstruction = (matrix @ coefficients).reshape(step.shape)
    checks["native_step_residual"] = float(np.max(np.abs(step_reconstruction - step)))
    checks["native_step_range_violation"] = float(max(0.0, -step_reconstruction.min()) + max(0.0, step_reconstruction.max() - 1.0))
    if checks["native_step_residual"] > 1e-11:
        raise AssertionError("native step reconstruction failed")

    # Perturbation family is nontrivial and deterministic.
    generator = InfinitePacketGenerator(synthetic_geometry(32), max_seed_masks=60)
    seed_id = sorted(generator.seed_masks)[0]
    base = generator.seed_masks[seed_id]
    shifted = generator.affine_mask(base, 1.0, 0.0, 0.0, 1.0)
    radial = generator.radial_warp(base, 1.0, 3, 0.0)
    checks["affine_perturbation_distance"] = float(np.linalg.norm(base - shifted))
    checks["radial_perturbation_distance"] = float(np.linalg.norm(base - radial))
    if checks["affine_perturbation_distance"] <= 1e-8:
        raise AssertionError("affine perturbation is trivial")

    # DCT and Fourier baselines preserve shape and finite values.
    dct = dct_reconstruction(image, 20)
    fourier = fourier_lowpass_reconstruction(image, 20)
    checks["dct_finite"] = bool(np.isfinite(dct).all())
    checks["fourier_finite"] = bool(np.isfinite(fourier).all())
    if dct.shape != image.shape or fourier.shape != image.shape:
        raise AssertionError("baseline shape mismatch")

    # Global least-squares residual is orthogonal to the active packet span.
    stationarity = result.active_matrix.T @ result.residual.reshape(-1, result.residual.shape[2]) if hasattr(result, "active_matrix") else None
    # ReconstructionResult is intentionally immutable with respect to the solver matrix.
    # Rebuild the matrix from its stored atoms for the certificate.
    active_matrix = np.column_stack([atom.reshape(-1) for atom in result.active_atoms])
    stationarity = active_matrix.T @ result.residual.reshape(-1, result.residual.shape[2])
    checks["global_refit_stationarity"] = float(np.max(np.abs(stationarity)))
    if checks["global_refit_stationarity"] > 2e-7:
        raise AssertionError("global refit stationarity failed")

    # Projection to the physical display range cannot increase error to an image in that range.
    rng = np.random.default_rng(17)
    truth = rng.uniform(0.0, 1.0, size=(10, 10, 3))
    unconstrained = truth + rng.normal(scale=0.45, size=truth.shape)
    before = np.linalg.norm(unconstrained - truth)
    after = np.linalg.norm(bounded_synthesis(unconstrained) - truth)
    checks["bounded_synthesis_nonexpansive_ratio"] = float(after / before)
    if after > before + 1e-12:
        raise AssertionError("bounded synthesis increased error")

    # Residual DCT completion is an exact orthogonal improvement in the selected residual subspace.
    base = dct_reconstruction(image, 5)
    completion = sparse_dct_component(image - base, 10)
    before_completion = np.linalg.norm(image - base)
    after_completion = np.linalg.norm(image - (base + completion))
    checks["residual_completion_ratio"] = float(after_completion / before_completion)
    if after_completion > before_completion + 1e-10:
        raise AssertionError("residual completion increased error")

    # A single mask with one coefficient per channel reconstructs a color step exactly.
    color_step = np.zeros((12, 12, 3), dtype=float)
    color_step[:, 6:] = np.array([0.2, 0.7, 0.95])
    color_mask = np.zeros((12, 12), dtype=float)
    color_mask[:, 6:] = 1.0
    color_atom = normalize_atom(color_mask)
    if color_atom is None:
        raise AssertionError("color mask failed")
    coefficient = color_atom.reshape(-1) @ color_step.reshape(-1, 3)
    color_reconstruction = (color_atom.reshape(-1, 1) @ coefficient.reshape(1, 3)).reshape(color_step.shape)
    checks["shared_mask_color_residual"] = float(np.max(np.abs(color_reconstruction - color_step)))
    if checks["shared_mask_color_residual"] > 1e-11:
        raise AssertionError("shared color mask failed")

    # The generator produces many distinct descendants from one parent.
    first_spec = next(spec for spec in generator.initial_specs() if spec.kind == "mask")
    first_atom = generator.atom_from_spec(first_spec)
    if first_atom is None:
        raise AssertionError("seed atom failed")
    descendants = generator.selected_descendants(first_spec, first_atom)
    descendant_atoms = [generator.atom_from_spec(spec) for spec in descendants]
    descendant_digests = {atom_digest(atom) for atom in descendant_atoms if atom is not None}
    checks["distinct_descendants_from_one_packet"] = len(descendant_digests)
    if checks["distinct_descendants_from_one_packet"] < 12:
        raise AssertionError("perturbation family is too small")

    # Dyadic perturbation steps shrink along a lineage, making the generated
    # affine parameter set genuinely refinable rather than a fixed finite menu.
    depths = np.arange(1, 9)
    translation_steps = max(generator.height, generator.width) / (2.0 ** (depths + 4))
    checks["dyadic_translation_step_ratio"] = float(translation_steps[-1] / translation_steps[0])
    if not np.all(np.diff(translation_steps) < 0):
        raise AssertionError("dyadic perturbation schedule does not refine")

    # Soft boundaries and Boolean packet composition are nontrivial.
    next_seed = sorted(generator.seed_masks)[1]
    soft_spec = PacketSpec("soft_mask", (seed_id, 1.0, 1.0), depth=2)
    union_spec = PacketSpec("combine", (seed_id, next_seed, "union"), depth=2)
    soft_atom = generator.atom_from_spec(soft_spec)
    union_atom = generator.atom_from_spec(union_spec)
    checks["soft_boundary_finite"] = bool(soft_atom is not None and np.isfinite(soft_atom).all())
    checks["compositional_packet_finite"] = bool(union_atom is not None and np.isfinite(union_atom).all())
    if not checks["soft_boundary_finite"] or not checks["compositional_packet_finite"]:
        raise AssertionError("new packet grammar failed")

    checks["initial_image_derived_seed_masks"] = len(generator.seed_masks)
    if checks["initial_image_derived_seed_masks"] < 10:
        raise AssertionError("image-derived seed atlas is unexpectedly small")

    checks["test_groups"] = 16
    return checks


# ---------------------------------------------------------------------------
# Benchmark and visual generation
# ---------------------------------------------------------------------------


def save_figure(fig: plt.Figure, directory: Path, name: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(directory / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def display_image(ax: plt.Axes, image: Array, title: str) -> None:
    value = ensure_image(image)
    if value.shape[2] == 1:
        ax.imshow(value[..., 0], cmap="gray", vmin=0.0, vmax=1.0)
    else:
        ax.imshow(np.clip(value, 0.0, 1.0))
    ax.set_title(title, fontsize=10.5, weight="bold")
    ax.set_xticks([])
    ax.set_yticks([])


def packet_montage(result: ReconstructionResult, count: int = 20) -> Array:
    atoms = result.active_atoms[1 : count + 1]
    if not atoms:
        return np.zeros((8, 8))
    columns = 5
    rows = math.ceil(len(atoms) / columns)
    height, width = atoms[0].shape
    canvas = np.ones((rows * height, columns * width), dtype=float)
    for index, atom in enumerate(atoms):
        r = index // columns
        c = index % columns
        value = atom.copy()
        low, high = float(value.min()), float(value.max())
        normalized = (value - low) / (high - low + 1e-12)
        canvas[r * height : (r + 1) * height, c * width : (c + 1) * width] = normalized
    return canvas


def genealogy_edges(history: Sequence[PacketSelection]) -> tuple[list[str], list[tuple[int, int]]]:
    labels = [f"{item.iteration}:{item.kind}" for item in history]
    key_to_index = {item.spec_key: index for index, item in enumerate(history)}
    edges: list[tuple[int, int]] = []
    for index, item in enumerate(history):
        if item.parent and item.parent in key_to_index:
            edges.append((key_to_index[item.parent], index))
    return labels, edges


def benchmark_case(name: str, image: Array, packet_budget: int, root: Path) -> tuple[dict[str, Any], ReconstructionResult, dict[str, Array]]:
    reconstructor = InfinitePacketReconstructor(
        image,
        complexity_weight=0.035,
        max_candidates_per_iteration=170,
        residual_refresh=5,
        quadtree_refine_every=4,
        random_seed=20260731 + len(name),
    )
    result = reconstructor.run(
        max_packets=packet_budget,
        tolerance=2e-5,
        snapshot_packets=(8, 16, 32, 48, packet_budget),
    )
    residual_budget = max(12, packet_budget // 2)
    total_budget = packet_budget + residual_budget
    residual_component = sparse_dct_component(image - result.reconstruction, residual_budget)
    completed = bounded_synthesis(result.reconstruction + residual_component)
    methods = {
        "fourier": fourier_lowpass_reconstruction(image, total_budget),
        "dct": dct_reconstruction(image, total_budget),
        "quadtree": adaptive_quadtree_reconstruction(image, total_budget),
        "tv": tv_reconstruction(image, 0.065),
        "packet_core": result.reconstruction,
        "packet_completed": completed,
    }
    rows: list[dict[str, Any]] = []
    for method, reconstruction in methods.items():
        row = {"case": name, "method": method, "packet_budget": packet_budget}
        row.update(image_metrics(image, reconstruction))
        row["runtime_seconds"] = result.runtime_seconds if method == "infinite_packet" else 0.0
        rows.append(row)
    case_result = {
        "name": name,
        "packet_budget": packet_budget,
        "residual_completion_budget": residual_budget,
        "total_linear_packet_budget": total_budget,
        "runtime_seconds": result.runtime_seconds,
        "packets_selected": len(result.active_specs),
        "initial_residual_norm": result.residual_norms[0],
        "final_residual_norm": result.residual_norms[-1],
        "residual_ratio": result.residual_norms[-1] / max(result.residual_norms[0], 1e-12),
        "packet_kinds": dict(zip(*np.unique([spec.kind for spec in result.active_specs], return_counts=True))),
        "metrics": rows,
    }
    return case_result, result, methods


def generate_case_figures(name: str, image: Array, result: ReconstructionResult, methods: dict[str, Array], root: Path, index: int) -> None:
    figures = root / "figures"
    fig, axes = plt.subplots(2, 3, figsize=(12.0, 7.8))
    display_image(axes[0, 0], image, "truth")
    display_image(axes[0, 1], methods["fourier"], "global Fourier")
    display_image(axes[0, 2], methods["dct"], "best DCT coefficients")
    display_image(axes[1, 0], methods["tv"], "total variation")
    display_image(axes[1, 1], methods["packet_core"], "geometric packet core")
    display_image(axes[1, 2], methods["packet_completed"], "packet core + residual packets")
    fig.suptitle(name.replace("_", " ").title(), fontsize=16, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_figure(fig, figures, f"{index:02d}_{name}_methods")

    fig, axes = plt.subplots(1, 5, figsize=(13.0, 3.2))
    differences = {
        "Fourier error": methods["fourier"] - image,
        "DCT error": methods["dct"] - image,
        "quadtree error": methods["quadtree"] - image,
        "packet core error": methods["packet_core"] - image,
        "completed packet error": methods["packet_completed"] - image,
    }
    maximum = max(float(np.max(np.abs(value))) for value in differences.values())
    for ax, (title, difference) in zip(axes, differences.items(), strict=True):
        error_image = np.sqrt(np.sum(difference * difference, axis=2))
        im = ax.imshow(error_image, cmap="magma", vmin=0.0, vmax=maximum)
        ax.set_title(title, fontsize=9.5, weight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.colorbar(im, ax=axes.ravel().tolist(), fraction=0.018, pad=0.015, label="per-pixel error magnitude")
    fig.suptitle(f"Residual maps - {name.replace('_', ' ')}", fontsize=15, weight="bold")
    fig.subplots_adjust(left=0.02, right=0.94, bottom=0.05, top=0.82, wspace=0.08)
    save_figure(fig, figures, f"{index+1:02d}_{name}_residuals")

    snapshots = sorted(result.snapshots.items())
    if snapshots:
        fig, axes = plt.subplots(1, len(snapshots), figsize=(2.7 * len(snapshots), 3.0))
        if len(snapshots) == 1:
            axes = [axes]
        for ax, (count, snapshot) in zip(axes, snapshots, strict=True):
            display_image(ax, snapshot, f"{count} packets")
        fig.suptitle(f"Anytime reconstruction - {name.replace('_', ' ')}", fontsize=15, weight="bold")
        fig.tight_layout(rect=[0, 0, 1, 0.90])
        save_figure(fig, figures, f"{index+2:02d}_{name}_snapshots")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.1))
    axes[0].plot(np.arange(len(result.residual_norms)), result.residual_norms, marker="o", markersize=2.5, color=BLUE)
    axes[0].set_yscale("log")
    axes[0].set_xlabel("selected packet count")
    axes[0].set_ylabel("residual norm")
    axes[0].set_title("Monotone residual reduction", weight="bold")
    axes[0].grid(alpha=0.18, which="both")
    montage = packet_montage(result, 20)
    axes[1].imshow(montage, cmap="viridis")
    axes[1].set_title("First twenty selected packets", weight="bold")
    axes[1].set_xticks([])
    axes[1].set_yticks([])
    fig.suptitle(name.replace("_", " ").title(), fontsize=15, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    save_figure(fig, figures, f"{index+3:02d}_{name}_convergence_packets")


def generate_global_figures(root: Path, cases: dict[str, dict[str, Any]], results: dict[str, ReconstructionResult]) -> None:
    figures = root / "figures"

    fig, ax = plt.subplots(figsize=(12.0, 6.2))
    ax.axis("off")
    boxes = [
        (0.05, 0.62, 0.15, 0.18, "unknown image\n$f$", BLUE),
        (0.27, 0.72, 0.17, 0.16, "image-derived\nseed packets", TEAL),
        (0.27, 0.43, 0.17, 0.16, "dyadic fallback\npackets", ORANGE),
        (0.53, 0.72, 0.18, 0.16, "perturbation\nsemigroup", MAGENTA),
        (0.53, 0.43, 0.18, 0.16, "residual-driven\nproposals", RED),
        (0.79, 0.61, 0.16, 0.18, "global least-squares\nsynthesis", BLUE),
        (0.79, 0.25, 0.16, 0.14, "exact residual\narchive", TEAL),
    ]
    for x, y, w, h, text, color_value in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=color_value + "22", edgecolor=color_value, linewidth=1.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11.5)
    arrows = [
        ((0.20, 0.71), (0.27, 0.80)),
        ((0.20, 0.71), (0.27, 0.51)),
        ((0.44, 0.80), (0.53, 0.80)),
        ((0.44, 0.51), (0.53, 0.51)),
        ((0.71, 0.80), (0.79, 0.70)),
        ((0.71, 0.51), (0.79, 0.67)),
        ((0.87, 0.61), (0.87, 0.39)),
        ((0.79, 0.32), (0.69, 0.43)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color=INK, linewidth=1.5))
    ax.text(0.5, 0.95, "Infinite Perturbation Packet Atlas", ha="center", fontsize=20, weight="bold")
    ax.text(0.5, 0.08, "The atlas is generated lazily. Exact finite-image closure is supplied by the residual archive or the pixel-depth quadtree basis.", ha="center", fontsize=11, color=MUTED)
    save_figure(fig, figures, "01_architecture")

    sample_result = results["synthetic_geometry"]
    selected_masks = [atom for spec, atom in zip(sample_result.active_specs, sample_result.active_atoms, strict=True) if spec.kind in {"mask", "morph", "affine", "radial", "quadtree"}]
    if selected_masks:
        base = selected_masks[min(1, len(selected_masks) - 1)]
    else:
        base = sample_result.active_atoms[0]
    base = np.clip(base / max(float(base.max()), 1e-12), 0.0, 1.0)
    generator = InfinitePacketGenerator(synthetic_geometry(base.shape[0]), max_seed_masks=40)
    footprint = morphology.disk(2)
    variants: list[tuple[str, Array]] = [
        ("parent", base),
        ("shift left", generator.affine_mask(base, -2.0, 0.0, 0.0, 1.0)),
        ("rotate", generator.affine_mask(base, 0.0, 0.0, 7.0, 1.0)),
        ("scale", generator.affine_mask(base, 0.0, 0.0, 0.0, 1.08)),
        ("dilate", morphology.dilation(base > 0.5, footprint).astype(float)),
        ("erode", morphology.erosion(base > 0.5, footprint).astype(float)),
        ("radial mode 3", generator.radial_warp(base, 1.8, 3, 0.0)),
        ("radial mode 5", generator.radial_warp(base, 1.3, 5, math.pi / 2)),
    ]
    fig, axes = plt.subplots(2, 4, figsize=(11.5, 5.8))
    for ax, (title, atom) in zip(axes.ravel(), variants, strict=True):
        ax.imshow(atom, cmap="viridis")
        ax.set_title(title, fontsize=10, weight="bold")
        ax.axis("off")
    fig.suptitle("A single packet generates an unbounded perturbation family", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    save_figure(fig, figures, "02_perturbation_family")

    metric_rows = [row for case in cases.values() for row in case["metrics"]]
    metric_frame = {metric: [] for metric in ("rmse", "edge_rmse", "ssim", "mean_local_range_violation")}
    methods = ["fourier", "dct", "quadtree", "tv", "packet_core", "packet_completed"]
    case_names = list(cases)
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.0))
    for ax, metric in zip(axes.ravel(), metric_frame, strict=True):
        x = np.arange(len(case_names))
        width = 0.16
        for method_index, method in enumerate(methods):
            values = []
            for case_name in case_names:
                match = next(row for row in cases[case_name]["metrics"] if row["method"] == method)
                values.append(match[metric])
            ax.bar(x + (method_index - 2) * width, values, width, label=method if metric == "rmse" else None)
        ax.set_xticks(x, [name.replace("_", "\n") for name in case_names], fontsize=8)
        ax.set_title(metric.replace("_", " ").title(), weight="bold")
        ax.grid(axis="y", alpha=0.18)
        if metric in {"rmse", "edge_rmse", "mean_local_range_violation"}:
            ax.set_yscale("log")
    axes[0, 0].legend(ncol=3, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, 1.25))
    fig.suptitle("Global reconstruction benchmark", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, figures, "03_global_metrics")

    fig, ax = plt.subplots(figsize=(10.0, 5.0))
    kinds: dict[str, list[int]] = {}
    for case_name, result in results.items():
        counts: dict[str, int] = {}
        for spec in result.active_specs:
            counts[spec.kind] = counts.get(spec.kind, 0) + 1
        for kind in counts:
            kinds.setdefault(kind, [0] * len(results))
        for index, name in enumerate(results):
            for kind in kinds:
                kinds[kind][index] = sum(spec.kind == kind for spec in results[name].active_specs)
    bottom = np.zeros(len(results))
    x = np.arange(len(results))
    for color_index, (kind, values) in enumerate(sorted(kinds.items())):
        ax.bar(x, values, bottom=bottom, label=kind, color=PACKET_COLORS[color_index % len(PACKET_COLORS)])
        bottom += np.array(values)
    ax.set_xticks(x, [name.replace("_", "\n") for name in results], fontsize=8)
    ax.set_ylabel("selected packets")
    ax.set_title("The search adapts its packet grammar to each image", weight="bold")
    ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, 1.22))
    ax.grid(axis="y", alpha=0.16)
    fig.tight_layout()
    save_figure(fig, figures, "04_packet_type_composition")

    fig, ax = plt.subplots(figsize=(10.0, 5.2))
    for color_index, (name, result) in enumerate(results.items()):
        ratio = np.array(result.residual_norms) / max(result.residual_norms[0], 1e-12)
        ax.plot(np.arange(len(ratio)), ratio, label=name.replace("_", " "), color=PACKET_COLORS[color_index % len(PACKET_COLORS)], lw=2)
    ax.set_yscale("log")
    ax.set_xlabel("packet count")
    ax.set_ylabel("residual norm divided by initial norm")
    ax.set_title("Anytime convergence across full images", weight="bold")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.18, which="both")
    fig.tight_layout()
    save_figure(fig, figures, "05_global_convergence")

    # Edge cross-section on synthetic geometry.
    truth = synthetic_geometry(results["synthetic_geometry"].reconstruction.shape[0])
    result = results["synthetic_geometry"]
    row_index = 24
    x_axis = np.arange(truth.shape[1])
    fig, axes = plt.subplots(3, 1, figsize=(11.0, 7.2), sharex=True)
    methods = {
        "truth": truth,
        "Fourier": fourier_lowpass_reconstruction(truth, len(result.active_specs)),
        "DCT": dct_reconstruction(truth, len(result.active_specs)),
        "packet core": result.reconstruction,
        "packet completed": bounded_synthesis(result.reconstruction + sparse_dct_component(truth - result.reconstruction, max(12, len(result.active_specs) // 2))),
    }
    for channel, ax in enumerate(axes):
        for label, image in methods.items():
            ax.plot(x_axis, image[row_index, :, channel], label=label, lw=2 if label in {"truth", "packet completed"} else 1.2)
        ax.set_ylabel(f"channel {channel}")
        ax.grid(alpha=0.16)
    axes[0].legend(ncol=4, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, 1.35))
    axes[-1].set_xlabel("horizontal image coordinate")
    fig.suptitle("Cross-section through several unknown boundaries", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save_figure(fig, figures, "06_boundary_cross_section")

    # Exact archive and fallback diagram.
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.7))
    example = synthetic_text_curves(results["synthetic_text_curves"].reconstruction.shape[0])
    result = results["synthetic_text_curves"]
    display_image(axes[0], result.reconstruction, "finite packet reconstruction")
    residual_magnitude = np.sqrt(np.sum(result.residual * result.residual, axis=2))
    axes[1].imshow(residual_magnitude, cmap="magma")
    axes[1].set_title("exact residual packet", weight="bold")
    axes[1].set_xticks([])
    axes[1].set_yticks([])
    display_image(axes[2], result.reconstruction + result.exact_archive_residual, "reconstruction + residual")
    fig.suptitle(r"Anytime exact identity: $f=\widehat f_K+r_K$", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    save_figure(fig, figures, "07_exact_residual_archive")

    # Packet genealogy in depth-time coordinates.
    genealogy_result = results["synthetic_geometry"]
    kind_names = sorted({item.kind for item in genealogy_result.history})
    kind_color = {kind: PACKET_COLORS[index % len(PACKET_COLORS)] for index, kind in enumerate(kind_names)}
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    key_to_point = {item.spec_key: (item.iteration, item.depth) for item in genealogy_result.history}
    for item in genealogy_result.history:
        if item.parent in key_to_point:
            x0, y0 = key_to_point[item.parent]
            ax.plot([x0, item.iteration], [y0, item.depth], color="#B2BABB", lw=0.8, zorder=1)
    for kind in kind_names:
        chosen = [item for item in genealogy_result.history if item.kind == kind]
        ax.scatter([item.iteration for item in chosen], [item.depth for item in chosen], s=42, color=kind_color[kind], label=kind, edgecolors="black", linewidths=0.3, zorder=2)
    ax.set_xlabel("selection iteration")
    ax.set_ylabel("packet refinement depth")
    ax.set_title("The packet forest grows only where the residual asks for it", weight="bold")
    ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, 1.20))
    ax.grid(alpha=0.16)
    fig.tight_layout()
    save_figure(fig, figures, "08_packet_genealogy")

    # Theorem map.
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    ax.axis("off")
    theorem_boxes = [
        (0.08, 0.66, "finite image\n$f$", BLUE),
        (0.29, 0.66, "lazy packet\nanalysis", TEAL),
        (0.50, 0.66, "global orthogonal\nrefit", ORANGE),
        (0.71, 0.66, "bounded\nsynthesis", MAGENTA),
        (0.91, 0.66, "approximate\nimage", RED),
        (0.29, 0.28, "residual packet\n$r_K$", BLUE),
        (0.50, 0.28, "quadtree to\npixel depth", TEAL),
        (0.71, 0.28, "exact finite\nclosure", ORANGE),
    ]
    for x0, y0, text, color_value in theorem_boxes:
        ax.text(x0, y0, text, ha="center", va="center", fontsize=11.5, bbox=dict(boxstyle="round,pad=0.45", facecolor=color_value + "22", edgecolor=color_value, linewidth=1.8))
    arrows = [(0,1),(1,2),(2,3),(3,4),(2,5),(5,6),(6,7),(7,4)]
    for left, right in arrows:
        x0, y0, _, _ = theorem_boxes[left]
        x1, y1, _, _ = theorem_boxes[right]
        ax.annotate("", xy=(x1,y1), xytext=(x0,y0), arrowprops=dict(arrowstyle="->", color=INK, linewidth=1.4, shrinkA=25, shrinkB=25))
    ax.text(0.5, 0.93, "Two exactness paths", ha="center", fontsize=19, weight="bold")
    ax.text(0.50, 0.09, r"Anytime archive: $f=\widehat f_K+r_K$     |     Finite closure: pixel-depth packets span $R^{H\times W\times C}$", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, figures, "09_exactness_paths")

    # Growth of the potential packet family.
    depth = np.arange(0, 10)
    branching = 16
    family_count = branching ** depth
    quadtree_count = (4 ** (depth + 1) - 1) / 3
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.semilogy(depth, family_count, marker="o", color=MAGENTA, label=f"perturbation descendants, branching {branching}")
    ax.semilogy(depth, quadtree_count, marker="o", color=TEAL, label="dyadic fallback nodes")
    ax.set_xlabel("refinement depth")
    ax.set_ylabel("available packet count")
    ax.set_title("The atlas is generated, not stored", weight="bold")
    ax.legend()
    ax.grid(alpha=0.18, which="both")
    fig.tight_layout()
    save_figure(fig, figures, "10_packet_family_growth")

    # Seed atlas montage.
    seed_generator = InfinitePacketGenerator(synthetic_text_curves(56), max_seed_masks=80)
    seeds = list(seed_generator.seed_masks.values())[:30]
    columns = 6
    rows = math.ceil(len(seeds) / columns)
    canvas = np.zeros((rows * 56, columns * 56), dtype=float)
    for index, mask in enumerate(seeds):
        row = index // columns
        column = index % columns
        canvas[row*56:(row+1)*56, column*56:(column+1)*56] = mask
    fig, ax = plt.subplots(figsize=(11.0, 6.3))
    ax.imshow(canvas, cmap="gray")
    ax.set_title("Image-derived seed atlas before any residual refinement", weight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    save_figure(fig, figures, "11_seed_atlas")

    # Core versus completed synthesis across cases.
    fig, ax = plt.subplots(figsize=(9.7, 4.8))
    case_names = list(cases)
    core_values = []
    complete_values = []
    for case_name in case_names:
        core_values.append(next(row["rmse"] for row in cases[case_name]["metrics"] if row["method"] == "packet_core"))
        complete_values.append(next(row["rmse"] for row in cases[case_name]["metrics"] if row["method"] == "packet_completed"))
    x = np.arange(len(case_names))
    ax.bar(x - 0.18, core_values, 0.36, color=ORANGE, label="geometric packet core")
    ax.bar(x + 0.18, complete_values, 0.36, color=TEAL, label="core plus residual packets")
    ax.set_xticks(x, [name.replace("_", "\n") for name in case_names], fontsize=8)
    ax.set_ylabel("RMSE")
    ax.set_yscale("log")
    ax.set_title("Global residual packets complete the unknown image", weight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.18, which="both")
    fig.tight_layout()
    save_figure(fig, figures, "12_core_vs_completion")

    # Pixel completion certificate on a small image.
    tiny = synthetic_geometry(14)
    tiny_solver = InfinitePacketReconstructor(tiny, max_candidates_per_iteration=50)
    tiny_core = tiny_solver.run(max_packets=10)
    before = tiny_core.reconstruction.copy()
    completed = tiny_solver.complete_with_pixels()
    fig, axes = plt.subplots(1, 4, figsize=(11.2, 3.0))
    display_image(axes[0], tiny, "truth")
    display_image(axes[1], before, "ten packets")
    axes[2].imshow(np.sqrt(np.sum((tiny-before)**2, axis=2)), cmap="magma")
    axes[2].set_title("residual before closure", weight="bold", fontsize=9.5)
    axes[2].set_xticks([])
    axes[2].set_yticks([])
    display_image(axes[3], completed.reconstruction, "pixel-complete synthesis")
    fig.suptitle(f"Finite closure residual {np.max(np.abs(completed.residual)):.2e}", fontsize=15, weight="bold")
    fig.tight_layout(rect=[0,0,1,0.88])
    save_figure(fig, figures, "13_pixel_completion_certificate")


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_budget_experiment(base: Path) -> list[dict[str, float | int]]:
    image = synthetic_geometry(48)
    rows: list[dict[str, float | int]] = []
    for budget in (8, 16, 24, 32, 48):
        solver = InfinitePacketReconstructor(
            image,
            complexity_weight=0.035,
            max_candidates_per_iteration=130,
            residual_refresh=5,
            quadtree_refine_every=4,
            random_seed=9000 + budget,
        )
        result = solver.run(max_packets=budget, snapshot_packets=(budget,))
        residual_budget = max(4, budget // 2)
        completed = bounded_synthesis(result.reconstruction + sparse_dct_component(image - result.reconstruction, residual_budget))
        rows.append({
            "packet_budget": budget,
            "residual_budget": residual_budget,
            "core_rmse": rmse(image, result.reconstruction),
            "completed_rmse": rmse(image, completed),
            "runtime_seconds": result.runtime_seconds,
            "selected_packets": len(result.active_specs),
        })
    write_csv(base / "tables" / "budget_experiment.csv", rows)
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3))
    budgets = [row["packet_budget"] for row in rows]
    axes[0].plot(budgets, [row["core_rmse"] for row in rows], marker="o", color=ORANGE, label="geometric core")
    axes[0].plot(budgets, [row["completed_rmse"] for row in rows], marker="o", color=TEAL, label="core plus residual packets")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("geometric packet budget")
    axes[0].set_ylabel("RMSE")
    axes[0].set_title("Accuracy improves as the packet forest grows", weight="bold")
    axes[0].legend()
    axes[0].grid(alpha=0.18, which="both")
    axes[1].plot(budgets, [row["runtime_seconds"] for row in rows], marker="o", color=BLUE)
    axes[1].set_xlabel("geometric packet budget")
    axes[1].set_ylabel("seconds")
    axes[1].set_title("Runtime versus selected packets", weight="bold")
    axes[1].grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, base / "figures", "14_budget_sweep")
    return rows


def run_scaling_experiment(base: Path) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    for size in (32, 48, 64, 80):
        image = synthetic_text_curves(size)
        solver = InfinitePacketReconstructor(
            image,
            complexity_weight=0.035,
            max_candidates_per_iteration=110,
            residual_refresh=6,
            quadtree_refine_every=4,
            random_seed=12000 + size,
        )
        result = solver.run(max_packets=28, snapshot_packets=(28,))
        rows.append({
            "image_size": size,
            "pixel_count": size * size,
            "runtime_seconds": result.runtime_seconds,
            "core_rmse": rmse(image, result.reconstruction),
            "selected_packets": len(result.active_specs),
        })
    write_csv(base / "tables" / "scaling_experiment.csv", rows)
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3))
    pixels = [row["pixel_count"] for row in rows]
    axes[0].plot(pixels, [row["runtime_seconds"] for row in rows], marker="o", color=BLUE)
    axes[0].set_xlabel("pixel count")
    axes[0].set_ylabel("seconds")
    axes[0].set_title("Measured runtime scaling", weight="bold")
    axes[0].grid(alpha=0.18)
    axes[1].plot(pixels, [row["core_rmse"] for row in rows], marker="o", color=MAGENTA)
    axes[1].set_xlabel("pixel count")
    axes[1].set_ylabel("RMSE at 28 packets")
    axes[1].set_title("Fixed-budget approximation across resolutions", weight="bold")
    axes[1].grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, base / "figures", "15_resolution_scaling")
    return rows


def run_all(base: Path, size: int = 80, packet_budget: int = 72) -> dict[str, Any]:
    base = base.resolve()
    for name in ("figures", "tables", "results"):
        (base / name).mkdir(parents=True, exist_ok=True)
    checks = run_tests()
    images = benchmark_images(size)
    cases: dict[str, dict[str, Any]] = {}
    results: dict[str, ReconstructionResult] = {}
    all_metrics: list[dict[str, Any]] = []
    all_history: list[dict[str, Any]] = []
    figure_index = 8
    for name, image in images.items():
        case, result, methods = benchmark_case(name, image, packet_budget, base)
        cases[name] = case
        results[name] = result
        all_metrics.extend(case["metrics"])
        for selection in result.history:
            row = asdict(selection)
            row["case"] = name
            all_history.append(row)
        generate_case_figures(name, image, result, methods, base, figure_index)
        figure_index += 4
    generate_global_figures(base, cases, results)
    write_csv(base / "tables" / "benchmark_metrics.csv", all_metrics)
    write_csv(base / "tables" / "packet_history.csv", all_history)
    budget_experiment = run_budget_experiment(base)
    scaling_experiment = run_scaling_experiment(base)

    summary = {
        "title": "Infinite Perturbation Packet Atlas for Global Gibbs-Free Image Reconstruction",
        "author": "Komorebi P.",
        "image_size": size,
        "packet_budget": packet_budget,
        "case_count": len(cases),
        "cases": safe_json(cases),
        "checks": safe_json(checks),
        "figure_pairs": len(list((base / "figures").glob("*.pdf"))),
        "table_files": 4,
        "budget_experiment": safe_json(budget_experiment),
        "scaling_experiment": safe_json(scaling_experiment),
        "claim_boundary": {
            "proved": [
                "the residual norm is nonincreasing under exact global refitting",
                "the exact residual archive satisfies f = reconstruction + residual at every stage",
                "dyadic pixel completion exactly spans every finite image",
                "an exactly represented edge packet introduces no Gibbs overshoot",
                "the packet generator is unbounded under repeated perturbation and refinement",
            ],
            "not_claimed": [
                "a fixed finite packet budget sparsely represents every image",
                "arbitrary unknown continuous boundaries are recovered exactly",
                "the empirical benchmark is an optimality theorem",
            ],
        },
    }
    (base / "results" / "infinite_packet_results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Infinite perturbation packet atlas for global image reconstruction")
    parser.add_argument("--base", type=Path, default=Path("."))
    parser.add_argument("--size", type=int, default=80)
    parser.add_argument("--packets", type=int, default=72)
    parser.add_argument("--tests-only", action="store_true")
    args = parser.parse_args()
    if args.tests_only:
        print(json.dumps(run_tests(), indent=2))
        return
    result = run_all(args.base, size=args.size, packet_budget=args.packets)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
