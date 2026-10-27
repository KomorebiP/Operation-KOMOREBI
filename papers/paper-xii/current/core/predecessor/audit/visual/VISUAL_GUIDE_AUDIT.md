# Final visual guide audit

Author: Komorebi P. · Finalized: 2026-10-06.

The final standalone guide has **27 complete topics on 27 pages**. It preserves the earlier 18 worked topics and adds nine focused explanations. Every page was inspected in full-page contact sheets generated from 140 dpi renders; the revised diagrams on V-13 and V-25 were inspected at full size. An independent companion reviewer inspected all pages and the final provenance/math wording, with full-size checks on V-2, V-4, V-7, V-17, V-19, V-23, V-26 and V-27. The final navigation correction changes no rendered page pixel.

## Frozen artifacts

- PDF SHA-256: `9cd5d6d3c3974deae2a2720a6dabed700817ffeb8b2331d96b514b2d6e74e94a`.
- Main TeX SHA-256: `ef0475d5d3f14c8175ac24e6eb4f9492f6815e86c5f86b1de0d3fd6718a054d7`.
- Pages TeX SHA-256: `dfa2a300040e03f6e3fe4dd2fb6dcabb1fe8af8072b1bb383aad8163b4a5d064`.
- Figure generator SHA-256: `40587860286b3da2adfbbc178abf4160fc3f847644972c805edf040e5c920641`.

## Mathematical and source scope

The guide was checked against the entire revised v0.17.0 manuscript and the entire earlier worked-guide source, its generator and checker, together with v0.17.1 status/claim records. Exact source labels and current source-line anchors are in `SOURCE_COVERAGE.md` and `checks/SOURCE_ANCHORS.json`. All 49 internal claims have reading entries; three numbered examples and eight external standard facts are kept outside that census.

The historical revised record is 49 complete / 0 partial / 0 unchecked; the original-wording record is 41 complete / 7 partial / 1 unchecked. Original 6.12 is the historically unchecked claim, while 10.5 is historically partial. The current mathematical audit refutes the reversed containment in original 6.12 and identifies incomplete effectivity in original 10.5. These judgments are separate from inherited verification labels. The eight inherited amendments remain 6.12, 9.4, 9.5, 9.6, 10.5, 12.2, 12.4 and 12.6.

Final editorial clarifications expose finite S, coherent Frobenius normalization, the local coefficient-test category, the Fitting r>n boundary and both ordinary-completion Frobenius polynomial identities. No new Lean replay is claimed for those clarifications or for this guide. The arithmetic inputs—representability, residual occupancy, applicable patching, classicality, attached representations and existing families, Frobenius density, semisimplification and Brauer–Nesbitt—remain explicit inputs.

## Mathematical proofreading self-review

Applied the mathbox `proofread-math` self-review workflow to the entire authored/changed guide, with surrounding source definitions and theorem labels.

- Routine corrections: closed a TeX quote, corrected historical item-status attribution, replaced a misleading named presentation-independence reference by the intrinsic property, used “representability” consistently, removed a stale manuscript page count, and separated historical/fresh evidence language.
- Mathematical-token corrections in proofreading: none. Newly authored example expressions were separately checked by exact arithmetic and source-aware mathematical review.
- Printed formulas, variable roles, degree conventions, topology names, matrices, field characteristic restrictions and source numbers were checked. Two graphic label collisions were corrected. Fixed-carrier stabilization is distinguished from stable cores and infinite tails; compatible classes from actual representatives; quotient geometry from Artin idempotents; pointwise arithmetic from universal existence.
- Unresolved guide issues: none found within this scope. External arithmetic hypotheses are neither proved nor removed by the visual examples.

## Exact illustrative assertions

`checks/verify_examples.py` passes **46 assertions**: 31 inherited illustrative checks plus 15 additional checks. It exhaustively enumerates the stated 625 order-three test-ring candidates, checks the stated symbolic minors and CRT polynomials, exact modular matrices, explicit basis data and uniform identities. Finite horizons are reported as bounded checks; all-level conclusions have algebraic arguments in the text. Assertion counts do not represent general theorem counts or a new Lean certificate.

Tested with Python 3.12.14, SymPy 1.14.0, PyMuPDF 1.26.6 and pdfTeX 1.40.25 (TeX Live 2023/Debian). The default runtime lacked SymPy; a pre-existing local dependency directory supplied it through PYTHONPATH. That environment-specific directory is not hardcoded into the builder. Declared requirements are included.

## Document preflight and reproducibility

- Zero overfull boxes, underfull boxes, unresolved-reference warnings or missing-character messages.
- Zero raster image objects on all 27 pages and on all 22 separately generated vector figure PDFs.
- Text stays inside the page-safe bounds; vector drawing rectangles stay inside the media box.
- All 35 font objects are embedded.
- All 27 outline items point to their correct topic pages; all 28 internal guide links resolve to valid pages.
- An inherited appendix destination-prefix bug was corrected for the standalone guide: explicit bookmarks now open the intended page rather than page one.
- The portable `build.py --output-dir` regenerates figure sources and vector PDFs in the requested directory. Fixed dates, metadata and trailer behavior make the two-directory rebuild byte-identical in the tested environment.
- Final isolated comparison: **27 page texts and 140 dpi renders identical, PDF bytes identical, all 44 vector .tex/.pdf files byte-identical**. `checks/compare_builds.py` reproduces this comparison.

The layout, finite calculations and rebuild checks are supporting evidence for this explanatory artifact. They do not verify universal arithmetic existence or upgrade an inherited proof contract.
