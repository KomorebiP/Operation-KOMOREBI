# Validation of the final traditional edition

The final manuscript was built twice into two fresh, isolated output directories using `build.py --output-dir`. Each build performed three pdfLaTeX passes and regenerated the bibliography with BibTeX. PDF creation/modification dates are fixed to 6 October 2026 at 00:00:00 UTC; the volatile trailer ID is suppressed. The generated PDF has 37 letter-sized pages.

| Check | Result |
|---|---|
| Independent PDF byte comparison | Identical |
| Extracted UTF-8 text comparison | Identical |
| Page count | 37 / 37 |
| Per-page rendered pixel comparison at 1.4 scale | Identical on all 37 pages |
| Per-page extracted text comparison | Identical on all 37 pages |
| Full-page preflight | Every page rasterized, every text span checked for clipping and side-margin overflow |
| Blank/clipped pages or replacement glyphs | None |
| Unresolved citations/cross-references or overfull boxes | None |
| Embedded fonts | All used fonts embedded |
| Supplied figures | 18 unchanged vector PDFs, no raster images |
| Revised proof preservation | 52 complete proof environments; 50 byte-identical bodies; 2 audited local expansions |
| LaTeX label sequence | All 106 labels retained in original order |
| Preserved raw snapshots | SHA-256 and byte counts recorded in SOURCE_PRESERVATION.json |

Seven contact sheets covering all pages were visually inspected. The final changed pages around the local-point clarification, higher Fitting proof, the forest-admissibility scope, and completion carrier/realization hypotheses were also inspected at full-page resolution. Equations, captions, theorem continuations, bibliography and the boundary table remain legible and inside page margins. Underfull horizontal/vertical warnings from table/paragraph/float spacing were reviewed and have no clipping consequence.

The conservative mathematical proofreading self-review covered the changed front matter, convention note, Proposition 3.3 statement/context, Theorem 6.4 proof boundary, Definitions 10.2, 12.1 and 12.3, Corollary 10.4, and formal-status attribution. Routine edits concerned date, publication metadata, file references, and evidence attribution. Mathematical changes are exactly those recorded in EDITORIAL_CHANGES.md. Separate raw-proof and literature audit findings were incorporated; no remaining blocker was reported for those final edits. No proof was abbreviated. This validation does not claim a new Lean run or a new proof of the external arithmetic inputs.

Detailed build, font, per-page preflight, proof-preservation, toolchain and rebuild reports accompany the collection's audit directory. Temporary compiler output directories and per-page intermediate raster folders were excluded from handoff.

The independent raw-proof audit accepted the final mathematical delta at source SHA-256 `cdf44fec9a3d0c42987bf2e1ef1f489ece658e785077b76d1bef868f9ef02895`: all 49 revised internal deductions reviewed, with internal statement clarifications confined to 3.3 and 10.4 and proof expansions confined to 3.3 and 6.4. No mathematical blocker remained.
