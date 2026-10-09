from __future__ import annotations

import argparse
import csv
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

import infinite_packet_gibbs_reconstruction as atlas
import singular_packet_decomposition_extension as spd
import adaptive_multiscale_spd as core

Array = NDArray[np.float64]


@dataclass
class Trial:
    case: str
    seed: str
    prune_fraction: float
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
class Portfolio:
    reconstruction: Array
    residual: Array
    parameter_count: int
    seed: str
    fraction: float
    trials: list[Trial]
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


def display(ax: plt.Axes, image: Array, title: str) -> None:
    value = atlas.bounded_synthesis(image)
    if value.shape[2] == 1:
        ax.imshow(value[..., 0], cmap='gray', vmin=0, vmax=1)
    else:
        ax.imshow(value[..., :3])
    ax.set_title(title, fontsize=10, weight='bold')
    ax.set_xticks([])
    ax.set_yticks([])


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
    max_actions: int = 10,
    max_rank: int = 2,
    max_regions: int = 14,
) -> Portfolio:
    target = image.reshape(-1)
    ranked: list[tuple[float, int, Array, float]] = []
    for index, (direction, cost) in enumerate(zip(seed_directions, seed_costs, strict=True)):
        vector = np.asarray(direction).reshape(-1)
        energy = float((vector @ target) ** 2)
        ranked.append((energy / max(cost, 1e-12), index, direction, float(cost)))
    trials: list[Trial] = []
    candidates: list[tuple[float, Array, Array, int, core.AMResult | None, Trial]] = []
    seed_metrics = atlas.image_metrics(image, atlas.bounded_synthesis(seed_reconstruction))
    seed_trial = Trial(case, seed, 0.0, len(seed_directions), 0, 0, 0, int(round(sum(seed_costs))), exact_rmse(image, seed_reconstruction), float(seed_metrics['rmse']), float(seed_metrics['ssim']), 0.0)
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
        trial = Trial(
            case,
            seed,
            float(fraction),
            len(kept),
            len(removed),
            len(replacement.blocks),
            max(0, len(replacement.directions) - len(kept)),
            replacement.parameter_count,
            exact_rmse(image, replacement.reconstruction),
            float(metrics['rmse']),
            float(metrics['ssim']),
            time.perf_counter() - started,
        )
        trials.append(trial)
        candidates.append((trial.exact_rmse, replacement.reconstruction, replacement.residual, replacement.parameter_count, replacement, trial))
    best = min(candidates, key=lambda item: (item[0], item[3]))
    best[5].selected_within_seed = True
    return Portfolio(best[1], best[2], best[3], seed, best[5].prune_fraction, trials, best[4])


def make_case_figures(base: Path, index: int, name: str, image: Array, original: spd.SingularPacketResult, tree: core.AMResult, final: Portfolio) -> None:
    prefix = 78 + index * 5
    fig, axes = plt.subplots(2, 3, figsize=(12.7, 7.3))
    panels = [
        ('truth', image),
        ('original greedy SPD', original.reconstruction),
        ('exact tree SPD', tree.reconstruction),
        ('final AM-SPD', final.reconstruction),
        ('original residual', np.abs(image - original.reconstruction)),
        ('final residual', np.abs(final.residual)),
    ]
    for ax, (title, value) in zip(axes.ravel(), panels, strict=True):
        display(ax, value, title)
    fig.suptitle(name.replace('_', ' ').title(), fontsize=16, weight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_figure(fig, base, f'{prefix:02d}_{name}_final_am_spd')

    fig, ax = plt.subplots(figsize=(8.7, 5.1))
    for seed, color in [('greedy', atlas.BLUE), ('tree', atlas.ORANGE)]:
        rows = [trial for trial in final.trials if trial.seed == seed]
        rows.sort(key=lambda trial: trial.prune_fraction)
        ax.plot([trial.prune_fraction for trial in rows], [trial.exact_rmse for trial in rows], marker='o', color=color, label=seed)
    selected = next(trial for trial in final.trials if trial.selected_final)
    ax.scatter([selected.prune_fraction], [selected.exact_rmse], marker='*', s=240, color=atlas.TEAL, edgecolors='black', label='final', zorder=5)
    ax.set_xlabel('reopened fraction')
    ax.set_ylabel('exact RMSE')
    ax.set_title('Two-seed backward replacement portfolio')
    ax.legend()
    ax.grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, base, f'{prefix+1:02d}_{name}_two_seed_portfolio')

    fig, ax = plt.subplots(figsize=(7.8, 6.2))
    display(ax, image, 'selected replacement supports')
    if final.replacement is not None:
        for block in final.replacement.blocks:
            region = block.region
            rect = plt.Rectangle((region.x0, region.y0), region.width, region.height, fill=False, linewidth=1.8)
            ax.add_patch(rect)
            ax.text(region.x0 + 1, region.y0 + 2, f'{block.orientation[0]}{block.rank}', fontsize=8, bbox=dict(facecolor='white', alpha=.7, edgecolor='none'))
    fig.tight_layout()
    save_figure(fig, base, f'{prefix+2:02d}_{name}_final_supports')

    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    values = [exact_rmse(image, original.reconstruction), exact_rmse(image, tree.reconstruction), exact_rmse(image, final.reconstruction)]
    ax.bar(['original SPD', 'tree seed', 'final AM-SPD'], values, color=[atlas.BLUE, atlas.ORANGE, atlas.TEAL])
    ax.set_ylabel('exact RMSE')
    ax.set_title('Seed and final residual')
    ax.grid(axis='y', alpha=.18)
    fig.tight_layout()
    save_figure(fig, base, f'{prefix+3:02d}_{name}_final_rmse')

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.4))
    selected = next(trial for trial in final.trials if trial.selected_final)
    axes[0].bar(['kept', 'removed', 'new modes'], [selected.kept_modes, selected.removed_modes, selected.replacement_components], color=[atlas.BLUE, atlas.RED, atlas.TEAL])
    axes[0].set_title('Direction counts')
    axes[0].grid(axis='y', alpha=.18)
    axes[1].bar(['budget', 'used'], [max(trial.parameter_count for trial in final.trials if trial.prune_fraction == 0.0), selected.parameter_count], color=[atlas.ORANGE, atlas.TEAL])
    axes[1].set_title('Added parameter budget')
    axes[1].grid(axis='y', alpha=.18)
    fig.suptitle(f'{selected.seed} seed, reopened fraction {selected.prune_fraction:.2f}', fontsize=14, weight='bold')
    fig.tight_layout(rect=[0, 0, 1, .92])
    save_figure(fig, base, f'{prefix+4:02d}_{name}_final_action')


def global_figures(base: Path, summaries: dict[str, dict[str, Any]]) -> None:
    names = list(summaries)
    x = np.arange(len(names))
    width = 0.24
    fig, ax = plt.subplots(figsize=(10.8, 5.0))
    ax.bar(x - width, [summaries[name]['original_bounded_rmse'] for name in names], width, label='original SPD', color=atlas.BLUE)
    ax.bar(x, [summaries[name]['matched_residual_svd_rmse'] for name in names], width, label='matched residual SVD', color=atlas.RED)
    ax.bar(x + width, [summaries[name]['final_bounded_rmse'] for name in names], width, label='final AM-SPD', color=atlas.TEAL)
    ax.set_xticks(x, [name.replace('_', '\n') for name in names])
    ax.set_ylabel('RMSE')
    ax.set_title('Adaptive Multiscale Singular Packet Decomposition')
    ax.legend()
    ax.grid(axis='y', alpha=.18)
    fig.tight_layout()
    save_figure(fig, base, '98_final_am_spd_global_rmse')

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    improvement = [100 * summaries[name]['bounded_improvement_fraction'] for name in names]
    ax.bar([name.replace('_', '\n') for name in names], improvement, color=atlas.TEAL)
    ax.set_ylabel('RMSE reduction from original SPD (%)')
    ax.set_title('Backward replacement improvement')
    ax.grid(axis='y', alpha=.18)
    fig.tight_layout()
    save_figure(fig, base, '99_final_am_spd_improvement')

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.7))
    seed_counts = [sum(summaries[name]['selected_seed'] == seed for name in names) for seed in ('greedy', 'tree')]
    axes[0].bar(['greedy', 'tree'], seed_counts, color=[atlas.BLUE, atlas.ORANGE])
    axes[0].set_ylabel('cases selected')
    axes[0].set_title('Winning initial decomposition')
    axes[1].bar([name.replace('_', '\n') for name in names], [summaries[name]['selected_prune_fraction'] for name in names], color=atlas.TEAL)
    axes[1].set_ylabel('reopened fraction')
    axes[1].set_title('Amount of backward replacement')
    fig.tight_layout()
    save_figure(fig, base, '100_final_am_spd_portfolio_structure')


def run(base: Path, size: int = 56, packet_budget: int = 44, mode_budget: int = 22, selected_cases: Sequence[str] | None = None) -> dict[str, Any]:
    base = base.resolve()
    for name in ('figures', 'tables', 'results'):
        (base / name).mkdir(parents=True, exist_ok=True)
    images = atlas.benchmark_images(size)
    histories = spd.load_packet_history(base / 'tables' / 'packet_history.csv')
    metric_rows = {row['case']: row for row in csv.DictReader((base / 'tables' / 'svd_spd_metrics.csv').open()) if row['method'] == 'packet_global_svd_param_matched'}
    requested = set(selected_cases) if selected_cases else set(images)
    summaries: dict[str, dict[str, Any]] = {}
    for case_name in images:
        existing = base / 'results' / f'am_spd_v2_case_{case_name}.json'
        if existing.exists() and case_name not in requested:
            summaries[case_name] = json.loads(existing.read_text())

    for index, (name, image) in enumerate(images.items()):
        if name not in requested:
            continue
        print(f'case {name}', flush=True)
        core_result = spd.replay_packet_core(image, name, histories[name], packet_budget)
        original = spd.singular_packet_completion(image, core_result, mode_budget=mode_budget)
        parameter_budget = int(original.parameter_counts[-1])
        tree = core.tree_result(image, core_result, parameter_budget, max_depth=3, max_rank=3)

        greedy_costs = [float(mode.parameter_count) for mode in original.modes]
        if name in {'camera', 'astronaut'}:
            greedy_fractions = (0.10,)
            tree_fractions = (0.04, 0.08, 0.12)
            natural_actions = 7
            natural_regions = 12
        else:
            greedy_fractions = (0.06, 0.10, 0.14, 0.18, 0.25, 0.35, 0.45)
            tree_fractions = (0.04, 0.08, 0.12, 0.18, 0.25)
            natural_actions = 12
            natural_regions = 18
        greedy = seed_portfolio(
            name, image, core_result, 'greedy', original.reconstruction, original.directions, greedy_costs,
            parameter_budget, greedy_fractions, max_actions=natural_actions, max_rank=2, max_regions=natural_regions,
        )
        tree_cost = tree.parameter_count / max(len(tree.directions), 1)
        tree_costs = [tree_cost] * len(tree.directions)
        tree_port = seed_portfolio(
            name, image, core_result, 'tree', tree.reconstruction, tree.directions, tree_costs,
            parameter_budget, tree_fractions, max_actions=natural_actions, max_rank=2, max_regions=natural_regions,
        )
        final = min([greedy, tree_port], key=lambda item: float(np.linalg.norm(item.residual)))
        selected_trial = next(trial for trial in final.trials if trial.selected_within_seed)
        selected_trial.selected_final = True
        trials = greedy.trials + tree_port.trials
        final.trials = trials
        metrics = atlas.image_metrics(image, atlas.bounded_synthesis(final.reconstruction))
        original_metrics = atlas.image_metrics(image, atlas.bounded_synthesis(original.reconstruction))
        tree_metrics = atlas.image_metrics(image, atlas.bounded_synthesis(tree.reconstruction))
        matched = float(metric_rows[name]['rmse'])
        summary = {
            'case': name,
            'parameter_budget': parameter_budget,
            'original_exact_rmse': exact_rmse(image, original.reconstruction),
            'original_bounded_rmse': float(original_metrics['rmse']),
            'original_ssim': float(original_metrics['ssim']),
            'tree_exact_rmse': exact_rmse(image, tree.reconstruction),
            'tree_bounded_rmse': float(tree_metrics['rmse']),
            'tree_ssim': float(tree_metrics['ssim']),
            'tree_parameters': tree.parameter_count,
            'tree_leaf_count': len(tree.tree_selections),
            'matched_residual_svd_rank': int(float(metric_rows[name]['rank'])),
            'matched_residual_svd_parameters': int(float(metric_rows[name]['estimated_added_parameters'])),
            'matched_residual_svd_rmse': matched,
            'final_exact_rmse': exact_rmse(image, final.reconstruction),
            'final_bounded_rmse': float(metrics['rmse']),
            'final_ssim': float(metrics['ssim']),
            'final_parameters': final.parameter_count,
            'selected_seed': final.seed,
            'selected_prune_fraction': final.fraction,
            'kept_seed_modes': selected_trial.kept_modes,
            'removed_seed_modes': selected_trial.removed_modes,
            'replacement_blocks': selected_trial.replacement_blocks,
            'replacement_components': selected_trial.replacement_components,
            'portfolio_runtime_seconds': sum(trial.runtime_seconds for trial in trials),
            'exact_improvement_fraction': 1 - exact_rmse(image, final.reconstruction) / exact_rmse(image, original.reconstruction),
            'bounded_improvement_fraction': 1 - float(metrics['rmse']) / float(original_metrics['rmse']),
            'nonworsening_certificate': exact_rmse(image, final.reconstruction) <= exact_rmse(image, original.reconstruction) + 1e-12,
            'beats_matched_residual_svd': float(metrics['rmse']) < matched,
        }
        summaries[name] = summary
        write_csv(base / 'tables' / f'am_spd_v2_trials_{name}.csv', [asdict(trial) for trial in trials])
        (base / 'results' / f'am_spd_v2_case_{name}.json').write_text(json.dumps(summary, indent=2) + '\n')
        make_case_figures(base, index, name, image, original, tree, final)

    if set(summaries) == set(images):
        global_figures(base, summaries)
    checks = {
        'case_count': len(summaries),
        'all_nonworsening_exact': all(item['nonworsening_certificate'] for item in summaries.values()),
        'all_within_budget': all(item['final_parameters'] <= item['parameter_budget'] for item in summaries.values()),
        'improved_exact_count': sum(item['final_exact_rmse'] < item['original_exact_rmse'] for item in summaries.values()),
        'improved_bounded_count': sum(item['final_bounded_rmse'] < item['original_bounded_rmse'] for item in summaries.values()),
        'beats_matched_residual_svd_count': sum(item['beats_matched_residual_svd'] for item in summaries.values()),
        'greedy_seed_wins': sum(item['selected_seed'] == 'greedy' for item in summaries.values()),
        'tree_seed_wins': sum(item['selected_seed'] == 'tree' for item in summaries.values()),
    }
    result = {
        'title': 'Adaptive Multiscale Singular Packet Decomposition',
        'subtitle': 'Exact tree best bases, two-seed backward replacement, moving variable-rank subspaces, and residual certificates',
        'author': 'Komorebi P.',
        'cases': summaries,
        'checks': checks,
        'claim_boundary': [
            'The tree result is globally optimal only on the declared finite dyadic tree and additive local rate-distortion model.',
            'The portfolio is globally optimal only over the declared seed and pruning family.',
            'Global SVD remains optimal inside its fixed global matrix-rank class.',
            'Exact closure still uses the explicit residual archive or complete coordinate fallback.',
        ],
    }
    (base / 'results' / 'adaptive_multiscale_spd_v2_results.json').write_text(json.dumps(result, indent=2) + '\n')
    write_csv(base / 'tables' / 'am_spd_v2_summary.csv', list(summaries.values()))
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
