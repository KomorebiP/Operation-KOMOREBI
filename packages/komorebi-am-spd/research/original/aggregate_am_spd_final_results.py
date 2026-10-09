from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import infinite_packet_gibbs_reconstruction as atlas
import singular_packet_decomposition_extension as spd
import adaptive_multiscale_spd_final as final

ROOT = Path(__file__).resolve().parent


def main() -> None:
    images = atlas.benchmark_images(56)
    histories = spd.load_packet_history(ROOT / 'tables' / 'packet_history.csv')
    summaries: dict[str, dict] = {}
    frontiers = {}
    for name, image in images.items():
        path = ROOT / 'results' / f'am_spd_final_case_{name}.json'
        if not path.exists():
            raise FileNotFoundError(path)
        summaries[name] = json.loads(path.read_text())
        core_result = spd.replay_packet_core(image, name, histories[name], 44)
        exact_tree = final.exact_budget_tree_result(
            image,
            core_result,
            int(summaries[name]['parameter_budget']),
            max_depth=3,
            max_rank=3,
        )
        frontiers[name] = exact_tree.frontier
        summaries[name]['frontier_states'] = len(exact_tree.frontier)
        summaries[name]['exact_budget_runtime_seconds_replay'] = exact_tree.runtime_seconds
    final.make_theory_figures(ROOT, summaries, frontiers)
    checks = {
        'case_count': len(summaries),
        'all_nonregression': all(item['nonregression'] for item in summaries.values()),
        'all_within_budget': all(item['within_budget'] for item in summaries.values()),
        'all_beat_matched_svd': all(item['beats_matched_residual_svd'] for item in summaries.values()),
        'all_frontiers_nonempty': all(item['frontier_states'] > 0 for item in summaries.values()),
        'exact_budget_seed_selected_count': sum(item['selected_seed'] == 'exact_budget_tree' for item in summaries.values()),
        'lagrange_seed_selected_count': sum(item['selected_seed'] == 'lagrange_tree' for item in summaries.values()),
        'greedy_seed_selected_count': sum(item['selected_seed'] == 'greedy' for item in summaries.values()),
    }
    result = {
        'title': 'Adaptive Multiscale Singular Packet Decomposition - Final Edition',
        'subtitle': 'Exact budget frontiers, three-seed backward replacement, self-contained proofs, and stress verification',
        'author': 'Komorebi P.',
        'cases': summaries,
        'checks': checks,
        'mean_improvement_fraction': float(np.mean([item['improvement_fraction'] for item in summaries.values()])),
        'theory': {
            'tree_optimizer': 'exact Pareto dynamic programming on the declared finite tree and integer parameter budget',
            'portfolio': 'exact minimum over the declared finite three-seed and reopened-budget family',
            'global_refit': 'orthogonal projection onto the completed active span',
            'closure': 'exact residual archive at every finite stage',
        },
        'claim_boundary': [
            'The exact-budget tree theorem concerns the declared finite dyadic tree, local unfolding family, rank range, and integer cost model.',
            'The final portfolio theorem concerns the finite seed and reopened-budget family actually evaluated.',
            'The moving residual-region proposal stage remains greedy.',
            'Global SVD remains optimal in its fixed global rank class.',
            'Lossless closure uses the residual archive or a complete finite coordinate fallback.',
        ],
    }
    (ROOT / 'results' / 'adaptive_multiscale_spd_final_results.json').write_text(json.dumps(result, indent=2) + '\n')
    final.write_csv(ROOT / 'tables' / 'am_spd_final_summary.csv', list(summaries.values()))
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
