# Komorebi Space progress ledger — v1.9.0

Checkpoint: `KS-v1.9.0-full-monograph-proofread`.
Parent: `KS-v1.8.0-WR01-WR02-complete`. The prior ledger remains unchanged in `history/v1.8.0/`.

## Completed in this edition

- Proofread all 29 chapter and appendix files, frontmatter, concordance, bibliography, tables and figure text.
- Disclosed and corrected local mathematical wording/hypothesis issues, including coordinate metrics, linearity, index endpoints, the zero-bound proof branch and both WR14 optimizers.
- Synchronized accepted v1.8.0 formal evidence throughout the full monograph.
- Built and reviewed the 166-page PDF. All final pages are covered: 153 identical to inspected candidate1 pages, thirteen changed pages inspected again.
- Preserved the formal source snapshot, raw accepted evidence, historical finite reports, prior reader set and prior ledger unchanged.

PDF SHA256: `c206ccac893366e2747126e584cf9ca9a4131a051e54d8c6109b3b220a44ece4`.

## Current mathematical evidence boundary

| State | WR groups |
|---|---|
| Complete formal counterparts | WR01, WR02, WR06, WR07, WR13, WR14 |
| Partial formal coverage | WR09 and WR16; pointwise estimates formal, limiting consequences written |
| Written-only | WR03, WR04, WR05, WR08, WR10, WR11, WR12, WR15 |

The accepted v1.8.0 final environment has 144 production modules and three roots, with 4,872 audited declarations. It combines a clean 144-target baseline with a four-target incremental continuation. This edition performed no new Lean run and did not rerun the retained 197,482 finite assertions. The printed weak-subsequence lemma remains a written argument.

## Failures and corrections

The initial PDF attempt used the wrong output directory and produced no PDF. Correcting the directory resolved it. Naive delimiter checks misread table row-spacing escapes; control-aware scanning resolved those false diagnostics. Initial source-callout and frontmatter layout changes were insufficient; revised anchoring and condensation passed final review. Harmless search/patch mismatches were recovered with exact text operations. Figure-title collision, image-set legend, interrupted floats, split summary box and short spill page were corrected. All evidence is retained in `audit/` and `reviews/`.

Thirteen underfull-line diagnostics remain accepted after visual review. Normal section-ending white space and readable table/proof continuations remain. No identified clipping, overlap, unreadable mathematics, missing glyph or unresolved reference remains. This is a complete proofreading pass with focused checks, not a new global referee audit.

## Restart point

The full-monograph proofreading and evidence synchronization are closed for v1.9.0. The historical 43-page Visual Guide and 36-page Lean Guide are retained unchanged; updating them as new editions remains open. For formal research, the next block remains WR03 budget attainment/profile, then WR04 dual certificates and WR05 robustness, using the accepted projection bridge. Preserve all existing evidence and record new work as a subsequent checkpoint.
