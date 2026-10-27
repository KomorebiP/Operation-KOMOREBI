from pathlib import Path
root = Path(__file__).resolve().parent
main = root/'main'/'Paper_IX_Traditional_Final.tex'
s = main.read_text()
s = s.replace('pdftitle={Projector-Resolved Seed Calculus IX: Traditional Final Edition}', 'pdftitle={Euler Congruences: Completion, Factorial Strengthening and Sharp Dyadic Geometry}')
s = s.replace('\\fancyhead[L]{\\small Projector-Resolved Seed Calculus IX}', '\\fancyhead[L]{\\small\\scshape Euler congruences / Paper IX}')
s = s.replace('\\fancyhead[R]{\\small Traditional final edition}', '\\fancyhead[R]{\\small\\scshape Final strengthened edition}')
s = s.replace('\\definecolor{paperink}{HTML}{20384B}', '\\definecolor{paperink}{HTML}{185B58}')
s = s.replace('\\definecolor{ink}{HTML}{20384B}', '\\definecolor{ink}{HTML}{185B58}')
start=s.index('\\title{')
end=s.index('\\usepackage[nameinlink',start)
s=s[:start]+r'''\title{\textbf{Euler Congruences}\\[5pt]
  \Large Completion, Factorial Strengthening,\\ and Sharp Dyadic Geometry\\[7pt]
  \large Projector-Resolved Seed Calculus IX}
\author{Komorebi P.}
\date{Final strengthened edition\quad 6 October 2026}

'''+s[end:]
start=s.index('\\begin{abstract}')
end=s.index('\\end{abstract}',start)+len('\\end{abstract}')
s=s[:start]+r'''\begin{abstract}
We prove Nishibuchi's generalized Euler congruence conjecture in its full stated parameter range and develop sharper arithmetic consequences. For every prime-power packet width, a charged Hurwitz differential operator transfers integral difference estimates through the reciprocal generating series. In the dyadic case this gives mixed finite-difference bounds at every row, without a starting threshold. For the four addresses of width four, a divided-power argument adds the factorial gain $v_2(k!)$, determines every repeated-step valuation in addresses zero and one, and gives a stronger address-two estimate with exact values at all power-of-two orders. The corresponding first differences yield least periods and bijective isometric continuations onto explicit dyadic residue classes. We also determine exact Taylor radii for three addresses. The manuscript retains the complete earlier arithmetic, lifting, deformation, and analytic-regularity development, with dated historical appendices. A separate appendix states the precise remaining simplicity problem for ordinary Euler tails. Formal coverage is explicit: the external conjecture and several four-address results have inherited Lean verification; the new factorial, mixed-step, all-rank, and radius arguments are written proofs with recorded audits and exact computational checks, and await dedicated Lean formalization.
\end{abstract}
\input{../edition_summary.tex}
'''+s[end:]
s=s.replace('\\input{parts/20_arithmetic}', '\\input{parts/20_arithmetic}\n\\clearpage\n\\input{../strengthening.tex}\n\\clearpage')
s=s.replace('\\input{parts/70_continuation}', '\\appendix\n\\input{../root_scope.tex}\n\\input{parts/70_continuation}')
s=s.replace('\\bibitem{DLMF24}', r'''\bibitem{gessel}
Ira M. Gessel, \emph{Applications of the classical umbral calculus},
arXiv:math/0108121v3, 22 November 2001, Section 9, in particular the Frobenius Euler congruence and the derivation following Theorem 9.2.
\url{https://arxiv.org/abs/math/0108121}.
The normalization and quantifiers of the ordinary Euler input were checked against the primary PDF in the strengthening checkpoint.

\bibitem{DLMF24}''')
main.write_text(s)
p=root/'main'/'parts'/'70_continuation.tex'
p.write_text(p.read_text().replace('\\clearpage\\appendix','\\clearpage',1))
p=root/'main'/'parts'/'00_scope.tex'
s=p.read_text().replace('This edition revises the exposition without adding Lean theorems or making\nnew claims of historical priority.', 'The inherited formal development is retained without adding Lean declarations. The strengthening chapters add written proofs and clearly mark their formalization boundary; no historical-priority claim is made.')
p.write_text(s)
p=root/'main'/'parts'/'20_arithmetic.tex'
s=p.read_text().replace('a separate analysis.  Exact valuations of arbitrary higher-order differences', 'a separate analysis.  The new strengthening chapters determine all repeated-step higher differences in addresses zero and one and a power-of-two-order family in address two. The full exact classification of arbitrary higher-order differences')
p.write_text(s)
p=root/'main'/'parts'/'50_open_questions.tex'
s=p.read_text()
a=s.index('\\item \\textbf{Higher dyadic differences.}')
b=s.index('\\item \\textbf{Exact affine Mahler-kernel valuations.}',a)
s=s[:a]+r'''\item \textbf{The remaining higher-difference classification.}
The new strengthening chapters determine every repeated-step valuation in addresses $j=0,1$, give the exact criterion for equality in the common mixed-step lower bound there, and determine address-two valuations at all power-of-two orders. What remains is a complete exact formula in address two at the other orders, a full classification in address three, and the amount of additional cancellation in mixed-step cases where the leading term vanishes. Numerical patterns through a finite range do not settle these questions.

\item \textbf{Upper-half addresses at larger dyadic rank.}
The exact first-difference laws now include $N=2,4,8$ and every lower-half address for $N=2^a\ge4$. Larger upper-half addresses need a finer classification. Explicit counterexamples show that extrapolating one low-order Newton coefficient to a universal metric law is false. A least period is measured in packet rows; its Euler-degree displacement is $NP$.

'''+s[b:]
a=s.index('\\item \\textbf{Exact classical dyadic tail values.}')
b=s.index('\\end{enumerate}',a)
s=s[:a]+r'''\item \textbf{Classical tail root classification and simplicity.}
The later tail program gives an exact factorization, finite preparation for each fixed depth, and several infinite regular-wall and simplicity families, as summarized in Appendix~\ref{app:root:scope}. A universal explicit root classification and universal simplicity of the remaining analytic factor are still open. In the exceptional address-one quadratic reduction, the residual task is a nonvanishing discriminant condition. Empty tails remain exactly zero. This problem is distinct from the solved Nishibuchi congruence conjecture.
'''+s[b:]
p.write_text(s)
