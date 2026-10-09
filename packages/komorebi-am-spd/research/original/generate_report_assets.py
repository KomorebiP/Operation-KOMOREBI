from pathlib import Path
import csv
import json
import pandas as pd

ROOT=Path(__file__).resolve().parent
TABLE=ROOT/'generated_tables.tex'

def esc(x):
    s=str(x)
    return (s.replace('\\','\\textbackslash{}').replace('&','\\&').replace('%','\\%').replace('_','\\_').replace('#','\\#'))

m=pd.read_csv(ROOT/'tables/benchmark_metrics.csv')
h=pd.read_csv(ROOT/'tables/packet_history.csv')
b=pd.read_csv(ROOT/'tables/budget_experiment.csv')
s=pd.read_csv(ROOT/'tables/scaling_experiment.csv')
tests=json.load(open(ROOT/'results/tests_output.json'))
lines=[]
lines.append(r'\begin{longtable}{llrrrr}')
lines.append(r'\caption{Benchmark metrics for every case and method.}\label{tab:benchmark}\\')
lines.append(r'\toprule Case & Method & RMSE & PSNR & SSIM & Edge RMSE\\\midrule')
lines.append(r'\endfirsthead\toprule Case & Method & RMSE & PSNR & SSIM & Edge RMSE\\\midrule\endhead')
for row in m.itertuples(index=False):
    lines.append(f'{esc(row.case.replace("_"," "))} & {esc(row.method.replace("_"," "))} & {row.rmse:.6f} & {row.psnr:.3f} & {row.ssim:.4f} & {row.edge_rmse:.6f}\\\\')
lines.append(r'\bottomrule\end{longtable}')
lines.append('')

kind=h.groupby(['case','kind']).size().reset_index(name='count')
lines.append(r'\begin{longtable}{llr}')
lines.append(r'\caption{Selected packet types in the four image reconstructions.}\label{tab:kinds}\\')
lines.append(r'\toprule Case & Packet type & Count\\\midrule')
lines.append(r'\endfirsthead\toprule Case & Packet type & Count\\\midrule\endhead')
for row in kind.itertuples(index=False):
    lines.append(f'{esc(row.case.replace("_"," "))} & {esc(row.kind.replace("_"," "))} & {row.count}\\\\')
lines.append(r'\bottomrule\end{longtable}')
lines.append('')

lines.append(r'\begin{table}[H]\centering')
lines.append(r'\caption{Earlier budget sweep for the same packet-selection architecture.}\label{tab:budget}')
lines.append(r'\small\begin{tabular}{rrrrrr}\toprule Packet budget & Residual budget & Core RMSE & Completed RMSE & Seconds & Selected\\\midrule')
for row in b.itertuples(index=False):
    lines.append(f'{row.packet_budget} & {row.residual_budget} & {row.core_rmse:.6f} & {row.completed_rmse:.6f} & {row.runtime_seconds:.3f} & {row.selected_packets}\\\\')
lines.append(r'\bottomrule\end{tabular}\end{table}')
lines.append('')

lines.append(r'\begin{table}[H]\centering')
lines.append(r'\caption{Earlier fixed-budget scaling sweep.}\label{tab:scaling}')
lines.append(r'\small\begin{tabular}{rrrrr}\toprule Side length & Pixels & Seconds & Core RMSE & Packets\\\midrule')
for row in s.itertuples(index=False):
    lines.append(f'{row.image_size} & {row.pixel_count} & {row.runtime_seconds:.3f} & {row.core_rmse:.6f} & {row.selected_packets}\\\\')
lines.append(r'\bottomrule\end{tabular}\end{table}')
lines.append('')

lines.append(r'\begin{longtable}{L{0.55\linewidth}L{0.33\linewidth}}')
lines.append(r'\caption{Verification ledger.}\label{tab:tests}\\')
lines.append(r'\toprule Check & Recorded value\\\midrule')
lines.append(r'\endfirsthead\toprule Check & Recorded value\\\midrule\endhead')
for key,val in tests.items():
    if isinstance(val,float): out=f'{val:.6e}'
    else: out=str(val)
    lines.append(f'{esc(key.replace("_"," "))} & {esc(out)}\\\\')
lines.append(r'\bottomrule\end{longtable}')

TABLE.write_text('\n'.join(lines)+'\n')
print(TABLE)
