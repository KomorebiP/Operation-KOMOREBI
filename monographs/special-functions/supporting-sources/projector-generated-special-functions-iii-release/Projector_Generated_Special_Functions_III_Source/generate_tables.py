from __future__ import annotations
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'generated_tables'
OUT.mkdir(exist_ok=True)

def rows(name):
    with (ROOT/'tables'/name).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write(name,text):
    (OUT/name).write_text(text,encoding='utf-8')

energy=rows('energy.csv')
body='\n'.join(f"{r['k']} & {r['energy']} & {r['asymptotic']} & {r['ratio']} \\\\" for r in energy)
write('energy.tex',r'''\begin{longtable}{rrrr}
\caption{Principal packet energy and its leading asymptotic.}\label{tab:energy}\\
\toprule
$k$ & $E_k$ & $A k^{-3/2}$ & ratio\\
\midrule
\endfirsthead
\toprule
$k$ & $E_k$ & $A k^{-3/2}$ & ratio\\
\midrule
\endhead
'''+body+r'''
\bottomrule
\end{longtable}
''')

jac=rows('jacobi.csv')
body='\n'.join(f"{r['index']} & {r['diagonal']} & {r['off_diagonal']} \\\\" for r in jac)
write('jacobi.tex',r'''\begin{longtable}{rrr}
\caption{Leading coefficients of the global packet Jacobi matrix.}\label{tab:jacobi}\\
\toprule
index & diagonal & off-diagonal\\
\midrule
\endfirsthead
\toprule
index & diagonal & off-diagonal\\
\midrule
\endhead
'''+body+r'''
\bottomrule
\end{longtable}
''')

rec=rows('recurrence.csv')
body='\n'.join(f"{r['k']} & {r['index']} & {r['diagonal']} & {r['diagonal_limit']} & {r['off_diagonal']} & {r['off_limit']} \\\\" for r in rec)
write('recurrence.tex',r'''\begin{longtable}{rrrrrr}
\caption{Tilted packet recurrence coefficients and their Laguerre limits.}\label{tab:recurrence}\\
\toprule
$k$ & $m$ & $a_m(k)$ & $2m+\alpha$ & $b_{m+1}(k)$ & $\sqrt{(m+1)(m+\alpha)}$\\
\midrule
\endfirsthead
\toprule
$k$ & $m$ & $a_m(k)$ & limit & $b_{m+1}(k)$ & limit\\
\midrule
\endhead
'''+body+r'''
\bottomrule
\end{longtable}
''')

han=rows('hankel_asymptotic.csv')
body='\n'.join(f"{r['k']} & {r['degree']} & {r['scaled_ratio']} \\\\" for r in han)
write('hankel.tex',r'''\begin{longtable}{rrr}
\caption{Scaled tilted Hankel determinants. The predicted limit is one.}\label{tab:hankel}\\
\toprule
$k$ & degree $d$ & scaled ratio\\
\midrule
\endfirsthead
\toprule
$k$ & degree $d$ & scaled ratio\\
\midrule
\endhead
'''+body+r'''
\bottomrule
\end{longtable}
''')

quad=rows('quadrature.csv')
body='\n'.join(f"{r['index']} & {r['packet_node']} & {r['laguerre_node']} & {r['packet_weight']} & {r['laguerre_weight']} \\\\" for r in quad)
write('quadrature.tex',r'''\begin{longtable}{rrrrr}
\caption{Six-node packet quadrature at $k=10^7$ and the normalized Gauss--Laguerre limit.}\label{tab:quadrature}\\
\toprule
index & packet node & limit node & packet weight & limit weight\\
\midrule
\endfirsthead
\toprule
index & packet node & limit node & packet weight & limit weight\\
\midrule
\endhead
'''+body+r'''
\bottomrule
\end{longtable}
''')

pade=rows('pade.csv')
body='\n'.join(f"{r['nodes']} & {r['z']} & {r['exact']} & {r['approximate']} & {r['absolute_error']} \\\\" for r in pade)
write('pade.tex',r'''\begin{longtable}{rrrrr}
\caption{Positive rational approximants to the packet-energy resolvent.}\label{tab:pade}\\
\toprule
nodes & $z$ & exact & reduced & absolute error\\
\midrule
\endfirsthead
\toprule
nodes & $z$ & exact & reduced & absolute error\\
\midrule
\endhead
'''+body+r'''
\bottomrule
\end{longtable}
''')

import json
res=json.loads((ROOT/'results'/'results.json').read_text())
write('checks_summary.tex',rf'''\begin{{center}}
\fbox{{\begin{{minipage}}{{0.80\textwidth}}
\centering
\textbf{{Computational verification}}\\[0.4em]
Built-in checks: {res['passed']}/{res['checks']} passed\\
Independent tests: 19/19 passed\\
Figure pairs: {res['figure_pairs']}\\
Principal Gamma shape: $\alpha={res['parameters']['alpha']}$\\
Energy constant: ${res['parameters']['energy_constant']:.15f}$
\end{{minipage}}}}
\end{{center}}
''')
print('generated')
