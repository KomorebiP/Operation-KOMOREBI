"""Author: Komorebi P. Generate scope documents only after the fresh fifth-block gate passes."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
rows=json.loads((R/'THEOREM_LEDGER.json').read_text())
report=json.loads((R/'verification/verification_status.json').read_text())
if report['status']!='LEAN_FIFTH_BLOCK_CHECKS_PASS' or not report['all_scoped_results_complete']:
    raise RuntimeError('Fresh passing fifth-block build and audit required')
g=report['gates'];N=g['source']['theorems'];M=g['source']['proof_modules'];D=g['lean']['namespace_declarations']
C=g['source']['complete'];P=g['source']['partial'];U=g['source']['pending']
if (C,P,U)!=(33,0,0):raise RuntimeError('Ledger is not complete')
notes=f'''# Paper VI — fifth checked formalization block

Author: Komorebi P. · 6 September 2026 · v0.5.0

**Both remaining scoped results are complete: memory/self-energy (13.2) and canonical holomorphic naturality (15.1). The ledger now contains 33 complete results, zero partial results and zero pending results.** The three separately stated conjectures remain open.

| Count | Fourth checked block | This release |
|---|---:|---:|
| Explicit Lean theorem declarations | 310 | {N} |
| Proof modules | 42 | {M} |
| Complete manuscript results | 31 | {C} |
| Partial manuscript results | 2 | {P} |
| Namespace declarations audited | 710 | {D} |

The {N-310} additional supporting theorem declarations close two existing manuscript results. Namespace declarations also include definitions and generated auxiliaries. These counts concern Paper VI only.

## Fresh verification

The full root project builds with Lean 4.34.0-rc2, strict implicit-variable settings and warnings treated as errors. All explicit theorem targets and all project namespace declarations pass the real axiom audit; only `propext`, `Classical.choice`, and `Quot.sound` are allowed. Mathlib remains pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; all nine locked dependency revisions and their tracked-source cleanliness are checked. All 54 companion tests and six verifier controls pass again.

The authoritative report is `verification/verification_status.json`, supported by `lean_build.log` and `lean_axiom_audit.log`. It records `lean_kernel_checked: true` and `all_scoped_results_complete: true`. The broader `full_paper_formalized` flag remains false: it does not certify every prose sentence, figure or open conjecture. Prose-to-Lean correspondence is manually reviewed. The existing ordinary real/complex specializations, including complexification, remain disclosed mathematical specializations rather than separately counted Lean constructions.

## 13.2 — arbitrary finite nonnormal memory

`ScalarDecay` proves actual Bochner integrability and convergence to zero of complex exponential-polynomial terms under a negative real-part condition.

`NonnormalMemory` applies the generalized-eigenspace decomposition to left multiplication by the hidden generator on its finite-dimensional complex matrix algebra. The nilpotent tail vanishes, so the actual exponential has a finite component expansion. Nonzero components have eigenvalues in the original algebra spectrum. The stated strict spectral half-plane therefore gives integrability and a zero limit, without a supplied exponential-growth bound or a normality assumption.

The improper-integral fundamental theorem is applied to both derivative identities of the shifted exponential. This derives both inverse equations and identifies the integral with the actual inverse. `MatrixMemory.rectangular_memory_self_energy` then carries the integral through the literal rectangular transfer matrices and proves

`integral exp(-z*t) • (U * exp(t*A) * V) = U * (z*I - A)^(-1) * V`.

The matrix dimensions are arbitrary, including zero dimensions. The result allows nonnormal hidden generators and all nilpotent Jordan parts. The manuscript now supplies this argument instead of simply invoking the Laplace identity.

## 15.1 — canonical holomorphic matrix functions

`CanonicalJets` constructs the unique basis-free linear operator whose action on each generalized eigenspace is the finite Taylor jet. It proves that increasing the cutoff does not change this action, that an intertwiner carries each generalized eigenspace into its counterpart, and that the canonical operators intertwine even when the two dimensions differ.

`HolomorphicFinite` proves uniqueness, dependence only on the spectral jets, and the Cauchy integral formula for every local coefficient. Every declared open holomorphic neighborhood supplies admissible positive-radius closed discs around its spectral points. Their circle integrals yield the canonical coefficients, independently of the chosen radii. The final theorem is the literal rectangular matrix identity `C * F(A) = F(B) * C`.

The manuscript now explicitly uses this standard finite Taylor-jet definition of the holomorphic matrix function. This completes the theorem through a canonical construction; it does not assume that a supplied contour expression already represents `F(A)`. Disconnected neighborhoods, unequal dimensions and nilpotent Jordan parts are included. Arbitrary-contour deformation theory for general Banach algebras is outside the finite-matrix statement and is not claimed.

## Manuscript and preserved scope

The two proofs are expanded and the finite holomorphic calculus is defined explicitly. The theorem statements retain their full finite-dimensional scope. All 33 theorem-like records and the three open conjectures are retained, as is authorship Komorebi P. Earlier corrections and the fractional-operator scope explanations remain in place.

The numerical code and 19 figure pairs are unchanged. The 54 tests were rerun. The first-block 79-field numerical comparison and regenerated figures remain historical evidence; the numerical study was not repeated in this block. PDF rendering, numbering, warnings and final hashes are recorded in `verification/pdf_validation.json`.

The previous PDF and ZIP save failure was repaired during this work. The preserved fourth-block files were saved successfully before the final edition was produced. Final deliverables use regular workspace files so their bytes are available for transfer.

## Reproduction

Use the exact toolchain in `formalization/lean/lean-toolchain` and preserve `lake-manifest.json`. Obtain the dependencies and Mathlib cache, then run `lake build KomorebiPaperVI` and `lake env lean -DwarningAsError=true KernelAudit.lean`. The complete gate is `python3 verification/verify.py` with the companion Python requirements and `lake` available. Missing Lean is a verification failure, not a pass.

The producing runtime adapter is documented under `verification/runtime`; compiler, kernel and dependency sources are unchanged. The original supplied edition and earlier checked ledgers, audit evidence and reviews are preserved under `provenance`. The source archive excludes dependency caches and build products and includes its own hash manifest. Credit and licensing for the inherited adapted Mathlib integral proof remain in `THIRD_PARTY_NOTICES.md`.
'''
(R/'REVIEW.md').write_text(notes)
(R/'README.md').write_text(f'''# PRSC VI v0.5.0 — fifth checked block

Author: Komorebi P.

**All 33 scoped manuscript results are complete in the ledger. Both final results, 13.2 and 15.1, are closed.** The three original conjectures remain open and are excluded from this count.

The fresh pinned build and namespace axiom audit pass: **{N} explicit Lean theorem declarations across {M} modules**, with {D} namespace declarations audited. All 54 companion tests and six verifier controls pass.

The reviewed manuscript expands the nonnormal memory/Laplace proof and defines the canonical finite-dimensional holomorphic calculus used in its naturality proof. Start with `manuscript/Paper_VI_Reviewed.pdf`, `REVIEW.md` and `THEOREM_LEDGER.md`.

Run `python3 verification/verify.py` to reproduce the full gate. Exact pins and evidence are included. Prose-to-Lean correspondence and ordinary specializations are manually reviewed; supporting theorem declarations, audited namespace declarations and manuscript results are different counting units.
''')
labels={'complete_scoped_statement':'Complete','partial':'Partial','not_formalized':'Pending'}
md=f'# Paper VI theorem ledger\n\nAuthor: Komorebi P.\n\n{N} checked supporting theorem declarations in {M} modules; {C} complete, {P} partial and {U} pending manuscript results. Both preceding outstanding results are complete. The three conjectures remain open and are excluded. Correspondence and ordinary specializations are manually reviewed.\n\n| Result | Title | Status | Checked scope | Remaining obligation |\n|---|---|---|---|---|\n'
for r in rows:md+='| '+' | '.join([r['number'],r['title'],labels[r['status']],r['checked_scope'] or '—',r['remaining'] or 'None in the stated scope.'])+' |\n'
md+='\n## Exact targets\n'
for r in rows:md+='\n'+r['number']+':\n\n'+''.join('- `'+t+'`\n' for t in r['targets'])
(R/'THEOREM_LEDGER.md').write_text(md)
tex=r'''\clearpage
\appendix
\section{Lean verification and scope}\label{sec:lean-status}
\noindent\textbf{Fifth checked block, 6 September 2026.}
'''
tex+=f'''The release contains {N} explicit Lean theorem declarations across {M} proof modules,
including {N-310} additional declarations since the fourth checked block. The full
build and namespace audit pass with Lean 4.34.0-rc2 and pinned mathlib. The audit
inspects {D} declarations, including definitions and generated auxiliaries; only
\\texttt{{propext}}, \\texttt{{Classical.choice}} and \\texttt{{Quot.sound}} are allowed.
These are different counting units from the paper's 33 theorem-like results.

The ledger has \\textbf{{33 complete, zero partial and zero pending results}}.
The last two results, 13.2 and 15.1, are now complete. The three separately stated
conjectures remain open and are excluded from this count.

'''
tex+=r'''``Complete'' means the stated scope follows from the named checked targets
and the ordinary specializations recorded in the ledger. Prose-to-Lean correspondence
is manually reviewed. The fractional targets use complex Hilbert spaces;
complexification for real operators is an ordinary mathematical specialization,
not a separately checked Lean construction. Completion of the theorem ledger does
not certify every prose sentence, numerical figure or open conjecture.

\small
\begin{longtable}{@{}p{0.08\textwidth}p{0.68\textwidth}p{0.17\textwidth}@{}}
\toprule Result & Manuscript statement & Lean scope\\
\midrule\endfirsthead
\toprule Result & Manuscript statement & Lean scope\\\midrule\endhead
\bottomrule\endfoot
'''
for r in rows:tex+=r['number']+' & '+r['title'].replace('&',r'\&')+' & Complete'+r'\\'+'\n'
tex+=r'''\end{longtable}
\normalsize

\paragraph{General nonnormal memory (13.2).}
The actual damped exponential is decomposed into finitely many terms of the form
$t^k e^{(\mu-z)t}$. Integrability and convergence to zero follow from
$\operatorname{Re}\mu<\operatorname{Re}z$. The formal proof uses generalized
eigenspaces of left multiplication on the matrix algebra, so nilpotent Jordan
parts are included. Both inverse identities follow by integrating the two
exponential derivative formulas. A continuous linear sandwich map gives the
literal rectangular matrix memory integral and the actual inverse. No normality
or externally supplied growth bound is required.

\paragraph{Canonical holomorphic naturality (15.1).}
The standard finite Taylor-jet calculus defined before the theorem is constructed
using the direct sum of generalized eigenspaces. Uniqueness, cutoff stability and
exact rectangular naturality are proved. Cauchy's formula identifies the local
coefficients with actual circle integrals; admissible radii exist in every stated
open holomorphic neighborhood, and changing them leaves the canonical operator
unchanged. The argument permits disconnected neighborhoods and different matrix
dimensions. It makes no assertion about general Banach-algebra contour deformation.

\paragraph{Fractional results (10.3--10.5).}
The inherited fourth block proves the scalar beta normalization, the Lebesgue
integral representation of actual positive fractional powers, the literal
resolvent-defect formula, both printed norm constants and exact intertwining.
The rectangular complex-Hilbert-space semigroup proof substitutes those constants
into Duhamel's identity. The varying-space tower proof gives summability of
fractional-defect norms and uniform convergence of time-defect norm series on
bounded time intervals. Here ``summable'' means summable in norm. Operators with
unrelated codomains are not added together; a separate fixed-space theorem proves
operator-series convergence when such a sum is defined.

\paragraph{Verification and numerical evidence.}
The full pinned build, project-wide axiom audit, all 54 companion tests and six
verifier controls pass. The 54 tests comprise the original 37 and 17 added boundary
and validation cases. The 19 numerical figure pairs are unchanged. The earlier
79-field numerical comparison remains historical evidence, not a rerun in this
block. Machine-readable source contracts, exact theorem targets, full logs and
previous checked ledgers accompany the source archive. Numerical tests are finite
regressions and are not substitutes for the Lean proofs.
'''
(R/'manuscript/lean_status.tex').write_text(tex)
print(json.dumps({'theorems':N,'modules':M,'namespace_declarations':D,'complete':C,'partial':P}))
