#!/usr/bin/env python3
"""Rebuild the standalone v0.8.0 TeX from the preserved base and proof blocks.
Overwrites the generated standalone source. Preserve edits before rerunning.
"""
from pathlib import Path
import difflib
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'previous/Komorebi_Seeded_Two_Axis_Calculus_v0.7.0.tex'
OUT=ROOT/'Komorebi_Seeded_Two_Axis_Calculus_v0.8.0.tex'
s=BASE.read_text()
original=s

def change(old,new):
    global s
    if s.count(old)!=1:
        raise ValueError(f'Expected one occurrence: {old[:100]!r}; found {s.count(old)}')
    s=s.replace(old,new,1)

change('pdftitle={Komorebi Seeded Two-Axis Calculus v0.7.0}',
       'pdftitle={Komorebi Seeded Two-Axis Calculus v0.8.0}')
change('pdfsubject={Semantic exchange diagrams, excisive reconstruction, and arithmetic interaction kernels}',
       'pdfsubject={Arithmetic resolution towers, completion defects, and effective lattice reconstruction}')
change('Working Formalization v0.7.0','Working Formalization v0.8.0')
change(r'\date{26 September 2026}',r'\date{27 September 2026}')
start=s.index(r'\begin{abstract}')
end=s.index(r'\end{abstract}',start)+len(r'\end{abstract}')
s=s[:start]+r'''\begin{abstract}
This manuscript develops a seed-generated calculus of transformations within a resolution, coarsening between resolutions, and the residuals of their exchange maps. Its categorical core uses indexed categories, coherent event diagrams, stable cofibers, and constructor-compatible Verdier quotients. It distinguishes a normalization endpoint, its comparison map, and the history-sensitive filtration of its residual. Excisive event diagrams reconstruct from principal ideals, while integral scalar and matrix models identify precise repair kernels and collapse conditions.

Version 0.8.0 adds genuinely nonidentity arithmetic coarsenings by derived reduction modulo powers of a squarefree integer. Coherent weighted exchange cells have explicit Koszul residuals. At a finite prime-power level, forcing an interaction of two nonunit scalar cells to be excisive collapses the whole perfect category. With several primes, the exact quotient removes precisely the selected prime components and commutes with finite coarsening. Uniform based-complex towers reconstruct coefficientwise, but repair need not commute with completion: the comparison's fiber consists of explicitly identified generic fibers.

An arithmetic fracture square retains the localized and completed descriptions together with their common generic data. A further theorem constructs a unique integral lattice from independently supplied localized modules, local lattices, and compatible generic identifications. Compatible operators descend to that lattice. These are restricted arithmetic reconstruction results using classical algebraic mechanisms, not an automorphic existence theorem. Written proofs, self-review, counterexamples, and exact finite regression checks accompany the constructions. No Lean certification, new foundational axiom, historical novelty, or Langlands reciprocity is claimed.
\end{abstract}'''+s[end:]
blocks='\n\n'.join((ROOT/'proofs'/p).read_text() for p in
                      ['arithmetic_resolution_towers.tex','completion_and_arithmetic_reconstruction.tex'])
change(r'\section{Local-to-global reconstruction}',blocks+'\n\n'+r'\section{Local-to-global reconstruction}')
change('K15 & Effective reconstruction theorem for a nontrivial arithmetic instance & Open domain theorem',
       'K15 & Effective reconstruction theorem for a nontrivial arithmetic instance & Lattice case proved in K51; the intended reciprocity instantiation remains open.')
anchor=r'K41 & Integral matrix collapse criterion & Verified Smith data classify free collapse versus torsion support, \cref{thm:matrix-collapse}.\\'
rows=r'''
K42 & Nonidentity arithmetic resolution tower & Derived reduction is exact and conservative, not faithful, \cref{thm:adic-tower}.\\
K43 & Coherent weighted exchange cells & Explicit source of residuals and base-change transport, \cref{thm:weighted-adic-exchange}.\\
K44 & Prime-power interaction cohomology & Full finite-level Koszul cohomology, \cref{thm:prime-power-koszul}.\\
K45 & Nilpotent excision collapse & Nonunit pairs force the prime-power quotient to zero, \cref{thm:nilpotent-collapse}.\\
K46 & Finite prime-component quotient & Exact quotient equivalence and tower coherence, \cref{thm:finite-prime-quotient}.\\
K47 & Based tower reconstruction & Uniform bounded ranks and compatible matrices required, \cref{thm:based-tower-reconstruction}.\\
K48 & Transient negative residual classes & Nonzero finite groups can form a pro-zero system, \cref{prop:transient-koszul}.\\
K49 & Completion--repair comparison defect & Explicit generic-fiber formula and vanishing criterion, \cref{thm:completion-repair-defect}.\\
K50 & Arithmetic fracture reconstruction & Perfect integral complexes and their residuals, \cref{thm:arithmetic-fracture,cor:residual-fracture}.\\
K51 & Effective arithmetic lattice gluing & Existence and uniqueness from specified generic identifications, \cref{thm:lattice-gluing}.\\
K52 & Compatible operator gluing & Preserves supplied integral polynomial relations, \cref{cor:lattice-operators}.\\'''
change(anchor,anchor+rows)
change('The general ordered-filtration independence target remains refuted. The concrete strict semantic and integral-kernel obligations now have positive solutions, but they do not close arithmetic globalization.',
       'The general ordered-filtration independence target remains refuted. A nonidentity arithmetic tower and an effective lattice-gluing instance now have proofs. Neither the finite prime-component quotient nor this lattice existence theorem supplies automorphic globalization.')
change(r'\item \textbf{A nontrivial resolution tower.} Replace identity coarsenings in the scalar model by actual arithmetic restriction or truncation functors. Compute the resulting interaction objects and test whether their invariant kernel preserves the information required by the application.',
       r'\item \textbf{Beyond weighted scalar cells.} The derived coefficient tower is now constructed. Find a specified arithmetic functor whose natural comparison with coarsening, rather than an imposed scalar weight, has a nonzero residual. Determine its information-preserving repair or gluing mechanism.')
change(r'\item \textbf{Arithmetic existence.} For K15 and K17, define an actual globalization defect and prove that its vanishing is equivalent to the desired existence statement. The event-poset reconstruction theorem reconstructs a diagram, not an automorphic object.',
       r'\item \textbf{Arithmetic existence beyond lattices.} K51 closes a concrete lattice case of K15. For the intended K17 application, construct the generic arithmetic or automorphic data and the required identifications, rather than importing them as gluing hypotheses. A globally glued lattice with supplied operators is not an automorphic representation.')
change('Given the specified comparison, its defect is a candidate completion-level mixed residual in a setting where such defects are defined.',
       r'Given the specified comparison, its defect is a candidate completion-level mixed residual in a setting where such defects are defined. The comparison is now explicit in \cref{thm:completion-repair-defect}: even compatible finite-level repairs can fail to commute with completion, with a nonzero generic-fiber defect. An unconditional bi-completion claim is therefore false.')
change('These results sharpen the proposed calculus rather than establish a new foundation or a reciprocity theorem. The arithmetic content still depends on constructing appropriate semantic diagrams, nontrivial repair systems, and effective reconstruction theorems. The abelian torsor example remains a verified classical test case, not a substitute for those arithmetic obligations.',
       r'''The arithmetic tower sharpens that boundary further. Finite resolution can turn a nonzero nilpotent interaction into a generator of the whole perfect category. Several prime components permit nontrivial excisive quotients, but deleting a component before completion loses a generic fiber. Retaining the localized and completed branches with their overlap instead gives a proved arithmetic fracture square and an effective lattice-gluing theorem. These use established algebraic mechanisms to make the calculus concrete.

The results do not establish a new foundation or a reciprocity theorem. The remaining arithmetic content requires actual generic parameters, compatible actions, and the specific existence theorem demanded by the intended correspondence. Neither a torsor trivialization, a reconstructed event diagram, nor a glued integral lattice is an automorphic realization by definition.''')
refs=r'''
\bibitem{StacksPerfect}
The Stacks Project Authors,
\emph{Perfect complexes}, Section 15.76, Tag 0656,
Definition 15.76.1 and Lemma 15.76.9, checked 27 September 2026.
\url{https://stacks.math.columbia.edu/tag/0656}.

\bibitem{StacksDerivedTensor}
The Stacks Project Authors,
\emph{Derived tensor product}, Section 15.60, Tag 06XY,
checked 27 September 2026. K-flat models and the exact derived tensor construction.
\url{https://stacks.math.columbia.edu/tag/06XY}.

\bibitem{StacksRlim}
The Stacks Project Authors,
\emph{Rlim of abelian groups}, Section 15.88, Tag 07KV,
checked 27 September 2026. The product model and the Mittag--Leffler case of derived inverse limits.
\url{https://stacks.math.columbia.edu/tag/07KV}.

\bibitem{StacksLocalization}
The Stacks Project Authors,
\emph{Localization}, Section 10.9, Tag 00CM,
checked 27 September 2026. The universal property and exactness on modules.
\url{https://stacks.math.columbia.edu/tag/00CM}.

\bibitem{StacksDerivedCompletion}
The Stacks Project Authors,
\emph{Derived Completion}, Section 15.93, Tag 091N,
Lemma 15.93.12, checked 27 September 2026. Inverting a defining element before derived completion gives zero.
\url{https://stacks.math.columbia.edu/tag/091N}.
'''
change(r'\end{thebibliography}',refs+'\n'+r'\end{thebibliography}')
newaudit=r'''
\clearpage
\section{Audit and verification record for v0.8.0}\label{app:audit-v080}

\subsection{Scope and proof boundary}
The supplied v0.7.0 PDF, source, and full package are preserved unchanged. Their hashes are recorded in the release. This continuation adds K42--K52, updates the restricted lattice status of K15, and retains the earlier open reciprocity obligations. The new proofs have received an authoring-session self-review, not an independent referee review or Lean certification. No fresh complete audit of all inherited theorems is claimed.

The three executed mathematical routes were derived coefficient towers, excision versus completion, and arithmetic reconstruction with retained overlaps. The first produces explicit finite-level interactions. The second refutes unconditional commutation of repair and completion and proves a generic-fiber criterion. The third proves a fracture square and effective lattice gluing, with compatible operator descent.

\subsection{Adversarial checks}
\begin{enumerate}
\item Derived reduction is exact, but naive tensor on arbitrary modules is not. The infinite periodic resolution over $\mathbb Z/p^2$ prevents replacing a perfect two-term cone by its degree-zero cohomology.
\item Canonical tensor/base-change exchanges have zero residual. Nonzero scalar cells are specified additional data, not an unexplained consequence of coarsening.
\item Prime-power interactions can generate the whole perfect category even for nonzero labels. A multi-prime quotient removes whole components and can still collapse if every prime is selected.
\item Coherent finite reductions do not imply commutation with an infinite inverse limit. The field factors in K49 exhibit the precise missing information.
\item The based tower theorem requires common bounded ranks and compatible matrices. Arbitrary incompatible level choices are not claimed to lift.
\item The fracture square reconstructs a supplied complex. K51 separately proves effective existence for independent lattice data, but requires the generic identifications explicitly. Operator gluing requires exact intertwining, not only matching characteristic polynomials.
\item Generic-fiber defects are computed in $D(\widehat B)$, not asserted to be perfect objects over the completed ring. Their cofiber is the $[1]$ shift of the stated fiber.
\end{enumerate}

\subsection{Reproducible finite checks}
All three check scripts passed in this session with Python 3.13.5. The inherited two scripts reproduce their earlier ranges. The new script additionally uses SymPy 1.14.0 for integer Hermite normal forms; each resulting lattice basis is checked by its exact finite residues and index. There is no random sampling or numerical tolerance.

The new suite checks all 1,080 ordered coefficient pairs in the eight listed rings $\mathbb Z/q$ with $q\in\{2,3,4,5,8,9,16,25\}$. It enumerates kernels and images to check three cohomology degrees and verifies middle-cohomology elementary divisors by torsion counts. It also checks 160 annihilator-transition tuples, 1,728 exchange coherences, 72 prime-component projections, 2,304 positive-label pair instances, all 30 pairs of subspaces of $\mathbb F_2^2$ and $\mathbb F_3^2$, 2,430 operator-preservation instances, 6,100 rank-one rational lattice membership tests, and 972 principal-part reconstruction witnesses. Exact bounds and nonclaims are in the JSON report.

These are finite regression checks, not computational proofs of universal categorical statements or assertions about every $p$-adic input. The limiting and gluing theorems have separate written proofs. The arithmetic-square argument and nilpotent-cone argument use classical mechanisms; no historical novelty is inferred from their packaging here.

\subsection{Build and source verification}
The standalone source is regenerated from the preserved base and the two new proof fragments by \texttt{audit/integrate\_v080.py}. The source diff, run reports, source checks, build log, and rendered-page audit accompany the release. The first general web search returned irrelevant results and was not used as evidence; the cited primary Stacks Project pages were then opened directly. No external source text or font files are bundled. The lack of a Lean executable in this runtime is recorded as an environment limitation, not a mathematical failure.

'''
change(r'\section{Version ledger}',newaudit+r'\section{Version ledger}')
change(r'\item[v0.7.0]',r'\item[v0.8.0] Adds nonidentity derived arithmetic coarsenings, coherent weighted exchanges, the prime-power Koszul formula, and nilpotent excision collapse. Classifies finite prime-component quotients and their coherence. Proves uniform based-tower reconstruction, computes transient negative classes, and identifies the generic-fiber defect of completion versus repair. Proves arithmetic fracture reconstruction, effective lattice gluing, and compatible operator descent. Preserves the v0.7.0 package and adds exact finite tests. Written proofs and self-review only.'+'\n'+r'\item[v0.7.0]')
OUT.write_text(s)
(ROOT/'audit/v0.7.0_to_v0.8.0.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile=BASE.name,tofile=OUT.name)))
labels=re.findall(r'\\label\{([^}]+)\}',s)
refs_used=[]
for content in re.findall(r'\\(?:c|C|eq)?ref\{([^}]+)\}',s):refs_used.extend(content.split(','))
cites_used=[]
for content in re.findall(r'\\cite\{([^}]+)\}',s):cites_used.extend(content.split(','))
bib=re.findall(r'\\bibitem\{([^}]+)\}',s)
report={'source_sha256':hashlib.sha256(s.encode()).hexdigest(),
        'line_count':len(s.splitlines()),'duplicate_labels':sorted({x for x in labels if labels.count(x)>1}),
        'missing_labels':sorted(set(refs_used)-set(labels)),
        'missing_citations':sorted(set(cites_used)-set(bib)),
        'proof_blocks_embedded':True,'preserved_base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest()}
(ROOT/'audit/static_source_checks.json').write_text(json.dumps(report,indent=2)+'\n')
if report['duplicate_labels'] or report['missing_labels'] or report['missing_citations']:
    raise AssertionError(report)
print(json.dumps(report,indent=2))
