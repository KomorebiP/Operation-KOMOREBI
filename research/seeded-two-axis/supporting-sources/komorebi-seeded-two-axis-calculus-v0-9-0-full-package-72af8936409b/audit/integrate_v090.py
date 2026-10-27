#!/usr/bin/env python3
"""Rebuild the standalone v0.9.0 source from its preserved v0.8.0 base."""
from pathlib import Path
import difflib

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'previous/Komorebi_Seeded_Two_Axis_Calculus_v0.8.0.tex'
DEST=ROOT/'Komorebi_Seeded_Two_Axis_Calculus_v0.9.0.tex'
s=BASE.read_text(); original=s

def once(old: str,new: str) -> None:
    global s
    if s.count(old)!=1:raise RuntimeError(f'Expected one integration anchor: {old[:90]!r}, found {s.count(old)}')
    s=s.replace(old,new,1)

once('pdftitle={Komorebi Seeded Two-Axis Calculus v0.8.0}',
     'pdftitle={Komorebi Seeded Two-Axis Calculus v0.9.0}')
once('pdfsubject={Arithmetic resolution towers, completion defects, and effective lattice reconstruction}',
     'pdfsubject={Intrinsic arithmetic exchange, finite-resolution lifting, and derived invariant obstructions}')
once(r'\normalsize Working Formalization v0.8.0',r'\normalsize Working Formalization v0.9.0')
a=s.index(r'\begin{abstract}'); b=s.index(r'\end{abstract}',a)+len(r'\end{abstract}')
s=s[:a]+r'''\begin{abstract}
This manuscript develops a seed-generated calculus of transformations within a resolution, coarsening between resolutions, and residuals of their exchange maps. The categorical core uses indexed categories, coherent event diagrams, stable cofibers, and constructor-compatible quotients. It retains history-sensitive filtrations rather than identifying different normalization schedules. Earlier arithmetic constructions include prime-support repair kernels, nonidentity coefficient towers, completion defects, and effective lattice reconstruction from specified generic identifications.

Version 0.9.0 supplies intrinsic arithmetic comparisons without imposed exchange weights. A kernel--reduction boundary identifies residuals with torsion in a cokernel. Smith data determine their exact precision profile and the sharp additional resolution needed to certify an integral lift. For finite-group lattices this residual is first cohomology, and the result gives explicit tests for lifting invariant vectors and equivariant isomorphisms.

The fully derived problem has a different answer. Perfect coefficient changes commute with derived invariants. A non-scalar cyclic action over $\mathbb Z/p^2$ instead gives a canonical exact-functor exchange whose cofiber has nonzero cohomology in every integer degree. This action cannot lift to the next coefficient level. Conversely, a supplied lift over a common ring forces exact exchange when both coefficient quotients are perfect over that ring. Nonvanishing of the comparison cone is therefore a necessary lifting obstruction, not a sufficient classification of all failures.

The release includes written proofs, self-review, counterexamples, and exact finite regression checks. Classical cohomological and categorical mechanisms are attributed explicitly. No Lean certification, new foundational axiom, historical novelty, unrestricted representation-lifting criterion, automorphic existence, or Langlands reciprocity theorem is claimed.
\end{abstract}'''+s[b:]
once(r'\tableofcontents',r'\begingroup\small\tableofcontents\endgroup')
once('uses small stable $\\infty$-categories, or a specified enhancement presenting them.',
     'uses stable $\\infty$-categories, or a specified enhancement presenting them. These are small unless a section explicitly uses an unbounded ambient derived category in a fixed universe.')
anchor=r'\section{Local-to-global reconstruction}'
once(anchor,(ROOT/'proofs/intrinsic_arithmetic_exchange.tex').read_text()+'\n\n'+anchor)
anchor='K52 & Compatible operator gluing & Preserves supplied integral polynomial relations, \\cref{cor:lattice-operators}.\\\\'
rows=r'''
K53 & Intrinsic kernel--reduction residual & Natural torsion boundary and transition law, \cref{thm:kernel-bockstein}.\\
K54 & Sharp finite-resolution lifting window & Smith profile, minimal delay, and pro-zero residuals, \cref{thm:precision-window}.\\
K55 & Finite-group invariant residual & Identified with $H^1[p^n]$, with group-order bound, \cref{thm:invariant-bockstein}.\\
K56 & Equivariant morphism lifting & Obstruction and finite-precision isomorphism test for supplied lattices, \cref{thm:intertwiner-lifting}.\\
K57 & Norm-quotient lattice family & Natural non-scalar actions and sharp transient invariants, \cref{thm:norm-quotient}.\\
K58 & Perfect-base derived exchange & Exact commutation, not a new residual, \cref{thm:perfect-invariant-exchange}.\\
K59 & Nonperfect-base intrinsic derived defect & Non-scalar action with unbounded cofiber and unit-loss boundary, \cref{thm:nonflat-invariant-exchange,cor:intrinsic-unit-loss}.\\
K60 & One-step action-lifting obstruction & The finite cyclic action cannot lift from $p^2$ to $p^3$, \cref{thm:one-step-group-lift}.\\
K61 & Exact exchange on coefficient-lifted inputs & Nonzero defect obstructs a lift; converse not proved, \cref{thm:lifted-input-exchange}.\\'''
once(anchor,anchor+rows)
once('The general ordered-filtration independence target remains refuted. A nonidentity arithmetic tower and an effective lattice-gluing instance now have proofs. Neither the finite prime-component quotient nor this lattice existence theorem supplies automorphic globalization.',
     'The general ordered-filtration independence target remains refuted. Nonidentity towers, lattice gluing, intrinsic arithmetic exchange, and a necessary representation-lifting obstruction now have proofs in specified regimes. They do not supply automorphic globalization or a sufficient criterion for arbitrary representation lifts.')
once(r'\item \textbf{Beyond weighted scalar cells.} The derived coefficient tower is now constructed. Find a specified arithmetic functor whose natural comparison with coarsening, rather than an imposed scalar weight, has a nonzero residual. Determine its information-preserving repair or gluing mechanism.',
     r'\item \textbf{Intrinsic lifting beyond the test bed.} K53--K61 supply natural invariant and derived-invariant comparisons, a non-scalar exact counterexample, and exact exchange for supplied coefficient lifts. Determine a sufficient intrinsic lifting criterion in a specified arithmetic class. Vanishing of the canonical comparison cone is only necessary at present. Find a bounded, non-destructive repair without assuming the missing lift.')
anchor='The results do not establish a new foundation or a reciprocity theorem.'
once(anchor,'The intrinsic exchange layer now distinguishes degree-zero information loss from a genuine failure between fully derived exact functors. Residual torsion gives a sharp finite lifting window for fixed integral constraints. A nonperfect coefficient change can instead expose an unbounded defect and a genuine missing representation lift. Exact comparison is restored on supplied coefficient-lifted inputs under the stated perfectness hypotheses, without taking a quotient that erases the coefficient unit.\n\n'+anchor)
anchor=r'\end{thebibliography}'
once(anchor,r'''\bibitem{MilneCFT2020}
J.~S. Milne, \emph{Class Field Theory}, version 4.03, 6 August 2020.
Chapter II, 1.9 (coefficient long exact sequence), 1.18--1.21 (crossed homomorphisms, cyclic $H^1$, and explicit boundaries), and 3.4 (cyclic periodic resolution). Primary source checked 27 September 2026, including PDF pages 70, 75, and 90, corresponding to printed pages 61, 66, and 81.
\url{https://www.jmilne.org/math/CourseNotes/CFT.pdf}.

'''+anchor)
once(r'\section{Version ledger}',(ROOT/'proofs/audit_v090.tex').read_text()+'\n'+r'\section{Version ledger}')
once(r'\item[v0.8.0]',r'''\item[v0.9.0] Adds intrinsic kernel and invariant comparisons, explicit cohomological residuals, sharp precision-window lifting, equivariant morphism correction, and norm-quotient examples. Proves perfect-base derived exchange and exhibits a non-scalar cyclic action with an unbounded canonical exchange defect over singular finite coefficients. Proves the one-step failure to lift that action and exact exchange for supplied coefficient-lifted inputs. Preserves the full v0.8.0 package. All four finite suites pass, including independent full-bar checks. Written proofs and self-review only.
\item[v0.8.0]''')
once(r'\section{Version ledger}'+'\n\n'+r'\begingroup\small\raggedright',
     r'\section{Version ledger}'+'\n\n'+r'\begingroup\footnotesize\raggedright')
DEST.write_text(s)
(ROOT/'audit/v0.8.0_to_v0.9.0.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile=BASE.name,tofile=DEST.name)))
print(f'Integrated {DEST.name}: {len(s.splitlines())} lines')
