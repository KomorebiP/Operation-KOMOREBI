#!/usr/bin/env python3
"""Assemble a reader-facing Lean guide from literal source windows."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
C=R/'checked_checkpoint'
inventory=json.loads((R/'Lean_Concordance.json').read_text())
parts=[]
def prose(s): parts.append(s.strip()+'\n\n')
def excerpt(file,a,b):
    lines=(C/file).read_text().splitlines()
    short=(b-a+1)<=18
    need=(b-a+6) if short else 6
    parts.append(r'\Needspace{'+str(need)+r'\baselineskip}'+'\n')
    prose(r'\noindent\textbf{Literal source.} '+r'\texttt{\detokenize{'+file+r'}}'+f', physical lines {a}--{b}.')
    options=r'breaklines=true,breakanywhere=true,fontsize=\footnotesize'+(',samepage=true' if short else '')
    parts.append(r'\begin{Verbatim}['+options+']'+'\n'+'\n'.join(lines[a-1:b])+'\n'+r'\end{Verbatim}'+'\n\n')
prose(r'''
\section{What this guide certifies}
The completed fixed example is a bridge between exact arithmetic and ordinary
complex linear algebra. It certifies a twelve-dimensional Fourier matrix, a
Ramanujan projector, two normalized states with the same initial probabilities,
and their opposite outcomes after a basis change. This guide maps those claims to
actual Lean declarations rather than treating numerical agreement as a proof.

The authoritative formal checkpoint is the later five-module version of the
September 21, 2026 development. It contains \textbf{96 named mathematical
theorems}. Their source and archived execution records are supplied unchanged.
The present release has independently reconciled the source and log hashes and
the complete theorem inventory. A new compiler run was blocked by a runtime
transfer error. The distinction between an archived checked proof and a fresh
replay is retained throughout.

\begin{center}
\begin{tabular}{lr}
\toprule
Production module & Named theorems\\
\midrule
\texttt{QuantumArithmeticBridge} & 22\\
\texttt{FiniteFourier} & 17\\
\texttt{SemanticBridge} & 30\\
\texttt{Conventions} & 17\\
\texttt{Publication} & 10\\
\midrule
Total & 96\\
\bottomrule
\end{tabular}
\end{center}

These counts include supporting lemmas. They count named source declarations,
not new discoveries, compiler jobs, or declarations generated internally by Lean.
The namespace is \texttt{Komorebi.QuantumArithmetic} throughout.

\section{The typed mathematical target}
The complex matrices act on vectors indexed by \(\operatorname{Fin}(12)\).
The Fourier convention is
\[
 F_{nk}=\frac{1}{\sqrt{12}}\exp\!\left(\frac{2\pi i nk}{12}\right),
 \qquad n,k\in\{0,\ldots,11\}.
\]
The adjoint \(F^*\) therefore carries the negative exponential sign. The
selector \(D\) is diagonal with value one precisely at the residues
\(U=\{1,5,7,11\}\). The transported operator is \(P=FDF^*\).

Write
\[
 c=(4,0,2,0,-2,0,-4,0,-2,0,2,0),\qquad
 \psi=\frac{c}{\sqrt{48}},\qquad \chi=\frac{|c|}{\sqrt{48}}.
\]
Both vectors have norm one. Their initial probability histograms are identical,
but their inner product is zero. The vector \(u\) has entry \(1/2\) on \(U\)
and zero elsewhere. Lean proves the actual complex identities \(Fu=\psi\) and
\(F^*\psi=u\), as well as transformed coprime probability one for \(\psi\)
and zero for \(\chi\).

The statements are finite and exact. No parameterized arbitrary-modulus theorem,
general circuit construction, physical phase-removal process, or quantum speedup
is included in these formal claims.

\section{Revision reconciliation}
Two retrieved archives carry version \texttt{0.2.0}, but they do not have the same
active source. The earlier four-module checkpoint has 59 mathematical theorems
and four separately checked refutation controls. The later five-module checkpoint
has 96 mathematical theorems and three rejected control files. Its proof receipt
is the later \texttt{verification/final/REPORT.json}.

The original 22 finite-table statements are retained inside both checkpoints.
They are not counted a second time. Likewise, \(59+96\) is not a meaningful
theorem total: these are overlapping revisions of one formal development.

The earlier proof boundary disclosed that explicit projector transport and
normalized-state matrix actions had not yet been supplied. The later source
supplies both, connects the Fourier matrix to the usual complex exponential, and
proves a histogram nonreconstruction theorem. The earlier boundary remains a
record of its own revision, rather than a gap list for the current publication.

The entire later checkpoint is preserved under \texttt{lean/checked\_checkpoint}.
The source files are not edited to match this guide.

\section{Architecture of the proof}
The proof crosses two representations. First, rational coordinates support exact
finite calculations. Second, a semantics map transfers those calculations to
ordinary complex matrices and vectors.

\begin{center}
\begin{tabular}{p{0.27\linewidth}p{0.64\linewidth}}
\toprule
Layer & Role\\
\midrule
Rational tables & Signal, projector entries, filtering, and energies.\\
Exact coordinates & Algebra in the basis \(1,\sqrt3,i,i\sqrt3\).\\
Finite matrices & All entries indexed by \(\operatorname{Fin}(12)\), with exact finite sums.\\
Complex semantics & Preservation of multiplication, adjoint, matrix action, and squared norm.\\
Conventions & Identification of roots and normalization with standard exponentials and square roots.\\
Publication theorem & Bundling of the actual complex identities and reconstruction obstructions.\\
\bottomrule
\end{tabular}
\end{center}

The active import chain is \texttt{QuantumArithmeticBridge} into
\texttt{FiniteFourier}, then \texttt{SemanticBridge}, then \texttt{Conventions},
then \texttt{Publication}. Supporting Mathlib imports enter at the layer that
uses them. There is no circular theorem dependency.
''')
prose(r'''
\section{The rational signal and its filter}
The first layer uses literal rational lists. The chosen perturbation is
\(r_n=3\cos(\pi n/2)+2\), whose displayed rational entries can be certified
without numerical trigonometric evaluation. Its sum with \(c\) is the test signal.
''')
excerpt('QuantumArithmeticBridge.lean',51,61)
prose(r'''
The cyclic matrix has entry \(c_{(n-m)\bmod12}/12\). The original layer proves
its symmetry, idempotence, preservation of \(c\), rejection of the chosen
perturbation, and exact recovery from the displayed contaminated signal.
The exact energy contract is \(150=48+102\).
''')
excerpt('QuantumArithmeticBridge.lean',92,126)
prose(r'''
The list operations use finite lists, including zero defaults and zip-based dot
products. These facts are therefore claims about the supplied twelve-entry
objects. They should not be silently interpreted as universal matrix theorems
for arbitrary ragged lists. The later \(\operatorname{Fin}(12)\) layer supplies
the typed matrix identities used in the publication.

\section{The exact phase arithmetic}
The structure \texttt{Cyclo12} represents
\[
 (a,b,c,d)\longmapsto a+b\sqrt3+i(c+d\sqrt3),\qquad a,b,c,d\in\mathbb Q.
\]
Its multiplication explicitly incorporates \((\sqrt3)^2=3\) and \(i^2=-1\).
It is a concrete arithmetic representation. The development does not need or
install a global field instance to certify the finite example.
''')
excerpt('QuantumArithmeticBridge.lean',130,141)
excerpt('QuantumArithmeticBridge.lean',155,173)
prose(r'''
The phase \(\zeta=(0,1/2,1/2,0)\) has complex meaning
\(\sqrt3/2+i/2\). Exact finite certificates establish its twelfth power, inverse,
and absence of a smaller positive power below twelve. Later the convention
module identifies it with \(\exp(\pi i/6)\).

The Ramanujan vector is obtained by summing powers of this phase over
\(1,5,7,11\). The negative-sign unnormalized DFT has value 12 at these four
frequencies and zero elsewhere. The absolute-value vector has Fourier support
on the even frequencies instead. These are exact phase calculations over
rational coordinates.

\section{Finite indices and normalized Fourier certificates}
The finite layer uses \texttt{Index := Fin 12}. Its normalized Fourier scale is
represented exactly as \(\sqrt3/6=1/\sqrt{12}\), and its state scale as
\(\sqrt3/12=1/\sqrt{48}\). The use of a finite index type makes every row and
column well defined without list-length side conditions.
''')
excerpt('FiniteFourier.lean',58,93)
prose(r'''
The two Fourier identities above quantify over all \(12\times12\) entries.
Kernel reduction proves these concrete universal statements over a finite type.
The selected-kernel equality and state actions are also complete finite
certificates, rather than floating-point matrix comparisons.

\section{Why the coordinate certificates mean complex identities}
The semantics map is explicitly defined with the positive real square root.
Soundness for addition, multiplication, conjugation, powers, and finite sums
prevents the exact coordinate layer from being a detached calculation with an
unproved interpretation.
''')
excerpt('SemanticBridge.lean',14,56)
prose(r'''
The multiplication proof uses complex extensionality, real polynomial
normalization, and the square-root identity. It proves preservation for arbitrary
coordinates, not merely for the handful of roots that occur in the example.
The power and finite-sum proofs use induction.

Injectivity of this interpretation is not needed to transfer an equality: if
two coordinate expressions are proved equal, applying the interpretation gives
equal complex expressions. No claim of a globally packaged field equivalence is
required by the theorem chain.

\section{Matrix transport and actual unitarity}
The semantics layer proves that coordinate matrix multiplication, adjoint,
identity, and matrix-vector action have their ordinary complex meanings.
The matrices \(F,P,D\) and the normalized states are then defined directly
in that complex representation.
''')
excerpt('SemanticBridge.lean',65,91)
prose(r'''
Consequently, the finite certificates produce actual complex unitarity and
projector transport. The following excerpt contains the full proofs of both
unitary identities, the cross-representation projector identity, and the two
state-action identities.
''')
excerpt('SemanticBridge.lean',93,120)
prose(r'''
This is the key strengthening over the earlier checkpoint. The rational matrix,
the exact coordinate kernel, and the complex matrix \(FDF^*\) are explicitly
connected. State preparation and recovery are equalities of actual complex
vectors. The theorem name \texttt{state\_preparation} describes a matrix identity,
not an efficient hardware preparation algorithm.

\section{The exponential sign and square-root normalization}
The usual Fourier matrix is not left as an informal interpretation. The
convention module proves that the coordinate root equals the positive
exponential root, including the selected square-root branch.
''')
excerpt('Conventions.lean',10,24)
prose(r'''
Its normalization lemmas prove \(\sqrt{12}=2\sqrt3\) and
\(\sqrt{48}=4\sqrt3\), then identify the exact scales with their ordinary
reciprocals. The matrix entry formula and state formula below are therefore
literal equalities in \(\mathbb C\).
''')
excerpt('Conventions.lean',42,54)
excerpt('Conventions.lean',56,65)
excerpt('Conventions.lean',67,82)
prose(r'''
The convention is positive sign for \(F\) and negative sign for \(F^*\). The
earlier unnormalized \texttt{dft12} uses the negative sign. The normalization
and adjoint are the precise link between those notations.

\section{Hermitian projection and phase-sensitive states}
The selector is Hermitian and idempotent. Transport through a unitary matrix
then proves the corresponding facts for \(P\). They are ordinary matrix
identities, not claims that every rational list operation is an orthogonal
projection.
''')
excerpt('Conventions.lean',84,108)
prose(r'''
The vectors \(\psi\) and \(\chi\) are separately defined states. One is the
signed arithmetic amplitude vector and the other its entrywise absolute value.
They have the same squared amplitudes at each initial index but retain different
relative phase. The development neither claims nor requires a universal quantum
operation implementing the nonlinear map \(v\mapsto |v|\).
''')
excerpt('SemanticBridge.lean',145,174)
prose(r'''
The transformed probability statement is exact. The measurement event is the
coprime-frequency subset. After applying \(F^*\), its probability is one for
\(\psi\) and zero for \(\chi\). This basis change reveals information that their
shared initial histogram does not contain.

\section{Two exact information-loss statements}
The formal development isolates distinct obstructions. First, the initial
histogram cannot be inverted on both states by any reconstruction function.
Second, the projector itself is noninjective because it annihilates the nonzero
normalized state \(\chi\).
''')
excerpt('Publication.lean',39,50)
excerpt('Publication.lean',52,57)
excerpt('Publication.lean',59,65)
prose(r'''
The nonreconstruction theorem quantifies over every function from real-valued
histograms to complex-valued vectors. It uses equality of the two histograms and
the incompatible transformed probabilities. This is a mathematical obstruction
to a specified inverse, not a statistical claim about estimating a state from
many measurements in several bases.

The traditional paper also proves that the two states cannot both be recovered
up to an overall phase from this histogram. That strengthening is a prose
corollary of their orthogonality and normalization. It is not separately exported
as a quotient-by-global-phase Lean theorem.

Projection becomes reconstructive when its residual is retained. The next
identity holds for every twelve-dimensional complex vector, including vectors
outside the arithmetic signal subspace.
''')
excerpt('Publication.lean',33,37)
prose(r'''
Its proof is algebraic. The identity \(Pv+(I-P)v=v\) itself does not require
idempotence. Hermitian idempotence supplies the stronger interpretation as
orthogonal retained and discarded components. This separates the reconstruction
identity from the additional geometric structure.

\section{The publication theorem in full}
The final declaration bundles the formal core of the worked example. Every
conjunct is supported by a previously proved declaration rather than by a new
numerical test or an implicit physical assumption.
''')
excerpt('Publication.lean',67,80)
prose(r'''
The bundled theorem has a fixed dimension and explicitly named operators and
states. It establishes the bridge used in the paper. Broader arbitrary-modulus
results remain separate prose theorems, with their own proofs and evidence.

The manuscript's QA18 additionally includes filtering and energy, normalization
of \(u\), the projector actions on both states, and noninjectivity. Those clauses
use separately exported declarations, including
\texttt{projector12\_recovers\_test\_signal}, \texttt{energy\_decomposition},
\texttt{unitState\_normalized}, \texttt{projector\_fixes\_psi},
\texttt{projector\_kills\_chi}, and \texttt{projector\_not\_injective}.
The complete machine concordance lists these supporting results. The manuscript
bundle is not identified with a literal statement that omits its extra clauses.

\section{Manuscript-to-Lean concordance}
The main paper labels its results QA01 through QA20. The table below distinguishes
the exact fixed-example formal coverage from the more general mathematical
development. ``Not formalized here'' is a scope label, not a claim that the prose
result is false.

\small
\begin{longtable}{p{0.08\linewidth}p{0.26\linewidth}p{0.56\linewidth}}
\toprule
Claim & Subject & Formal coverage\\
\midrule
\endhead
QA01 & Primitive root & Exact order 12 and standard exponential root.\\
QA02 & Character orthogonality & Fixed-example content through both exact unitary identities; general theorem not separately exported.\\
QA03 & Fourier theory & Both ordinary complex unitary identities and standard entry formula; general Parseval theorem not separately exported.\\
QA04 & M\"obius formula & General modulus formula not formalized; exact integer table for 12 certified.\\
QA05 & Ramanujan support & Exact signed and unsigned twelve-frequency DFT tables and arithmetic energy 48.\\
QA06 & Divisor projectors & Primitive-order projector at 12 certified; the full divisor family not a general Lean family.\\
QA07 & Projector geometry & Hermitian idempotence, displayed energies, explicit noninjectivity, and all-vector residual reconstruction.\\
QA08 & Residue recombination & No theorem in this checkpoint.\\
QA09 & Polyphase aliasing & No theorem in this checkpoint.\\
QA10 & Arithmetic example & Phase sum connected to the exact rational sample table.\\
QA11 & Exact filtering & Displayed contaminated signal and orthogonal energy decomposition.\\
QA12 & State preparation & Ordinary complex normalized vector actions and recovery.\\
QA13 & Shared histogram & Entrywise probability equality and state orthogonality.\\
QA14 & Phase separation & Actual transformed coprime probabilities 1 versus 0.\\
QA15 & Reconstruction barrier & No vector-valued initial-histogram inverse works on both specified states; the global-phase corollary is prose only.\\
QA16 & Measurement law & Relevant projector algebra and state probabilities; no general conditional-state-update API.\\
QA17 & Arithmetic semantics & Soundness for scalar, matrix, vector, adjoint, and mass operations.\\
QA18 & Central bridge & Publication bundle plus separately exported filter, energy, normalization, projector-action, and noninjectivity results.\\
QA19 & Relative-phase family & Prose extension \(\sin^2(\theta/2)\); not an inherited Lean theorem.\\
QA20 & Dephased probability & Prose density-matrix calculation \(1/3\); not an inherited Lean theorem.\\
\bottomrule
\end{longtable}
\normalsize

The machine concordance includes all theorem statements verbatim, per-theorem
axiom records, source hashes, and exact physical line locators. Its mapping
records formal scope; it does not upgrade general manuscript claims merely
because a nearby finite special case is checked.

\section{Trust boundary and current verification}
The archived run used Lean 4.34.0-rc2, compiler commit
\texttt{\detokenize{6a10ac8c22beadecabdbb0919c2b50214762f91d}}, and Mathlib revision
\texttt{\detokenize{aeb72f1e9981b6d35b426b16dca7759be3e7ba06}}.
It built the five source modules with warnings treated as errors, printed axiom
dependencies for all 96 named theorems, and replayed each module with
\texttt{leanchecker}. The compiler and imported dependency cache were not rebuilt
from their source. Kernel replay uses Lean's own kernel, not a second independent
proof checker.

The axiom union is exactly \texttt{propext}, \texttt{Classical.choice}, and
\texttt{Quot.sound}. This is the standard foundation used by the audited proof
terms, not an axiom-free claim. The active source contains no proof placeholders,
custom axiom declarations, native decision proofs, or unsafe declarations.
Historical failed or native-decision drafts are excluded from the active build.

Current source reconciliation checked all five source hashes and all eleven
archived check-log hashes against the archived report. All sixteen match.
The current inventory contains exactly 96 unique names and 96 archived axiom
records. All line numbers agree with the archived source index.

The present environment had no \texttt{lean}, \texttt{lake}, or
\texttt{leanchecker} on PATH. The exact pinned five-part portable runtime was
resolved from its documented existing files, but three materialization attempts
failed with HTTP status 502. No runtime bytes landed and no compiler process ran.
The current \texttt{FRESH\_LEAN\_STATUS.json} therefore says
\textbf{NOT\_RUN}. This transfer failure is preserved; the release does not claim
a fresh Lean pass.

\section{Controls, failed attempts, and reproducibility}
The latest archive rejected a deliberately false signal sign and a proof using
\texttt{sorry} under warnings as errors. Its false Fourier-mode control also
failed, but the compiler stopped at opaque \texttt{Decidable} reduction. That
failure alone is not a direct mathematical certificate that the proposition is
false. The positive \texttt{ramanujan\_dft\_table} theorem separately establishes
the correct value 12.

The control runner's broad diagnostic expression can match the word ``false''
in a filename. The guide does not interpret that match as a stronger arithmetic
test than the actual log provides. The earlier checkpoint's four explicit
refutation proofs are retained as earlier evidence and are not silently counted
as current production theorems.

The supplied verifier creates a fresh source project, checks dependency revisions,
builds, prints all theorem axiom dependencies, replays all five modules, and runs
the controls. It refuses to overwrite an existing fresh build directory and
treats timeouts as failures. It makes no network requests or installations.
With the pinned runtime restored, the documented command is:
''')
parts.append(r'''\begin{Verbatim}[breaklines=true,fontsize=\footnotesize]
python scripts/verify_lean.py \
  --toolchain /path/to/Komorebi_Portable_Lean_4.34.0-rc2/toolchain \
  --packages /path/to/Komorebi_Portable_Lean_4.34.0-rc2/workspace/.lake/packages \
  --out verification/reproduction_new
\end{Verbatim}
''')
prose(r'''
The runner was exercised under Linux x86-64. It uses POSIX process groups and
filesystem symlinks. Native Windows behavior is not tested. WSL2 with the pinned
Linux runtime is the documented route for a Windows machine.

Full proof source, manifests, archived build and replay logs, the static
concordance builder, and the current failed runtime restoration status are
included. The runtime itself remains an external dependency.

\section{Complete active theorem inventory}
All names in the following table have prefix
\texttt{Komorebi.QuantumArithmetic}. File and physical source line identify the
exact declaration. The full literal statements and axiom lists are also available
in \texttt{Lean\_Concordance.json} and \texttt{Lean\_Concordance.csv}.
''')
for module,count in inventory['module_theorem_counts'].items():
    parts.append(r'\Needspace{10\baselineskip}'+'\n')
    prose(r'\subsection{\texttt{\detokenize{'+module+'}}'+f': {count} theorems'+r'}')
    parts.append(r'\small\begin{longtable}{p{0.79\linewidth}r}'+'\n'+r'\toprule Declaration & Line\\\midrule\endhead'+'\n')
    for row in inventory['theorems']:
        if row['module']==module:
            parts.append(r'\texttt{\detokenize{'+row['basename']+'}} & '+str(row['source_line'])+r'\\'+'\n')
    parts.append(r'\bottomrule\end{longtable}\normalsize'+'\n\n')
prose(r'''
\section{What completion means here}
The fixed twelve-dimensional bridge is formally covered in the preserved later
checkpoint. This guide and machine concordance expose its proof and trust
boundaries.

General-modulus M\"obius and divisor-projector theory, polyphase identities, and a
general measurement API remain outside this Lean package. The traditional paper
supplies separate proofs. Runtime restoration failed, so no fresh replay is
claimed.
''')
(R/'Quantum_Arithmetic_Lean_Guide_Body.tex').write_text(''.join(parts))
print('Wrote guide body:',len(''.join(parts)), 'characters')
