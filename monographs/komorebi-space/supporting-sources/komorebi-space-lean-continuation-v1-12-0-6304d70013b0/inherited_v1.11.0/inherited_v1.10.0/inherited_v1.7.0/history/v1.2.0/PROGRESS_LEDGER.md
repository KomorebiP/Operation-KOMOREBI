# Komorebi Space publication and formal progress ledger

**Version:** 1.2.0  
**Date:** 11 October 2026  
**Status:** The identified core release obligations are complete.

## Authoritative baseline and current closure

This edition continues `Komorebi_Space_Complete_v1.1.0.zip`. Its SHA-256 is `7f49dd467fab7baa7a2bf7261c1bbcb0d461ab9d9ad7bf9cdecedb58e7ad58d5`. The prior publication source and audit snapshot is `history/v1.1.0/`. All four original mathematical source/evidence archives remain unchanged.

The canonical project is `formal/KomorebiSpace.lean` and `formal/KomorebiSpace/`. It contains **138 production modules plus one root**. All 133 inherited production modules retain their original source bytes, counting the shared byte-identical module only once. Five new modules formalize KS54–KS58.

## Completed obligations

| Workstream | Current result |
|---|---|
| Runtime | Seven-part portable archive restored with payload/stream checks; actual Lean version and all nine dependency revisions checked. |
| Combined compiler replay | **139/139 targets PASS** in the accepted empty-build-directory replay `replay2`. |
| Axiom audit | **4,745 project declarations audited**, including generated declarations. Only `propext`, `Classical.choice`, and `Quot.sound` occur. No unsafe project declarations. |
| Explicit source inventory | **1,507 named theorem/lemma declarations**, including auxiliary results. |
| Five additions | **54 named theorems/lemmas and 17 indexed constructions** across the five new modules. |
| KS54 | Actual nonempty prefixes, empty original point/ambient types, and absence of a matching prefix family. |
| KS55 | Actual varying-fiber dyadic support, reconstruction coordinates, and valuation threshold. |
| KS56 | Feasibility, unique nearest protected repair, Pythagorean identity, restricted closed-range criterion, and least gain. |
| KS57 | Arbitrary-field exclusive certificate alternative, literal normalized row witnesses, affine ambiguity, and matrix rank-nullity. |
| KS58 | Original point/section equivalence, finite-fiber existence, and persistent-image extension criterion. |
| Controls | One positive regression file passes; 6 false/placeholder/compiler controls and 1 custom-axiom policy control are rejected as intended. |
| Principal source concordance | **58 items, 139 source references, 0 written-only principal items**. Names and hashes are bound to the accepted current environment. |
| Finite computation | **34,204 exact assertions** across the three rerun suites. |
| Reader set | Monograph 57 pages, visual guide 21 pages, Lean/evidence guide 23 pages. |
| Publication review | All pages rendered and reviewed; final PDFs bound to mechanical preflight and visual-review hashes. |

## Failed attempts retained, not promoted

The initial inherited-source development build passed. The first complete integrated attempt, `replay1`, compiled all 139 targets and passed its axiom audit, then failed its positive regression examples. It remains **FAIL**. The fixture issues were an obsolete matrix-notation import path, insufficient reduction by `decide`, and missing type/finite-fiber instance annotations. Those were corrected, independently checked, and followed by the accepted clean replay.

New-proof development also encountered reserved-name syntax, unused-section-variable warnings, coercion rewrites, inner-product notation, a nonexistent provisional matrix constructor, and typeclass elaboration issues. No positive-source theorem was admitted to bypass a failure. Draft snapshots and actual logs are retained under `audit/formal/development/`. Early direct draft tool windows timed out without a terminal result; those are not pass evidence. Unsupported interactive streaming was replaced with supervised ordinary subprocesses.

## Scope still excluded

The official Lean compiler/kernel and pinned imported caches remain trusted. Mathlib was not rebuilt independently. The prose map is an editorial correspondence, not a machine-certified translation. Some illustrative calculations remain written examples rather than separately named Lean theorems. The Python program has tested exact certificates, not a universal Lean refinement or complexity theorem. The broader universal-view, infinity-stack, unrestricted semantic-realization, and arithmetic/physical targets are not asserted.

These boundaries are not uncompleted KS54–KS58 obligations. **No item remains open on the identified five-item completion list.**

## Reproducible restart

Begin with this v1.2.0 package and run `python3 checks/verify_payload.py` before changing anything. For a new formal replay, supply the pinned portable runtime to `formal/scripts/verify.py` and use a fresh label. The verifier refuses to overwrite old replay directories. Bind only a terminal PASS record, then rebuild the reader set and review the new rendered PDFs. Preserve the stable KS identifiers and all historical source archives. See `FORMAL_SCOPE_REVIEW.md`, `BUILD.md`, and `formal/README.md`.

Final publication corrections include the chart-font embedding warnings, a crowded holonomy label, companion scope labels, and evidence-guide pagination. They were corrected and rerendered; details are in `REVIEW_NOTES.md` and `audit/development/visual_final/`. The final reader set totals 101 pages.
