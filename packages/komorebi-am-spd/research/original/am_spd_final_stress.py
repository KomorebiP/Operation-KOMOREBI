from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from skimage import color, data, draw, transform

import adaptive_multiscale_spd_exact as exact

Array = NDArray[np.float64]


@dataclass
class StressRow:
    case: str
    method: str
    rmse: float
    parameter_count: int
    leaf_count: int
    rank_sum: int
    row_models: int
    column_models: int
    channel_models: int
    zero_models: int


def ensure_float(image: np.ndarray, size: int) -> Array:
    value = np.asarray(image)
    if value.ndim == 2:
        value = np.repeat(value[..., None], 3, axis=2)
    if value.shape[2] == 4:
        value = value[..., :3]
    value = value.astype(np.float64)
    if value.max() > 1.0:
        value /= 255.0
    value = transform.resize(value, (size, size, value.shape[2]), anti_aliasing=True, preserve_range=True)
    return np.clip(value, 0.0, 1.0)


def synthetic_images(size: int) -> dict[str, Array]:
    yy, xx = np.mgrid[0:size, 0:size]
    t = np.linspace(0.0, 1.0, size)
    X, Y = np.meshgrid(t, t)

    diagonal = np.zeros((size, size, 3), dtype=np.float64)
    base = 0.16 + 0.32 * X + 0.18 * Y
    diagonal[..., 0] = base
    diagonal[..., 1] = 0.85 * base
    diagonal[..., 2] = 0.65 * base
    mask = yy > 0.62 * xx + 0.16 * size
    diagonal[mask] += np.array([0.38, 0.18, 0.08])
    diagonal = np.clip(diagonal, 0, 1)

    block = max(2, size // 8)
    checker = (((yy // block) + (xx // block)) % 2).astype(float)
    checker_rgb = np.stack([0.12 + 0.76 * checker, 0.20 + 0.55 * (1 - checker), 0.18 + 0.35 * checker], axis=2)

    cx = cy = (size - 1) / 2
    radius = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    rings = 0.5 + 0.38 * np.sign(np.sin(0.92 * radius))
    concentric = np.stack([rings, 0.55 * rings + 0.15, 1.0 - 0.72 * rings], axis=2)
    concentric = np.clip(concentric, 0, 1)

    angle = np.pi * (0.12 + 0.45 * Y)
    phase = 2 * np.pi * (5.2 * (X * np.cos(angle) + Y * np.sin(angle)))
    texture = 0.5 + 0.36 * np.sin(phase)
    oriented = np.stack([texture, 0.5 + 0.28 * np.cos(phase + 0.7), 0.45 + 0.25 * np.sin(phase * 0.6)], axis=2)
    oriented = np.clip(oriented, 0, 1)

    color_blocks = np.full((size, size, 3), 0.12, dtype=np.float64)
    color_blocks[: size // 2, : size // 2] = [0.82, 0.18, 0.12]
    color_blocks[: size // 2, size // 2 :] = [0.15, 0.72, 0.25]
    color_blocks[size // 2 :, : size // 2] = [0.15, 0.28, 0.82]
    color_blocks[size // 2 :, size // 2 :] = [0.82, 0.72, 0.12]
    rr, cc = draw.disk((0.67 * size, 0.67 * size), 0.16 * size, shape=color_blocks.shape[:2])
    color_blocks[rr, cc] = [0.92, 0.35, 0.75]

    return {
        'diagonal_edge': diagonal,
        'checkerboard': checker_rgb,
        'concentric_rings': concentric,
        'oriented_texture': oriented,
        'color_blocks': color_blocks,
    }


def benchmark_images(size: int) -> dict[str, Array]:
    images = synthetic_images(size)
    images.update(
        {
            'camera': ensure_float(data.camera(), size),
            'coins': ensure_float(data.coins(), size),
            'moon': ensure_float(data.moon(), size),
            'page': ensure_float(data.page(), size),
            'astronaut': ensure_float(data.astronaut(), size),
        }
    )
    return images


def channel_mean_core(image: Array) -> tuple[Array, Array]:
    mean = np.mean(image, axis=(0, 1), keepdims=True)
    core = np.broadcast_to(mean, image.shape).copy()
    return core, image - core


def configured_models(
    residual: Array,
    region: exact.Region,
    orientations: Sequence[str],
    max_rank: int,
) -> list[exact.LocalModel]:
    models = exact.local_models(residual, region, max_rank=max_rank)
    return [model for model in models if model.rank == 0 or (model.orientation in orientations and model.rank <= max_rank)]


def fill_configured_tree(
    node: exact.TreeNode,
    residual: Array,
    orientations: Sequence[str],
    max_rank: int,
) -> None:
    node.models = configured_models(residual, node.region, orientations, max_rank)
    for child in node.children:
        fill_configured_tree(child, residual, orientations, max_rank)


def reconstruct_state(shape: tuple[int, int, int], state: exact.ParetoState) -> Array:
    reconstruction = np.zeros(shape, dtype=np.float64)
    for selection in state.selections:
        model = selection.model
        for singular_value, direction in zip(model.singular_values, model.directions, strict=True):
            reconstruction += float(singular_value) * np.asarray(direction)
    return reconstruction


def tree_method(
    image: Array,
    budget: int,
    max_depth: int,
    max_rank: int,
    orientations: Sequence[str],
) -> tuple[Array, exact.ParetoState]:
    core, residual = channel_mean_core(image)
    root = exact.build_tree(image.shape[0], image.shape[1], max_depth=max_depth)
    fill_configured_tree(root, residual, orientations, max_rank)
    frontier = exact.exact_tree_frontier(root, budget)
    state = exact.best_budget_state(frontier, budget)
    if state is None:
        state = exact.ParetoState(0, float(np.sum(residual * residual)), [])
    reconstruction = core + reconstruct_state(image.shape, state)
    return np.clip(reconstruction, 0.0, 1.0), state


def global_svd_method(image: Array, budget: int) -> tuple[Array, int]:
    core, residual = channel_mean_core(image)
    h, w, channels = residual.shape
    matrix = residual.reshape(h, w * channels)
    cost_per_rank = h + w * channels + 1
    rank = max(0, min(min(matrix.shape), budget // cost_per_rank))
    if rank == 0:
        return core.copy(), 0
    U, singular_values, Vt = np.linalg.svd(matrix, full_matrices=False)
    approximation = (U[:, :rank] * singular_values[:rank]) @ Vt[:rank]
    return np.clip(core + approximation.reshape(image.shape), 0.0, 1.0), rank * cost_per_rank


def rmse(left: Array, right: Array) -> float:
    return float(np.sqrt(np.mean((np.asarray(left) - np.asarray(right)) ** 2)))


def describe_state(case: str, method: str, image: Array, reconstruction: Array, state: exact.ParetoState) -> StressRow:
    orientations = [selection.model.orientation for selection in state.selections]
    return StressRow(
        case=case,
        method=method,
        rmse=rmse(image, reconstruction),
        parameter_count=int(state.parameter_count),
        leaf_count=len(state.selections),
        rank_sum=sum(selection.model.rank for selection in state.selections),
        row_models=orientations.count('row'),
        column_models=orientations.count('column'),
        channel_models=orientations.count('channel'),
        zero_models=orientations.count('zero'),
    )


def save_csv(path: Path, rows: list[StressRow]) -> None:
    import csv

    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def save_figure(fig: plt.Figure, directory: Path, name: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(directory / f'{name}.png', dpi=220, bbox_inches='tight')
    plt.close(fig)


def draw_figures(base: Path, images: dict[str, Array], rows: list[StressRow], reconstructions: dict[tuple[str, str], Array]) -> None:
    figure_dir = base / 'figures'
    methods = ['global_svd', 'row_rank1', 'row_column_rank1', 'full_am_spd']
    labels = ['global SVD', 'row rank 1', 'row + column rank 1', 'full AM-SPD']
    cases = list(images)
    table = {(row.case, row.method): row for row in rows}

    fig, ax = plt.subplots(figsize=(13.0, 5.8))
    x = np.arange(len(cases))
    width = 0.19
    for index, (method, label) in enumerate(zip(methods, labels, strict=True)):
        ax.bar(x + (index - 1.5) * width, [table[(case, method)].rmse for case in cases], width, label=label)
    ax.set_xticks(x, [case.replace('_', '\n') for case in cases], fontsize=8)
    ax.set_ylabel('RMSE')
    ax.set_title('Ten-case exact-tree stress suite')
    ax.legend(ncol=2)
    ax.grid(axis='y', alpha=.18)
    fig.tight_layout()
    save_figure(fig, figure_dir, '101_final_stress_rmse')

    improvement = [1 - table[(case, 'full_am_spd')].rmse / table[(case, 'row_rank1')].rmse for case in cases]
    fig, ax = plt.subplots(figsize=(11.4, 4.8))
    ax.bar([case.replace('_', '\n') for case in cases], [100 * value for value in improvement])
    ax.axhline(0, linewidth=1.0)
    ax.set_ylabel('RMSE reduction from row-only rank-one tree (%)')
    ax.set_title('Value of adaptive orientation and variable local rank')
    ax.grid(axis='y', alpha=.18)
    fig.tight_layout()
    save_figure(fig, figure_dir, '102_final_stress_ablation_gain')

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))
    full_rows = [table[(case, 'full_am_spd')] for case in cases]
    axes[0].bar(cases, [row.row_models for row in full_rows], label='row')
    axes[0].bar(cases, [row.column_models for row in full_rows], bottom=[row.row_models for row in full_rows], label='column')
    bottom = [row.row_models + row.column_models for row in full_rows]
    axes[0].bar(cases, [row.channel_models for row in full_rows], bottom=bottom, label='channel')
    axes[0].set_title('Selected packet orientations')
    axes[0].tick_params(axis='x', rotation=80, labelsize=7)
    axes[0].legend(fontsize=8)
    axes[1].bar(cases, [row.rank_sum for row in full_rows])
    axes[1].set_title('Total selected local rank')
    axes[1].tick_params(axis='x', rotation=80, labelsize=7)
    axes[2].bar(cases, [row.parameter_count for row in full_rows])
    axes[2].set_title('Used parameter budget')
    axes[2].tick_params(axis='x', rotation=80, labelsize=7)
    fig.tight_layout()
    save_figure(fig, figure_dir, '103_final_stress_structure')

    chosen = ['diagonal_edge', 'oriented_texture', 'camera', 'astronaut']
    fig, axes = plt.subplots(len(chosen), 5, figsize=(13.2, 10.2))
    display_methods = ['input', 'global_svd', 'row_rank1', 'row_column_rank1', 'full_am_spd']
    titles = ['input', 'global SVD', 'row rank 1', 'row + column rank 1', 'full AM-SPD']
    for row_index, case in enumerate(chosen):
        for column_index, method in enumerate(display_methods):
            image = images[case] if method == 'input' else reconstructions[(case, method)]
            axes[row_index, column_index].imshow(image)
            axes[row_index, column_index].set_xticks([])
            axes[row_index, column_index].set_yticks([])
            if row_index == 0:
                axes[row_index, column_index].set_title(titles[column_index], fontsize=10)
            if column_index == 0:
                axes[row_index, column_index].set_ylabel(case.replace('_', ' '), fontsize=9)
    fig.tight_layout()
    save_figure(fig, figure_dir, '104_final_stress_reconstructions')


def run(base: Path, size: int = 32, budget: int = 720) -> dict[str, object]:
    base = base.resolve()
    for name in ('figures', 'tables', 'results'):
        (base / name).mkdir(parents=True, exist_ok=True)
    images = benchmark_images(size)
    rows: list[StressRow] = []
    reconstructions: dict[tuple[str, str], Array] = {}

    for case, image in images.items():
        svd_reconstruction, svd_params = global_svd_method(image, budget)
        svd_rank = svd_params // (size + size * image.shape[2] + 1) if svd_params else 0
        rows.append(
            StressRow(case, 'global_svd', rmse(image, svd_reconstruction), svd_params, 1 if svd_rank else 0, svd_rank, 0, 0, 0, 0)
        )
        reconstructions[(case, 'global_svd')] = svd_reconstruction

        configurations = [
            ('row_rank1', ('row',), 1),
            ('row_column_rank1', ('row', 'column'), 1),
            ('full_am_spd', ('row', 'column', 'channel'), 3),
        ]
        for method, orientations, max_rank in configurations:
            reconstruction, state = tree_method(image, budget, max_depth=3, max_rank=max_rank, orientations=orientations)
            rows.append(describe_state(case, method, image, reconstruction, state))
            reconstructions[(case, method)] = reconstruction

    save_csv(base / 'tables' / 'am_spd_final_stress.csv', rows)
    draw_figures(base, images, rows, reconstructions)
    table = {(row.case, row.method): row for row in rows}
    result = {
        'cases': len(images),
        'size': size,
        'parameter_budget': budget,
        'methods': ['global_svd', 'row_rank1', 'row_column_rank1', 'full_am_spd'],
        'full_beats_row_rank1': sum(table[(case, 'full_am_spd')].rmse <= table[(case, 'row_rank1')].rmse + 1e-12 for case in images),
        'full_beats_row_column_rank1': sum(table[(case, 'full_am_spd')].rmse <= table[(case, 'row_column_rank1')].rmse + 1e-12 for case in images),
        'full_beats_global_svd': sum(table[(case, 'full_am_spd')].rmse < table[(case, 'global_svd')].rmse for case in images),
        'median_full_to_global_svd_ratio': float(np.median([table[(case, 'full_am_spd')].rmse / table[(case, 'global_svd')].rmse for case in images])),
        'median_full_to_row_rank1_ratio': float(np.median([table[(case, 'full_am_spd')].rmse / table[(case, 'row_rank1')].rmse for case in images])),
        'rows': [asdict(row) for row in rows],
    }
    (base / 'results' / 'am_spd_final_stress.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'rows'}, indent=2))
    return result


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=Path('.'))
    parser.add_argument('--size', type=int, default=32)
    parser.add_argument('--budget', type=int, default=720)
    args = parser.parse_args()
    run(args.base, args.size, args.budget)


if __name__ == '__main__':
    main()
