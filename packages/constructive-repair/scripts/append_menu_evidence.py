"""Append the v0.4.0 mathematical/formal evidence register to the monograph."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
reg=json.loads((ROOT/'docs/theorem_registry.json').read_text(encoding="utf-8"))['theorems']
index=json.loads((ROOT/'evidence/menu_export_index.json').read_text(encoding="utf-8"))
current=ROOT/'evidence/verification/current/verification.json'
rec=json.loads(current.read_text(encoding="utf-8"))
if rec['status']!='PASS': raise RuntimeError('Refuse to typeset a claimed PASS before verification finishes')
text=r'''\chapter{Menu certificates: sources and fresh verification}
\label{app:menu-verification}

This appendix records the v0.4.0 continuation. The 23 proof modules from v0.3.0 remain byte-for-byte unchanged. Fourteen additional modules supply a seven-theorem cover interface, 24 exported rational-menu problems, and eight paired corruption controls. The full combined project is compiled and replayed again, rather than accepting the prior receipts as a substitute for the new run.

\section{General declarations}

The new general source is \nolinkurl{lean/KomorebiRepair/RationalMenuCover.lean}. The following records give its exact current line locations. Definitions, decidability instances, and diagnostic JSON display functions are not counted as theorems.

'''
desc={
'mul_masked_entry':'A column-mask identity for exact matrix multiplication.',
'separates_subset':'A valid separator for a larger menu separates every subset.',
'covered_infeasible':'A covered selection is infeasible when every listed block is valid.',
'checkCoveredOptimal_sound':'Acceptance proves admissibility, the original equations, and minimum cost among admissible feasible selections.',
'checkCoveredNoRepair_sound':'Acceptance excludes every selection admitted by the original rule.',
'tableAllowed_iff':'The Boolean admissibility table is equivalent to membership in its fixed input list.',
'additiveCost_empty':'The empty selection has zero additive cost.'}
for r in reg:
 if r['module']=='RationalMenuCover':
  text+=r'\record{'+r['name']+'}{'+str(r['line'])+'}{'+desc[r['name'].split('.')[-1]]+'}\n'
text+=r'''
\section{Exported original problems}

Every input is emitted independently of its coefficient and separation witnesses. The six input modules and six certificate modules under \nolinkurl{MenuGenerated/} hold four cases each. The full source registry, JSON files, and hashes are included in the package.

\begin{longtable}{@{}p{0.12\linewidth}p{0.44\linewidth}p{0.15\linewidth}rr@{}}
\toprule Case & Main test & Outcome & Cost & Blocks\\\midrule
\endfirsthead
\toprule Case & Main test & Outcome & Cost & Blocks\\\midrule
\endhead
'''
for x in index:
 label=x['label'].replace('_',' ')
 state='optimum' if x['kind']=='optimal_menu' else 'none'
 cost='--' if x['cost'] is None else str(x['cost'])
 text+=f'Menu{x["id"]:03d} & {label} & {state} & {cost} & {x["separation_blocks"]}'+r'\\'+'\n'
text+=r'''\bottomrule\end{longtable}

There are twenty positive optimal-menu results and four no-admissible-menu results. One of the latter has an empty admissibility table. Its rejection is explicitly vacuous, not a claim that a nonzero cokernel class has been detected.

\section{Fresh verification results}

\begin{center}\begin{tabularx}{\linewidth}{@{}Xr@{}}\toprule Check & Result\\\midrule
Combined proof modules compiled and replayed & 37 / 37\\
Named theorem dependencies audited & 378 / 378\\
Unchanged v0.3.0 declarations & 227\\
Additional general declarations & 7\\
Additional concrete declarations & 144\\
New original menu problems exported to Lean & 24 / 24\\
New matrix, admissibility, and cost echoes & 24 / 24\\
New paired corruption controls & 8 / 8\\
Previous paired corruption controls rerun & 6 / 6\\
Separate forbidden-axiom policy control & 1 / 1\\
New Python unit tests & 50 / 50\\
Exact menu problems independently compared & 120 / 120\\
Individual subset rank comparisons & 709 / 709\\
Previous rational Python unit tests rerun & 34 / 34\\
Original Python unit tests rerun & 20 / 20\\
Original exact audit records reproduced & 3,307\\
\bottomrule\end{tabularx}\end{center}

The 144 additional concrete declarations comprise 136 input and certificate statements for the 24 problems and eight positive proofs that corrupted checks return false. This is a coverage count, not a count of new mathematical discoveries. The underlying finite linear alternative, monotonicity of linear span, and finite optimization arguments are classical.

All transitive axiom lists are contained in \{\code{propext}, \code{Classical.choice}, \code{Quot.sound}\}. Concrete certificates use \code{decide +kernel}. Replay invokes Lean's own kernel against the pinned imports. It is not an independently implemented checker and does not rebuild or re-prove all Mathlib dependencies.

The independent Python comparison uses SymPy matrix ranks to assess every subset of each recorded problem. It checks the producer's selected minimum or infeasibility outcome, rather than merely comparing two calls to the same elimination routine. The seeded run contains 120 problems and 709 individual subset comparisons. All rational arithmetic is exact.

\section{Rejection controls and command execution}

The new corruption controls remove cheaper-menu coverage, replace a separator by zero, overstate a block's scope, change correction coefficients, propose an expensive singleton despite a cheaper repair, select a forbidden menu, claim rejection of a feasible family, and attempt to use an unselected column. Each corrupted Boolean check is first proved false. A separate invalid source then tries to use that result as true and must fail with the intended type mismatch. An unrelated missing instance or syntax failure is not accepted as a rejection result.

The single-command workflow was executed on the fractional problem and on the four-candidate globally infeasible menu. The former returns \nolinkurl{KERNEL_CHECKED_OPTIMAL_MENU}, cost seven, with coefficient $-5/4$. The latter returns \nolinkurl{KERNEL_CHECKED_NO_ADMISSIBLE_MENU}, using one separator for sixteen subsets. Both commands compile the sources, audit all relevant theorem dependencies, replay the modules, and match the Lean input echo to the original matrices and constraints.

A separate trial-budget control deliberately permits zero trials. It returns \code{UNRESOLVED} before claiming a mathematical outcome. The log is retained. This distinction is part of the operational contract, not merely a closing qualification.

\section{Development record and remaining scope}

The first new cover-module compilation failed because \code{if_true} and \code{if_false} are deprecated in the pinned runtime and warnings are treated as errors. They were replaced by \code{ite_true} and \code{ite_false}; the subsequent source compiled. That failed attempt and its exact source snapshot remain in the development evidence.

The existing free-repair command was also adjusted to select only the general declarations it actually imports, rather than every declaration later assigned the general-layer label. Its mathematical modules are unchanged. This prevents an expanded registry from causing the older command to request nonexistent imports.

The external JSON parser, source emission, hashing, and file system are tested but not formally verified. The checked mathematical statements apply to the literal typed input compiled by Lean. Separate input emission, hashes, and a Lean-decoded echo provide executed evidence that those literals match the intended problem. This boundary remains explicit.

The current producer is exhaustive and bounded, not a scalable branch-and-bound solver. It does not minimize evidence size. No integration into the authoritative Komorebi Python package or Paper III source tree is claimed. No theorem here constructs native arithmetic hosts, proves nonlinear convergence, or establishes a universal realization theorem for Komorebi Space. Those tasks remain separate from the now-operational costed rational-menu certificate path.

'''
p=ROOT/'monograph/Constructive_Repair.tex';s=p.read_text(encoding="utf-8")
s=s.replace('\\backmatter',text+'\n\\backmatter',1)
s=s.replace('\\begin{thebibliography}{9}','\\begin{thebibliography}{10}\n\\bibitem{menurelease}\nKomorebi P. \\emph{Constructive Repair v0.4.0: Costed Rational Menus and Rejection Covers}. Exact producer, checked cover theorems, typed certificates, verification records, and original-input echoes, 19 October 2026.\n',1)
p.write_text(s, encoding="utf-8")
print('Appended fresh v0.4.0 evidence')
