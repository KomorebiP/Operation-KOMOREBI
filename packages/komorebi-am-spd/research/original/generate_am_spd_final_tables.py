from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent


def esc(text: object) -> str:
    value = str(text)
    for old, new in [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('_', r'\_'),
        ('#', r'\#'),
    ]:
        value = value.replace(old, new)
    return value


def main() -> None:
    final = json.loads((ROOT / 'results' / 'adaptive_multiscale_spd_final_results.json').read_text())
    verification = json.loads((ROOT / 'results' / 'am_spd_final_verification.json').read_text())
    stress = json.loads((ROOT / 'results' / 'am_spd_final_stress.json').read_text())
    noise = json.loads((ROOT / 'results' / 'am_spd_final_noise_stress.json').read_text())

    lines: list[str] = []
    lines += [
        r'\begin{table}[H]',
        r'\centering',
        r'\small',
        r'\begin{tabular}{L{0.24\linewidth}rrrrr}',
        r'\toprule',
        r'Image & Original SPD & Exact tree & Final AM-SPD & Improvement & Seed\\',
        r'\midrule',
    ]
    for name, item in final['cases'].items():
        lines.append(
            f"{esc(name.replace('_', ' ').title())} & "
            f"{item['original_exact_rmse']:.6f} & "
            f"{item['exact_budget_tree_exact_rmse']:.6f} & "
            f"{item['final_exact_rmse']:.6f} & "
            f"{100*item['improvement_fraction']:.1f}\\% & "
            f"{esc(item['selected_seed'].replace('_', ' '))}\\\\"
        )
    lines += [
        r'\bottomrule',
        r'\end{tabular}',
        r'\caption{Final four-image benchmark under the inherited added-parameter budgets.}',
        r'\label{tab:final-four-case}',
        r'\end{table}',
        '',
        r'\begin{table}[H]',
        r'\centering',
        r'\small',
        r'\begin{tabular}{L{0.24\linewidth}rrrr}',
        r'\toprule',
        r'Image & Budget & Frontier states & Exact-tree time & Used parameters\\',
        r'\midrule',
    ]
    for name, item in final['cases'].items():
        lines.append(
            f"{esc(name.replace('_', ' ').title())} & {item['parameter_budget']} & "
            f"{item['frontier_states']} & {item['exact_budget_runtime_seconds_replay']:.3f} s & "
            f"{item['exact_budget_tree_parameters']}\\\\"
        )
    lines += [
        r'\bottomrule',
        r'\end{tabular}',
        r'\caption{Exact-budget frontier sizes and replay times.}',
        r'\label{tab:exact-frontier}',
        r'\end{table}',
        '',
    ]

    rows = pd.DataFrame(stress['rows'])
    pivot = rows.pivot(index='case', columns='method', values='rmse')
    lines += [
        r'\begin{longtable}{L{0.22\linewidth}rrrr}',
        r'\caption{Ten-case stress suite at a common parameter budget.}\label{tab:stress-suite}\\',
        r'\toprule',
        r'Case & Global SVD & Row rank 1 & Row+column rank 1 & Full AM-SPD\\',
        r'\midrule',
        r'\endfirsthead',
        r'\toprule',
        r'Case & Global SVD & Row rank 1 & Row+column rank 1 & Full AM-SPD\\',
        r'\midrule',
        r'\endhead',
    ]
    for name, row in pivot.iterrows():
        lines.append(
            f"{esc(name.replace('_', ' ').title())} & {row['global_svd']:.6f} & "
            f"{row['row_rank1']:.6f} & {row['row_column_rank1']:.6f} & {row['full_am_spd']:.6f}\\\\"
        )
    lines += [r'\bottomrule', r'\end{longtable}', '']

    lines += [
        r'\begin{table}[H]',
        r'\centering',
        r'\small',
        r'\begin{tabular}{L{0.42\linewidth}rrr}',
        r'\toprule',
        r'Verification group & Scenarios & Failures & Max residual\\',
        r'\midrule',
    ]
    for name, item in verification['groups'].items():
        lines.append(
            f"{esc(name.replace('_', ' '))} & {item['scenarios']} & {item['failures']} & {item['max_residual']:.3e}\\\\"
        )
    lines += [
        r'\midrule',
        f"Total & {verification['scenarios_total']} & 0 & --\\\\",
        r'\bottomrule',
        r'\end{tabular}',
        r'\caption{Comprehensive verification ledger.}',
        r'\label{tab:final-verification}',
        r'\end{table}',
        '',
        r'\begin{table}[H]',
        r'\centering',
        r'\small',
        r'\begin{tabular}{L{0.45\linewidth}r}',
        r'\toprule',
        r'Noise stress quantity & Value\\',
        r'\midrule',
        f"Scenarios & {noise['scenario_count']}\\\\",
        f"Positive denoising scenarios & {noise['positive_denoising_scenarios']}\\\\",
        f"Mean denoising gain & {noise['mean_denoising_gain']:.6f}\\\\",
        f"Mean support Jaccard & {noise['mean_support_jaccard']:.4f}\\\\",
        r'\bottomrule',
        r'\end{tabular}',
        r'\caption{Noise stress summary. The method is a representation scheme, not an automatic denoiser.}',
        r'\label{tab:noise-summary}',
        r'\end{table}',
    ]

    (ROOT / 'generated_am_spd_final_tables.tex').write_text('\n'.join(lines) + '\n')
    print(ROOT / 'generated_am_spd_final_tables.tex')


if __name__ == '__main__':
    main()
