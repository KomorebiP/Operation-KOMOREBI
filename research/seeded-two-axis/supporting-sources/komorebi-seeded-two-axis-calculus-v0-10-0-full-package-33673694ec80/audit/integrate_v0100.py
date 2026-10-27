#!/usr/bin/env python3
"""Build the cumulative v0.10.0 TeX from its exact v0.9.0 base and new fragments."""
from pathlib import Path
import difflib
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'previous/Komorebi_Seeded_Two_Axis_Calculus_v0.9.0.tex'
DEST=ROOT/'Komorebi_Seeded_Two_Axis_Calculus_v0.10.0.tex'
s=BASE.read_text(); original=s

def once(old, new):
    global s
    count=s.count(old)
    if count!=1: raise RuntimeError(f'Integration anchor count {count}: {old[:110]!r}')
    s=s.replace(old,new,1)

once('pdftitle={Komorebi Seeded Two-Axis Calculus v0.9.0}', 'pdftitle={Komorebi Seeded Two-Axis Calculus v0.10.0}')
once('pdfsubject={Intrinsic arithmetic exchange, finite-resolution lifting, and derived invariant obstructions}', 'pdfsubject={Complete finite-group lifting obstructions, convergent repair, and a finite resolution horizon}')
once(r'\normalsize Working Formalization v0.9.0',r'\normalsize Working Formalization v0.10.0')
a=s.index(r'\begin{abstract}'); b=s.index(r'\end{abstract}',a)+len(r'\end{abstract}')
s=s[:a]+r'''\begin{abstract}
This manuscript develops a seed-generated calculus of transformation, resolution, and exchange residuals. Its categorical core uses indexed systems, coherent event diagrams, stable cofibers, and constructor-compatible quotients. Arithmetic models distinguish genuine reconstruction from information lost by forcing a residual to vanish. The running development preserves history-sensitive filtrations and explicitly records failures of stronger claims.

Version 0.10.0 gives a sufficient lifting criterion for representations of a fixed finite group over $\mathbb Z_p$. The complete one-step obstruction is a normalized multiplicativity class in $H^2$ of the residual adjoint module. Linear cochain corrections provide positive witnesses and dual nonexistence certificates. A central sign action proves that vanishing of the derived-invariant comparison cone alone is not sufficient for a representation lift.

An explicit averaging argument repairs sufficiently accurate approximate actions. If $e=v_p(|G|)$ and the defect depth is $m>2e$, correction converges with depths $m_j=2e+2^j(m-2e)$ while preserving level $m-e$. Consequently a representation modulo $p^n$ lifts integrally exactly when it extends to level $\max\{n+e,2e+1\}$. Controlled conjugacy gives a finite catalogue of integral isomorphism classes. A profinite example shows why fixing the finite source is an essential restriction.

The cohomological mechanism and quantitative finite-group stability bound are classical or already established in the cited literature. This release supplies explicit proofs, a finite-certificate implementation, counterexamples, and their integration into the two-axis calculus. The new work is self-reviewed and computationally regression-tested, not independently reviewed or Lean-certified. No new foundational axiom, historical novelty, general profinite lifting criterion, automorphic existence, or Langlands reciprocity theorem is claimed.
\end{abstract}'''+s[b:]
anchor=r'\section{Local-to-global reconstruction}'
once(anchor,(ROOT/'proofs/finite_group_lifting.tex').read_text()+'\n\n'+anchor)
# Correct current prose, not historical records or inherited proof blocks.
once('The converse is not claimed. Vanishing of this one obstruction does not prove that an integral representation exists, nor does it discharge all group relations or higher deformation obstructions. The positive theorem preserves information on the class with supplied lifts; it is not a procedure that manufactures missing lifts or repairs arbitrary nonliftable objects.',
     r'The converse is false in general: \cref{thm:blind-exchange} supplies a zero comparison cone for a nonliftable finite-group representation. The positive theorem preserves information on the class with supplied lifts. A sufficient criterion for a fixed finite source instead comes from the actual relation obstruction and the finite lifting horizon in \cref{thm:relation-H2,thm:finite-action-horizon}.')
once('These statements close the next intrinsic-exchange test bed in specified arithmetic settings. They do not establish that every such defect has a non-destructive repair. They also do not close unrestricted resolution-tower existence or the Langlands-facing globalization condition. A useful next problem is to prove a sufficient intrinsic criterion for assembling a compatible tower of representations from finite-level inputs, accounting explicitly for the remaining relation and deformation obstructions. Vanishing of the comparison cone alone has not been shown sufficient. Any repair must retain both the coefficient unit and the relevant representation data.',
     r'These statements distinguish intrinsic exchange from actual existence. The following section refutes sufficiency of the single comparison-cone test and proves a finite necessary-and-sufficient lifting criterion for a fixed finite group. That correction preserves the requested finite-level representation without killing the coefficient unit. It does not close unrestricted profinite-tower existence or the Langlands-facing globalization condition.')
old='K61 & Exact exchange on coefficient-lifted inputs & Nonzero defect obstructs a lift; converse not proved, \\cref{thm:lifted-input-exchange}.\\\\'
new=r'''K61 & Exact exchange on coefficient-lifted inputs & Necessary diagnostic; converse refuted by K64, \cref{thm:lifted-input-exchange}.\\
K62 & Complete one-step relation obstruction & $H^2$ class vanishes exactly for a next-level lift, \cref{thm:relation-H2}.\\
K63 & Repair ambiguity and certificates & $H^1$, $H^0$, and exact finite linear witnesses, \cref{prop:repair-H1}.\\
K64 & Blind derived-invariant comparison & Central sign refutes sufficiency of the single exchange cone, \cref{thm:blind-exchange}.\\
K65 & Averaged quadratic repair & Exact associativity and explicit division loss, \cref{lem:quadratic-repair}.\\
K66 & Convergent action repair & Fixed finite group and $m>2v_p(|G|)$, \cref{thm:convergent-action-repair}.\\
K67 & Finite action-lifting horizon & Necessary and sufficient level $\max\{n+e,2e+1\}$, \cref{thm:finite-action-horizon}.\\
K68 & Controlled integral conjugacy & Agreement beyond group-order valuation suffices, \cref{thm:close-action-conjugacy}.\\
K69 & Finite integral action catalogue & Isomorphism classes, not an equivalence of groupoids, \cref{cor:finite-action-catalogue}.\\
K70 & Cyclic relation Jacobian & Affine next-level certificate with $d^2$ variables, \cref{prop:cyclic-jacobian}.\\
K71 & Fixed quotient versus profinite lifting & Explicit continuous lift with growing image, \cref{prop:profinite-quotient-boundary}.\\'''
once(old,new)
once('The general ordered-filtration independence target remains refuted. Nonidentity towers, lattice gluing, intrinsic arithmetic exchange, and a necessary representation-lifting obstruction now have proofs in specified regimes. They do not supply automorphic globalization or a sufficient criterion for arbitrary representation lifts.',
     'The general ordered-filtration independence target remains refuted. A sufficient finite-precision criterion now exists for the fixed-finite-group lifting problem, while the converse of the single derived-invariant exchange test is refuted. These results do not supply continuous lifting for arbitrary profinite sources, geometric local conditions, or automorphic globalization.')
once(r'\item \textbf{Intrinsic lifting beyond the test bed.} K53--K61 supply natural invariant and derived-invariant comparisons, a non-scalar exact counterexample, and exact exchange for supplied coefficient lifts. Determine a sufficient intrinsic lifting criterion in a specified arithmetic class. Vanishing of the canonical comparison cone is only necessary at present. Find a bounded, non-destructive repair without assuming the missing lift.',
     r'\item \textbf{Continuous and constrained lifting.} K62--K71 close the fixed-finite-group problem with an exact obstruction and finite horizon. Extend the repair only after specifying continuity, permitted growth of finite images, and any geometric local conditions. The constant $v_p(|G|)$ is not uniform over growing quotients. A failure for one fixed quotient is not automatically a failure for the profinite source.')
anchor='The results do not establish a new foundation or a reciprocity theorem.'
once(anchor, r'The sufficient-lifting layer now adds an explicit distinction between detection and construction. The adjoint relation cocycle is a complete next-level obstruction, whereas derived invariants can be blind to nonliftability. For a fixed finite group, quantitative averaging converts a finite high-precision witness into an integral representation and gives controlled uniqueness up to conjugacy. The stated threshold is known in ultrametric stability, and the direct proof here makes its relation to residual repair explicit. It does not justify substituting fixed finite-group existence for a continuous Galois or automorphic existence problem.'+'\n\n'+anchor)
once(r'\end{thebibliography}',r'''\bibitem{FournierFacio2026}
F.~Fournier-Facio, \emph{Ultrametric analogues of Ulam stability of groups},
arXiv:2105.00516v5, version posted 22 July 2026, manuscript dated 23 July 2026.
Lemma 7.3, Proposition 7.4, and Example 7.5, printed pages 54--55. Exact version and displayed hypotheses checked 27 September 2026.
\url{https://arxiv.org/abs/2105.00516v5}.

'''+r'\end{thebibliography}')
once(r'\section{Version ledger}',(ROOT/'proofs/audit_v0100.tex').read_text()+'\n'+r'\section{Version ledger}')
once(r'\item[v0.9.0]',r'''\item[v0.10.0] Adds a complete $H^2$ next-level obstruction, cochain repair certificates, and a central-sign counterexample to the sufficiency of derived-invariant exchange. Gives a direct averaging proof of known finite-group ultrametric stability, an exact finite lifting horizon, controlled conjugacy, a finite class catalogue, a cyclic Jacobian certificate, and an explicit profinite scope boundary. Five exact suites pass. Preserves every inherited theorem/proof block and the full v0.9.0 package. Written proofs and self-review only.
\item[v0.9.0]''')
once("This section preserves the preceding release's audit. The present release's work is recorded in \\cref{app:audit-v070}.",
     r'This section is a historical audit record. The current continuation is recorded in \cref{app:audit-v0100}; the intervening version records retain their original scopes.')
once(r'\appendix', r'\appendix'+'\n'+r'\addtocontents{toc}{\protect\setcounter{tocdepth}{1}}')
DEST.write_text(s)
(ROOT/'audit/v0.9.0_to_v0.10.0.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile=BASE.name,tofile=DEST.name)))
print(f'Integrated {DEST.name}: {len(s.splitlines())} lines')
