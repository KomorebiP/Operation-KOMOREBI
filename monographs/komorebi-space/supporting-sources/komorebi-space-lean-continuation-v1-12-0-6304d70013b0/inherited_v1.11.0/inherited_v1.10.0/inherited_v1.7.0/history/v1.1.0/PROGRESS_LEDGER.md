# Komorebi Space publication progress ledger

**Version:** 1.1.0  
**Date:** 10 October 2026  
**Status:** Revised publication set completed; cumulative formal integration remains a separate task.

## Authoritative current baseline

Use this edition's `source/Komorebi_Space_Monograph.tex`, the chapter sources, and the two companion sources. The stable exposition identifiers remain KS01–KS54 with KS55–KS58 appended. `data/claim_specs.tsv` generates the concordance. `checks/edition_stats.py` generates the common evidence counts from the current audit results.

The unchanged mathematical source inputs are the foundation v0.20.0 archive, the focused moving-space v0.32.0 archive, their corresponding replay archives, and the separately identified Hilbert holonomy source. The predecessor publication sources and ledger are under `history/v1.0.0/`. The original complete package hash is recorded in `history/PREDECESSOR.json`.

## Completed in this revision

| Workstream | Result |
|---|---|
| Proofreading | Mathematical statements, field assumptions, proof flow, notation, captions, source references, and verification boundaries reviewed. |
| KS28 | Printed dyadic proof outline replaced with a complete scale-uniform parity argument. |
| Written additions | KS55 sharper dyadic support; KS56 nearest protected repair; KS57 finite certificates; KS58 finite-fiber existence. |
| Quantitative descent | Squared estimate and sharper sufficient gain added with two additional actual source references. |
| Exact implementation | Rational protected-repair CLI/API returns feasible answers with ambiguity bases or obstruction certificates. |
| Concordance | 58 principal IDs, 53 source-correspondence items, 114 declaration references, five written-only items. |
| Historical integrity | Four frozen archives pass hash/CRC checks. All 135 historical source files, counting roots separately, match archive and historical replay hashes. |
| Current finite suites | 14,224 + 2,767 + 17,213 = 34,204 exact assertions; all suites pass. |
| Static integration | 134 production copies, 133 distinct modules, one identical shared module, no missing local imports or cycles. |
| Visuals | Eighteen plates, eight generated numeric assets, revised schematics, explicit 3D geometry, clear coordinate/depth and norm conventions. |
| Reader set | Monograph 56 pages, visual guide 21 pages, Lean/evidence guide 22 pages. |
| Review | All 99 pages rendered and reviewed; final mechanical PDF preflight passes. |
| Continuity | Updated review report, build instructions, source-change inventory, manifest, and this ledger. |

## Verification classification

Freshly executed: integrity comparison, exact declaration-name resolution, static local graph checks, three finite suites, figure generation, TeX compilation, PDF preflight, and rendered-page review.

Historical only: the compiler and axiom evidence inside the four frozen archives and retained receipts. Those dates and scopes are preserved.

Not executed: a fresh cumulative Lean compiler run, an imported-axiom audit of the proposed union, or new Lean formalizations for KS55–KS58. The selected Hilbert source is not newly compiler-certified by this edition. The import plan ends in `.lean.txt` to mark it as an uncompiled proposal.

## Corrections and failed attempts

The initial Matplotlib figure build rejected `\ge`; the source now uses `\geq`. Early rendering exposed a clipped axis label, an oversized plot, and poor page breaks. These were corrected and the PDFs rebuilt. The first ZIP manifest-coverage assertion also caught exclusion of the historical manifest by basename; only the current root manifest is now excluded. See `REVIEW_NOTES.md` and `audit/development/` for detail. No positive claim is based on a failed build.

## Exact restart point

For publication edits, retain the current source and stable KS identifiers. Read `REVIEW_NOTES.md`, update the appropriate chapters and source correspondence, then run `bash build.sh`. Re-render and inspect any new PDFs before replacing the hash-bound visual-review record. Regenerate the payload manifest after edits.

For formal integration, start with `audit/static_integration.json` and `data/ProposedKomorebiSpace.lean.txt`. The one duplicated production module is byte-identical. Materialize one canonical source tree without overwriting either frozen archive, choose its entrypoint, restore the pinned Lean/mathlib environment, compile all project modules cleanly, and run exact declaration axiom audits and negative controls. Include the selected Hilbert module. Only a successful compiler and axiom record permits classifying the union as a newly verified release.

For new formalization, port KS55–KS58 as a separately versioned block. Preserve the present written-only status until actual source, compiler evidence, and scope audits exist.

## Mathematical boundaries unchanged

No universal view doctrine, unrestricted semantic essential-surjectivity theorem, complete infinity-stack theory, universal norm convergence for bounded residual hierarchies, or unrestricted arithmetic correspondence is claimed. These are separate research questions, not hidden assumptions used to close the present proofs.
