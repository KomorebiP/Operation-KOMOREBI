from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent


def main() -> None:
    data = json.loads((ROOT / 'results' / 'singular_packet_results.json').read_text())
    metrics = pd.read_csv(ROOT / 'tables' / 'svd_spd_metrics.csv')
    modes = pd.read_csv(ROOT / 'tables' / 'singular_packet_modes.csv')
    checks: dict[str, object] = {}

    checks['packet_svd_exact'] = max(case['packet_svd_exact_residual'] for case in data['cases'].values()) < 1e-10
    checks['all_spd_modes_present'] = all(case['singular_packet_count'] == data['singular_packet_budget'] for case in data['cases'].values())
    checks['monotone_residual'] = all(case['singular_packet_residual_monotone'] for case in data['cases'].values())
    metric_columns = ['rmse', 'psnr', 'ssim', 'edge_rmse', 'range_violation', 'max_local_range_violation', 'mean_local_range_violation', 'fraction_outside_local_range']
    checks['finite_metrics'] = bool(metrics[metric_columns].replace([float('inf'), float('-inf')], float('nan')).notna().all().all())

    pure_wins = []
    param_wins = []
    for case in data['cases']:
        frame = metrics[metrics.case == case].set_index('method')
        pure_wins.append(frame.loc['global_svd', 'rmse'] <= frame.loc['pure_spd', 'rmse'] + 1e-12)
        param_wins.append(frame.loc['packet_spd', 'rmse'] <= frame.loc['packet_global_svd_param_matched', 'rmse'] + 1e-12)
    checks['global_svd_beats_or_matches_pure_spd'] = all(pure_wins)
    checks['hybrid_spd_beats_parameter_matched_residual_svd'] = all(param_wins)

    expected_modes = len(data['cases']) * data['singular_packet_budget']
    checks['mode_table_rows'] = len(modes) == expected_modes
    pdf_figures = {path.stem for path in (ROOT / 'figures').glob('*.pdf')}
    png_figures = {path.stem for path in (ROOT / 'figures').glob('*.png')}
    checks['figure_pairing'] = pdf_figures == png_figures and len(pdf_figures) >= 54

    failed = [name for name, value in checks.items() if value is not True]
    output = {'checks': checks, 'passed': len(checks) - len(failed), 'total': len(checks), 'failed': failed}
    (ROOT / 'results' / 'singular_packet_verification.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
