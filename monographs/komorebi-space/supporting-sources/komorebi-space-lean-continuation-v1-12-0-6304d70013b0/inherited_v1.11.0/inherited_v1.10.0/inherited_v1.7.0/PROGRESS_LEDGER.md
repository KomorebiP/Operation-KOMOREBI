# Komorebi Space proof-exposition ledger

**Version:** 1.7.0  
**Date:** 12 October 2026  
**Status:** Proof-expanded reader set. Formal source scope retained, not recompiled.

## Authoritative predecessor

This edition begins from `Komorebi_Space_Complete_v1.6.0.zip`, SHA-256 `cccd56e8e896b64f89a7521ee29827cdbfd07cd0723419f283d125eecd305bcf`. Its ZIP CRC and 2,057-file payload manifest passed before editing. The predecessor publication sources, checks, metadata and selected top-level audit summaries are retained in `history/v1.6.0/`. Original evidence archives are unchanged.

The canonical `formal/` tree retains the accepted v1.2.0 source closure. The separate `extension/` tree retains the accepted focused v1.6.0 regularization closure. All **169 files across those two trees** match the predecessor inventory. Neither tree was edited. No new Lean compilation or axiom audit was run.

## What this edition changes

| Workstream | Result |
|---|---|
| Main monograph | 161 pages, six parts, 35 numbered sections, six appendices. Previously 133 pages. |
| Existing proofs | 67 blocks expanded: 50 KS results, all 16 WR groups, and the weak-subsequence lemma. |
| Proof scope | Existing principal statements and evidence identifiers retained. The edit audit checks 88 labeled principal statement envelopes and every inherited source label. |
| Background | Five written classical lemmas: convex projection, Riesz representation, Baire's principle, Banach inverse, and Neumann inversion. |
| Companions | Visual guide 43 pages with the same forty plates. Lean/evidence guide 36 pages, synchronized with retained evidence. |
| Source map | 80 KS items and 211 references retained. The focused WR resolver retains 30 references. |
| Formal preservation | 169 files unchanged across `formal/` and `extension/`. No new typed theorem claims. |
| Finite checks | Seven suites rerun. 197,482 assertions per complete run, not a cumulative total inflated by repeated builds. |
| Publication build | `audit/proof_detail/proof_build02.json` is the accepted terminal zero-exit build, superseding the mechanically successful first draft. |
| Review | See `audit/visual_review.json` for the final PDF/pixel hashes and exact inspection scope. |

The proof-by-proof map is `PROOF_EXPANSION_MAP.md`. Its machine-readable counterpart is `audit/proof_detail/proof_inventory.json`. These identify changes to written arguments, not new formal proofs.

## Important logical details now explicit

The revised arguments show how maps land in their claimed fibers, how common finite stages are chosen, where projection surjectivity is needed, and how both inverse identities are established. Effective descent retains the actual overlap gauges and all morphisms. The analytic proofs separate kernel closedness from range closedness, weak compactness from strong convergence, and a projected datum from an attained datum. The diagonal asymptotic controls both improper-sum tails before passing to arbitrary correction budgets.

The analytic appendix supplies the projection, adjoint and inverse tools instead of leaving them as opaque proof steps. It does not eliminate ordinary background real analysis, nor claim new Lean coverage for those printed derivations.

## Coverage remains deliberately nonuniform

WR06, WR07, WR13 and WR14 retain complete focused counterparts. WR09 and WR16 retain formal pointwise inequalities with written limiting consequences. WR01–WR05, WR08, WR10–WR12 and WR15 remain written-only. Expanding their proofs does not promote their evidence status. The earlier KS54–KS58 completion remains closed.

## Failures and review corrections

The interactive build launch was rejected by the container with `StreamingExecNotEnabledContainerError`. It supplied no build result. A supervised ordinary subprocess replaced it. Both complete publication builds returned zero. The first draft was superseded after review found source callouts separated from the end of their proofs. Stronger keep-with-previous penalties were added without changing the body font. Some source callouts still begin continuation pages; the review does not claim every such break was eliminated. A diagnostic wildcard lookup for a nonexistent `checks/*visual*` match returned a nonzero shell status after printing successful build information; it was not a build failure or pass evidence. All accepted results come from their own terminal receipts.

A stale concluding coverage paragraph inherited from an earlier publication was corrected to the actual four-complete, two-partial, ten-written WR split. No principal mathematical statement was weakened or silently changed.

## Next restart

Run `python3 checks/verify_payload.py` before editing. For a proof-exposition pass, retain KS01–KS80 and WR01–WR16, consult `PROOF_EXPANSION_MAP.md`, and update the exact proof-edit inventory whenever a recorded proof changes. Run `bash build.sh`, render the PDFs, inspect them, and renew payload hashes last.

For new formal work, use the existing focused extension with a new verifier label and an actual compiler/axiom replay. Preserve the historical accepted records. A full merged-library replay is a separate obligation and must not inherit the focused scope by relabeling it.

No independent Lean kernel, full source rebuild of mathlib, native Windows replay, universal Python refinement, unrestricted semantic-realization theorem, or general higher-stack doctrine is claimed.
