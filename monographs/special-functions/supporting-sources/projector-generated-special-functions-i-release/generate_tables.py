from __future__ import annotations
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'generated_tables'; OUT.mkdir(exist_ok=True)

def esc(s:str)->str:
    return s.replace('\\','\\textbackslash{}').replace('&','\\&').replace('_','\\_').replace('%','\\%').replace('#','\\#')

# cyclotomic rows
rows=list(csv.DictReader((ROOT/'tables/cyclotomic_norms_L3.csv').open()))
lines=[r'\begin{longtable}{rllll}',r'\caption{Exact first non-DC cyclotomic detail data for $L=3$ and $a=0$.}\label{tab:cyclotomic-norms}\\',r'\toprule',r'$n$ & $A_n$ & $B_n$ & $N_n=A_n^2-A_nB_n+B_n^2$ & factor pattern\\',r'\midrule',r'\endfirsthead',r'\toprule',r'$n$ & $A_n$ & $B_n$ & $N_n$ & factor pattern\\',r'\midrule',r'\endhead']
for row in rows[:12]:
    n=int(row['n']); norm=row['norm']
    if n%2==0:
        pattern=r'$9N_n$ is a square'
    elif n>=3:
        pattern=r'$3N_n$ is a square'
    else:
        pattern=r'first-order exception'
    lines.append(f"{n} & ${row['A']}$ & ${row['B']}$ & ${norm}$ & {pattern}\\\\")
lines += [r'\bottomrule',r'\end{longtable}']
(OUT/'cyclotomic_norms.tex').write_text('\n'.join(lines)+'\n')

# Möbius selected rows
rows=list(csv.DictReader((ROOT/'tables/mobius_transfer_samples.csv').open()))
targets=[10,50,100,500,1000,5000,10000,50000,100000]
selected=[]
for target in targets:
    row=min(rows,key=lambda r:abs(int(r['k'])-target))
    if row not in selected: selected.append(row)
lines=[r'\begin{table}[htbp]',r'\centering',r'\small',r'\caption{Selected numerical values of the principal Möbius-Bernoulli transfer.}',r'\label{tab:mobius-samples}',r'\begin{tabular}{rrrrr}',r'\toprule',r'$k$ & $c_k$ & $E_k$ & $\Gamma_k$ & $S_k^2/E_k$\\',r'\midrule']
for row in selected:
    lines.append(f"{int(row['k'])} & {float(row['c_k']):.5e} & {float(row['energy']):.5e} & {float(row['coherence']):.5e} & {float(row['effective_dimension']):.5e}\\\\")
lines += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
(OUT/'mobius_samples.tex').write_text('\n'.join(lines)+'\n')

# checks summary
checks=list(csv.DictReader((ROOT/'results/checks.csv').open()))
groups={}
for row in checks:
    prefix=row['name'].split()[0]
    groups.setdefault(prefix,[0,0])
    groups[prefix][0]+=1
    groups[prefix][1]+=row['passed'].lower()=='true'
lines=[r'\begin{table}[htbp]',r'\centering',r'\small',r'\caption{Exact and high-precision verification summary.}',r'\label{tab:checks}',r'\begin{tabular}{lrr}',r'\toprule',r'Check family & checks & passed\\',r'\midrule']
for group,(count,passed) in sorted(groups.items()):
    lines.append(f"{esc(group)} & {count} & {passed}\\\\")
lines += [r'\midrule',f"Total & {len(checks)} & {sum(r['passed'].lower()=='true' for r in checks)}\\\\",r'\bottomrule',r'\end{tabular}',r'\end{table}']
(OUT/'checks_summary.tex').write_text('\n'.join(lines)+'\n')
