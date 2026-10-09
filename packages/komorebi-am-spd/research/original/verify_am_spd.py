from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import adaptive_multiscale_spd as core

ROOT = Path(__file__).resolve().parent


def model(error: float, params: int, rank: int = 1) -> core.LocalModel:
    return core.LocalModel(
        orientation='row',
        rank=rank,
        parameter_count=params,
        error_squared=error,
        directions=[],
        singular_values=[1.0] * rank,
    )


def tree_dp_certificate() -> bool:
    root = core.TreeNode(core.Region(0, 0, 4, 4, 0, 'test'))
    child_a = core.TreeNode(core.Region(0, 0, 2, 4, 1, 'test'))
    child_b = core.TreeNode(core.Region(2, 0, 4, 4, 1, 'test'))
    root.children = [child_a, child_b]
    root.models = [model(6.0, 2), model(2.0, 8, 2)]
    child_a.models = [model(1.5, 2), model(0.4, 7, 2)]
    child_b.models = [model(1.2, 3), model(0.3, 8, 2)]
    rate = 0.2
    cost, params, selections = core.solve_tree(root, rate)

    keep_options = [m.error_squared + rate * m.parameter_count for m in root.models]
    split_options = [
        left.error_squared + rate * left.parameter_count
        + right.error_squared + rate * right.parameter_count
        for left in child_a.models
        for right in child_b.models
    ]
    expected = min(min(keep_options), min(split_options))
    selected_params = sum(item.model.parameter_count for item in selections)
    return abs(cost - expected) < 1e-12 and params == selected_params


def complement_certificate() -> bool:
    rng = np.random.default_rng(20260731)
    base_raw = rng.normal(size=(24, 4))
    base, _ = np.linalg.qr(base_raw)
    raw = [rng.normal(size=(4, 6)) for _ in range(6)]
    Q = core.complement_basis(raw, base)
    if Q.shape[1] == 0:
        return False
    orthogonal = float(np.max(np.abs(base.T @ Q))) < 2e-12
    orthonormal = float(np.max(np.abs(Q.T @ Q - np.eye(Q.shape[1])))) < 2e-12
    return orthogonal and orthonormal


def main() -> None:
    results = json.loads((ROOT / 'results' / 'adaptive_multiscale_spd_v2_results.json').read_text())
    table = pd.read_csv(ROOT / 'tables' / 'am_spd_v2_summary.csv')
    cases = results['cases']
    checks: dict[str, bool] = {}

    checks['four_cases_present'] = set(cases) == {
        'synthetic_geometry', 'synthetic_text_curves', 'camera', 'astronaut'
    }
    checks['all_nonworsening_exact'] = bool(results['checks']['all_nonworsening_exact'])
    checks['all_within_budget'] = bool(results['checks']['all_within_budget'])
    checks['all_exactly_improved'] = int(results['checks']['improved_exact_count']) == 4
    checks['all_bounded_improved'] = int(results['checks']['improved_bounded_count']) == 4
    checks['all_beat_matched_residual_svd'] = int(results['checks']['beats_matched_residual_svd_count']) == 4
    checks['one_greedy_three_tree'] = (
        int(results['checks']['greedy_seed_wins']) == 1
        and int(results['checks']['tree_seed_wins']) == 3
    )
    checks['natural_image_gain'] = (
        float(cases['camera']['bounded_improvement_fraction']) > 0.60
        and float(cases['astronaut']['bounded_improvement_fraction']) > 0.65
    )
    checks['synthetic_gain_positive'] = (
        float(cases['synthetic_geometry']['bounded_improvement_fraction']) > 0.06
        and float(cases['synthetic_text_curves']['bounded_improvement_fraction']) > 0.03
    )
    checks['summary_csv_matches_json'] = (
        len(table) == 4
        and set(table['case']) == set(cases)
        and all(
            abs(
                float(table.loc[table['case'] == name, 'final_bounded_rmse'].iloc[0])
                - float(item['final_bounded_rmse'])
            ) < 1e-12
            for name, item in cases.items()
        )
    )
    checks['tree_dp_matches_exhaustive'] = tree_dp_certificate()
    checks['complement_basis_certificate'] = complement_certificate()

    pdf_figures = {path.stem for path in (ROOT / 'figures').glob('*.pdf')}
    png_figures = {path.stem for path in (ROOT / 'figures').glob('*.png')}
    final_figures = {
        stem for stem in pdf_figures
        if stem.split('_', 1)[0].isdigit() and int(stem.split('_', 1)[0]) >= 78
    }
    checks['all_figure_pairs_present'] = pdf_figures == png_figures and len(pdf_figures) >= 77
    checks['at_least_twenty_three_final_figure_pairs'] = len(final_figures) >= 23
    checks['generated_table_present'] = (ROOT / 'generated_am_spd_v2_tables.tex').exists()

    failed = [name for name, passed in checks.items() if passed is not True]
    output = {
        'checks': checks,
        'passed': len(checks) - len(failed),
        'total': len(checks),
        'failed': failed,
    }
    destination = ROOT / 'results' / 'am_spd_v2_verification.json'
    destination.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
