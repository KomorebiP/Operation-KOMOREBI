from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent
metrics=pd.read_csv(ROOT/'tables'/'svd_spd_metrics.csv')
results=json.load(open(ROOT/'results'/'singular_packet_results.json'))

def esc(value):
    return str(value).replace('\\','\\textbackslash{}').replace('&','\\&').replace('_','\\_').replace('%','\\%').replace('#','\\#')

lines=[]
selected_methods=['global_svd','pure_spd','packet_core_refit','packet_dct','packet_global_svd_param_matched','packet_spd']
labels={
 'global_svd':'global SVD, rank 22',
 'pure_spd':'pure singular packets, 22',
 'packet_core_refit':'packet core, 44',
 'packet_dct':'packet core + 22 DCT coordinates',
 'packet_global_svd_param_matched':'packet core + parameter-matched residual SVD',
 'packet_spd':'packet core + 22 adaptive singular packets',
}
lines.append(r'\scriptsize\setlength{\tabcolsep}{3pt}\begin{longtable}{@{}L{0.16\linewidth}L{0.29\linewidth}rrrr@{}}')
lines.append(r'\caption{Direct SVD and Singular Packet Decomposition comparison.}\label{tab:svd-spd}\\')
lines.append(r'\toprule Case & Method & RMSE & SSIM & Edge RMSE & Added parameters\\\midrule')
lines.append(r'\endfirsthead\toprule Case & Method & RMSE & SSIM & Edge RMSE & Added parameters\\\midrule\endhead')
for case in results['cases']:
    frame=metrics[metrics.case==case].set_index('method')
    for method in selected_methods:
        row=frame.loc[method]
        params=row.get('estimated_added_parameters')
        if pd.isna(params): params=row.get('estimated_parameters')
        ptext='--' if pd.isna(params) else f'{int(params)}'
        lines.append(f'{esc(case.replace("_"," "))} & {esc(labels[method])} & {row.rmse:.6f} & {row.ssim:.4f} & {row.edge_rmse:.6f} & {ptext}\\\\')
lines.append(r'\bottomrule\end{longtable}')
lines.append('')
lines.append(r'\begin{table}[H]\centering')
lines.append(r'\caption{Canonical SVD of the selected packet span.}\label{tab:packet-span-svd}')
lines.append(r'\small\begin{tabular}{lrrrrrr}\toprule Case & Packets & Rank & Condition & 99\% energy & 99.9\% energy & Top-10 energy\\\midrule')
for case,data in results['cases'].items():
    lines.append(f'{esc(case.replace("_"," "))} & {data["packet_count"]} & {data["packet_span_rank"]} & {data["packet_span_condition"]:.2f} & {data["singular_packets_for_99pct_core_energy"]} & {data["singular_packets_for_999pct_core_energy"]} & {data["top10_singular_packet_energy_fraction"]:.3f}\\\\')
lines.append(r'\bottomrule\end{tabular}\end{table}')
lines.append('')
lines.append(r'\begin{table}[H]\centering')
lines.append(r'\caption{Parameter-matched residual comparison.}\label{tab:param-matched}')
lines.append(r'\small\begin{tabular}{lrrrrr}\toprule Case & SPD modes & SPD parameters & SVD rank & SVD parameters & RMSE: SPD / SVD\\\midrule')
for case,data in results['cases'].items():
    frame=metrics[metrics.case==case].set_index('method')
    spd=frame.loc['packet_spd']
    svd=frame.loc['packet_global_svd_param_matched']
    lines.append(f'{esc(case.replace("_"," "))} & {data["singular_packet_count"]} & {int(spd.estimated_added_parameters)} & {int(svd["rank"])} & {int(svd.estimated_added_parameters)} & {spd.rmse:.6f} / {svd.rmse:.6f}\\\\')
lines.append(r'\bottomrule\end{tabular}\end{table}')
(ROOT/'generated_spd_tables.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(ROOT/'generated_spd_tables.tex')
