# Paper VI — first checked formalization block

Author: Komorebi P. · 6 September 2026 · v0.1.0

The starting point is the later **Fractional Naturality Resolved** edition, retaining its Bayesian and fractional refinements. This is a first checked Lean block, not a claim that Paper VI is fully formalized.

- **63 explicit Lean theorem declarations in five modules** build with Lean 4.34.0-rc2 and the pinned mathlib revision.
- The kernel audit accepts **145 declarations in the Paper VI namespace**, including definitions and generated auxiliaries. This is not 145 additional theorems. Only `propext`, `Classical.choice`, and `Quot.sound` are allowed; no placeholder or custom axiom is accepted.
- The manual manuscript-to-Lean mapping has **11 complete results, 8 partial results, and 14 pending results**, out of 33 theorem-like records. The 63 supporting declarations are a different counting unit.
- **54 companion tests pass**: 37 inherited tests and 17 new boundary/validation cases. **Six verifier controls pass**, including rejection under optimized Python. These finite software tests do not prove the universal mathematical statements.
- The complete numerical study regenerated **19 figure pairs**. All **79 numeric fields** agree with the supplied record within absolute tolerance 1e-10 and relative tolerance 1e-8. This is numerical reproducibility, not kernel proof.

## What is now checked

The block includes the actual Banach-algebra exponential law and derivatives; literal exponential packet convolution; rectangular Duhamel differentiation and integration; exact exponential intertwining; the contraction defect bound; integer-iterate and resolvent identities; Bayesian composition and normalization; the weighted L1 stability bound; finite packet reconstruction with zero-evidence fibers; effective-likelihood coarsening; blockwise sufficiency; and the normalized exponential Bayesian flow with its centered multiplicative derivative.

The full mapping is in THEOREM_LEDGER.md and THEOREM_LEDGER.json. “Complete” means the scoped statement is covered by named checked theorems and ordinary specializations documented in the ledger. The PDF-to-source correspondence itself is a manual review, not a mechanized translation.

## Corrections integrated into the main manuscript

1. **7.1 — sequential evidence.** Positive individual evidences do not ensure a defined second update. The statement now requires positive first and combined evidence. The disjoint-support counterexample is in the regression suite.
2. **7.2 — zero-evidence packets.** The local packet shape is explicitly zero when its evidence vanishes. Only positive-evidence packets carry conditional probabilities. The proof and Lean reconstruction handle this boundary.
3. **8.2 — zero prior mass in the sufficiency proof.** The correct universal identity is weighted: P_a r_a = c times coarse-likelihood_a times P_a. An unweighted effective-likelihood equality need not hold on an empty-mass fiber.
4. **8.4 — information-loss hypotheses.** Both fine and declared coarse evidences are required to be positive. The last estimate treats zero-mass packets before dividing by their mass.
5. **8.5 — singleton tower levels.** Coarsening to one packet is automatic; the two-packet necessity criterion cannot be applied there.
6. **8.6 — the canonical partition claim.** A one-packet partition is always Bayesian-closed. The corrected unconditional claim is the unique coarsest *likelihood-resolving* partition. Under strict positivity and at least two profile classes it is also the unique coarsest nontrivial all-prior closed partition. Identical profiles need a separate boundary case.
7. **9.3 — probability hypotheses.** The initial vector, stochastic matrix, nonnegative likelihoods, and evidence conditions are stated explicitly.
8. **13.1 — Schur–Feshbach.** Invertibility of the hidden block alone does not imply existence of the full resolvent. Both are now assumed, and the projected identity is stated as an operator on the retained subspace.
9. **14.1 — possible nonabsorption.** A subgenerator's sign conditions allow a defective exit-time density. The paper now separates finite-time exit density from eventual absorption and a proper probability density.
10. **15.1 — analytic naturality.** A general holomorphic function near both spectra need not be represented by one Taylor series there. The proof now uses the resolvent identity and contour functional calculus, with complexification for real matrices. The arbitrary holomorphic theorem remains outside this first Lean block.

The abstract, figure caption, and formalization appendix reflect these distinctions. No new theorem-like numbering was inserted into the original 33-result sequence. The original three open conjectures remain open.

## Companion changes

Bayesian routines reject negative, non-vector, and nonfinite priors and nonfinite likelihoods. Packet reconstruction validates that groups are a genuine partition and rejects noninteger state indices. Canonical profile partitioning is exact when atol is zero; its documented positive-tolerance behavior is greedy representative clustering, which depends on state order and is not an equivalence-relation theorem. The original numerical examples are preserved and rerun.

## What remains

**22 of the 33 manuscript results still need some or all of their formalization.** The nearest completion work is the all-prior necessity direction for Bayesian refinement, complete tower/quotient packaging, the general growth and finite-horizon norm bounds, and the final information-loss estimate. The larger blocks are Markov semigroup positivity; weighted conditional expectation; spectral fractional calculus and subordination; bounded fractional naturality; Green/PDE results; Feynman–Kac; Schur–Feshbach and memory; survival/hazard analysis; and arbitrary holomorphic naturality.

There is no meaningful time estimate or percentage based on declaration counts: these remaining results vary greatly in difficulty. The next cohesive block is Bayesian necessity and its partition/tower consequences, followed by Markov and conditional-expectation operators.

## Reproduction

Install the pinned Lean toolchain with elan. From `formalization/lean`, keep the included lockfile pinned. Fetch dependencies and the mathlib cache with `lake exe cache get`, then run `lake build KomorebiPaperVI` and `lake env lean -DwarningAsError=true KernelAudit.lean`.

For the full verification entry point, install the companion's requirements and run `python3 verification/verify.py` from the package root with `lake` on PATH. `--static-only` reports only source and companion checks. A missing compiler returns exit code 2; a failed check returns 1. Successful block verification explicitly leaves `full_paper_formalized` false. The six negative controls exercise source hashes, forbidden proof placeholders, import coverage, audit coverage, and optimized-Python rejection.

`companion/run_all.py` regenerates the numerical record and figures. Compile `manuscript/Paper_VI_Reviewed.tex` with pdflatex twice. The producing environment used a disclosed executable-self-location adapter; see verification/runtime/RUNTIME.md. No compiler, kernel, or mathlib source was patched, and no toolchain/cache binaries are distributed in this package.

## Provenance

The untouched supplied edition is preserved under provenance/original_release. Exact source changes are in verification/manuscript.patch and verification/bayes.patch. The source contract freezes the Lean modules, audit, pins and 33-result ledger. Release hashes cover all delivered files. The numerical records, complete logs, and source make the scope reviewable without treating the old release's claims as new Lean certification.
