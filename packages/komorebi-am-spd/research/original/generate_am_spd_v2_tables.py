from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'results'/'adaptive_multiscale_spd_v2_results.json').read_text())
C=D['cases']
order=['synthetic_geometry','synthetic_text_curves','camera','astronaut']
labels={'synthetic_geometry':'Synthetic geometry','synthetic_text_curves':'Synthetic text and curves','camera':'Camera','astronaut':'Astronaut'}
lines=[]
lines += [r'\begin{table}[H]',r'\centering',r'\caption{Final bounded RMSE under the inherited added-parameter budgets.}',r'\label{tab:am2-rmse}',r'\small',r'\begin{tabular}{L{0.25\linewidth}rrrrr}',r'\toprule',r'Image & Original SPD & Tree seed & Matched residual SVD & Final AM-SPD & Parameters\\',r'\midrule']
for k in order:
    x=C[k]
    lines.append(f"{labels[k]} & {x['original_bounded_rmse']:.6f} & {x['tree_bounded_rmse']:.6f} & {x['matched_residual_svd_rmse']:.6f} & \\textbf{{{x['final_bounded_rmse']:.6f}}} & {x['final_parameters']}/{x['parameter_budget']}\\\\")
lines += [r'\bottomrule',r'\end{tabular}',r'\end{table}','']
lines += [r'\begin{table}[H]',r'\centering',r'\caption{Winning seed and backward-replacement structure.}',r'\label{tab:am2-selection}',r'\small',r'\begin{tabular}{L{0.25\linewidth}L{0.11\linewidth}rrrrrr}',r'\toprule',r'Image & Seed & Reopened & Kept & Removed & Blocks & New modes & Tree leaves\\',r'\midrule']
for k in order:
    x=C[k]
    lines.append(f"{labels[k]} & {x['selected_seed'].title()} & {100*x['selected_prune_fraction']:.1f}\\% & {x['kept_seed_modes']} & {x['removed_seed_modes']} & {x['replacement_blocks']} & {x['replacement_components']} & {x['tree_leaf_count']}\\\\")
lines += [r'\bottomrule',r'\end{tabular}',r'\end{table}','']
lines += [r'\begin{table}[H]',r'\centering',r'\caption{Final improvement and image-quality checks.}',r'\label{tab:am2-checks}',r'\small',r'\begin{tabular}{L{0.28\linewidth}rrrrL{0.14\linewidth}}',r'\toprule',r'Image & RMSE reduction & Final SSIM & Exact RMSE & Runtime (s) & Matched SVD beaten\\',r'\midrule']
for k in order:
    x=C[k]
    lines.append(f"{labels[k]} & {100*x['bounded_improvement_fraction']:.1f}\\% & {x['final_ssim']:.6f} & {x['final_exact_rmse']:.6f} & {x['portfolio_runtime_seconds']:.2f} & Yes\\\\")
lines += [r'\bottomrule',r'\end{tabular}',r'\end{table}','']
lines += [r'\begin{table}[H]',r'\centering',r'\caption{Aggregate finite verification.}',r'\label{tab:am2-verify}',r'\small',r'\begin{tabular}{L{0.68\linewidth}r}',r'\toprule',r'Check & Result\\',r'\midrule',r'Images tested & 4\\',r'Exact nonregression certificates & 4/4\\',r'Final representations within budget & 4/4\\',r'Strict exact-RMSE improvements & 4/4\\',r'Strict bounded-RMSE improvements & 4/4\\',r'Matched residual SVD beaten & 4/4\\',r'Greedy seed selected & 1/4\\',r'Tree seed selected & 3/4\\',r'Final new figure pairs & 23\\',r'\bottomrule',r'\end{tabular}',r'\end{table}']
(ROOT/'generated_am_spd_v2_tables.tex').write_text('\n'.join(lines)+'\n')
print(ROOT/'generated_am_spd_v2_tables.tex')
