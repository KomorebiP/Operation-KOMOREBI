# Paper VIII: final publication review

**Packet Operator Algorithms, Exact Compilation, and GPU Realization**  
Komorebi P.  
**Release closure: 10 October 2026. Book edition: 9 October 2026.**

## Decision

The three-volume publication set is complete within its stated internal review
scope. The recovered 9 October package already contained the substantive
proofreading record. This closure verifies preservation of that reviewed
mathematics, reruns the available tests, rebuilds the PDFs, reviews the rendered
pages and reconciles the delivery metadata. It does not add or strengthen a
theorem merely by marking the publication complete.

| Volume | PDF pages | Contents |
|---|---:|---|
| Traditional monograph | 124 | Complete main manuscript, six substantive proof supplements, integrated worked visual atlas and references |
| Visual guide | 34 | 32 worked pages and 30 editable mathematical plates |
| Lean and evidence guide | 94 | 61 exact source excerpts, the 56-result correspondence and all 458 named theorem/construction audit entries |
| Total | 252 | Three coordinated reader volumes |

## Mathematics and source preservation

All seven mathematical part files remain byte-identical to the predecessor.
So do all 258 editable mathematical markup files and all 1,062 archived
scientific source files. The manuscript retains its 85 numbered mathematical
records and 56 explicit main proof bodies. All six supplements retain their
complete substantive mathematics. These overlapping units are not independent
discovery counts.

The complete ordered extracted body-text sequences of all three PDFs are
unchanged after rebuilding. Their respective token counts under the recorded
body-region comparison are 37,296, 9,723 and 21,685. The comparison excludes
running headers and footers equally from both copies. Source byte comparison
provides the stronger independent preservation check for the authored text.

The earlier proofreading record is retained at
`verification/monograph_proofread_report.md`. Its review was internal and
bounded, not independent external refereeing. This closure does not relabel it
as a new exhaustive proof audit.

## Fresh execution

All twelve bounded replay gates passed. Each has an actual command, input/output
hashes, result, runtime and validation record under suffix `20261010_release`.

| Check | Recorded result |
|---|---|
| Actual pytest session | 34 passed, 0 failures, 0 errors, 0 skips, confirmed from JUnit XML |
| Verifier unittest suite | 43 methods passed |
| Original deterministic suite | 37,392 assertions in 9 groups passed |
| Original symbolic visual examples | 190 assertions and 11 rejected invalid controls |
| Independent portable visual examples | 208 exact assertions and 15 rejected invalid controls |
| Traditional exact examples | 74 rational assertions and 5 rejected invalid controls |
| Small-core numerical mirror | 638 truncation cases, 3,190 sampled rank-bounded competitors |
| Mathematical vector generator | 30 plates regenerated, with the two previously documented authored header-position adjustments kept explicit |
| Historical corpus arithmetic | 154 stored rows, 264 ratios and 146 logical-throughput fields recalculated |

The structured-transform and fifth-block graph/solver mirrors also passed.
These numerical and exact example families overlap, so their counts are not
summed. Direct invocation of 34 functions and the pytest run cover the same
archival tests. The original deterministic total includes 778 corpus-metadata
and 26 source-integrity assertions. Sampled numerical agreement is not a
universal theorem or a GPU benchmark.

## What failed, and its resolution

**The first strict PDF replay did not reproduce the saved Lean guide's per-page
extracted text.** Its 94-page count was unchanged, but 16 pages had body lines
move across page boundaries. Raster comparison detected positioning changes on
33 pages overall. The complete ordered body-text sequence was identical. The
precise environmental cause of that reflow was not independently isolated.

The new Lean pagination was reviewed and all three rebuilt PDFs were refrozen.
A second isolated build then reproduced all three final PDFs **byte for byte**,
with identical page counts and exact per-page text. The failed comparison,
body-conservation check and successful final replay remain separate artifacts.
Traditional and visual-guide renders are pixel-identical to the predecessor.
No mathematical text was altered to force a passing result.

The test-report wrapper also contained an inaccurate hardcoded statement that
pytest was unavailable. That wording is corrected. The actual pytest gate now
reads collection, failure and skip totals from JUnit XML instead of reporting
an assumed count. Previous historical failed dependency attempts remain dated
historical records.

A dangling BibTeX command was handled by an explicit working fallback. Font
files are no longer bundled. Builders resolve compatible locally installed
fonts, verify meaningful table fingerprints, stage them temporarily and fail
clearly when dependencies are missing. No download or installation is hidden
inside the builders.

## Layout, navigation and reproduction

All 252 final pages were rendered. Every page was inspected on one of 22 contact
sheets. Sixteen selected dense or changed pages were also checked at 150 dpi,
including the Lean proof continuations and complex/quantized visual examples.
No unresolved clipping, plot-label collision or missing mathematical glyph was
found in this review. This is not a claim of full-size visual inspection of
every page.

Automated page geometry found no out-of-page text boxes or replacement
characters. Final build logs contained no missing-glyph messages, undefined
references/citations or overfull boxes. Nonblocking underfull-box and
unicode-math command-override warnings remain recorded.

The publication consistency check passed for nine active PDF copies, 441
canonical labels and aliases, 230 companion locators, 372 internal links,
1,320 source/markup pins, all twelve current bounded manifests and all seven
mathematical parts. All three final PDFs pass the isolated byte-identical replay.
Build and replay instructions are in `BUILD_AND_REPLAY.md`.

## Formal and empirical boundary

The accepted Lean compilation remains the inherited 6 September 2026 run. Its
registered finite coverage is 56/56 items under their stated hypotheses, with
392 theorem declarations across 40 modules. Nineteen declarations are reused
foundation results. The 66 construction audits are counted separately. Four
classical inputs remain explicit.

No new Lean/Lake kernel execution occurred here. Static comparison verifies
sources, declarations and saved logs, not the kernel again. The ordered-thin-SVD
result does not establish general SVD existence, a verified numerical QR/SVD
implementation, or canonical singular-values API identification.

No new GPU timings or CUDA verification occurred. Recalculated historical ratios
do not fill missing source-array fingerprints, correctness-reference fields or
complete timing provenance. No external peer review or historical-novelty audit
was performed.

The three wider research targets remain open: unrestricted profitable structure
discovery, compilation with nonlocal/overlapping candidate models, and a packet
communication theorem for a specified architecture. Those are not silently
absorbed into the finite result count or the publication sign-off.

## Delivery record

The current machine-readable receipt is `verification/RELEASE_CLOSURE.json`.
Current evidence is under `verification/closure_2026-10-10/`. Prior PDFs,
metadata and relevant replaced scripts are preserved under
`provenance/closure_2026-10-10/`. The global SHA-256 manifest covers every delivered
file except itself. Original scientific archives remain included. Only Paper
VIII is changed by this release.
