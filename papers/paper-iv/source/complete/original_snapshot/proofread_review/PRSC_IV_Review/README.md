# Paper IV proofreading review

Read `REVIEW.md` for the findings and verification limits.

`PRSC_IV_Proofread_Draft.pdf` is the corrected 39-page manuscript. Its LaTeX source and bibliography are in `paper/`. The PDF is marked as a proofread draft, not a new verified release. All 95 mathematical label numbers were preserved. No Lean source was modified.

`proposed_manuscript.patch` gives the exact changes against `paper/paper4.tex` in the uploaded v1.0.0 archive. Do not apply the patch and retain the old release checksums as though they certify the modified files. Rebuild and regenerate release metadata before publication.

`theorem_coverage.csv` describes the coverage claimed by the original register and contract. It is not a fresh Lean compilation result. The current environment could not run Lean because `lake` is absent. The saved successful audit was inspected, not reproduced.

The original PDF was not stale in text or rendered appearance: all 39 pages matched a clean rebuild. Its differing binary hash is documented separately in the review and evidence logs.

Author of the underlying manuscript: Komorebi P.
