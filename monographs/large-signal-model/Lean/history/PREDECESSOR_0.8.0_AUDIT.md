# Large Signal Model — Lean 0.8.0 audit

**Komorebi P. · 10 October 2026 · Frozen Foundations 1.0.0**

## Result and mathematical scope

The reviewed numbered mappings completed here are P13 and P18–P21. Cumulative coverage is **30 complete, none partial and 57 unformalized**. The full 87-proposition volume remains the Lean 1.0 target. Version numbers are not percentages of proof difficulty.

There are 67 active proof modules, 1,178 explicitly named declarations and 904 named theorems. Of the theorems, 613 are foundations/supporting results and 291 occur in example modules. Ten new modules add 115 named theorems, including 47 example-module results. Compiler-generated declarations are not added to those source counts but belong to the replayed module environments.

All 57 predecessor proof files, all 1,023 explicitly named predecessor declaration records, all 52 predecessor rejection controls and both frozen source files are unchanged. Production PR-LASM 2.3.0 is not modified or verified.

## P13: topology and fixed horizons

Actual continuous linear maps are used. The proof derives the compression estimate and uniform operator bound, then strong convergence on varying convergent vectors and each fixed power. An adapter uses actual orthogonal subspace projections with their norm bound over real or complex inner-product spaces. There is no assumed operator-norm convergence or time-uniform accuracy. The fitted-operator extension retains its separate boundedness and strong-error hypotheses.

The scalar example applies the general fixed-power result to rates n/(n+1). At each fixed resolution its long-time error against the identity tends to one, and that limit is separately proved. Those scalar maps are approximating operators, not projections. The manuscript's adjacent infinite-dimensional operator-norm counterexample is not separately formalized here.

## P18: actual typed defects and trajectory recursion

State spaces are genuinely time indexed. Domain membership is required for both true and predicted inputs, and the local residual is calculated from the true representation and actual approximate step. Lean derives the one-step inequality and the suffix-product/sum bound. Decoding, constant contraction and the exact representation-versus-fit defect decomposition are separate theorems.

The expanding trajectory example invokes the theorem and identifies its envelope as 2^T-1. Individual nilpotence is also proved insufficient under switching through an exact all-powers amplification example. The result does not silently compare different control policies without a mismatch bound.

## P19: stable finite-memory prediction

The recurrence uses integer histories and a separate initialized window. The norm-sum gain, local residual and actual predicted step imply the uniform supremum bound; a scalar error recurrence is derived rather than supplied as the conclusion. Zero-prehistory identities cover H=0 and times shorter than H.

Coefficient differences, the geometric unresolved-memory tail and initialization forcing are separated algebraically and norm-bounded. The bound is inserted into the own-history prediction theorem. Discarded forcing is bounded by the initial unresolved-state term; exactly retained forcing contributes zero. The norm-sum criterion is sufficient, not necessary.

A separately declared stable scalar recurrence applies the general theorem and has uniform error at most 1/2. It is not claimed as a reproduction of the old hidden-state dataset. A gain-one recurrence demonstrates unbounded accumulation despite bounded local residual.

## P20: ordered nonlinear interactions

The full and retained polynomials are actual sums of continuous multilinear maps. Restricted block bounds quantify over the actual product of packet ranges. Exact subtraction gives the omitted ordered-tuple sum. The norm estimate retains packet magnitudes, while telescoping gives the degree-dependent Lipschitz bound on a specified ball. Actual orthogonal projectors supply contractivity in the Hilbert adapter.

A nonpolynomial approximation error must be supplied separately. The proof does not infer that trajectories remain in the ball. The two-coordinate example includes all degree-one terms, retains diagonal quadratic terms, applies the general theorems and checks the exact cross term. Its explicit product norm is the maximum norm, not an unlabeled Euclidean norm.

## P21: coherent reconciliation and explicit coefficient metrics

Linear atlases have exact reconstruction and their consistent coefficient spaces are actual analysis-range subtypes. Encode/decode inverse laws are derived. Repaired outputs are consistent and intertwine. Weighted means of pulled-back fitted operators satisfy the target-error bound in actual continuous-operator norms.

Weighted variance and unique minimization are proved for the explicit squared Frobenius sum. A constructed orthonormal basis and matrix coordinate equivalence connect the objective to actual endomorphisms of a finite-dimensional real Hilbert space. The target norm inequality requires nonnegative weights summing to one.

The pullback norm is constructed as a genuine normed additive group and normed space using the injective decoder. The general transport is an isometry in those explicitly induced structures, and every Lipschitz constant is equivalent in both directions. These claims are not made about arbitrary ambient subtype metrics. The concrete example uses explicit decoded distances to avoid competing ambient metric instances. The adjacent learned singular-value and pseudoinverse paragraph is not marked as an additional formal theorem.

## Accepted cumulative source verification

The complete source-candidate verifier report is `verification/release_run/report.json`. It completed all 198 stages with no subprocess timeouts and shell exit zero.

| Check | Result |
|---|---:|
| Proof modules compiled | 67 |
| Root import compiled | 1 |
| Explicit declaration axiom records | 1,178 |
| Project modules kernel-replayed | 67 |
| Deliberately invalid proof files rejected | 62 |
| Separate metadata/tooling records | 69 |

The verifier removes project compiled objects before the run, checks the compiler commit and all nine dependency revisions, uses one worker and warnings as errors, records actual commands/exits/stdout/stderr/durations/source hashes, and confirms an unchanged source snapshot at completion. No previous PASS is reused.

Every observed axiom dependency is among `propext`, `Classical.choice` and `Quot.sound`. Active proof sources contain no custom mathematical axioms, admitted proof placeholders, unsafe definitions or native-decision shortcuts. Classical basis and representative choices are explicit.

Kernel replay invokes the pinned upstream `LeanChecker.replayFromImports`. This is additional checking in Lean's own implementation, not a second independent proof assistant or an exhaustive reconstruction of imported Mathlib. The English-to-Lean mapping is separately reviewed, not kernel-certified as a translation.

## Rejections and metadata

Ten new negative controls cover local-versus-global error, missing strict stability, nilpotent switching, horizon exchange, dropped negative prehistory, omitted nonlinear interactions, incorrect weighting, consensus confused with correctness, an ambient metric substituted for a pullback metric, and loss of the polynomial domain condition. All old controls remain unchanged. Every accepted rejection has a mathematical proof diagnostic, not a missing import, identifier or timeout.

The 69 metadata checks cover source identities/counts, every frozen proposition hash and Lean target, unchanged predecessor records, the exact root/build order, axiom-parser failure modes, all controls, retained scope qualifications and the exhaustive nonoverlapping 57-proposition roadmap. They are not additional mathematical proofs.

## Development failures and repairs

The development directory contains 93 completed invocation records: 68 successful compile/interface runs, 15 failed compile/interface runs and 10 expected new-control rejections. No development subprocess timed out. Baseline compilation of inherited modules is included in those counts. Full source snapshots and diagnostics remain in `verification/development_block8/`, with a classified summary.

Early failures involved pinned library names, continuous-linear-map and multilinear interfaces, finite-sum/product rewriting, implicit fields, real division needing a noncomputable declaration, integer casts in the initialized memory example, norm/inner-product notation and redundant tactic warnings. The actual previous-time identity was used rather than replacing integer indices by truncated natural subtraction.

The class-valued pullback-norm definitions were marked with Lean's instance-reducibility attribute. A concrete atlas example initially selected an ambient subtype metric despite a local norm instance. The example was corrected to state the intended decoded pullback distances explicitly. The general induced-metric theorem was retained; an ambient-isometry claim is now an intentional false control. No warning, heartbeat, recursion or axiom policy was relaxed.

The first updated metadata check retained obsolete previous-block increment constants. It rejected the mismatch. Those constants were corrected to ten new modules, ten controls and the correct predecessor theorem count. The failing checker source and actual diagnostic are preserved under `verification/metadata_development_block8/`. No proof or negative test was removed to obtain a pass.

## Runtime and lineage

The seven available offline parts were streamed and the complete archive hash checked before restoration. `verification/runtime_restore_block8.json` records successful completion and SHA-256 `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`.

Lean is 4.34.0-rc2 at commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, with Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The actual Python version is `3.13.5 (main, Jul 15 2026, 20:25:40) [GCC 14.2.0]` on `linux`. Runtime binaries are not redistributed. No Windows/WSL wrapper execution or fresh online Lake resolution is claimed.

The preserved immediate predecessor ZIP has SHA-256 `800572fed039be6dc212f3c760bea72f9882da97c1301d3b2612e05398c32ffc`. It contains the older archives, which are not redundantly copied at the current top level. Historical reports retain their versions and original statuses. The frozen source hashes and active inherited file hashes are recorded in `SOURCE_LINEAGE.json`.

## Delivery and open scope

The archive contains cumulative proofs, exact inventories, frozen source, guides, progress, controls, the verifier, the unchanged immediate predecessor and verification records. Project compiled objects, runtime binaries, Python caches and temporary API probes are excluded. Hash checking must precede regeneration of reports and caches.

The exact delivered ZIP is extracted separately and fully verified without copied project objects. Its actual outcome, ZIP hash and complete pre-replay inventory are in the separately delivered verification JSON. That report is external to avoid a self-referential checksum; this source-candidate audit alone does not establish an unexecuted extraction.

No production-code verification, model training, empirical statistical coverage, sensor experiment, independent referee review, second proof assistant, license change or publication is claimed. P14–P17 and P25 are next. All 57 outstanding mappings remain explicit.
