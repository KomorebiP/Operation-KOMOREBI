from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

import infinite_packet_gibbs_reconstruction as atlas
import singular_packet_decomposition_extension as spd

ROOT = Path(__file__).resolve().parent


def main() -> None:
    size = 56
    packet_budget = 44
    histories = spd.load_packet_history(ROOT / 'tables' / 'packet_history.csv')
    images = atlas.benchmark_images(size)
    cases = {}
    results = {}
    all_metrics = []
    figure_index = 8
    for name, image in images.items():
        result = spd.replay_packet_core(image, name, histories[name], packet_budget)
        residual_budget = max(12, packet_budget // 2)
        total_budget = packet_budget + residual_budget
        residual_component = atlas.sparse_dct_component(image - result.reconstruction, residual_budget)
        completed = atlas.bounded_synthesis(result.reconstruction + residual_component)
        methods = {
            'fourier': atlas.fourier_lowpass_reconstruction(image, total_budget),
            'dct': atlas.dct_reconstruction(image, total_budget),
            'quadtree': atlas.adaptive_quadtree_reconstruction(image, total_budget),
            'tv': atlas.tv_reconstruction(image, 0.065),
            'packet_core': result.reconstruction,
            'packet_completed': completed,
        }
        rows = []
        for method, reconstruction in methods.items():
            row = {'case': name, 'method': method, 'packet_budget': packet_budget}
            row.update(atlas.image_metrics(image, reconstruction))
            row['runtime_seconds'] = 0.0
            rows.append(row)
        case = {
            'name': name,
            'packet_budget': packet_budget,
            'residual_completion_budget': residual_budget,
            'total_linear_packet_budget': total_budget,
            'runtime_seconds': 0.0,
            'packets_selected': len(result.active_specs),
            'initial_residual_norm': result.residual_norms[0],
            'final_residual_norm': result.residual_norms[-1],
            'residual_ratio': result.residual_norms[-1] / max(result.residual_norms[0], 1e-12),
            'packet_kinds': dict(zip(*np.unique([spec.kind for spec in result.active_specs], return_counts=True))),
            'metrics': rows,
            'source': 'exact replay of final packet history',
        }
        cases[name] = case
        results[name] = result
        all_metrics.extend(rows)
        atlas.generate_case_figures(name, image, result, methods, ROOT, figure_index)
        figure_index += 4
    atlas.generate_global_figures(ROOT, cases, results)
    atlas.write_csv(ROOT / 'tables' / 'benchmark_metrics.csv', all_metrics)
    old = json.loads((ROOT / 'results' / 'infinite_packet_results.json').read_text())
    old['cases'] = atlas.safe_json(cases)
    old['benchmark_status'] = 'replayed from the final recorded packet history and superseding the stale earlier metric table'
    old['replayed_packet_core_rmse'] = {
        name: next(row['rmse'] for row in case['metrics'] if row['method'] == 'packet_core')
        for name, case in cases.items()
    }
    (ROOT / 'results' / 'infinite_packet_results.json').write_text(json.dumps(old, indent=2) + '\n')
    print(json.dumps(old['replayed_packet_core_rmse'], indent=2))


if __name__ == '__main__':
    main()
