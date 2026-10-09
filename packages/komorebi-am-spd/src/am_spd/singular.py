from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from . import atlas

Array = NDArray[np.float64]


@dataclass
class SingularPacketMode:
    iteration: int
    rectangle: tuple[int, int, int, int]
    depth: int
    singular_value: float
    gain: float
    score: float
    parameter_count: int
    cumulative_parameter_count: int
    residual_norm: float
    component_norm: float


@dataclass
class SingularPacketResult:
    reconstruction: Array
    residual: Array
    modes: list[SingularPacketMode]
    directions: list[Array]
    coefficients: Array
    residual_norms: list[float]
    runtime_seconds: float
    parameter_counts: list[int]
    snapshots: dict[int, Array]


def _flatten_image(image: Array) -> Array:
    return np.asarray(image, dtype=np.float64).reshape(-1)


def _core_design(active_atoms: Sequence[Array], channels: int) -> Array:
    if not active_atoms:
        return np.empty((0, 0), dtype=np.float64)
    height, width = active_atoms[0].shape
    columns: list[Array] = []
    for atom in active_atoms:
        for channel in range(channels):
            value = np.zeros((height, width, channels), dtype=np.float64)
            value[..., channel] = atom
            columns.append(value.reshape(-1))
    return np.column_stack(columns)



def load_packet_history(path: Path) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            grouped.setdefault(row["case"], []).append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["iteration"]))
    return grouped


def replay_packet_core(
    image: Array,
    case_name: str,
    history_rows: Sequence[dict[str, str]],
    max_packets: int,
) -> atlas.ReconstructionResult:
    solver = atlas.InfinitePacketReconstructor(
        image,
        complexity_weight=0.035,
        max_candidates_per_iteration=170,
        residual_refresh=5,
        quadtree_refine_every=4,
        random_seed=20260731 + len(case_name),
    )
    snapshots: dict[int, Array] = {1: solver.reconstruction.copy()}
    for row in history_rows:
        if len(solver.active_specs) >= max_packets:
            break
        iteration = int(row["iteration"])
        solver._refresh_candidates(iteration)
        key = row["spec_key"]
        spec = solver.candidate_specs.get(key)
        if spec is None:
            raise KeyError(f"recorded packet {key} was not regenerated for {case_name} at iteration {iteration}")
        candidate = solver._score_spec(spec)
        if candidate is None:
            raise RuntimeError(f"recorded packet {key} could not be scored during replay")
        solver._add_candidate(candidate, iteration)
        count = len(solver.active_specs)
        if count in {8, 16, 32, 44, max_packets}:
            snapshots[count] = solver.reconstruction.copy()
    if len(solver.active_specs) != max_packets:
        raise AssertionError((case_name, len(solver.active_specs), max_packets))
    return atlas.ReconstructionResult(
        reconstruction=solver.reconstruction.copy(),
        residual=solver.residual.copy(),
        coefficients=solver.coefficients.copy(),
        active_specs=list(solver.active_specs),
        active_atoms=[atom.copy() for atom in solver.active_atoms],
        history=list(solver.history),
        snapshots=snapshots,
        residual_norms=list(solver.residual_norms),
        runtime_seconds=0.0,
        exact_archive_residual=solver.residual.copy(),
    )


def exact_packet_core_refit(image: Array, active_atoms: Sequence[Array]) -> tuple[Array, Array, Array]:
    value = atlas.ensure_image(image)
    matrix = _core_design(active_atoms, value.shape[2])
    target = value.reshape(-1)
    coefficients = np.linalg.lstsq(matrix, target, rcond=1e-11)[0]
    reconstruction = (matrix @ coefficients).reshape(value.shape)
    return reconstruction, coefficients, matrix


def packet_span_svd(
    result: atlas.ReconstructionResult,
    tolerance: float = 1e-11,
) -> dict[str, Any]:
    packet_matrix = np.column_stack([atom.reshape(-1) for atom in result.active_atoms])
    U, singular_values, Vt = np.linalg.svd(packet_matrix, full_matrices=False)
    rank = int(np.sum(singular_values > tolerance * max(float(singular_values[0]), 1e-15)))
    transformed_coefficients = singular_values[:, None] * (Vt @ result.coefficients)
    exact = (U @ transformed_coefficients).reshape(result.reconstruction.shape)
    coordinate_energy = np.sum(transformed_coefficients * transformed_coefficients, axis=1)
    order = np.argsort(coordinate_energy)[::-1]
    return {
        'U': U,
        'singular_values': singular_values,
        'Vt': Vt,
        'coefficients': transformed_coefficients,
        'coordinate_energy': coordinate_energy,
        'energy_order': order,
        'rank': rank,
        'condition_number': float(singular_values[0] / max(singular_values[rank - 1], 1e-15)) if rank else math.inf,
        'exact_reconstruction': exact,
        'exact_residual': float(np.max(np.abs(exact - result.reconstruction))),
    }


def packet_singular_truncation(
    packet_svd: dict[str, Any],
    shape: tuple[int, int, int],
    count: int,
) -> Array:
    order = packet_svd['energy_order'][: max(0, min(count, len(packet_svd['energy_order'])))]
    if len(order) == 0:
        return np.zeros(shape, dtype=np.float64)
    U = packet_svd['U'][:, order]
    coefficients = packet_svd['coefficients'][order]
    return (U @ coefficients).reshape(shape)


def _raw_image_array(image: Array) -> Array:
    value = np.asarray(image, dtype=np.float64)
    if value.ndim == 2:
        value = value[..., None]
    if value.ndim != 3 or not np.isfinite(value).all():
        raise ValueError("array must be finite with shape H x W or H x W x C")
    return value


def joint_svd_decomposition(image: Array) -> tuple[Array, Array, Array]:
    value = _raw_image_array(image)
    height, width, channels = value.shape
    matrix = value.reshape(height, width * channels)
    return np.linalg.svd(matrix, full_matrices=False)


def joint_svd_reconstruction(
    image: Array,
    rank: int,
    decomposition: tuple[Array, Array, Array] | None = None,
) -> Array:
    value = _raw_image_array(image)
    height, width, channels = value.shape
    U, singular_values, Vt = decomposition if decomposition is not None else joint_svd_decomposition(value)
    r = max(0, min(rank, len(singular_values)))
    if r == 0:
        return np.zeros_like(value)
    matrix = (U[:, :r] * singular_values[:r]) @ Vt[:r]
    return matrix.reshape(height, width, channels)


def per_channel_svd_reconstruction(image: Array, rank_per_channel: int) -> Array:
    value = atlas.ensure_image(image)
    reconstruction = np.zeros_like(value)
    for channel in range(value.shape[2]):
        U, singular_values, Vt = np.linalg.svd(value[..., channel], full_matrices=False)
        r = max(0, min(rank_per_channel, len(singular_values)))
        reconstruction[..., channel] = (U[:, :r] * singular_values[:r]) @ Vt[:r]
    return reconstruction


def dyadic_rectangles(height: int, width: int, max_depth: int = 5, min_size: int = 3) -> list[tuple[int, int, int, int, int]]:
    rectangles: list[tuple[int, int, int, int, int]] = []
    frontier = [(0, 0, height, width, 0)]
    while frontier:
        y0, x0, y1, x1, depth = frontier.pop()
        rectangles.append((y0, x0, y1, x1, depth))
        h, w = y1 - y0, x1 - x0
        if depth >= max_depth or (h <= min_size and w <= min_size):
            continue
        ym = (y0 + y1) // 2
        xm = (x0 + x1) // 2
        children = [
            (y0, x0, ym, xm, depth + 1),
            (y0, xm, ym, x1, depth + 1),
            (ym, x0, y1, xm, depth + 1),
            (ym, xm, y1, x1, depth + 1),
        ]
        for child in children:
            if child[2] > child[0] and child[3] > child[1]:
                frontier.append(child)
    return rectangles


def packet_bounding_rectangles(
    result: atlas.ReconstructionResult,
    max_count: int = 80,
    threshold: float = 0.22,
) -> list[tuple[int, int, int, int, int]]:
    rectangles: list[tuple[int, int, int, int, int]] = []
    for spec, atom in zip(result.active_specs, result.active_atoms, strict=True):
        if spec.kind in {'constant', 'dct'}:
            continue
        magnitude = np.abs(atom)
        maximum = float(magnitude.max())
        if maximum <= 1e-12:
            continue
        mask = magnitude >= threshold * maximum
        points = np.argwhere(mask)
        if points.size == 0:
            continue
        y0, x0 = points.min(axis=0)
        y1, x1 = points.max(axis=0) + 1
        if (y1 - y0) * (x1 - x0) <= 3:
            continue
        rectangles.append((int(y0), int(x0), int(y1), int(x1), int(spec.depth)))
        if len(rectangles) >= max_count:
            break
    return rectangles


def unique_rectangles(rectangles: Iterable[tuple[int, int, int, int, int]]) -> list[tuple[int, int, int, int, int]]:
    best: dict[tuple[int, int, int, int], int] = {}
    for y0, x0, y1, x1, depth in rectangles:
        key = (int(y0), int(x0), int(y1), int(x1))
        best[key] = min(int(depth), best.get(key, int(depth)))
    return [(*key, depth) for key, depth in sorted(best.items(), key=lambda item: (item[1], item[0]))]


def local_singular_direction(residual: Array, rectangle: tuple[int, int, int, int, int]) -> tuple[Array, float, int]:
    y0, x0, y1, x1, _ = rectangle
    patch = residual[y0:y1, x0:x1]
    h, w, channels = patch.shape
    matrix = patch.reshape(h, w * channels)
    if min(matrix.shape) <= 0 or float(np.linalg.norm(matrix)) <= 1e-14:
        return np.zeros_like(residual), 0.0, 0
    U, singular_values, Vt = np.linalg.svd(matrix, full_matrices=False)
    sigma = float(singular_values[0])
    component_patch = sigma * np.outer(U[:, 0], Vt[0]).reshape(h, w, channels)
    component = np.zeros_like(residual)
    component[y0:y1, x0:x1] = component_patch
    parameter_count = int(h + w * channels + 6)
    return component, sigma, parameter_count


def _orthonormal_basis(matrix: Array, tolerance: float = 1e-10) -> Array:
    if matrix.size == 0 or matrix.shape[1] == 0:
        return np.empty((matrix.shape[0], 0), dtype=np.float64)
    U, singular_values, _ = np.linalg.svd(matrix, full_matrices=False)
    rank = int(np.sum(singular_values > tolerance * max(float(singular_values[0]), 1e-15)))
    return U[:, :rank]


def core_channel_basis(active_atoms: Sequence[Array], channels: int, tolerance: float = 1e-11) -> Array:
    packet_matrix = np.column_stack([atom.reshape(-1) for atom in active_atoms])
    U_packet, singular_values, _ = np.linalg.svd(packet_matrix, full_matrices=False)
    rank = int(np.sum(singular_values > tolerance * max(float(singular_values[0]), 1e-15)))
    height, width = active_atoms[0].shape
    columns: list[Array] = []
    for index in range(rank):
        spatial = U_packet[:, index].reshape(height, width)
        for channel in range(channels):
            column = np.zeros((height, width, channels), dtype=np.float64)
            column[..., channel] = spatial
            columns.append(column.reshape(-1))
    return np.column_stack(columns) if columns else np.empty((height * width * channels, 0), dtype=np.float64)


def project_with_core_and_directions(
    image: Array,
    active_atoms: Sequence[Array],
    directions: Sequence[Array],
) -> Array:
    value = atlas.ensure_image(image)
    target = value.reshape(-1)
    basis = core_channel_basis(active_atoms, value.shape[2])
    for direction_image in directions:
        direction = np.asarray(direction_image, dtype=np.float64).reshape(-1)
        norm = float(np.linalg.norm(direction))
        if norm <= 1e-14:
            continue
        direction = direction / norm
        orthogonal = direction - basis @ (basis.T @ direction) if basis.shape[1] else direction
        if basis.shape[1]:
            orthogonal -= basis @ (basis.T @ orthogonal)
        orthogonal_norm = float(np.linalg.norm(orthogonal))
        if orthogonal_norm <= 1e-10:
            continue
        unit = orthogonal / orthogonal_norm
        basis = np.column_stack([basis, unit])
    return (basis @ (basis.T @ target)).reshape(value.shape) if basis.shape[1] else np.zeros_like(value)


def global_svd_directions(signal: Array, rank: int) -> list[Array]:
    value = _raw_image_array(signal)
    height, width, channels = value.shape
    U, singular_values, Vt = joint_svd_decomposition(value)
    output: list[Array] = []
    for index in range(min(rank, len(singular_values))):
        direction = np.outer(U[:, index], Vt[index]).reshape(height, width, channels)
        output.append(direction)
    return output


def singular_packet_completion(
    image: Array,
    core_result: atlas.ReconstructionResult,
    mode_budget: int = 22,
    max_depth: int = 5,
    max_regions_per_iteration: int = 28,
    complexity_exponent: float = 0.50,
    snapshot_modes: Sequence[int] = (1, 4, 8, 12, 16, 22),
    parameter_budget: int | None = None,
) -> SingularPacketResult:
    started = time.perf_counter()
    value = atlas.ensure_image(image)
    height, width, channels = value.shape
    target = value.reshape(-1)

    # The packet-span SVD supplies an orthonormal basis for the exact core span.
    basis = core_channel_basis(core_result.active_atoms, channels)
    # Columns are exactly orthonormal because spatial_basis is orthonormal and channels are disjoint.
    projection_coefficients = basis.T @ target if basis.shape[1] else np.empty(0)
    reconstruction_flat = basis @ projection_coefficients if basis.shape[1] else np.zeros_like(target)
    residual_flat = target - reconstruction_flat

    directions: list[Array] = []
    modes: list[SingularPacketMode] = []
    parameter_counts: list[int] = [0]
    residual_norms: list[float] = [float(np.linalg.norm(residual_flat))]
    snapshots: dict[int, Array] = {}
    cumulative_parameters = 0

    rectangles = unique_rectangles(
        dyadic_rectangles(height, width, max_depth=max_depth)
        + packet_bounding_rectangles(core_result)
    )

    for iteration in range(1, mode_budget + 1):
        residual = residual_flat.reshape(value.shape)
        energy_image = np.sum(residual * residual, axis=2)
        region_scores: list[tuple[float, tuple[int, int, int, int, int]]] = []
        for rectangle in rectangles:
            y0, x0, y1, x1, _ = rectangle
            h, w = y1 - y0, x1 - x0
            energy = float(np.sum(energy_image[y0:y1, x0:x1]))
            params = h + w * channels + 6
            region_scores.append((energy / max(params, 1) ** complexity_exponent, rectangle))
        region_scores.sort(key=lambda item: item[0], reverse=True)

        # Compute local SVDs only on the strongest energy regions. The leading
        # singular value is the exact rank-one residual gain before span removal.
        candidates: list[tuple[float, Array, float, int, tuple[int, int, int, int, int]]] = []
        for _, rectangle in region_scores[:max_regions_per_iteration]:
            component, sigma, parameter_count = local_singular_direction(residual, rectangle)
            if parameter_budget is not None and cumulative_parameters + parameter_count > parameter_budget:
                continue
            if sigma <= 1e-13:
                continue
            direction = component.reshape(-1)
            norm = float(np.linalg.norm(direction))
            if norm <= 1e-13:
                continue
            direction /= norm
            score = sigma * sigma / max(parameter_count, 1) ** complexity_exponent
            candidates.append((score, direction, sigma, parameter_count, rectangle))
        candidates.sort(key=lambda item: item[0], reverse=True)

        selected = None
        for score, direction, sigma, parameter_count, rectangle in candidates:
            orthogonal = direction - basis @ (basis.T @ direction) if basis.shape[1] else direction.copy()
            if basis.shape[1]:
                orthogonal -= basis @ (basis.T @ orthogonal)
            orthogonal_norm = float(np.linalg.norm(orthogonal))
            if orthogonal_norm <= 1e-8:
                continue
            unit = orthogonal / orthogonal_norm
            coefficient = float(unit @ residual_flat)
            gain = coefficient * coefficient
            if gain <= 1e-14:
                continue
            selected = (score, gain, unit, sigma, parameter_count, rectangle, coefficient)
            break
        if selected is None:
            break

        score, gain, unit, sigma, parameter_count, rectangle, coefficient = selected
        basis = np.column_stack([basis, unit])
        reconstruction_flat = reconstruction_flat + coefficient * unit
        residual_flat = residual_flat - coefficient * unit
        directions.append(unit.reshape(value.shape))
        cumulative_parameters += parameter_count
        residual_norm = float(np.linalg.norm(residual_flat))
        residual_norms.append(residual_norm)
        parameter_counts.append(cumulative_parameters)
        modes.append(
            SingularPacketMode(
                iteration=iteration,
                rectangle=rectangle[:4],
                depth=rectangle[4],
                singular_value=sigma,
                gain=gain,
                score=score,
                parameter_count=parameter_count,
                cumulative_parameter_count=cumulative_parameters,
                residual_norm=residual_norm,
                component_norm=1.0,
            )
        )
        if iteration in snapshot_modes:
            snapshots[iteration] = reconstruction_flat.reshape(value.shape).copy()

    runtime = time.perf_counter() - started
    return SingularPacketResult(
        reconstruction=reconstruction_flat.reshape(value.shape),
        residual=residual_flat.reshape(value.shape),
        modes=modes,
        directions=directions,
        coefficients=np.r_[projection_coefficients, [float(direction.reshape(-1) @ target) for direction in directions]],
        residual_norms=residual_norms,
        runtime_seconds=runtime,
        parameter_counts=parameter_counts,
        snapshots=snapshots,
    )


def dct_residual_curve(residual: Array, max_count: int) -> tuple[list[Array], list[int]]:
    value = _raw_image_array(residual)
    channels = value.shape[2]
    coefficients = np.stack([atlas.spfft.dctn(value[..., channel], norm='ortho') for channel in range(channels)], axis=-1)
    energy = np.sum(coefficients * coefficients, axis=2)
    order = np.argsort(energy.ravel())[::-1]
    outputs: list[Array] = []
    params: list[int] = []
    mask = np.zeros(energy.size, dtype=bool)
    for count in range(1, max_count + 1):
        mask[order[count - 1]] = True
        shaped = mask.reshape(energy.shape)
        filtered = coefficients * shaped[..., None]
        reconstruction = np.stack([atlas.spfft.idctn(filtered[..., channel], norm='ortho') for channel in range(channels)], axis=-1)
        outputs.append(reconstruction)
        params.append(count * (channels + 2))
    return outputs, params


def global_residual_svd_curve(residual: Array, max_rank: int) -> tuple[list[Array], list[int]]:
    value = _raw_image_array(residual)
    height, width, channels = value.shape
    U, singular_values, Vt = joint_svd_decomposition(value)
    outputs: list[Array] = []
    params: list[int] = []
    for rank in range(1, min(max_rank, len(singular_values)) + 1):
        outputs.append(joint_svd_reconstruction(value, rank, (U, singular_values, Vt)))
        params.append(rank * (height + width * channels + 1))
    return outputs, params


def metric_row(case: str, method: str, image: Array, reconstruction: Array, **extra: Any) -> dict[str, Any]:
    row: dict[str, Any] = {'case': case, 'method': method}
    row.update(atlas.image_metrics(image, atlas.bounded_synthesis(reconstruction)))
    row.update(extra)
    return row


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    if not rows:
        path.write_text('', encoding='utf-8')
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def save_figure(fig: plt.Figure, root: Path, name: str) -> None:
    directory = root / 'figures'
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(directory / f'{name}.png', dpi=220, bbox_inches='tight')
    plt.close(fig)


def display_image(ax: plt.Axes, image: Array, title: str) -> None:
    value = atlas.bounded_synthesis(image)
    if value.shape[2] == 1:
        ax.imshow(value[..., 0], cmap='gray', vmin=0, vmax=1)
    else:
        ax.imshow(value[..., :3])
    ax.set_title(title, fontsize=10, weight='bold')
    ax.set_xticks([])
    ax.set_yticks([])


def generate_case_figures(
    root: Path,
    case_index: int,
    name: str,
    image: Array,
    packet_result: atlas.ReconstructionResult,
    packet_svd: dict[str, Any],
    spd: SingularPacketResult,
    methods: dict[str, Array],
    curves: dict[str, Any],
) -> None:
    prefix = 36 + 4 * case_index
    fig, axes = plt.subplots(2, 4, figsize=(14.5, 7.2))
    display_image(axes[0, 0], image, 'truth')
    display_image(axes[0, 1], methods['global_svd'], 'global SVD')
    display_image(axes[0, 2], methods['packet_core_refit'], 'packet core')
    display_image(axes[0, 3], methods['packet_dct'], 'core + DCT residual')
    display_image(axes[1, 0], methods['packet_global_svd'], 'core + global residual SVD')
    display_image(axes[1, 1], methods['packet_spd'], 'core + singular packets')
    axes[1, 2].imshow(np.sqrt(np.sum((methods['packet_spd'] - image) ** 2, axis=2)), cmap='magma')
    axes[1, 2].set_title('singular-packet error', fontsize=10, weight='bold')
    axes[1, 2].set_xticks([])
    axes[1, 2].set_yticks([])
    montage_count = min(12, len(spd.directions))
    if montage_count:
        h, w, c = image.shape
        tiles = []
        for direction in spd.directions[:montage_count]:
            magnitude = np.sqrt(np.sum(direction * direction, axis=2))
            if float(magnitude.max()) > 0:
                magnitude = magnitude / magnitude.max()
            tiles.append(magnitude)
        rows = 3
        cols = math.ceil(montage_count / rows)
        canvas = np.zeros((rows * h, cols * w))
        for index, tile in enumerate(tiles):
            rr, cc = divmod(index, cols)
            canvas[rr*h:(rr+1)*h, cc*w:(cc+1)*w] = tile
        axes[1, 3].imshow(canvas, cmap='viridis')
        axes[1, 3].set_title('first singular packets', fontsize=10, weight='bold')
    axes[1, 3].set_xticks([])
    axes[1, 3].set_yticks([])
    fig.suptitle(name.replace('_', ' '), fontsize=16, weight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, root, f'{prefix:02d}_{name}_svd_spd_comparison')

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))
    singular_values = packet_svd['singular_values']
    axes[0].semilogy(np.arange(1, len(singular_values) + 1), singular_values, marker='o', markersize=3, color=atlas.BLUE)
    axes[0].set_xlabel('packet-span singular coordinate')
    axes[0].set_ylabel('singular value')
    axes[0].set_title('selected packet-span spectrum', weight='bold')
    axes[0].grid(alpha=0.18, which='both')
    axes[1].semilogy(np.arange(1, len(packet_svd['energy_order']) + 1), np.sort(packet_svd['coordinate_energy'])[::-1] + 1e-20, color=atlas.TEAL)
    axes[1].set_xlabel('singular packet ordered by image energy')
    axes[1].set_ylabel('coordinate energy')
    axes[1].set_title('canonical singular-packet energy', weight='bold')
    axes[1].grid(alpha=0.18, which='both')
    axes[2].plot(np.arange(len(spd.residual_norms)), np.array(spd.residual_norms) / max(spd.residual_norms[0], 1e-15), marker='o', markersize=3, color=atlas.MAGENTA)
    axes[2].set_xlabel('added local singular packets')
    axes[2].set_ylabel('relative residual norm')
    axes[2].set_title('monotone hybrid refinement', weight='bold')
    axes[2].grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, root, f'{prefix+1:02d}_{name}_singular_spectra')

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    for label, color in [('dct', atlas.ORANGE), ('global_svd', atlas.BLUE), ('spd', atlas.TEAL)]:
        axes[0].plot(curves[label]['components'], curves[label]['rmse'], marker='o', markersize=3, label=label.replace('_', ' '), color=color)
        axes[1].plot(curves[label]['parameters'], curves[label]['rmse'], marker='o', markersize=3, label=label.replace('_', ' '), color=color)
    axes[0].set_xlabel('residual components')
    axes[0].set_ylabel('completed-image RMSE')
    axes[0].set_title('component-matched completion', weight='bold')
    axes[0].set_yscale('log')
    axes[0].grid(alpha=0.18, which='both')
    axes[0].legend()
    axes[1].set_xlabel('estimated added scalar parameters')
    axes[1].set_ylabel('completed-image RMSE')
    axes[1].set_title('parameter-aware completion', weight='bold')
    axes[1].set_xscale('log')
    axes[1].set_yscale('log')
    axes[1].grid(alpha=0.18, which='both')
    axes[1].legend()
    fig.tight_layout()
    save_figure(fig, root, f'{prefix+2:02d}_{name}_rate_distortion')

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    rectangles = [mode.rectangle for mode in spd.modes]
    display_image(ax, image, 'singular-packet support path')
    colors = plt.cm.viridis(np.linspace(0.1, 0.95, max(1, len(rectangles))))
    for index, (rectangle, color) in enumerate(zip(rectangles, colors, strict=True)):
        y0, x0, y1, x1 = rectangle
        patch = plt.Rectangle((x0, y0), x1-x0, y1-y0, fill=False, edgecolor=color, linewidth=1.2)
        ax.add_patch(patch)
        if index < 12:
            ax.text(x0+1, y0+2, str(index+1), fontsize=6.5, color=color, weight='bold')
    ax.set_title('adaptive local SVD packet rectangles', weight='bold')
    fig.tight_layout()
    save_figure(fig, root, f'{prefix+3:02d}_{name}_singular_packet_supports')


def global_summary_figures(root: Path, all_rows: list[dict[str, Any]], case_summaries: dict[str, dict[str, Any]]) -> None:
    frame = {case: {} for case in case_summaries}
    for row in all_rows:
        frame[row['case']][row['method']] = row
    cases = list(case_summaries)
    methods = ['global_svd', 'pure_spd', 'packet_core_refit', 'packet_dct', 'packet_spd']
    labels = ['global SVD', 'pure SPD', 'packet core', 'core + DCT', 'core + SPD']
    colors = [atlas.BLUE, '#6C5CE7', atlas.ORANGE, atlas.YELLOW, atlas.TEAL]
    x = np.arange(len(cases))
    width = 0.15
    fig, ax = plt.subplots(figsize=(12.2, 5.2))
    for index, (method, label, color) in enumerate(zip(methods, labels, colors, strict=True)):
        values = [frame[case][method]['rmse'] for case in cases]
        ax.bar(x + (index-2)*width, values, width, label=label, color=color)
    ax.set_xticks(x, [case.replace('_', '\n') for case in cases])
    ax.set_yscale('log')
    ax.set_ylabel('RMSE')
    ax.set_title('Direct SVD and singular-packet comparison', weight='bold')
    ax.legend(ncol=3, fontsize=8)
    ax.grid(axis='y', alpha=0.18, which='both')
    fig.tight_layout()
    save_figure(fig, root, '52_global_svd_spd_rmse')

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.6))
    ranks = [case_summaries[case]['packet_span_rank'] for case in cases]
    packets = [case_summaries[case]['packet_count'] for case in cases]
    conds = [case_summaries[case]['packet_span_condition'] for case in cases]
    axes[0].bar(x-0.18, packets, 0.36, label='selected packet atoms', color=atlas.ORANGE)
    axes[0].bar(x+0.18, ranks, 0.36, label='numerical packet-span rank', color=atlas.TEAL)
    axes[0].set_xticks(x, [case.replace('_', '\n') for case in cases], fontsize=8)
    axes[0].set_ylabel('dimension')
    axes[0].set_title('SVD exposes packet redundancy', weight='bold')
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.18)
    axes[1].bar(x, conds, color=atlas.BLUE)
    axes[1].set_xticks(x, [case.replace('_', '\n') for case in cases], fontsize=8)
    axes[1].set_yscale('log')
    axes[1].set_ylabel('condition number')
    axes[1].set_title('conditioning of the selected packet span', weight='bold')
    axes[1].grid(axis='y', alpha=0.18, which='both')
    fig.tight_layout()
    save_figure(fig, root, '53_packet_span_rank_condition')

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    dct = [frame[case]['packet_dct']['rmse'] for case in cases]
    spd = [frame[case]['packet_spd']['rmse'] for case in cases]
    global_residual = [frame[case]['packet_global_svd']['rmse'] for case in cases]
    ax.scatter(dct, spd, s=85, color=atlas.TEAL, label='SPD vs DCT')
    ax.scatter(global_residual, spd, s=85, color=atlas.MAGENTA, marker='s', label='SPD vs global residual SVD')
    lo = min(dct + spd + global_residual)
    hi = max(dct + spd + global_residual)
    ax.plot([lo, hi], [lo, hi], '--', color=atlas.MUTED)
    for case, xv, yv in zip(cases, dct, spd, strict=True):
        ax.annotate(case.replace('_',' '), (xv,yv), xytext=(4,4), textcoords='offset points', fontsize=7)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('comparison-method RMSE')
    ax.set_ylabel('singular-packet RMSE')
    ax.set_title('Residual completion methods', weight='bold')
    ax.legend()
    ax.grid(alpha=0.18, which='both')
    fig.tight_layout()
    save_figure(fig, root, '54_residual_completion_scatter')


def constant_core_result(image: Array) -> atlas.ReconstructionResult:
    value = atlas.ensure_image(image)
    atom = atlas.normalize_atom(np.ones(value.shape[:2], dtype=np.float64))
    if atom is None:
        raise RuntimeError("constant atom failed")
    matrix = _core_design([atom], value.shape[2])
    coefficients = np.linalg.lstsq(matrix, value.reshape(-1), rcond=1e-12)[0]
    reconstruction = (matrix @ coefficients).reshape(value.shape)
    residual = value - reconstruction
    spec = atlas.PacketSpec("constant", (), depth=0, complexity=0.5)
    return atlas.ReconstructionResult(
        reconstruction=reconstruction,
        residual=residual,
        coefficients=coefficients.reshape(1, value.shape[2]),
        active_specs=[spec],
        active_atoms=[atom],
        history=[],
        snapshots={1: reconstruction.copy()},
        residual_norms=[float(np.linalg.norm(residual))],
        runtime_seconds=0.0,
        exact_archive_residual=residual.copy(),
    )


def run(base: Path, size: int = 56, packet_budget: int = 44, singular_budget: int = 22) -> dict[str, Any]:
    base = base.resolve()
    for name in ('figures', 'tables', 'results'):
        (base / name).mkdir(parents=True, exist_ok=True)
    images = atlas.benchmark_images(size)
    histories = load_packet_history(base / 'tables' / 'packet_history.csv')
    all_rows: list[dict[str, Any]] = []
    all_mode_rows: list[dict[str, Any]] = []
    case_summaries: dict[str, dict[str, Any]] = {}

    for case_index, (name, image) in enumerate(images.items()):
        print(f'Replaying packet core: {name}', flush=True)
        packet_result = replay_packet_core(image, name, histories[name], packet_budget)
        packet_svd = packet_span_svd(packet_result)
        core_refit, _, _ = exact_packet_core_refit(image, packet_result.active_atoms)
        residual = image - core_refit

        print(f'Running singular packets: {name}', flush=True)
        spd = singular_packet_completion(image, packet_result, mode_budget=singular_budget)
        packet_spd = atlas.bounded_synthesis(spd.reconstruction)
        pure_spd_result = singular_packet_completion(image, constant_core_result(image), mode_budget=singular_budget)
        pure_spd = atlas.bounded_synthesis(pure_spd_result.reconstruction)
        dct_component = atlas.sparse_dct_component(residual, singular_budget)
        packet_dct = atlas.bounded_synthesis(core_refit + dct_component)
        residual_svd_decomposition = joint_svd_decomposition(residual)
        residual_svd_directions = global_svd_directions(residual, singular_budget)
        packet_global_svd = atlas.bounded_synthesis(project_with_core_and_directions(image, packet_result.active_atoms, residual_svd_directions))
        image_svd_decomposition = joint_svd_decomposition(image)
        global_svd = atlas.bounded_synthesis(joint_svd_reconstruction(image, singular_budget, image_svd_decomposition))
        channel_rank = max(1, singular_budget // max(image.shape[2], 1))
        channel_svd = atlas.bounded_synthesis(per_channel_svd_reconstruction(image, channel_rank))
        global_component_cost = image.shape[0] + image.shape[1] * image.shape[2] + 1
        pure_param_rank = max(1, min(len(image_svd_decomposition[1]), (pure_spd_result.parameter_counts[-1] + image.shape[2]) // global_component_cost))
        residual_param_rank = max(1, min(len(residual_svd_decomposition[1]), spd.parameter_counts[-1] // global_component_cost))
        global_svd_param = atlas.bounded_synthesis(joint_svd_reconstruction(image, pure_param_rank, image_svd_decomposition))
        packet_global_svd_param = atlas.bounded_synthesis(project_with_core_and_directions(image, packet_result.active_atoms, global_svd_directions(residual, residual_param_rank)))

        methods = {
            'global_svd': global_svd,
            'global_svd_param_matched': global_svd_param,
            'channel_svd': channel_svd,
            'packet_core_original': packet_result.reconstruction,
            'packet_core_refit': core_refit,
            'packet_dct': packet_dct,
            'packet_global_svd': packet_global_svd,
            'packet_global_svd_param_matched': packet_global_svd_param,
            'packet_spd': packet_spd,
            'pure_spd': pure_spd,
        }
        for method, reconstruction in methods.items():
            extra: dict[str, Any] = {'component_budget': singular_budget}
            if method == 'global_svd':
                extra['estimated_parameters'] = singular_budget * global_component_cost
                extra['rank'] = singular_budget
            elif method == 'global_svd_param_matched':
                extra['estimated_parameters'] = pure_param_rank * global_component_cost
                extra['rank'] = pure_param_rank
            elif method == 'channel_svd':
                extra['estimated_parameters'] = channel_rank * image.shape[2] * (2*size + 1)
            elif method == 'packet_dct':
                extra['estimated_added_parameters'] = singular_budget * (image.shape[2] + 2)
            elif method == 'packet_global_svd':
                extra['estimated_added_parameters'] = singular_budget * global_component_cost
                extra['rank'] = singular_budget
            elif method == 'packet_global_svd_param_matched':
                extra['estimated_added_parameters'] = residual_param_rank * global_component_cost
                extra['rank'] = residual_param_rank
            elif method == 'packet_spd':
                extra['estimated_added_parameters'] = spd.parameter_counts[-1]
                extra['runtime_seconds'] = spd.runtime_seconds
            elif method == 'pure_spd':
                extra['estimated_parameters'] = pure_spd_result.parameter_counts[-1] + image.shape[2]
                extra['runtime_seconds'] = pure_spd_result.runtime_seconds
            row = metric_row(name, method, image, reconstruction, **extra)
            all_rows.append(row)

        dct_curve_components, dct_parameters = dct_residual_curve(residual, singular_budget)
        global_curve_components, global_parameters = global_residual_svd_curve(residual, singular_budget)
        spd_rmse = []
        spd_parameters = []
        spd_components = []
        # Use stored snapshots. Fill absent counts by the final fit at available iterations only.
        for count in sorted(spd.snapshots):
            spd_components.append(count)
            spd_parameters.append(spd.parameter_counts[count])
            spd_rmse.append(atlas.rmse(image, atlas.bounded_synthesis(spd.snapshots[count])))
        curves = {
            'dct': {
                'components': list(range(1, len(dct_curve_components)+1)),
                'parameters': dct_parameters,
                'rmse': [atlas.rmse(image, atlas.bounded_synthesis(core_refit + comp)) for comp in dct_curve_components],
            },
            'global_svd': {
                'components': list(range(1, len(global_curve_components)+1)),
                'parameters': global_parameters,
                'rmse': [atlas.rmse(image, atlas.bounded_synthesis(core_refit + comp)) for comp in global_curve_components],
            },
            'spd': {
                'components': spd_components,
                'parameters': spd_parameters,
                'rmse': spd_rmse,
            },
        }
        for mode in spd.modes:
            row = asdict(mode)
            row['case'] = name
            all_mode_rows.append(row)

        singular_values = packet_svd['singular_values']
        ordered_energy = np.sort(packet_svd['coordinate_energy'])[::-1]
        cumulative_energy = np.cumsum(ordered_energy) / max(float(np.sum(ordered_energy)), 1e-20)
        count_99 = int(np.searchsorted(cumulative_energy, 0.99) + 1)
        count_999 = int(np.searchsorted(cumulative_energy, 0.999) + 1)
        case_summaries[name] = {
            'packet_count': len(packet_result.active_atoms),
            'packet_span_rank': packet_svd['rank'],
            'packet_span_condition': packet_svd['condition_number'],
            'packet_svd_exact_residual': packet_svd['exact_residual'],
            'packet_span_singular_values': singular_values.tolist(),
            'singular_packets_for_99pct_core_energy': count_99,
            'singular_packets_for_999pct_core_energy': count_999,
            'top10_singular_packet_energy_fraction': float(cumulative_energy[min(9, len(cumulative_energy)-1)]),
            'singular_packet_count': len(spd.modes),
            'singular_packet_parameters': spd.parameter_counts[-1],
            'singular_packet_runtime_seconds': spd.runtime_seconds,
            'pure_singular_packet_parameters': pure_spd_result.parameter_counts[-1] + image.shape[2],
            'pure_singular_packet_runtime_seconds': pure_spd_result.runtime_seconds,
            'global_svd_parameter_matched_rank': pure_param_rank,
            'residual_svd_parameter_matched_rank': residual_param_rank,
            'singular_packet_residual_monotone': bool(np.all(np.diff(spd.residual_norms) <= 1e-8)),
            'curves': curves,
        }
        generate_case_figures(base, case_index, name, image, packet_result, packet_svd, spd, methods, curves)

    global_summary_figures(base, all_rows, case_summaries)
    write_csv(base / 'tables' / 'svd_spd_metrics.csv', all_rows)
    write_csv(base / 'tables' / 'singular_packet_modes.csv', all_mode_rows)

    checks = {
        'packet_svd_exact_max': max(summary['packet_svd_exact_residual'] for summary in case_summaries.values()),
        'singular_packet_monotone_all': all(summary['singular_packet_residual_monotone'] for summary in case_summaries.values()),
        'singular_packet_count_min': min(summary['singular_packet_count'] for summary in case_summaries.values()),
        'finite_metrics': all(math.isfinite(float(row['rmse'])) for row in all_rows),
        'figure_pairs_added': len(list((base / 'figures').glob('[3-5][0-9]_*.pdf'))),
    }
    if checks['packet_svd_exact_max'] > 2e-9:
        raise AssertionError('packet-span SVD did not reconstruct the packet core')
    if not checks['singular_packet_monotone_all']:
        raise AssertionError('singular packet residual was not monotone')
    if checks['singular_packet_count_min'] < max(4, singular_budget // 2):
        raise AssertionError('singular packet search terminated too early')
    if not checks['finite_metrics']:
        raise AssertionError('nonfinite metrics')

    summary = {
        'title': 'Projector-Resolved Singular Packet Decomposition',
        'subtitle': 'Canonical packet-span SVD, adaptive local singular packets, and direct global SVD comparison',
        'author': 'Komorebi P.',
        'image_size': size,
        'geometric_packet_budget': packet_budget,
        'singular_packet_budget': singular_budget,
        'case_count': len(case_summaries),
        'cases': atlas.safe_json(case_summaries),
        'metrics': atlas.safe_json(all_rows),
        'checks': atlas.safe_json(checks),
        'new_figure_pairs': checks['figure_pairs_added'],
        'definitions': {
            'canonical_spd': 'Thin SVD of the selected packet synthesis matrix P = U Sigma V^T, followed by exact coefficient transport B = Sigma V^T A.',
            'adaptive_spd': 'Residual-driven selection of local rank-one SVD modes on a dyadic and packet-derived region atlas with exact global refitting.',
        },
        'claim_boundary': [
            'Global SVD is optimal only within the chosen global matrix-rank class and matricization.',
            'Component-matched comparisons are not parameter matched because one SVD component contains many scalar degrees of freedom.',
            'The packet atlas is not a self-contained compression code unless seed-mask and grammar costs are included.',
            'Adaptive singular packets give a monotone finite approximation, not a universal sparse-rank theorem for natural images.',
        ],
    }
    (base / 'results' / 'singular_packet_results.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary['checks'], indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description='SVD comparison and Singular Packet Decomposition extension')
    parser.add_argument('--base', type=Path, default=Path('.'))
    parser.add_argument('--size', type=int, default=56)
    parser.add_argument('--packets', type=int, default=44)
    parser.add_argument('--singular-packets', type=int, default=22)
    args = parser.parse_args()
    run(args.base, size=args.size, packet_budget=args.packets, singular_budget=args.singular_packets)


if __name__ == '__main__':
    main()
