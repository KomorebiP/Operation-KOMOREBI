# Source indexes and manuscript reviews

The current manuscript has 48 pages. `STATEMENT_INDEX.json` and `.csv` resolve 62 statements to 202 preserved source declarations. The index records the final manuscript hashes. The section maps provide the underlying references.

The fresh reviews for this edition are in `../editorial/`:

- `SEMANTIC_REVIEW.json`: mathematical meaning, corrections and final source binding.
- `COMPLETENESS_REVIEW.json`: coverage of available historical material and completed blocks, with explicit limits.
- `PDF_VISUAL_REVIEW.json`: final PDF hash, page count and visual inspection.

The prior `MANUSCRIPT_REVIEW` and `PDF_VISUAL_REVIEW` files describe the preceding 45-page edition. They have moved to `../../historical/consolidated_pre_proofread/consolidation/audit/`; they are historical evidence, not reviews of the current revision.

`EVIDENCE_INDEX.json`, `DECLARATIONS.csv`, and the retained consolidation notes document the earlier proof frontiers and source recovery. Their historical compiler, external-access and provenance statements keep their original scope. This proofreading edition did not modify Lean sources or rerun the inherited Lean builds.
