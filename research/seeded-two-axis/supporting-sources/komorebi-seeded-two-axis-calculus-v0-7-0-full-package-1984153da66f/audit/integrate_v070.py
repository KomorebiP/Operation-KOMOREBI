#!/usr/bin/env python3
"""Rebuild the standalone v0.7.0 manuscript from its preserved v0.6.0 base."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / 'previous/Komorebi_Seeded_Two_Axis_Calculus_v0.6.0.tex').read_text()

def replace_once(old: str, new: str) -> None:
    global s
    if s.count(old) != 1:
        raise RuntimeError(f'Expected one occurrence, got {s.count(old)}: {old[:100]!r}')
    s = s.replace(old, new, 1)

replace_once('pdftitle={Komorebi Seeded Two-Axis Calculus v0.6.0}',
             'pdftitle={Komorebi Seeded Two-Axis Calculus v0.7.0}')
replace_once('pdfsubject={Audited formalization, residual histories, and invariant obstruction quotients}',
             'pdfsubject={Semantic exchange diagrams, excisive reconstruction, and arithmetic interaction kernels}')
replace_once(r'\normalsize Working Formalization v0.6.0', r'\normalsize Working Formalization v0.7.0')
start, end = s.index(r'\begin{abstract}'), s.index(r'\end{abstract}') + len(r'\end{abstract}')
s = s[:start] + r'''\begin{abstract}
This manuscript develops a seed-generated calculus of transformations within a resolution, coarsening between resolutions, and the residuals of their exchange maps. Its categorical core uses indexed categories, coherent event diagrams, stable cofibers, and constructor-compatible Verdier quotients. It retains the distinction between a normalization endpoint, its comparison map, and the history-sensitive filtration of its residual.

Version 0.7.0 constructs semantic event diagrams for strict chain-natural realizations of the typed pure exchange grammar. A second cofiber measures whether one independent exchange changes the residual of another. Vanishing of these interaction residuals is equivalent to excision and context-independent event residuals. Reduced excisive diagrams on the ideal lattice of a finite event poset are proved equivalent to diagrams on that poset itself. Thus the full residual diagram is reconstructed from principal ideals while retaining dependency and extension data. An invariant Verdier quotient universally enforces this excision condition.

An integral model makes the construction explicit. Scalar exchanges produce Koszul interaction complexes, whose cohomology is computed by the gcd of their labels. Their excisive kernel is classified by shared prime support and has a nonzero exact localization detector. A finite signature certifies arbitrarily long finite scalar event diagrams. A further criterion for tensor cubes of integer matrices distinguishes finite-prime torsion kernels from complete quotient collapse. Written proofs, counterexamples, and exact finite regression tests accompany the constructions. No Lean certification, new set-theoretic axiom, historical novelty, arithmetic globalization, or Langlands reciprocity theorem is claimed.
\end{abstract}''' + s[end:]

replace_once(r'\section{Obstruction theory}',
             (ROOT / 'proofs/semantic_and_excision.tex').read_text() + '\n\n' + r'\section{Obstruction theory}')
replace_once(r'\section{Local-to-global reconstruction}',
             (ROOT / 'proofs/excisive_quotient_and_arithmetic.tex').read_text() + '\n\n' + r'\section{Local-to-global reconstruction}')
replace_once('K27 & Ideal-indexed residual diagram & Proved for a coherent event diagram in \\cref{thm:ideal-residual}.\\\\',
             'K27 & Ideal-indexed residual diagram & Proved for coherent input; K32 constructs strict chain-natural instances.\\\\')
old = r'K31 & Noncollapse certificate & Exact equivariant detector criterion, \cref{prop:noncollapse}.\\'
new = old + '\n' + r'''K32 & Strict semantic event realization & Proved for typed pure swaps and strict chain-natural cells, \cref{thm:strict-event-realization}.\\
K33 & Interaction residual and excision & Total-cofiber criterion, \cref{thm:interaction-cofiber}.\\
K34 & Context-independent event residuals & Equivalent to vanishing square interactions, \cref{thm:event-context-invariance}.\\
K35 & Principal-ideal reconstruction & Reduced excisive diagrams classified by diagrams on $P$, \cref{thm:principal-reconstruction}.\\
K36 & Universal excisive quotient & Constructor-compatible minimal thick kernel, \cref{thm:excisive-quotient}.\\
K37 & Tensor-cube residual formula & Proved by finite-colimit interchange and exact tensor, \cref{thm:tensor-cube}.\\
K38 & Integral gcd interaction formula & Explicit Koszul change of basis and cohomology, \cref{thm:integral-gcd}.\\
K39 & Prime-overlap kernel & Exact kernel and noncollapse for positive scalar labels, \cref{thm:prime-overlap-quotient}.\\
K40 & Finite-signature arithmetic certificate & All finite event diagrams in the stated scalar grammar, \cref{cor:finite-signature}.\\
K41 & Integral matrix collapse criterion & Verified Smith data classify free collapse versus torsion support, \cref{thm:matrix-collapse}.\\'''
replace_once(old, new)
start = s.index(r'\section{Immediate next formal steps}')
end = s.index(r'\section{Brainstorm: stronger directions}', start)
s = s[:start] + r'''\section{Immediate next formal steps}

The general ordered-filtration independence target remains refuted. The concrete strict semantic and integral-kernel obligations now have positive solutions, but they do not close arithmetic globalization.

\begin{enumerate}
\item \textbf{Beyond strict pure exchange.} Extend K32 to a specified non-strict enhanced realization or a rewrite signature with additional critical overlaps. Identify the missing coherent cells explicitly rather than assume that homotopy-category diamonds supply them.
\item \textbf{A nontrivial resolution tower.} Replace identity coarsenings in the scalar model by actual arithmetic restriction or truncation functors. Compute the resulting interaction objects and test whether their invariant kernel preserves the information required by the application.
\item \textbf{Arithmetic existence.} For K15 and K17, define an actual globalization defect and prove that its vanishing is equivalent to the desired existence statement. The event-poset reconstruction theorem reconstructs a diagram, not an automorphic object.
\item \textbf{Broader coefficient rings.} Determine which parts of the prime-support kernel and matrix criterion persist over a specified Dedekind ring or a higher-dimensional ring. A replacement for the integral Smith decomposition must be proved, not silently imported.
\item \textbf{Lean core.} Formalize the finite event-poset correspondence, strict naturality argument, closure statements, and integral certificate checks. This manuscript still has no Lean proof package.
\item \textbf{Beyond stability.} Develop another precisely typed nonadditive obstruction example beyond torsor sections. Do not identify a nonabelian obstruction set with a cofiber object without a comparison theorem.
\end{enumerate}

''' + s[end:]

# Extend, rather than overwrite, the current concluding synthesis.
needle = 'These results sharpen the proposed calculus rather than establish a new foundation or a reciprocity theorem.'
replace_once(needle, r'''The next layer is now explicit. Strict chain-natural cells construct semantic exchange diagrams. Their second cofibers measure excision, and vanishing of those interaction objects makes event residuals independent of unrelated prior events. Principal-ideal reconstruction retains exactly the poset diagram needed to assemble the whole residual history. In the integral models, common prime support identifies what must be removed, while free cofiber components identify a genuine collapse risk. These are concrete semantic and arithmetic results, not a conclusion drawn solely from the breadth of the vocabulary.

''' + needle)

replace_once(r'\end{thebibliography}', r'''\bibitem{StacksCones}
The Stacks Project Authors,
\emph{Cones and termwise split sequences}, Section 13.9, Tag 014D,
Definition 13.9.1 and Lemma 13.9.2, checked 26 September 2026.
\url{https://stacks.math.columbia.edu/tag/014D}.

\bibitem{StacksKoszul}
The Stacks Project Authors,
\emph{The Koszul complex}, Section 15.29, Tag 0621,
Definitions 15.29.1--2 and Lemmas 15.29.4, 15.29.7--8, 15.29.12,
checked 26 September 2026.
The cited section uses homological grading. This manuscript puts the exterior
$k$-th term in cohomological degree $-k$ and states all differentials explicitly.
\url{https://stacks.math.columbia.edu/tag/0621}.
\end{thebibliography}''')

replace_once(r'\section{Audit and verification record for v0.6.0}\label{app:audit}',
             r'\section{Preserved audit and verification record for v0.6.0}\label{app:audit}' + '\n\n' +
             'This section preserves the preceding release\'s audit. The present release\'s work is recorded in \\cref{app:audit-v070}.')

new_audit = r'''\section{Audit and verification record for v0.7.0}\label{app:audit-v070}

\subsection{Scope, proof status, and provenance}
The source base is the supplied v0.6.0 manuscript and its complete package. This release preserves that manuscript, integrates new proof blocks, and updates the abstract, theorem ledger, and next obligations. It does not claim a fresh independent audit of every retained earlier theorem. The new proofs received an authoring-session self-review. No independent referee review or Lean compilation was performed.

The three executed routes were strict semantic realization, interaction/excision reconstruction, and integral quotient classification. They produced K32--K41 under their written hypotheses. The arithmetic test bed uses perfect complexes over $\mathbb Z$ and explicit finite integer data. It does not discharge a Langlands-facing existence hypothesis.

\subsection{Adversarial boundaries}
\begin{enumerate}
\item Strict naturality supplies the event diagram only for the specified pure grammar. Weak cells and additional rewrite relations retain separate coherence obligations.
\item A square's commutativity is not its excision. The second cofiber vanishes precisely for a homotopy pushout, not for every commuting square.
\item Context-independent event residuals do not identify ordered filtrations. Nor do they split extensions along dependent events: the $\mathbb Z/p^2$ chain is an explicit counterexample.
\item The total normalization residual $C(N)$ and a cube's total cofiber $K(n_1,\ldots,n_m)$ are different objects. The $(6,10,15)$ example refutes an inference from highest interaction vanishing to all lower interactions vanishing.
\item The integral noncollapse theorem uses positive scalar labels. Two zero labels give an interaction with a free unit summand and collapse the entire quotient. The matrix criterion identifies the analogous free-cofiber failure.
\item Equality of the kernel with that of localization is proved. No unproved equivalence of complete quotient categories or idempotent completions is substituted for it.
\end{enumerate}

\subsection{Exact finite checks}
Both regression scripts ran successfully on Python 3.13.5. They use exact integer identities and finite-field elimination, with no random sampling or numerical tolerance. The inherited check was rerun with every two-sort word through length 10: 2,047 initial words, 82,499 states, and 168,454 edges. Its constructor and filtration counterexamples also passed.

The new check covers the following explicitly bounded populations.
\begin{center}
\begin{tabular}{p{0.72\textwidth}r}
\toprule
Check population & Count\\
\midrule
Positive label vectors, arity 1--4, entries 1--6 & 1,554\\
Integral exterior-power chain-map identities & 5,910\\
Integral differential-square identities & 4,356\\
Cohomology dimensions over $\mathbb F_2,\mathbb F_3,\mathbb F_5,\mathbb F_7$ & 29,856\\
Initial scalar two-sort words through length 8 & 511\\
Ideal states in those scalar diagrams & 6,917\\
Cover arrows and eligible event contexts & 10,660\\
Elementary independent-event squares & 4,931\\
Explicit localized context-map inverses & 5,019\\
Ideal-pair combinatorial excision checks, word length at most 6 & 5,289\\
Ordered pairs from an explicit 11-matrix test family & 121\\
Matrix-pair cohomology dimensions over five finite fields & 1,815\\
\bottomrule
\end{tabular}
\end{center}

The matrix family includes identity, zero, rank-deficient, triangular, and torsion examples. Its 121 pairs are exhaustive for that listed family, not for all integer matrices. Nine pairs have two free cone components. Additional signed/zero-vector checks, the excluded all-zero pair, and the named $(6,10)$, $(6,10,15)$, and nonsplit prime-chain examples are recorded separately. No primary case within the stated bounds was skipped.

The integral normal-form checks verify unimodular exterior-power chain isomorphisms. Finite-field ranks provide a distinct check on signs and degree dimensions. These are reproducible implementation checks. They neither instantiate every stable category nor replace the written universal proofs.

\subsection{Sources and remaining review}
The exact source check used Stacks Tags 014D, 0621, and 05RA, and Drew's arXiv:1511.08287v1, Definition 1.1 and Theorem 1.3. The source record separates the homological Koszul convention from the cohomological convention used here. Direct finite-colimit, lattice, and integer arguments are supplied for the new deductions. This was not a comprehensive novelty search. The companion audit contains the dependency map, script hashes, source record, build logs, and visual-review record.

Independent mathematical review remains outstanding. K15, K17, K18, arbitrary higher-coherent exchange signatures, and the nonadditive universal construction remain open within this project.

\clearpage
'''
replace_once(r'\section{Version ledger}', new_audit + r'\section{Version ledger}')
replace_once(r'\item[v0.6.0] Audits size',
             r'''\item[v0.7.0] Constructs strict chain-natural event diagrams. Defines interaction residuals and proves the total-cofiber and context-independence criteria. Proves principal-ideal reconstruction for reduced excisive event diagrams. Constructs the universal constructor-compatible excisive quotient. Gives tensor-cube, integral gcd, prime-overlap kernel, finite-signature, and integral matrix collapse theorems. Adds explicit nonsplitting, higher/lower interaction, and zero-label collapse boundaries, together with exact finite regression and a preserved full v0.6.0 package. Written proofs and self-review only.
\item[v0.6.0] Audits size''')

# Compact only the version history, avoiding an orphaned final paragraph.
replace_once(r'\begin{description}[leftmargin=8em,style=nextline]',
             r'\begingroup\small\raggedright' + '\n' + r'\begin{description}[leftmargin=8em,style=nextline]')
replace_once(r'\end{description}' + '\n\n' + r'\end{document}',
             r'\end{description}' + '\n' + r'\endgroup' + '\n\n' + r'\end{document}')

(ROOT / 'Komorebi_Seeded_Two_Axis_Calculus_v0.7.0.tex').write_text(s)
print(f'Integrated {len(s.splitlines())} lines, {len(s.encode())} bytes.')
