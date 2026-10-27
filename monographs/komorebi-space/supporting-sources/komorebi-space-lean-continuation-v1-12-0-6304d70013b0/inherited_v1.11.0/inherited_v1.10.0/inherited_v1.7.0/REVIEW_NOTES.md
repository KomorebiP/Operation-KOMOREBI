# Komorebi Space proof-expansion review — 1.7.0

**Recorded:** 2026-10-12T19:28:17.651832+00:00  
**Accepted publication build:** `audit/proof_detail/proof_build02.json`

## Result

The monograph is **161 pages**, compared with 133 in version 1.6.0. It retains six parts and 35 numbered sections. A new analytic-background appendix brings the appendices to six. The visual guide is 43 pages with the same forty plates, and the Lean/evidence guide is 36 pages. The complete reader set is **240 pages**.

This edition expands existing arguments rather than enlarging the principal theorem program. **67 existing proof blocks** were rewritten across **17 chapter files**: 50 KS proofs, all sixteen WR proofs, and the existing weak-subsequence lemma. Five classical supporting lemmas were added in the new appendix. The original 87 proof environments become 92 because rewriting an existing proof does not count it twice.

## The substantive proof changes

**Realizations, obstructions, and finite observations.** The revised arguments explicitly check fiber membership, quotient well-definedness, lift independence, and both inverse equations. The eventual transport proofs construct common finite stages before using equality on those stages. The finite-observation characterization identifies the precise use of surjective point projections and constructs a monotone running-maximum schedule. The cofinal argument includes repeated levels and both conjugation directions.

**Split repair and representation change.** The tower recurrence is shown to define a bounded operator rather than just formal coordinates. The proofs retain the innovation observable, verify both chart inverses, and derive the triangular mismatch formula in the correct order. Membership of the mismatch in the exact target is proved before interpreting its size.

**Nonabelian symmetry and descent.** The normalization calculation cancels only adjacent inverse factors. The effective descent proof now separates normalization, literal overlap matching, global cocycle construction, full faithfulness, and the quasi-inverse. The site proof addresses arbitrary common subpatches and covering sieves rather than treating singleton values as sufficient without naturality. The identified-boundary comparison keeps the natural isomorphism in the square and checks its direction.

**Hilbert geometry and stability.** The closed-range proof explicitly constructs the transverse bijection, checks completeness of both spaces, and derives the least gain and the converse. Protected repair is performed in the declared kernel. The two-stage argument does not assume that a sequence in the invisible component converges. The projector-motion estimate supplies the restricted dual estimate and both orthogonal decompositions. Neumann inversion and the two kernel-transport inverse identities are written out.

**Convergence, budgets, and regularization.** The weak-subsequence construction works inside the separable closed span of the given sequence, not by assuming the ambient space separable. The budget theorem constructs an attaining witness directly, with zero-budget and zero-residual cases included. The regularization-limit proof distinguishes the projected datum from a datum in the actual range, and shows how weak convergence plus norm convergence yields strong convergence. The inexact-solver proofs explicitly retain the restricted adjoint and the positive parameter in each division.

**Infinite diagonal asymptotics.** The proof now bounds the tails uniformly before replacing finite Riemann sums by improper integrals. It then moves from the selected regularization budgets to all sufficiently large budgets by monotonicity and a consecutive-budget ratio. A plotted truncation is not used as an infinite-dimensional proof.

The detailed item-level changes and exact old/new proof hashes are in `PROOF_EXPANSION_MAP.md` and `audit/proof_detail/proof_inventory.json`.

## The new background appendix

Appendix E supplies five complete written classical lemmas: projection onto a nonempty closed convex set, Riesz representation and the adjoint, Baire's complete-metric principle, bounded preimages and the Banach inverse theorem, and the Neumann series with both inverse identities. It includes the relevant completeness arguments rather than merely naming the tools.

The Banach argument does not assert that every surjection has a bounded linear right inverse. Linear inverse structure is concluded only in the bijective case. These supporting lemmas are ordinary written background proofs, not five newly compiled Lean declarations or novelty claims.

## Statement and source preservation

The editorial checker verifies that **88 labeled principal statement envelopes** are unchanged and all inherited source labels and evidence calls survive. It checks the hashes of all 67 predecessor/current proof blocks. No principal statement was weakened to make its proof shorter or easier.

All **169 files across the canonical and focused formal trees** match the version 1.6.0 predecessor: 156 canonical files and thirteen extension files. Neither tree was edited. **No new Lean compilation or axiom audit was executed.** This text/label/source audit is not a mathematical proof checker.

The retained catalogue has **80 KS entries and 211 references**. The focused WR resolver retains thirty references. WR06, WR07, WR13, and WR14 retain complete focused counterparts. WR09 and WR16 retain formal pointwise estimates and written limiting arguments. The other ten WR groups remain written-only. Longer prose does not alter that coverage.

A stale concluding paragraph that described an earlier WR status was corrected to the actual four-complete, two-partial, ten-written split. This was a coverage-description correction, not a new theorem.

## Executed checks

The accepted publication build returned exit code zero. Its seven freshly rerun exact suites passed **197,482 assertions**: 14,224 original, 2,767 recovered moving-space, 17,213 revision, 96,345 expansion, 13,817 deepening, 34,388 regularization, and 18,728 inexact-certificate assertions. Repeating the build is not counted as additional distinct coverage. No new finite suite is claimed for an infinite proof.

Historical source/evidence integrity, canonical source preservation, focused source-bound evidence, the principal concordance, written-scope metadata, and the new proof-edit audit passed. All three reader PDFs were rebuilt. Final mechanical preflight found no overfull boxes, undefined references, text outside the page, replacement characters, or unembedded fonts.

## Visual review

All **240 final pages** were rendered at 100 dpi. Every page was inspected through the complete set of 41 contact sheets. Ten selected monograph pages were inspected individually: PDF pages 48, 73, 101, 106, 112, 117, 156, 157, 158, and 159. Those cover noncommutative descent, projector bounds, weak convergence, budget duality, the regularization limit, improper sums, and the new analytic lemmas. The final PDF and raster hashes are retained in `audit/visual_review.json`.

The review found no clipped or overlapping equations. Existing body typography was retained. The first draft exposed detached source callouts, so stronger keep-with-previous penalties were added. Some continuation-page callouts and chapter-ending whitespace remain. This record does not claim that every inherited word was reread at enlarged size or that every possible layout preference was eliminated.

## Actual failures and superseded work

An interactive container launch was rejected with `StreamingExecNotEnabledContainerError`. It did not run a build. Supervised ordinary subprocesses then produced two complete zero-exit publication builds. The first passed mechanically but was superseded after layout review. The second is the accepted build. Both complete rasterization runs returned zero, with the second binding the final PDFs.

A diagnostic wildcard listing found no `checks/*visual*` match and returned a nonzero shell status after showing successful build information. It did not affect any source or supply verification evidence. The tool failure, accepted and superseded builds, and rasterization dispositions are retained in `audit/proof_detail/attempts.json` and their original receipts.

## Remaining boundary

This edition is a substantial proof-exposition revision, not a fresh formal release. The ten written-only WR groups and two written limiting arguments retain their previous formalization obligations. The official Lean compiler/kernel and imported dependency caches remain trusted. No independent kernel, source rebuild of mathlib, native Windows run, universal Python refinement, unrestricted semantic realization, or general higher-stack theorem is claimed.

Start the next revision from `PROGRESS_LEDGER.md`. Verify the payload before editing, retain stable KS/WR identifiers, update recorded proof hashes when a mapped argument changes, and rebuild and inspect before renewing the delivery manifest.
