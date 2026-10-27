# Paper VI — second checked formalization block

Author: Komorebi P. · 6 September 2026 · v0.2.0

**14 of the 22 previously outstanding manuscript results are now completed in their stated scope.** Paper VI now has **25 complete, 1 partial, and 7 pending results out of 33**. Eight results still require formal work; this release does not claim full-paper certification.

| Count | First checked block | This release |
|---|---:|---:|
| Explicit Lean theorem declarations | 63 | 152 |
| Proof modules | 5 | 19 |
| Complete manuscript results | 11 | 25 |
| Partial manuscript results | 8 | 1 |
| Pending manuscript results | 14 | 7 |

The 89 added supporting declarations are not 89 additional manuscript theorems. The namespace audit covers 338 declarations, including definitions, instances and compiler-generated auxiliaries; that is a third counting unit. The table records Paper VI only, not a cumulative count across Papers I–VI.

## Fresh verification

- The complete root module builds with Lean 4.34.0-rc2, strict elaboration options and warnings treated as errors.
- Every explicit theorem is printed in the axiom audit. Every declaration in the project namespace is inspected. Only `propext`, `Classical.choice`, and `Quot.sound` are allowed. No active proof placeholder or custom axiom is accepted.
- All nine dependency revisions match the lockfile and have no tracked source modifications. Mathlib is pinned at `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- All 54 companion tests pass again. All six verifier controls pass again, including rejection of corrupted input under optimized Python.
- Source hashes, the exact declaration inventory, root-import coverage, audit-target coverage, and the 33-result scope ledger pass.

The authoritative current results are `verification/verification_status.json`, `lean_build.log`, and `lean_axiom_audit.log`. Development logs retain failed attempts for provenance and are not final certification logs. A successful run explicitly records `full_paper_formalized: false`.

## Newly completed results

| Result | Statement | What closes the gap |
|---|---|---|
| 2.2 | Reducing packets | A finite orthogonal idempotent resolution with zero off-diagonal generator blocks commutes with the generator; actual exponential cross blocks vanish and compressed dynamics agree with the exponential of the compressed generator. |
| 3.2 | Norm bound | The displayed exponential-growth integral estimate for rectangular bounded real operators, with the contraction specialization. |
| 4.1 | Finite Markov semigroup | The actual real matrix exponential of any finite generator has nonnegative entries and columns summing to one for nonnegative time; consequently it preserves probability vectors. |
| 5.2 | Finite-horizon defect formula | The literal rectangular finite-sum defect identity and the norm bound for arbitrary rectangular contractions, including horizon zero and zero spaces. |
| 6.1 | Finite conditional-expectation projector | Literal finite complex weighted conditional expectation: idempotence, self-adjointness for the weighted inner product, and range exactly the block-constant functions. Strictly positive finite weights are explicit. |
| 6.2 | Tower law and martingale packets | Both concrete conditional-expectation tower identities; arbitrary pairs of nested projector kernels multiply to the coarser kernel; their differences are pairwise orthogonal idempotents and sum to the terminal projector. |
| 8.2 | Bayesian refinement criterion | The all-prior equivalence for strictly positive fine and coarse likelihoods and a surjective partition with at least two packets; necessity is derived from actual two-state priors. Singleton coarsening is automatic. |
| 8.4 | Bayesian information-loss packet | The literal information-loss matrix factorization, null scale direction, minimum-evidence L1 estimate, and the final fine-to-coarse weighted bound, including zero prior-mass fibers. |
| 8.5 | Nested Bayesian packet tower | The necessary-and-sufficient adjacent likelihood criterion with singleton exception, and exact Bayesian commutation over every finite span of a varying-state-space tower. |
| 8.6 | Canonical coarsest likelihood-resolving partition | Actual quotient by equality of likelihood profiles, canonical coarse likelihoods and exact closure, unique factorization from every likelihood-resolving partition, and the corrected coarsest nontrivial all-prior-closed property under strict positivity and distinct profiles. |
| 10.1 | Fractional packet calculus | Fractional powers and transfer for the given finite spectral resolution, including zero eigenvalues; multiplication/addition laws, packet reduction, and identification with the actual algebra exponential. Finite spectral resolution is the stated starting data. |
| 11.2 | Second-order low-mode convergence | The exact bound 0 <= w^2 - 4/h^2 sin(w*h/2)^2 <= w^4*h^2/12 for every nonzero spacing, with w=k*pi. This uniform bound implies the printed O(h^2) assertion as positive h tends to zero. |
| 12.1 | Discrete Feynman--Kac path formula | The actual potential-weighted matrix power equals the expectation over all finite paths; the path law is nonnegative and has total mass one for column-stochastic K. Product transition probabilities, the sum over departure-state potentials, and the terminal-state index are proved explicitly. |
| 13.1 | Schur--Feshbach projected resolvent | Literal finite complex block matrices: under invertibility of the full resolvent matrix and the hidden resolvent block, the retained block of the actual inverse is the inverse Schur complement; invertibility equivalence is included. |

## Scope of the new proofs

Bayesian necessity is proved using actual equal-weight two-state priors, then a state in a different packet to compare two states inside the same packet. No necessity conclusion is supplied as a hypothesis. The quotient construction uses equality of complete likelihood profiles and proves its universal factorization property. Tower proofs allow varying finite state spaces and explicitly separate singleton targets.

The conditional expectation is the literal weighted finite average with complex values. Its range and weighted self-adjointness are proved before connecting nested partition kernels to every pair of martingale-difference packets. The operator bounds concern actual bounded rectangular maps and actual Bochner integrals. Matrix-specialized identities and the Banach-space norm statements are connected by the ordinary finite-dimensional specializations documented in the ledger.

The Markov proof establishes entrywise positivity of the actual matrix exponential by shifting a Metzler generator to an entrywise nonnegative matrix. It derives column conservation from the exponential series. The Feynman–Kac proof constructs the distribution on all finite paths, proves its mass and positivity, and identifies its recursive quantities with the printed transition product, potential sum, and terminal index.

The fractional module starts from the finite spectral resolution assumed in the paper. It proves the coefficient laws, handles zero eigenvalues, and constructs a continuous ring homomorphism to identify spectral transfer with the actual exponential. This does not certify the separate subordination or bounded infinite-dimensional fractional-naturality results. The low-mode estimate is stronger in spacing than stated: the printed constant holds for every nonzero h once the displayed eigenvalue formula is used. The O(h²) consequence is the ordinary implication of that uniform bound; it is not a separately counted Lean declaration.

The Schur–Feshbach theorem uses actual complex block-matrix inverses and proves the projected-inverse identity under both invertibility hypotheses. It does not assume that identity as input.

## Remaining results

- **10.2 — Poisson subordination (pending)**: Full stated result remains to be formalized.
- **10.3 — Fractional intertwining theorem (pending)**: Full stated result remains to be formalized.
- **10.4 — Fractional semigroup refinement (pending)**: Full stated result remains to be formalized.
- **10.5 — Fractional refinement towers (pending)**: Full stated result remains to be formalized.
- **11.1 — Exact discrete Green reconstruction at grid nodes (pending)**: Full stated result remains to be formalized.
- **13.2 — Memory/self-energy correspondence (pending)**: Full stated result remains to be formalized.
- **14.1 — Semigroup survival identities (pending)**: Full stated result remains to be formalized.
- **15.1 — Naturality under exact intertwining (partial)**: Arbitrary holomorphic functional calculus on a neighborhood of both spectra.

The remaining work consists of seven unformalized statements and the general holomorphic extension of an already checked intertwining theorem. Their difficulty differs substantially, so declaration counts are not a reliable completion-time estimate. The original three conjectures remain open and are excluded from the 33-result theorem ledger.

## Corrections retained in the manuscript


1. **7.1 — sequential evidence.** Positive individual evidences do not ensure a defined second update. The statement now requires positive first and combined evidence. The disjoint-support counterexample is in the regression suite.
2. **7.2 — zero-evidence packets.** The local packet shape is explicitly zero when its evidence vanishes. Only positive-evidence packets carry conditional probabilities. The proof and Lean reconstruction handle this boundary.
3. **8.2 — zero prior mass in the sufficiency proof.** The correct universal identity is weighted: P_a r_a = c times coarse-likelihood_a times P_a. An unweighted effective-likelihood equality need not hold on an empty-mass fiber.
4. **8.4 — information-loss hypotheses.** Both fine and declared coarse evidences are required to be positive. The last estimate treats zero-mass packets before dividing by their mass.
5. **8.5 — singleton tower levels.** Coarsening to one packet is automatic; the two-packet necessity criterion cannot be applied there.
6. **8.6 — the canonical partition claim.** A one-packet partition is always Bayesian-closed. The corrected unconditional claim is the unique coarsest *likelihood-resolving* partition. Under strict positivity and at least two profile classes it is also the unique coarsest nontrivial all-prior closed partition. Identical profiles need a separate boundary case.
7. **9.3 — probability hypotheses.** The initial vector, stochastic matrix, nonnegative likelihoods, and evidence conditions are stated explicitly.
8. **13.1 — Schur–Feshbach.** Invertibility of the hidden block alone does not imply existence of the full resolvent. Both are now assumed, and the projected identity is stated as an operator on the retained subspace.
9. **14.1 — possible nonabsorption.** A subgenerator's sign conditions allow a defective exit-time density. The paper now separates finite-time exit density from eventual absorption and a proper probability density.
10. **15.1 — analytic naturality.** A general holomorphic function near both spectra need not be represented by one Taylor series there. The proof now uses the resolvent identity and contour functional calculus, with complexification for real matrices. The arbitrary holomorphic theorem remains outside the two checked Lean blocks.

The abstract, figure caption, and formalization appendix reflect these distinctions. No new theorem-like numbering was inserted into the original 33-result sequence. The original three open conjectures remain open.


## Numerical and manuscript provenance

The latest Fractional Naturality Resolved manuscript remains the mathematical baseline. All ten earlier corrections are retained. This second block updates the title-page scope statement, abstract and expanded formalization appendix without changing the 33 original theorem-like statements or their order. The appendix explains the newly completed proof connections and names all eight remaining results. The abstract's broken appendix cross-reference and the source generator's escaping are also repaired. Authorship remains Komorebi P.

The companion implementation and numerical figures are unchanged in this block. Its 54 tests were rerun. The retained first-block numerical comparison records agreement of all 79 numeric fields at absolute tolerance 1e-10 and relative tolerance 1e-8, after regenerating 19 figure pairs. That numerical experiment was not repeated for this source-only formalization expansion; it is retained evidence, not a new universal proof.

The untouched supplied edition is under `provenance/original_release`; the preceding checked scope, audit and review are under `provenance/first_checked_block`. Exact manuscript and Lean source changes, the current source contract and release hashes are included.

## Reproduction

Install the pinned Lean toolchain using elan. In `formalization/lean`, preserve the lockfile, obtain dependencies and the mathlib cache with `lake exe cache get`, then run `lake build KomorebiPaperVI` and `lake env lean -DwarningAsError=true KernelAudit.lean`.

For the complete gate, install the companion Python requirements and run `python3 verification/verify.py` with `lake` on PATH. Missing `lake` returns exit code 2; any failed mandatory check returns 1. `--static-only` verifies source and companion checks without claiming kernel verification. Source scanning is a lexical check, separate from the actual compiler and axiom audit. The PDF-to-Lean correspondence remains a manual mathematical review, not a mechanized translation.

Run `companion/run_all.py` to regenerate the independent numerical study. Compile `manuscript/Paper_VI_Reviewed.tex` twice with pdflatex. The producing environment's executable-self-location adapter is disclosed in `verification/runtime/RUNTIME.md`; the compiler, kernel and dependency sources are unmodified. No toolchain or mathlib binaries are distributed.
