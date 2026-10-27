# Komorebi Space certified-repair continuation — 1.6.0

**Recorded:** 2026-10-12T18:50:22.511840+00:00

## Delivered result

The monograph has **133 pages**, up from 125, with six parts, 35 numbered sections and five appendices. The visual guide has **43 pages and forty plates**. The Lean/evidence guide has **36 pages**. The reader set totals **212 pages**. Two new chapters, four plots and three solved problems develop certificates for an inexact protected regularized correction.

## Mathematical review and new development

The prior WR01–WR12 arguments were checked for the distinctions they require: weak versus strong convergence, fixed-budget attainment versus closedness of the full range, projected-data attainment, the actual restricted adjoint, the two escaping limits, and the matched-budget diagonal argument. Their verification labels were not promoted collectively.

WR13 proves correction, fit and objective-error bounds from the actual Hilbert normal residual. The constants are 1/alpha, 1/(2 sqrt(alpha)), and 1/alpha respectively, with the objective bound applied to the squared normal residual. A scalar counterexample shows why vanishing fit, normal residual and objective alone need not make a proposal track the optimizer when alpha vanishes.

WR14 proves the exact two-square primal/dual gap, weak duality, attainment at the constructed optimizer's residual, and a correction-distance bound for an arbitrary dual witness. The protected rational example explicitly separates an objective excess of 1/48 from a certificate gap of 1/32.

WR15 derives the actual coordinate-covector metric q^T G^-1 q and its invariance under a full invertible basis change. This remains a written matrix proof, with exact finite tests. WR16 combines data, solver and regularization bias. Its pointwise inequality is formal, while its convergence step still uses written WR08. The explicit diagonal stopping rule retains 0 < delta <= 1 and its ceiling convention.

## Fresh focused formal verification

Three new modules contain **51 explicit named theorems and lemmas** and **10 indexed constructions**, including auxiliary results. They construct the positive-parameter optimizer through an actual coercive normal operator, prove the certificates, and instantiate them on the existing `ProtectedHilbertRepair.restricted` operator. The restricted adjoint is proved to be the projected ambient adjoint. The manuscript's inverse argument and Lean's coercive-form proof are documented alternative routes to the same stated construction.

The accepted run is **focused2**, bound by `audit/extension/release.json`. It cleanly compiles all **7 targets**: three new modules, three actual inherited dependencies and the root. It audits **223 module-origin declarations**, including **97** from the new modules and generated declarations. Only `propext`, `Classical.choice`, and `Quot.sound` occur. No unsafe production declaration is admitted. One positive regression file and four compiler rejection cases plus one custom-axiom policy case pass their intended checks.

Four groups have complete focused counterparts: WR06, WR07, WR13 and WR14. WR09 and WR16 have partial pointwise coverage. Ten groups remain written-only: WR01–WR05, WR08, WR10–WR12 and WR15. The scope resolver checks **30 exact references** against actual imported declaration types and source hashes. This is editorial correspondence, not machine translation of prose.

All **156 canonical formal-tree files** are unchanged. Their retained accepted cumulative result is still version 1.2.0: 138 production modules and root, 139 compiler targets, 4,745 audited declarations and 1,507 explicit named theorems/lemmas. No new successful full cumulative replay is claimed. The original 80 KS items and 211 source references retain their original coverage.

## Exact software and fresh finite checks

The proposal verifier `examples/inexact_repair_certificate.py` does not call an exact optimizer. It accepts exact rational data, validates the entire protected kernel basis, retains its Gram metric, preserves the observable, and distinguishes measured fit from the actual candidate residual. It supports arbitrary dual witnesses, squared error certificates and record recomputation. Consistency with the included problem is not authentication that it is the externally intended task.

Seven freshly rerun suites pass **197,482 assertions**. The new suite contributes **18,728**: 1,458 candidate comparisons with an independent ambient determinant oracle, 909 arbitrary dual witnesses, 286 basis changes, 144 scalar solver/data cases, and eighteen structured 3D/4D/redundant-prescription cases. It rejects ten stronger claims, twelve invalid inputs and four tampered output records. These finite checks do not supply universal Python refinement or infinite-dimensional proofs.

## Publication and visual review

The accepted publication run is **build03**, with terminal exit code zero. All three PDFs pass the recorded preflight, with embedded fonts, no overfull boxes, undefined references, off-page text or replacement characters. All **212 final pages** were rendered. New chapter equations, four plots, coverage tables, workshop additions, source appendix and front matter were inspected through contact sheets and selected enlarged pages. The record identifies those inspected pages rather than claiming another line-by-line audit of every inherited page.

The final layout removes one one-line continuation and two short appendix continuations without reducing the body font. Figure annotations were moved clear of the plotted curves and neighboring labels. The final PDF and rendered-pixel hashes are in `audit/visual_review.json`.

## Failures preserved and corrected

The current cumulative attempt `baseline16` was explicitly stopped before completion and remains **INTERRUPTED**, never an accepted full replay. Draft proof work encountered source-root/import lookup failures, coercion and rewrite errors, unused-assumption linter failures, a misplaced `omit`, and command-window interruptions. The failed snapshots and logs are retained. No theorem was admitted to bypass a failure.

**focused1** compiled all seven targets, then its axiom export exceeded a 300-second command limit. It remains **FAIL**. For focused2, the audit still inspected every project declaration's axioms, while expensive type rendering was limited to new theorem statements and the export received a longer time window. The full second execution and every control completed successfully.

**build01** failed the unchanged-canonical-file check because disposable compiler objects remained under the canonical tree. Hash comparison showed that all 156 original files were identical. The scratch objects were moved outside the tree, with the preservation guard unchanged. **build02** passed mechanically but was superseded after review found short continuation pages. **build03** produced the final reviewed files.

## Remaining boundaries and restart

The official pinned Lean kernel/compiler and imported caches remain trusted. Mathlib was not independently rebuilt, no native Windows run or independent kernel was used, and the exact Python program is tested rather than universally refined against Lean. The focused proof record is not a cumulative integration certificate. Universal view doctrines, general higher stacks, unrestricted semantic realization and the remaining written WR groups retain their stated boundaries.

Start with `PROGRESS_LEDGER.md` and run `python3 checks/verify_payload.py`. New focused proof work uses a fresh label with `extension/scripts/verify.py`. A changed source cannot inherit an old successful record. Read `BUILD.md` and `FORMAL_SCOPE_REVIEW.md` before broadening a verification claim.
