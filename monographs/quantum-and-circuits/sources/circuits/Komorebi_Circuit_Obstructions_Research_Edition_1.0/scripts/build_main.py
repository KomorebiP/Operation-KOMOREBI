from pathlib import Path
import re, hashlib

ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'historical_companion/Komorebi_Theorem_Companion_Source/theorems.tex'
s=old.read_text()
def replace(a,b):
    global s
    if a not in s: raise ValueError('Missing source anchor: '+a[:90])
    s=s.replace(a,b)

replace('Source v1.0.0\\enspace /\\enspace Document edition 1','Research edition 1.0\\enspace /\\enspace Source v1.2.0')
replace('THEOREM REFERENCE','MAIN PAPER')
replace(r'\usepackage{newtxtext,newtxmath}',r'\usepackage{lmodern,mathpazo,amssymb}')
replace(r'\usepackage{booktabs,longtable,tabularx,array,multirow}',r'\usepackage{booktabs,longtable,tabularx,array,multirow,ragged2e}')
replace('THEOREMS, PROOFS, AND VERIFICATION','RESTORATION, COVERS, AND PROJECTION')
replace('Theorem companion to the closed v1.0.0 research release; written proofs, not Lean verification','Consolidated written proofs and scoped Lean evidence from source release v1.2.0')
front=r'''
\hypersetup{pageanchor=false}
\begin{titlepage}\thispagestyle{empty}
{\sffamily\small\bfseries\color{accent}OPERATION KOMOREBI\par}
\vspace{0.8in}
{\sffamily\bfseries\color{ink}\fontsize{32}{36}\selectfont Circuit Obstructions\par}
\vspace{0.25in}
{\sffamily\fontsize{22}{27}\selectfont Restoration, Complete Covers,\\and the Limits of Exact Projection\par}
\vspace{0.35in}
{\large Komorebi P.\par}
\vspace{0.15in}
{\sffamily\small Main paper\quad\textbullet\quad Research edition 1.0\\7 October 2026\par}
\vspace{0.45in}
{\color{accent}\rule{0.75\textwidth}{1.2pt}\par}
\vfill
\begin{minipage}{0.96\textwidth}\small
A self-contained treatment of the eight maintained claim groups, with full written proofs, the later degree-with-sharing formal development, exact calibration families, and explicit counterexamples. The accompanying visual and Lean guides use the same source baseline.

\textbf{Formal frontier.} The archived Lean Block 02 covers the cut theorem, the classical register-degree invariant, and the numerical complete-cover bound. The dual certificates and later claim groups retain written-proof status. Fresh exact computations are recorded separately from the archived kernel checks.
\end{minipage}
\end{titlepage}
\pagenumbering{roman}\hypersetup{pageanchor=true}
\chapter*{Abstract and reading contract}
\addcontentsline{toc}{chapter}{Abstract and reading contract}
An arbitrary cut in a classical reversible circuit with restored inputs and workspace yields a complete cover of the accepting set by safe coordinate discrepancies. Tracking products of current registers preserves shared computation and gives an algebraic degree bound of $t+r$ after $t$ Toffoli gates for a product of $r$ registers. Together with a balanced cut and a zero-Toffoli affine-output implementation, this yields
\[
\deg f\le T+1,\qquad 2\beta^*(f)\le T+3.
\]
Here $\beta^*$ optimizes the least degree needed for complete safe coverage over all affine changes of the output. An exact evaluation-span dual supplies finite obstructions to low-degree detection. An unbalanced disjunction separates one-packet immunity from complete coverage, while matching constructions calibrate every function through three inputs.

A second family shows that extracting a homogeneous quadratic component can raise nonlinear cost and destroy support safety. Its separation is exponential in a structural parameter but linear in the actual input length. Orthogonal witness idempotents impose an exponential dimension requirement on a fixed faithful linear multiplicative summary. A weighted witness polynomial avoids cancellation, but computing its trace remains a separate operation; shared variables provide explicit failures of a context-free multiplicative compiler.

All general claims are proved under the stated models. This edition consolidates their mathematical content rather than enlarging the fixed scope to unrestricted circuit hardness. The results establish neither a superpolynomial general circuit lower bound nor a polynomial-time satisfiability evaluator.

\begin{scopebox}{One source baseline, three complementary documents}
\textbf{Main paper:} definitions, theorems, proofs, calibration families, and limitations.\\
\textbf{Visual guide:} exact finite examples and Python-generated figures.\\
\textbf{Lean guide:} actual formal definitions, proof structure, complete 115-declaration register, and reproducibility instructions.
\end{scopebox}

\chapter*{Edition and evidence status}
\addcontentsline{toc}{chapter}{Edition and evidence status}
The mathematical baseline is \emph{Komorebi Circuit Obstructions}, local source release v1.2.0, dated 21 September 2026. This research edition incorporates the later Lean Block 02 into the original theorem companion while preserving all original source archives. The controlling register remains C01--C08. Numbered supporting statements are not a count of independent discoveries.

\begin{tabularx}{\textwidth}{@{}p{1.5in}X@{}}\toprule
Baseline & \texttt{komorebi-circuit-obstructions-v1.2.0}\\
Source commit & \nolinkurl{9e6688e32248926b73950d0560722799b6195ad7}\\
Current edition & 1.0, 7 October 2026\\
Formal source & 115 theorem declarations in eight modules; 40 inherited, 75 added in Block 02\\
Author & Komorebi P., publication pseudonym\\\bottomrule
\end{tabularx}

\textbf{Archived formal checks, 21 September.} The source release records a strict fresh-source build, axiom audit, eight module replays, and rejection of eight false controls with Lean 4.34.0-rc2 and bundled Std. The allowed logical dependencies are \texttt{propext}, \texttt{Classical.choice}, and \texttt{Quot.sound}. No Mathlib dependency is needed.

\textbf{Fresh exact checks, 7 October.} The complete \texttt{--all} command passed: quick controls, rebuilt one-to-four-input profiles, complete-cover checks, projection checks, witness fingerprints, Block 02 degree checks, and the preserved historical runner. The source seal also passed for 321 sealed source files and 27 sealed evidence files. These counts describe different inventories and are not added together as a theorem or file census.

\textbf{Fresh Lean attempt, 7 October.} The verifier stopped because the \texttt{lean} executable is absent. No proof was compiled in this edition's environment. Its saved failure is an environment limitation; the archived formal results remain attached to their exact source revision. The missing compiler is not reported as a new formal pass.

\textbf{Review.} Fresh model-assisted adversarial reviews reconstructed the written arguments and checked selected examples. They share potential model errors and do not constitute independent human review. The review reports retain the discovered boundary and notation corrections. Publication completion does not promote C02's dual or C03--C08 to Lean proofs.

This work was developed with AI assistance. No legal name, affiliation, DOI, public repository destination, or new distribution licence is asserted. The supplied rights record is preserved. This edition is a local publication set.

\textbf{Evidence vocabulary.} \emph{Written} means a supplied argument under explicit hypotheses. \emph{Formal} identifies the exact archived Lean declarations. \emph{Finite} means an executed bounded assertion. \emph{Counterexample} identifies a failed implication. \emph{Conditional} identifies a conclusion with an unimplemented premise.
\tableofcontents\clearpage\pagenumbering{arabic}
'''
start=s.index('\\begin{titlepage}')
stop=s.index('\\chapter{Scope, notation, and computational model}')
s=s[:start]+front+s[stop:]

addition=r'''
\section{A degree invariant that retains sharing}
The preceding Boolean substitution proof applies to general XOR--AND straight-line computations. The later formal development proves the classical reversible specialization directly on the evolving register state. This route makes the resource accounting visible without unfolding reused registers into duplicated formulas.

\begin{theorem}[Register-product degree invariant]\label{thm:register-products}
Let $s_i(x)$ be the contents of a finite register after $t$ Toffoli gates, with arbitrary intervening NOT and CNOT gates. Initial register contents are affine functions of $x$. For every finite list $L$ of $r$ register indices, including repeated indices,
\[
 \deg\left(\prod_{i\in L}s_i(x)\right)\le t+r.
\]
The zero-function convention is as above. In the formal source the conclusion is the concrete representation certificate \texttt{DegreeLE}.
\end{theorem}
\begin{proof}
Initially a product of $r$ affine functions has degree at most $r$. Suppose a gate toggles register $u$ by a product of $q$ controls, with $q=0,1,2$ for NOT, CNOT, and Toffoli respectively. If $u$ does not occur in $L$, the product is unchanged. If it occurs, Boolean idempotence removes all its repetitions. Let $R$ be the remaining list, so $|R|+1\le r$. The updated product is
\[
 s_u\prod_{i\in R}s_i+
 \left(\prod_{j\in\mathrm{controls}}s_j\right)\prod_{i\in R}s_i.
\]
By the old invariant, these two summands have degrees at most $t+1+|R|$ and $t+q+|R|$. The latter is at most $t+r+\max\{q-1,0\}$. NOT and CNOT therefore consume no degree budget; a Toffoli consumes at most one. Induction along the actual gate list proves the claim. The empty list is the constant-one product and is also covered.
\end{proof}
For $r=1$ this recovers the coordinate bound. The initial target can be fixed to either boundary bit while the inputs vary. Temporary input disturbance, dirty intermediate workspace, output controls, and repeated use of earlier products are all allowed. The formal locators are \texttt{workspaceDegree\_run} and \texttt{canonical\_run\_coordinate\_degree}.

\begin{scopebox}{The representation is part of the theorem}
\texttt{DegreeLE(d,f)} is tied by proved equivalences to an explicit finite XOR of monomials with length at most $d$. It is not an assumed degree oracle. Canonical algebraic-normal-form extraction and a separate generic XOR--AND simulation compiler are outside this formal block.
\end{scopebox}
'''
replace('\\chapter{Exact cut comparison and safe discrepancies}',addition+'\n\\chapter{Exact cut comparison and safe discrepancies}')
replace('Consequently,\n\\[\n \\alpha_1(f)=\\text{minimum minterm size}', 'Consequently, for nonzero $f$,\n\\[\n \\alpha_1(f)=\\text{minimum minterm size}')
replace('Such a scalar summary necessarily loses every singleton witness other than $v_0$.','For $m\\ge1$, such a scalar summary loses at least one singleton witness other than $v_0$. At $m=0$, the unique empty witness is preserved by the identity map.')
replace('The preceding one-packet bound, even optimized over affine target adjustments, gives only $n-1$ for this family.',r'The preceding combined bound $\max\{0,\deg F_k-1,2\max_{\ell}\alpha_1(F_k+\ell)-3\}$ gives $n-1$ for this family; its immunity-only term is the constant $3$.')
replace('This reference expands their proofs and supporting facts into 29 numbered entries. Those entries are not 29 independent discoveries, and none is a Lean declaration. The machine-readable \\pathref{theorem-map.json} accompanies the document source.','This reference expands the maintained arguments into individually numbered statements and adds the later register-product invariant. Prose statement counts and formal lemma counts have different meanings. The Lean guide lists all 115 formal declarations; the original theorem companion and its historical theorem map remain preserved.')
replace('\\resultrow{lem:degree}{Degree per multiplication}{Base}{}','\\resultrow{lem:degree}{Degree per multiplication}{Base}{}\n\\resultrow{thm:register-products}{Register-product degree invariant}{Base / formal}{}')

verification=r'''
\section{Fresh checks for this edition}
The original v1.2.0 ZIP and repository bundle were recovered, and the ZIP's digest matches the supplied release digest. Original source files and frozen scientific results remain unchanged. The integrity checker passed with 321 sealed source files and 27 sealed evidence files.

The fresh command \texttt{python scripts/verify.py --all} completed with status PASS. Every requested group ran, including the C++ profiles, the maintained exact science checks, the additional degree controls, and the original historical runner. The run manifest identifies commands, input and output hashes, software versions, and elapsed times. Its source-relative path is
\pathref{build/verification/20261007T131040268104Z-all/manifest.json}.

The archived formal release records 115 checked theorem declarations, eight replayed modules and eight rejected false controls. A fresh invocation in this edition failed before proof checking because \texttt{lean} is unavailable. That attempt is retained as a failed environment check, with no fresh theorem or axiom count. The exact formal source, historical successful evidence, and reproduction commands are included in the complete set.

The fresh proof reviews additionally compare primal and dual safe-detection criteria over every truth table at $n=0,1,2,3$ and reconstruct selected calibration, projection and fingerprint controls. Their scripts and exact scopes are retained in the review directory. Counts can overlap the baseline and are not summed as independent mathematical evidence.

Document checks cover multi-pass LaTeX builds, resolved references, text extraction, font embedding, page bounds, and visual rendering. The final validation report identifies the actual outcomes. PDF compilation is separate from proof compilation.

\section{Baseline domains reproduced by the full run}
The exact mathematical outputs below were compared with the preserved baseline. The historical runner also reproduced its seven scientific output records. These finite ranges remain part of the evidence even where a universal written theorem accompanies them.
'''
a=s.index('\\section{What was checked for this PDF edition}')
b=s.index('\\small\n\\begin{longtable}',a)
s=s[:a]+verification+s[b:]
replace('From the root of the supplied v1.0.0 repository:','From the root of the supplied v1.2.0 repository:')
replace(r'Replace \texttt{RUN\_ID} with the actual emitted directory. The immutable source and baseline evidence are not overwritten.','')
replace('Each run writes a new directory under \\pathref{build/verification/}. A run manifest can be validated with','Each run writes a new directory under \\pathref{build/verification/}. Validate a run manifest using its actual emitted RUN\\_ID in')
a=s.index('\\section{Reproduction commands}')
b=s.index('\\chapter{Boundaries, corrections, and source provenance}',a)
s=s[:a]+r'''
\section{Reproduction commands}
From the supplied v1.2.0 source root, run the source seal and complete scientific replay. Substitute the actual emitted RUN\_ID when checking a run manifest:
\begin{verbatim}
python scripts/check_integrity.py
python scripts/verify.py --all
python scripts/validate_manifest.py \
  build/verification/RUN_ID/manifest.json --root .
\end{verbatim}
The scientific checks require Python 3.10+ and a C++17 compiler. The compiler is selected through \texttt{CXX}, with \texttt{g++} as the default. There is no external solver, hidden dataset, package installation, or network dependency for these checks. Historical replay is documented for Linux/WSL; native Windows full replay is not newly established here.

Assertions are part of the checker, so optimized Python is rejected. Missing results, command failures, timeouts, modified source inputs, and baseline mismatches make a requested run fail. Each run creates a new directory under \pathref{build/verification/}; source and baseline evidence remain unchanged. Quick, full, and history modes are documented individually in the source reproduction guide.

Formal replay is separate. It requires the pinned Lean 4.34.0-rc2 toolchain and runs through \texttt{scripts/verify\_lean.py}. The Lean companion gives the actual commands, permitted axioms, false controls, and archived outcome. This edition's missing compiler is retained as a failed attempt, not a formal pass.

''' +s[b:]
replace('There is no resolution of $P$ versus $NP$, no superpolynomial unrestricted Boolean-circuit lower bound, no polynomial-time weighted-trace evaluator, no quantum-circuit lower bound, no Lean kernel check, no independent review, and no comprehensive novelty or best-known-bound audit.','There is no resolution of $P$ versus $NP$, no superpolynomial unrestricted Boolean-circuit lower bound, no polynomial-time weighted-trace evaluator, and no quantum-circuit lower bound. Formal evidence is scoped to the named archived Block 02 declarations. No fresh kernel pass, independent human review, comprehensive novelty search, or best-known-bound audit is claimed.')

provenance=r'''
\section{Source identity and editorial treatment}
The original v1.2.0 ZIP, repository bundle, delivery report, earlier theorem companion and formal guide are included unchanged. Their identity is preserved separately from this edition's new manuscripts and figures. The source ZIP SHA-256 is
\begin{quote}\footnotesize\nolinkurl{88628c8274660bd20e11fec83249fdc04960403b9d64d1e5068a476b8c025936}\end{quote}

This edition corrects the old front matter's formal-status description, incorporates the direct register-product invariant, restricts the monotone minterm formulas to nonzero functions, and states the $m=0$ exception for scalar-summary loss. It also preserves the explicit efficient-field hypothesis in the randomized implication and the own-variable-set convention in disjoint factorization. No source claim group is enlarged, and no original proof file is overwritten.

The publication package carries the original source and evidence plus this edition's reviews, fresh computations, figure scripts, document sources and a full file manifest. The original rights record is retained. No new licence or public hosting status is assigned by this edition.

\section{Rebuilding the publication set}
From the publication-set root, run
\begin{verbatim}
python scripts/make_figures.py
python scripts/build_main.py
python scripts/build_documents.py
python scripts/verify_publication.py
\end{verbatim}
The traditional source is generated from the preserved historical companion plus documented edition updates. Repeated LaTeX passes resolve the bibliography and result index. Font programs are embedded in the PDFs by the TeX build; standalone font files are not distributed. Reproduction of document layout and reproduction of mathematical checks are separate commands.
'''
a=s.index('\\section{Source identity and editorial treatment}')
b=s.index('\\clearpage\n\\begin{thebibliography}',a)
s=s[:a]+provenance+s[b:]
s=s.replace('source release v1.0.0','source release v1.2.0')
s=s.replace('\\emph{Release audit: 1.0.0}', '\\emph{Release audit: 1.2.0}')
s=s.replace('\\pathref{evidence/closure/RELEASE_AUDIT.md}, September 21, 2026. Recorded release verification, provenance, failures, and publication status.', '\\pathref{evidence/lean-block02/RELEASE_AUDIT.md}, September 21, 2026. Scoped archived formal verification. This edition also supplies fresh computational and document validation records.')
s=s.replace('Magnus Gausdal Find and Joan Boyar.', 'Joan Boyar and Magnus Gausdal Find.')
s=s.replace('pdftitle={Komorebi Circuit Obstructions: Theorems, Proofs, and Verification}', 'pdftitle={Komorebi Circuit Obstructions: Main Paper}')
s=re.sub(r'(?<![A-Za-z])p\{([0-9.]+in)\}',lambda m:r'>{\RaggedRight\arraybackslash}p{'+m.group(1)+'}',s)
(ROOT/'manuscripts/main.tex').write_text(s)
print('main.tex generated',len(s),'characters')
