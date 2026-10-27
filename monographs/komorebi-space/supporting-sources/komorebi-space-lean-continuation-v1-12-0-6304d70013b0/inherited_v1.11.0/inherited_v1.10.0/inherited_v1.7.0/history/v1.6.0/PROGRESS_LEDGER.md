# Komorebi Space publication and focused formalization ledger

**Version:** 1.6.0  
**Date:** 12 October 2026  
**Status:** Certified-inexact-repair expansion and separately verified focused regularization extension.

## Authoritative predecessor and source policy

Begin with `Komorebi_Space_Complete_v1.6.0.zip`. The predecessor was v1.5.0, whose SHA-256 is `0841e56c46dd281f340df15706321b098a6939d4180b94a3ae40db3db304e564`. Its 1,643-file manifest was verified before editing. `history/v1.5.0/` preserves its publication sources, checks and records.

All 156 canonical `formal/` files remain unchanged. Their accepted cumulative formal baseline is v1.2.0. The new code is in `extension/`, not silently merged into that canonical source tree. Its entrypoint is `extension/KomorebiSpaceRegularization.lean`, and its accepted record is `audit/extension/release.json`.

## Completed in this block

| Workstream | Result |
|---|---|
| Reader set | Monograph 133 pages, visual guide 43 pages, Lean/evidence guide 36 pages. |
| Exposition | Two new chapters on a posteriori normal-residual bounds, quadratic primal/dual gaps, coordinate covectors and solver stopping rules. |
| Visuals | Forty mathematical plates, including four new reproducible vector plots. |
| Workshop | Fifteen problems with complete solutions. |
| Formal extension | Three new modules and their actual three inherited dependency modules, plus the root. |
| Fresh compiler | 7/7 targets in the accepted clean focused replay. Not a full cumulative canonical replay. |
| Axiom audit | 223 declarations from the six production modules, including 97 from new modules. Standard permitted axioms only. |
| New explicit inventory | 51 named theorems/lemmas and 10 constructions. Includes auxiliary statements. |
| WR coverage | WR06, WR07, WR13, WR14: complete focused counterparts. WR09, WR16: partial pointwise coverage. Ten groups remain written-only. |
| Exact software | Proposed-correction verifier, actual protected kernel and Gram metric, arbitrary dual witness, squared error certificates, tamper checks. |
| Finite checks | Seven suites, 197,482 exact assertions, including 18,728 new assertions. |
| Preserved KS coverage | 80 items and 211 source references retain their prior accepted correspondence. |

## Verification boundaries

The newly accepted run is delimited by its actual imports and module-origin declaration audit. It does not imply a new successful compilation of all 138 canonical modules. The official pinned Lean kernel/compiler and dependency caches are trusted, and mathlib was not rebuilt independently. No native Windows test was run. Source correspondence is editorial, not machine translation of prose. The exact Python verifier is tested rather than universally verified against Lean.

WR01–WR05, WR08, WR10–WR12 and WR15 remain written-only. WR09 and WR16 retain written convergence consequences even though their fixed-parameter estimates are formal. The existing KS54–KS58 obligations stay closed. No universal-view, higher-stack or unrestricted semantic-realization result is inferred.

## Failures and interrupted work

The cumulative attempt `audit/formal/baseline16/` was explicitly stopped before completion. Its status remains INTERRUPTED; it contributes no accepted cumulative PASS. Development source-root and imported-object lookup errors were corrected. Proof development retained linter failures for an unused positivity parameter and an unused completeness instance, coercion and rewrite errors, a mispositioned `omit`, and timed-out command windows. No source theorem was admitted or new axiom introduced to bypass them. The first focused replay compiled all seven targets, then its axiom export exceeded a 300-second command limit and remained FAIL. The accepted second replay retained an all-declaration axiom audit, restricted expensive type rendering to the new theorem statements, and allowed a longer audit window. It completed all seven targets, all 223 declaration audits, and every positive and rejection control. The first publication build also failed the original canonical-file preservation guard because disposable compiler outputs were still under the canonical tree. All 156 original files were unchanged. The scratch outputs were moved outside that tree, without weakening the guard, before the next build.

The first visual inspection found a curve crossing the minimizer annotation in the objective plot. The label was moved into open space and the figure regenerated. All later publication attempts, final rendering and delivery checks are listed in the review record.

## Exact restart

Run `python3 checks/verify_payload.py` before editing. For publication work, preserve KS01–KS80 and WR01–WR16, and run `bash build.sh`. That command checks source-bound accepted evidence and finite tests but does not itself launch Lean. Render and inspect the new PDFs, then renew hashes last.

For focused proof work, edit only the appropriate extension and run `python3 extension/scripts/verify.py --runtime /path/to/runtime --label NEW_LABEL`. Preserve old receipts and bind only a terminal PASS. For a full combined library release, make a separately versioned integration plan and perform its complete replay. Do not relabel the focused record as cumulative evidence.
