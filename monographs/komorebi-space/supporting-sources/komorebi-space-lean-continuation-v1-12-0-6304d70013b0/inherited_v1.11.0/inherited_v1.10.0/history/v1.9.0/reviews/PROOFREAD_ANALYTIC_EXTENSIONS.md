# Analytic extension proofreading

Mode: conservative EDIT, followed by self-review of every changed sentence in context. The `mathbox:proofread-math` skill and checklist were applied. A narrowly scoped `mathbox:proof-audit` pass was also applied to the finite-coordinate metric convention identified below. This was not a new audit or compilation of the Lean project, and it does not certify every printed proof by reference to an accepted Lean statement.

## Full coverage

Every line of each of the following files was read, including statements, proofs, examples, tables, captions, scope boxes, source callouts, and closing interpretations. The publication preamble and its notation/macros were read. Cross-references were checked against all current source labels. The final assigned files contain 1,725 lines and 14,945 whitespace-separated source tokens; the token count is not an extracted-PDF word count.

| File | Coverage | Result |
|---|---|---|
| `source/chapters/05a_certificates.tex` | Complete | No correction required. Measurement/operator perturbation distinctions and norm conventions retained. |
| `source/chapters/05b_transport_cost.tex` | Complete | No correction required. Extended directed costs, free-path example, and zero-arrow distinction retained. |
| `source/chapters/05c_iteration.tex` | Complete | No correction required. Complete statements and proofs of KS71–KS75, all counterexamples, and captions read. |
| `source/chapters/05d_floors.tex` | Complete | Corrected the environment name used for the KS73 cross-reference. |
| `source/chapters/05e_escape.tex` | Complete | No correction required. Infinite-space definitions, finite repairs, tail bounds, escape argument, and inverse-limit interpretation read. |
| `source/chapters/05f_bounded_realization.tex` | Complete | Updated the stale scope box as explicitly directed by the root editor. All printed weak-subsequence, WR01, and WR02 arguments retained. |
| `source/chapters/05g_budget_certificates.tex` | Complete | No correction required. WR03–WR05, endpoint cases, dual-witness proof, and worked calculation read. |
| `source/chapters/05h_regularized_repair.tex` | Complete | Made the ambient and residual orthonormal-coordinate convention explicit. Preserved the arbitrary kernel basis and all abstract Hilbert results. |
| `source/chapters/05i_diagonal_regularization.tex` | Complete | Corrected prose describing an equality followed by an inequality. No displayed formula changed. |
| `source/chapters/05j_inexact_certificates.tex` | Complete | Made explicit the primal optimizer used in the WR14 equality case. |
| `source/chapters/05k_stopping_rules.tex` | Complete | Made the same ambient/residual coordinate convention explicit before WR15. Preserved the arbitrary kernel basis and stopping-rule statements. |

## Exact changes

1. **05d, “The bridge back to exactification.”** Changed `Theorem~\ref{KS73}` to `Proposition~\ref{KS73}`. KS73 is declared in a `proposition` environment. The label and target are unchanged.
2. **05f, opening scope box.** Replaced the stale statement “The present chapter remains written-only” and the separate version 1.6.0 regularization-scope description. The paragraph now records complete WR01–WR02 counterparts in the accepted version 1.8.0 combined Lean project and inclusion of WR06–WR07 in that project. It explicitly retains the printed weak-subsequence lemma as a written background argument and states that formal acceptance does not automatically verify the printed WR01 route. It retains the written limit boundary of WR09 and the separate evidence status of WR03–WR05. This status synchronization was authorized by the root editor; no formal source or verification record was modified here.
3. **05h, “Coordinate bases must retain the correction metric.”** Replaced the opening `In finite dimensions, let B ...` by an explicit choice of orthonormal coordinates in the ambient candidate and residual spaces, followed by the original independent spanning columns condition. Added: “The columns of B need not be orthonormal.” All displayed equations remain unchanged.
4. **05i, WR10 proof, bound for the first m residual coordinates.** Changed “The exact identity” to “The sum-of-squares estimate.” The following display includes both an equality and an inequality, so “identity” alone was an inaccurate description. The display and proof are unchanged.
5. **05j, WR14 statement.** Changed the equality-case phrase from `At z_α = r − T a_α, equality holds` to `At a = a_α and z = z_α = r − T a_α, equality holds`. The immediately following proof already sets both values explicitly. This removes the possible reading that the optimizing dual witness makes the inequality an equality for every primal proposal.
6. **05k, “The residual of the coordinate equation is a covector.”** Added the same orthonormal ambient/residual coordinate convention. Described B as an arbitrary kernel basis, “not necessarily an orthonormal one.” All formulas, including the nonorthogonal basis change C, are unchanged.

## Mathematical-token and scope changes

The following are the complete mathematical changes in this proofreading pass. They are not hidden as ordinary grammar changes.

- **WR14 equality case:** inserted the condition `a=a_\alpha` and explicitly bound `z=z_\alpha`. This is uniquely forced by the existing proof and intended optimizer equality, with no new argument or changed downstream formula.
- **05h coordinate setup:** added an explicit orthonormal ambient-candidate and residual-coordinate convention. This is a mathematical scope clarification authorized after identifying the unrestricted-coordinate failure below.
- **05k coordinate setup:** added the same convention before WR15, while expressly retaining arbitrary independent kernel basis columns B.

There were no changes to displayed coefficients, signs, exponents, indices, norm formulas, convergence hypotheses, proof steps, or source identifiers. The scope-box changes alter evidence claims, not theorem hypotheses.

## Focused coordinate audit

**Normalized claim.** In finite-dimensional real Hilbert spaces, a full independent kernel-basis matrix B, forward matrix d, coefficient c, and positive parameter α give S=dB, G=BᵀB, the normal covector q=(SᵀS+αG)c−Sᵀr, the actual Hilbert normal residual g=BG⁻¹q, and squared norm ‖g‖²=qᵀG⁻¹q. Under B′=BC with invertible C, q′=Cᵀq and the scalar certificate is invariant.

**Primary verdict on the inherited unrestricted-coordinate reading: correct only after a stated restriction.** The matrices must be written in orthonormal coordinates in the ambient candidate and residual spaces. The revised local introductions now state exactly that restriction. The kernel basis B is not restricted to be orthonormal.

Dependency chain and obligations:

| Obligation | Evidence and result |
|---|---|
| Ambient norm equals the standard sum of coordinate squares | A coordinate convention, previously implicit; now explicit. |
| Residual inner product is represented by the identity matrix | A coordinate convention, previously implicit; now explicit. |
| Full independent columns of B give invertible G=BᵀB | Internal displayed proof; passed, including the empty-dimensional convention. |
| Euclidean transpose represents the adjoint in ambient and residual coordinates | Follows from the explicit orthonormal choices; passed. |
| P=BG⁻¹Bᵀ projects onto the entire protected kernel | Symmetry, P²=P, PB=B, and full-span assumption are checked in the printed argument; passed. |
| g=BG⁻¹q and the scalar norm formula | Direct substitutions and symmetry of G⁻¹; passed under the stated coordinate convention. |
| Basis-change invariance for arbitrary invertible C | The existing cancellation calculation is valid; passed. No assumption C is orthogonal was introduced. |
| Abstract Hilbert regularization, budget, and stopping bounds | Outside this coordinate-notation correction. Their definitions use the actual adjoint and actual Hilbert norms, so they do not depend on choosing these coordinates. |

**Small exact counterexample to arbitrary ambient coordinates.** Let the ambient/correction space be R with inner product ⟨x,y⟩=4xy, the residual space be standard R, d=1, p=0, B=[1], r=1, α=1, and proposed a=c=0. In the unnormalized ambient coordinate, the actual adjoint is T* y=y/4. Thus g=−1/4 and its actual squared Hilbert norm is 1/4. The unrestricted formulas G=BᵀB=1 and q=−1 would instead give g=−1 and squared certificate 1. Likewise, the true objective is (a−1)²+4a², whose minimizer is 1/5, whereas omitting the ambient metric gives 1/2. These are exact rational calculations, not numerical evidence for a universal theorem.

**Blast radius.** The affected interpretations are the finite matrix normal equation in 05h and the coordinate-covector/Gram formula in 05k. Their exact examples already use ambient and residual Euclidean norms, so their numbers do not change. The arbitrary kernel-coordinate scaling example remains valid. The abstract Hilbert operator formulas in WR06–WR09 and WR13–WR16 use genuine adjoints and norms and are unaffected. The appendix's WR15 summary should be read with the local setup of WR15; the root editor has been notified of the clarified convention. No extension to fully weighted ambient/residual matrix coordinates was authored in this proofreading pass.

## Remaining observations and boundaries

- **No unresolved substantive issue remains within the focused coordinate audit** after the explicit convention is added. This statement is not a global proof-audit verdict for every chapter.
- **05f local notation:** the final attainable-diagonal paragraph reuses `a_n` for correction coordinate n after earlier using `a_n` for the nth minimum correction vector. The intended coordinate meaning is recoverable from the immediate sentence. No new notation was imposed in this conservative pass; the root editor may prefer a prose-only clarification.
- **05j scalar counterexample:** `α_n=n^{-2}` implicitly starts at n=1. An explicit `n≥1` qualifier would remove that indexing convention. The example's argument is correct on positive indices; no shifted sequence or altered formula was introduced.
- **Formal evidence remains distinct from prose verification.** WR01–WR02's accepted formal counterparts do not turn the printed weak-subsequence lemma into a newly compiled statement. No new Lean work was performed for this proofreading task.

## Validation

- Read every assigned file in full and reread all changed passages with neighboring definitions and proof text.
- Checked all assigned `ref`, `eqref`, and `pageref` targets against the current source label inventory: no unresolved target.
- Checked theorem/proposition/lemma/corollary nouns against labeled environments where explicitly used: the one mismatch, KS73, was corrected.
- Checked brace balance, begin/end environment nesting, inline dollar parity, and control-aware display/inline math delimiters in all eleven files: passed.
- A first naive delimiter count falsely treated table row-spacing syntax `\\[3pt]` as a display opener in 05h. The escaped-control-aware check resolved that checker false positive; no manuscript change was made for it.
- Compared final assigned files with the inherited v1.7.0 source: exactly the six files and six localized changes listed above differ. No proof block was rewritten.
- No local PDF build or rendering was run by this agent. The root publication build and full-size review must assess the expanded scope box and coordinate-introduction line breaks.
