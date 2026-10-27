#!/usr/bin/env python3
"""Regenerate v0.11.0 from the preserved v0.10.0 source and proof fragments."""
from pathlib import Path
import difflib
import re

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'previous/Komorebi_Seeded_Two_Axis_Calculus_v0.10.0.tex'
OUT=ROOT/'Komorebi_Seeded_Two_Axis_Calculus_v0.11.0.tex'

def replace_once(text: str, before: str, after: str) -> str:
    if text.count(before)!=1:
        raise ValueError(f'Expected one integration anchor, found {text.count(before)}: {before[:90]}')
    return text.replace(before,after,1)

def main() -> None:
    base=BASE.read_text(); s=base
    s=replace_once(s,'pdftitle={Komorebi Seeded Two-Axis Calculus v0.10.0}',
                  'pdftitle={Komorebi Seeded Two-Axis Calculus v0.11.0}')
    s=replace_once(s,'pdfsubject={Complete finite-group lifting obstructions, convergent repair, and a finite resolution horizon}',
                  'pdfsubject={Continuous source resolution, normalized commutators, and sharp rank-two lifting}')
    s=replace_once(s,'Working Formalization v0.10.0','Working Formalization v0.11.0')
    abstract=r'''\begin{abstract}
This manuscript develops a seed-generated calculus of transformations, resolution changes, and residuals of their exchange maps. Its categorical core uses indexed categories, coherent event diagrams, stable cofibers, and constructor-compatible quotients, while retaining history-sensitive filtrations. Arithmetic test beds include nonidentity coefficient towers, completion defects, lattice reconstruction, intrinsic derived exchanges, and a finite lifting horizon for a fixed finite group.

Version 0.11.0 retains the actual profinite source. Continuous relation cohomology characterizes next-level lifts, and source inflation identifies when a finite-quotient obstruction disappears after that source resolution is refined. Compatible towers reconstruct continuously, and free pro-$p$ sources admit arbitrary coefficient lifts of their generator matrices.

For continuous representations of $\mathbb Z_p^r$, removing a common scalar precision exposes normalized commutators. When one normalized generator is cyclic modulo $p$, their vanishing is necessary and sufficient for an integral lift, constructed by finite polynomial certificates. This condition covers every rank-two input. It yields a complete finite-matrix decision and a sharp uniform horizon $2n-1$ for lifting a representation modulo $p^n$. Explicit positive and negative examples distinguish genuine abelian relations from torsion relations introduced by fixing a finite quotient. A mixed-variance groupoid records coefficient reduction and source inflation without identifying their directions.

Written proofs, self-review, exact regression tests, and a usable rank-two certificate tool accompany the construction. No Lean certification, independent review, historical novelty, universal profinite lifting theorem, prescribed geometric deformation condition, automorphic existence, or Langlands reciprocity theorem is claimed.
\end{abstract}'''
    s,n=re.subn(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:abstract,s,count=1,flags=re.S)
    assert n==1
    anchor=r'\section{Local-to-global reconstruction}'
    s=replace_once(s,anchor,(ROOT/'proofs/profinite_lifting.tex').read_text()+'\n\n'+anchor)
    row=r'K71 & Fixed quotient versus profinite lifting & Explicit continuous lift with growing image, \cref{prop:profinite-quotient-boundary}.\\'
    rows=r'''
K72 & Continuous one-step obstruction & Finite discrete adjoint coefficients and continuous repair, \cref{thm:continuous-H2}.\\
K73 & Source-inflation criterion & Continuous vanishing occurs on some finer quotient, \cref{thm:source-inflation}.\\
K74 & Continuous tower reconstruction & Vanishing $H^2$ or a compatible tower; finite-generation compactness, \cref{thm:continuous-tower}.\\
K75 & Free pro-$p$ coefficient lifting & Arbitrary integral generator lifts extend continuously, \cref{thm:free-pro-p-lift}.\\
K76 & Procyclic matrix powers & Exact residual $p$-power-order criterion, including $p=2$, \cref{lem:procyclic-powers}.\\
K77 & Cyclic-centralizer certificate & Finite polynomial description over a coefficient ring, \cref{lem:cyclic-centralizer}.\\
K78 & Normalized cyclic lifting & Complete obstruction and explicit polynomial reconstruction, \cref{thm:normalized-cyclic-lift}.\\
K79 & Cyclic-stratum horizon & Level $n+a$ suffices under the cyclic hypothesis, \cref{cor:abelian-cyclic-horizon}.\\
K80 & Complete rank-two profinite test & All continuous $\mathbb Z_p^r$ inputs, no extra deformation conditions, \cref{thm:rank-two-profinite}.\\
K81 & Sharp rank-two horizon & Level $2n-1$, optimal for $n,r\geq2$, \cref{cor:rank-two-sharp-horizon}.\\
K82 & Mixed source--coefficient variance & Source inflation is not arbitrary source coarsening, \cref{prop:mixed-source-variance}.\\'''
    s=replace_once(s,row,row+rows)
    intro='The general ordered-filtration independence target remains refuted. A sufficient finite-precision criterion now exists for the fixed-finite-group lifting problem, while the converse of the single derived-invariant exchange test is refuted. These results do not supply continuous lifting for arbitrary profinite sources, geometric local conditions, or automorphic globalization.'
    newintro=r'The general ordered-filtration independence target and the converse of the single derived-invariant test remain refuted. Fixed-finite-group lifting, continuous free pro-$p$ lifting, and rank-two lifting for $\mathbb Z_p^r$ now have constructive solutions. Higher-rank abelian lifting is covered on the specified cyclic normalized stratum. Arbitrary profinite relations, geometric local conditions, and automorphic globalization remain separate obligations.'
    s=replace_once(s,intro,newintro)
    item=r'\item \textbf{Continuous and constrained lifting.} K62--K71 close the fixed-finite-group problem with an exact obstruction and finite horizon. Extend the repair only after specifying continuity, permitted growth of finite images, and any geometric local conditions. The constant $v_p(|G|)$ is not uniform over growing quotients. A failure for one fixed quotient is not automatically a failure for the profinite source.'
    newitem=r'\item \textbf{Noncommutative and constrained lifting.} K72--K82 handle continuous source refinement and give complete rank-two $\mathbb Z_p^r$ reconstruction. Next specify a noncommutative profinite presentation or a noncyclic higher-rank centralizer. Construct its actual relation obstruction and a sufficient repair criterion. Prescribed determinants and geometric local conditions must be added as equations with their own compatibility checks. No uniform averaging bound over growing finite quotients is assumed.'
    s=replace_once(s,item,newitem)
    ending='The results do not establish a new foundation or a reciprocity theorem.'
    newparagraph=r'The continuous-source layer now separates coefficient precision from source inflation. A finite-quotient obstruction can disappear when more of the source is allowed to act, but an actual commutativity relation cannot be discarded. Scalar-depth normalization exposes that relation, and a cyclic centralizer constructs compatible integral matrices from finite polynomial data. In rank two the cyclic condition is automatic after normalization, yielding a complete test and the sharp $2n-1$ horizon. This proves reconstruction without eliminating the coefficient category, while the mixed-variance diagram states exactly how the two resolution coordinates interact.'
    s=replace_once(s,ending,newparagraph+'\n\n'+ending)
    bib=r'''
\bibitem{StacksContinuous}
The Stacks Project Authors,
\emph{Tate's continuous cohomology}, Section 59.58, Tag 0DVG.
\url{https://stacks.math.columbia.edu/tag/0DVG}.
Continuous inhomogeneous-cochain conventions checked on 27 September 2026. The new continuous obstruction results use finite discrete coefficient modules, not an identification of arbitrary topological cohomology theories.
'''
    s=replace_once(s,r'\end{thebibliography}',bib+'\n'+r'\end{thebibliography}')
    anchor='\\section{Version ledger}'
    s=replace_once(s,anchor,(ROOT/'audit/audit_appendix_v0110.tex').read_text()+'\n\n\\clearpage\n'+anchor)
    version=r'\item[v0.11.0] Proves continuous one-step obstruction and source-inflation criteria, continuous tower reconstruction, and free pro-$p$ coefficient lifting. Gives a normalized cyclic-centralizer lifting criterion for $\mathbb Z_p^r$, a complete rank-two test, and the sharp uniform horizon $2n-1$. Correctly separates source inflation from coefficient reduction by mixed variance. Adds exact positive and negative examples, a certificate CLI, and a sixth regression suite. Preserves the entire v0.10.0 package. Written proofs and self-review only.'
    s=replace_once(s,r'\item[v0.10.0]',version+'\n'+r'\item[v0.10.0]')
    OUT.write_text(s)
    diff=''.join(difflib.unified_diff(base.splitlines(True),s.splitlines(True),fromfile=BASE.name,tofile=OUT.name))
    (ROOT/'audit/source_changes.patch').write_text(diff)
    print(OUT.name, len(s.splitlines()), 'lines')

if __name__=='__main__':main()
