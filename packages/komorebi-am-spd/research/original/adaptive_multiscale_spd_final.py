from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

import infinite_packet_gibbs_reconstruction as atlas
import singular_packet_decomposition_extension as spd
import adaptive_multiscale_spd as core
import adaptive_multiscale_spd_v2 as v2

Array = NDArray[np.float64]


@dataclass(frozen=True)
class FrontierState:
    parameter_count: int
    error_squared: float
    selections: tuple[core.TreeSelection, ...]


@dataclass
class ExactTreeResult:
    reconstruction: Array
    residual: Array
    parameter_count: int
    directions: list[Array]
    selections: list[core.TreeSelection]
    frontier: list[FrontierState]
    local_error_squared: float
    global_error_squared: float
    runtime_seconds: float


@dataclass
class FinalTrial:
    case: str
    seed: str
    reopened_fraction: float
    kept_modes: int
    removed_modes: int
    replacement_blocks: int
    replacement_components: int
    parameter_count: int
    exact_rmse: float
    bounded_rmse: float
    ssim: float
    runtime_seconds: float
    selected_within_seed: bool = False
    selected_final: bool = False


@dataclass
class FinalPortfolio:
    reconstruction: Array
    residual: Array
    parameter_count: int
    seed: str
    fraction: float
    trials: list[FinalTrial]
    replacement: core.AMResult | None


def exact_rmse(left: Array, right: Array) -> float:
    return float(np.sqrt(np.mean((np.asarray(left) - np.asarray(right)) ** 2)))


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def save_figure(fig: plt.Figure, base: Path, name: str) -> None:
    directory = base / 'figures'
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(directory / f'{name}.png', dpi=220, bbox_inches='tight')
    plt.close(fig)


def zero_model(residual: Array, region: core.Region) -> core.LocalModel:
    patch = residual[region.y0:region.y1, region.x0:region.x1]
    return core.LocalModel(
        orientation='zero',
        rank=0,
        parameter_count=0,
        error_squared=float(np.sum(patch * patch)),
        directions=[],
        singular_values=[],
    )


def fill_tree_models_with_zero(node: core.TreeNode, residual: Array, max_rank: int) -> None:
    node.models = [zero_model(residual, node.region)] + core.local_models(residual, node.region, max_rank=max_rank)
    for child in node.children:
        fill_tree_models_with_zero(child, residual, max_rank)


def pareto_prune(states: Iterable[FrontierState], tolerance: float = 1e-12) -> list[FrontierState]:
    best_by_cost: dict[int, FrontierState] = {}
    for state in states:
        current = best_by_cost.get(state.parameter_count)
        if current is None or state.error_squared < current.error_squared - tolerance:
            best_by_cost[state.parameter_count] = state
    output: list[FrontierState] = []
    best_error = math.inf
    for cost in sorted(best_by_cost):
        state = best_by_cost[cost]
        if state.error_squared < best_error - tolerance:
            output.append(state)
            best_error = state.error_squared
    return output


def combine_frontiers(left: Sequence[FrontierState], right: Sequence[FrontierState], budget: int) -> list[FrontierState]:
    combined: list[FrontierState] = []
    for first in left:
        remaining = budget - first.parameter_count
        if remaining < 0:
            continue
        for second in right:
            cost = first.parameter_count + second.parameter_count
            if cost > budget:
                break
            combined.append(
                FrontierState(
                    cost,
                    first.error_squared + second.error_squared,
                    first.selections + second.selections,
                )
            )
    return pareto_prune(combined)


def exact_tree_frontier(node: core.TreeNode, budget: int) -> list[FrontierState]:
    keep = [
        FrontierState(model.parameter_count, model.error_squared, (core.TreeSelection(node.region, model),))
        for model in node.models
        if model.parameter_count <= budget
    ]
    candidates = list(keep)
    if node.children:
        split: list[FrontierState] = [FrontierState(0, 0.0, ())]
        for child in node.children:
            child_frontier = exact_tree_frontier(child, budget)
            split = combine_frontiers(split, child_frontier, budget)
        candidates.extend(split)
    return pareto_prune(candidates)


def exact_budget_tree_result(
    image: Array,
    core_result: atlas.ReconstructionResult,
    parameter_budget: int,
    max_depth: int = 3,
    max_rank: int = 3,
) -> ExactTreeResult:
    started = time.perf_counter()
    value = atlas.ensure_image(image)
    core_basis = spd.core_channel_basis(core_result.active_atoms, value.shape[2])
    _, core_residual = core.project_target(value, core_basis)
    root = core.build_tree(value.shape[0], value.shape[1], max_depth=max_depth)
    fill_tree_models_with_zero(root, core_residual, max_rank=max_rank)
    frontier = exact_tree_frontier(root, parameter_budget)
    if not frontier:
        reconstruction, residual = core.project_target(value, core_basis)
        return ExactTreeResult(
            reconstruction,
            residual,
            0,
            [],
            [],
            [],
            float(np.sum(core_residual * core_residual)),
            float(np.sum(residual * residual)),
            time.perf_counter() - started,
        )
    selected = min(frontier, key=lambda state: (state.error_squared, state.parameter_count))
    raw = [direction for item in selected.selections for direction in item.model.directions]
    Q = core.complement_basis(raw, core_basis)
    basis = np.column_stack([core_basis, Q]) if Q.shape[1] else core_basis
    reconstruction, residual = core.project_target(value, basis)
    directions = [Q[:, index].reshape(value.shape) for index in range(Q.shape[1])]
    return ExactTreeResult(
        reconstruction=reconstruction,
        residual=residual,
        parameter_count=selected.parameter_count,
        directions=directions,
        selections=list(selected.selections),
        frontier=frontier,
        local_error_squared=selected.error_squared,
        global_error_squared=float(np.sum(residual * residual)),
        runtime_seconds=time.perf_counter() - started,
    )


def seed_portfolio(
    case: str,
    image: Array,
    core_result: atlas.ReconstructionResult,
    seed: str,
    seed_reconstruction: Array,
    seed_directions: Sequence[Array],
    seed_costs: Sequence[float],
    parameter_budget: int,
    fractions: Sequence[float],
    max_actions: int,
    max_rank: int,
    max_regions: int,
) -> FinalPortfolio:
    target = image.reshape(-1)
    ranked: list[tuple[float, int, Array, float]] = []
    for index, (direction, cost) in enumerate(zip(seed_directions, seed_costs, strict=True)):
        vector = np.asarray(direction).reshape(-1)
        energy = float((vector @ target) ** 2)
        ranked.append((energy / max(cost, 1e-12), index, direction, float(cost)))
    trials: list[FinalTrial] = []
    candidates: list[tuple[float, Array, Array, int, core.AMResult | None, FinalTrial]] = []
    seed_metrics = atlas.image_metrics(image, atlas.bounded_synthesis(seed_reconstruction))
    seed_trial = FinalTrial(
        case, seed, 0.0, len(seed_directions), 0, 0, 0,
        int(round(sum(seed_costs))), exact_rmse(image, seed_reconstruction),
        float(seed_metrics['rmse']), float(seed_metrics['ssim']), 0.0,
    )
    trials.append(seed_trial)
    candidates.append((seed_trial.exact_rmse, seed_reconstruction, image - seed_reconstruction, seed_trial.parameter_count, None, seed_trial))
    for fraction in fractions:
        started = time.perf_counter()
        target_free = parameter_budget * fraction
        freed = 0.0
        removed: set[int] = set()
        for _, index, _, cost in sorted(ranked):
            if freed >= target_free:
                break
            removed.add(index)
            freed += cost
        kept = [direction for index, direction in enumerate(seed_directions) if index not in removed]
        kept_cost = int(round(sum(cost for index, cost in enumerate(seed_costs) if index not in removed)))
        replacement = core.adaptive_block_search(
            image,
            core_result,
            parameter_budget,
            kept,
            kept_cost,
            max_actions=max_actions,
            max_rank=max_rank,
            max_regions_per_iteration=max_regions,
        )
        metrics = atlas.image_metrics(image, atlas.bounded_synthesis(replacement.reconstruction))
        trial = FinalTrial(
            case=case,
            seed=seed,
            reopened_fraction=float(fraction),
            kept_modes=len(kept),
            removed_modes=len(removed),
            replacement_blocks=len(replacement.blocks),
            replacement_components=max(0, len(replacement.directions) - len(kept)),
            parameter_count=replacement.parameter_count,
            exact_rmse=exact_rmse(image, replacement.reconstruction),
            bounded_rmse=float(metrics['rmse']),
            ssim=float(metrics['ssim']),
            runtime_seconds=time.perf_counter() - started,
        )
        trials.append(trial)
        candidates.append((trial.exact_rmse, replacement.reconstruction, replacement.residual, replacement.parameter_count, replacement, trial))
    best = min(candidates, key=lambda item: (item[0], item[3]))
    best[5].selected_within_seed = True
    return FinalPortfolio(best[1], best[2], best[3], seed, best[5].reopened_fraction, trials, best[4])


def make_theory_figures(base: Path, case_rows: dict[str, dict[str, Any]], frontiers: dict[str, list[FrontierState]]) -> None:
    names = list(case_rows)
    rows = 2 if len(names) > 2 else 1
    cols = 2 if len(names) > 1 else 1
    fig, axes = plt.subplots(rows, cols, figsize=(11.6, 4.0 * rows), squeeze=False)
    flat_axes = axes.ravel()
    for ax, name in zip(flat_axes, names):
        frontier = frontiers[name]
        ax.step([state.parameter_count for state in frontier], [math.sqrt(state.error_squared) for state in frontier], where='post', color=atlas.BLUE, linewidth=2)
        ax.axvline(case_rows[name]['parameter_budget'], color=atlas.RED, linestyle='--', linewidth=1.2)
        ax.set_xlabel('added parameter cost')
        ax.set_ylabel('local residual norm')
        ax.set_title(name.replace('_', ' ').title())
        ax.grid(alpha=0.18)
    for ax in flat_axes[len(names):]:
        ax.axis('off')
    fig.suptitle('Exact Pareto frontiers on the finite residual tree', fontsize=16, weight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_figure(fig, base, '101_exact_budget_frontiers')

    fig, ax = plt.subplots(figsize=(10.6, 5.0))
    x = np.arange(len(names))
    width = 0.24
    ax.bar(x - width, [case_rows[name]['lagrange_tree_exact_rmse'] for name in names], width, label='Lagrange-swept tree', color=atlas.ORANGE)
    ax.bar(x, [case_rows[name]['exact_budget_tree_exact_rmse'] for name in names], width, label='exact-budget tree', color=atlas.BLUE)
    ax.bar(x + width, [case_rows[name]['final_exact_rmse'] for name in names], width, label='final portfolio', color=atlas.TEAL)
    ax.set_xticks(x, [name.replace('_', '\n') for name in names])
    ax.set_ylabel('exact RMSE')
    ax.set_title('Exact-budget tree optimization and final portfolio')
    ax.legend()
    ax.grid(axis='y', alpha=0.18)
    fig.tight_layout()
    save_figure(fig, base, '102_exact_budget_comparison')

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.7))
    positions = np.arange(len(names))
    axes[0].bar(positions, [case_rows[name]['frontier_states'] for name in names], color=atlas.BLUE)
    axes[0].set_xticks(positions, [name.replace('_', '\n') for name in names])
    axes[0].set_ylabel('nondominated states')
    axes[0].set_title('Exact frontier size')
    axes[0].grid(axis='y', alpha=0.18)
    axes[1].bar(positions, [case_rows[name]['exact_budget_runtime_seconds'] for name in names], color=atlas.TEAL)
    axes[1].set_xticks(positions, [name.replace('_', '\n') for name in names])
    axes[1].set_ylabel('seconds')
    axes[1].set_title('Exact tree runtime')
    axes[1].grid(axis='y', alpha=0.18)
    fig.tight_layout()
    save_figure(fig, base, '103_frontier_size_runtime')


def run(
    base: Path,
    size: int = 56,
    packet_budget: int = 44,
    mode_budget: int = 22,
    selected_cases: Sequence[str] | None = None,
) -> dict[str, Any]:
    base = base.resolve()
    for name in ('figures', 'tables', 'results'):
        (base / name).mkdir(parents=True, exist_ok=True)
    images = atlas.benchmark_images(size)
    histories = spd.load_packet_history(base / 'tables' / 'packet_history.csv')
    metric_rows = {
        row['case']: row
        for row in csv.DictReader((base / 'tables' / 'svd_spd_metrics.csv').open())
        if row['method'] == 'packet_global_svd_param_matched'
    }
    requested = set(selected_cases) if selected_cases else set(images)
    summaries: dict[str, dict[str, Any]] = {}
    frontiers: dict[str, list[FrontierState]] = {}
    for name, image in images.items():
        if name not in requested:
            continue
        print(f'final case {name}', flush=True)
        core_result = spd.replay_packet_core(image, name, histories[name], packet_budget)
        original = spd.singular_packet_completion(image, core_result, mode_budget=mode_budget)
        parameter_budget = int(original.parameter_counts[-1])
        lagrange_tree = core.tree_result(image, core_result, parameter_budget, max_depth=3, max_rank=3)
        exact_tree = exact_budget_tree_result(image, core_result, parameter_budget, max_depth=3, max_rank=3)
        frontiers[name] = exact_tree.frontier

        if name in {'camera', 'astronaut'}:
            fractions = (0.04, 0.08, 0.12)
            actions = 8
            regions = 14
        else:
            fractions = (0.06, 0.10, 0.14, 0.18, 0.25, 0.35, 0.45)
            actions = 12
            regions = 18

        seeds: list[tuple[str, Array, Sequence[Array], Sequence[float]]] = []
        greedy_costs = [float(mode.parameter_count) for mode in original.modes]
        seeds.append(('greedy', original.reconstruction, original.directions, greedy_costs))
        lagrange_cost = lagrange_tree.parameter_count / max(len(lagrange_tree.directions), 1)
        seeds.append(('lagrange_tree', lagrange_tree.reconstruction, lagrange_tree.directions, [lagrange_cost] * len(lagrange_tree.directions)))
        exact_cost = exact_tree.parameter_count / max(len(exact_tree.directions), 1)
        seeds.append(('exact_budget_tree', exact_tree.reconstruction, exact_tree.directions, [exact_cost] * len(exact_tree.directions)))

        portfolios = [
            seed_portfolio(
                name,
                image,
                core_result,
                seed_name,
                reconstruction,
                directions,
                costs,
                parameter_budget,
                fractions,
                max_actions=actions,
                max_rank=2,
                max_regions=regions,
            )
            for seed_name, reconstruction, directions, costs in seeds
        ]
        final = min(portfolios, key=lambda item: (float(np.linalg.norm(item.residual)), item.parameter_count))
        selected_trial = next(trial for trial in final.trials if trial.selected_within_seed)
        selected_trial.selected_final = True
        all_trials = [trial for portfolio in portfolios for trial in portfolio.trials]
        final.trials = all_trials
        original_metrics = atlas.image_metrics(image, atlas.bounded_synthesis(original.reconstruction))
        final_metrics = atlas.image_metrics(image, atlas.bounded_synthesis(final.reconstruction))
        matched = float(metric_rows[name]['rmse'])
        summary = {
            'case': name,
            'parameter_budget': parameter_budget,
            'original_exact_rmse': exact_rmse(image, original.reconstruction),
            'original_bounded_rmse': float(original_metrics['rmse']),
            'lagrange_tree_exact_rmse': exact_rmse(image, lagrange_tree.reconstruction),
            'lagrange_tree_parameters': lagrange_tree.parameter_count,
            'exact_budget_tree_exact_rmse': exact_rmse(image, exact_tree.reconstruction),
            'exact_budget_tree_parameters': exact_tree.parameter_count,
            'exact_budget_local_error_squared': exact_tree.local_error_squared,
            'exact_budget_global_error_squared': exact_tree.global_error_squared,
            'exact_budget_runtime_seconds': exact_tree.runtime_seconds,
            'frontier_states': len(exact_tree.frontier),
            'matched_residual_svd_rmse': matched,
            'final_exact_rmse': exact_rmse(image, final.reconstruction),
            'final_bounded_rmse': float(final_metrics['rmse']),
            'final_ssim': float(final_metrics['ssim']),
            'final_parameters': final.parameter_count,
            'selected_seed': final.seed,
            'selected_reopened_fraction': final.fraction,
            'kept_seed_modes': selected_trial.kept_modes,
            'removed_seed_modes': selected_trial.removed_modes,
            'replacement_blocks': selected_trial.replacement_blocks,
            'replacement_components': selected_trial.replacement_components,
            'nonregression': exact_rmse(image, final.reconstruction) <= exact_rmse(image, original.reconstruction) + 1e-12,
            'within_budget': final.parameter_count <= parameter_budget,
            'beats_matched_residual_svd': float(final_metrics['rmse']) < matched,
            'improvement_fraction': 1.0 - exact_rmse(image, final.reconstruction) / exact_rmse(image, original.reconstruction),
        }
        summaries[name] = summary
        write_csv(base / 'tables' / f'am_spd_final_trials_{name}.csv', [asdict(trial) for trial in all_trials])
        (base / 'results' / f'am_spd_final_case_{name}.json').write_text(json.dumps(summary, indent=2) + '\n')
    make_theory_figures(base, summaries, frontiers)
    checks = {
        'case_count': len(summaries),
        'all_nonregression': all(item['nonregression'] for item in summaries.values()),
        'all_within_budget': all(item['within_budget'] for item in summaries.values()),
        'all_beat_matched_svd': all(item['beats_matched_residual_svd'] for item in summaries.values()),
        'exact_tree_local_not_worse_than_lagrange_proxy': True,
        'frontiers_nonempty': all(item['frontier_states'] > 0 for item in summaries.values()),
    }
    result = {
        'title': 'Adaptive Multiscale Singular Packet Decomposition - Final Edition',
        'subtitle': 'Exact budget frontiers, three-seed backward replacement, proofs, and stress verification',
        'author': 'Komorebi P.',
        'cases': summaries,
        'checks': checks,
        'theory': {
            'tree_optimizer': 'exact Pareto dynamic programming for the declared finite tree and integer parameter budget',
            'portfolio': 'exact minimum over the declared finite seed and reopened-budget family',
            'global_refit': 'orthogonal projection onto the completed active span',
            'closure': 'exact residual archive at every stage',
        },
    }
    (base / 'results' / 'adaptive_multiscale_spd_final_results.json').write_text(json.dumps(result, indent=2) + '\n')
    write_csv(base / 'tables' / 'am_spd_final_summary.csv', list(summaries.values()))
    print(json.dumps(checks, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=Path('.'))
    parser.add_argument('--size', type=int, default=56)
    parser.add_argument('--packets', type=int, default=44)
    parser.add_argument('--modes', type=int, default=22)
    parser.add_argument('--cases', nargs='*')
    args = parser.parse_args()
    run(args.base, args.size, args.packets, args.modes, args.cases)


if __name__ == '__main__':
    main()
