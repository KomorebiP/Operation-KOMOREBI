from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import am_spd_final_stress as stress


def signature(state) -> set[tuple[int, int, int, int, str, int]]:
    return {
        (
            selection.region.y0,
            selection.region.x0,
            selection.region.y1,
            selection.region.x1,
            selection.model.orientation,
            selection.model.rank,
        )
        for selection in state.selections
        if selection.model.rank > 0
    }


def jaccard(left: set, right: set) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / max(1, len(left | right))


def save_figure(fig: plt.Figure, directory: Path, name: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(directory / f'{name}.png', dpi=220, bbox_inches='tight')
    plt.close(fig)


def run(base: Path, size: int = 32, budget: int = 720) -> dict[str, object]:
    base = base.resolve()
    for name in ('figures', 'tables', 'results'):
        (base / name).mkdir(parents=True, exist_ok=True)
    all_images = stress.benchmark_images(size)
    names = ['diagonal_edge', 'oriented_texture', 'camera', 'astronaut']
    images = {name: all_images[name] for name in names}
    sigmas = [0.01, 0.03, 0.05]
    seeds = [17, 101, 509]
    rows: list[dict[str, object]] = []
    clean_states = {}
    for name, image in images.items():
        clean_reconstruction, clean_state = stress.tree_method(
            image, budget, max_depth=3, max_rank=3,
            orientations=('row', 'column', 'channel'),
        )
        clean_states[name] = clean_state
        clean_signature = signature(clean_state)
        rows.append(
            {
                'case': name,
                'sigma': 0.0,
                'seed': 0,
                'input_rmse': 0.0,
                'reconstruction_rmse_to_clean': stress.rmse(image, clean_reconstruction),
                'reconstruction_rmse_to_observed': stress.rmse(image, clean_reconstruction),
                'denoising_gain': 0.0,
                'support_jaccard': 1.0,
                'parameter_count': clean_state.parameter_count,
                'leaf_count': len(clean_state.selections),
            }
        )
        for sigma in sigmas:
            for seed in seeds:
                rng = np.random.default_rng(seed)
                observed = np.clip(image + rng.normal(scale=sigma, size=image.shape), 0.0, 1.0)
                reconstruction, state = stress.tree_method(
                    observed, budget, max_depth=3, max_rank=3,
                    orientations=('row', 'column', 'channel'),
                )
                input_rmse = stress.rmse(image, observed)
                output_rmse = stress.rmse(image, reconstruction)
                rows.append(
                    {
                        'case': name,
                        'sigma': sigma,
                        'seed': seed,
                        'input_rmse': input_rmse,
                        'reconstruction_rmse_to_clean': output_rmse,
                        'reconstruction_rmse_to_observed': stress.rmse(observed, reconstruction),
                        'denoising_gain': input_rmse - output_rmse,
                        'support_jaccard': jaccard(clean_signature, signature(state)),
                        'parameter_count': state.parameter_count,
                        'leaf_count': len(state.selections),
                    }
                )

    fields = list(rows[0])
    with (base / 'tables' / 'am_spd_final_noise_stress.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.0))
    for ax, name in zip(axes.ravel(), names, strict=True):
        case_rows = [row for row in rows if row['case'] == name and row['sigma'] > 0]
        input_means = [float(np.mean([row['input_rmse'] for row in case_rows if row['sigma'] == sigma])) for sigma in sigmas]
        output_means = [float(np.mean([row['reconstruction_rmse_to_clean'] for row in case_rows if row['sigma'] == sigma])) for sigma in sigmas]
        input_stds = [float(np.std([row['input_rmse'] for row in case_rows if row['sigma'] == sigma])) for sigma in sigmas]
        output_stds = [float(np.std([row['reconstruction_rmse_to_clean'] for row in case_rows if row['sigma'] == sigma])) for sigma in sigmas]
        ax.errorbar(sigmas, input_means, yerr=input_stds, marker='o', linewidth=2, label='noisy input')
        ax.errorbar(sigmas, output_means, yerr=output_stds, marker='o', linewidth=2, label='AM-SPD tree')
        ax.set_title(name.replace('_', ' ').title())
        ax.set_xlabel('noise standard deviation')
        ax.set_ylabel('RMSE to clean image')
        ax.grid(alpha=.18)
        ax.legend(fontsize=8)
    fig.suptitle('Noise stress under a fixed exact tree budget', fontsize=16, weight='bold')
    fig.tight_layout(rect=[0, 0, 1, .95])
    save_figure(fig, base / 'figures', '105_final_noise_stress')

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.6))
    for name in names:
        case_rows = [row for row in rows if row['case'] == name and row['sigma'] > 0]
        jaccard_means = [float(np.mean([row['support_jaccard'] for row in case_rows if row['sigma'] == sigma])) for sigma in sigmas]
        gains = [float(np.mean([row['denoising_gain'] for row in case_rows if row['sigma'] == sigma])) for sigma in sigmas]
        axes[0].plot(sigmas, jaccard_means, marker='o', label=name.replace('_', ' '))
        axes[1].plot(sigmas, gains, marker='o', label=name.replace('_', ' '))
    axes[0].set_xlabel('noise standard deviation')
    axes[0].set_ylabel('Jaccard similarity to clean selection')
    axes[0].set_title('Packet-selection stability')
    axes[0].grid(alpha=.18)
    axes[1].axhline(0, linewidth=1)
    axes[1].set_xlabel('noise standard deviation')
    axes[1].set_ylabel('input RMSE minus output RMSE')
    axes[1].set_title('Denoising gain')
    axes[1].grid(alpha=.18)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    save_figure(fig, base / 'figures', '106_final_noise_selection')

    noisy_rows = [row for row in rows if row['sigma'] > 0]
    result = {
        'cases': names,
        'noise_levels': sigmas,
        'seeds': seeds,
        'scenario_count': len(noisy_rows),
        'all_within_budget': all(int(row['parameter_count']) <= budget for row in rows),
        'finite_metrics': all(np.isfinite(float(row[key])) for row in rows for key in ('input_rmse', 'reconstruction_rmse_to_clean', 'support_jaccard')),
        'mean_denoising_gain': float(np.mean([row['denoising_gain'] for row in noisy_rows])),
        'positive_denoising_scenarios': sum(float(row['denoising_gain']) > 0 for row in noisy_rows),
        'mean_support_jaccard': float(np.mean([row['support_jaccard'] for row in noisy_rows])),
        'rows': rows,
    }
    (base / 'results' / 'am_spd_final_noise_stress.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'rows'}, indent=2))
    return result


if __name__ == '__main__':
    run(Path('.'))
