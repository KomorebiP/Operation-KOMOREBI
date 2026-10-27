# Komorebi Space — Technical Record

This companion preserves the accepted formal verification and the editorial evidence for publication edition 1.13.0. Reader-facing books, sources, and examples are in the separate Publication package.

## Accepted verification

The original v1.12.0 archive and four companion records are retained byte for byte in `accepted_verification/`. They contain the exact Lean sources, verification scripts, command receipts, permitted axiom audit, controls, dependency pins, and earlier research history. The clean run had 156 compilation targets, 5,048 exported declarations, 44 controls, and 238 exact commands.

The original independent archive checker rejected an inherited source/text directory because its exclusion rule was overbroad. A separate recorded amendment retained global compiled-file exclusions while allowing the pinned historical directory names. The amended nine-gate review passed without changing the accepted archive. Both the failure and its reviewed amendment remain in the supplemental archive; the original checker is not represented as having passed.

## Publication evidence

`publication/records/` records the editorial contract and metadata changes. `publication/review/` contains preservation, proofreading, declaration-reference, and visual reviews. `publication/build/` retains actual commands, build results, example output, figure regeneration reports, and final artifact comparisons. `publication/scripts/` contains the coordinator’s reproducible checks. Failed or superseded build attempts are retained with their resolutions.

Production Lean sources were not changed. A strict read-only declaration inspection supplements, but does not replace or repeat, the accepted full verification. The publication is not a new whole-monograph proof audit.

The complete file inventory is in `SHA256SUMS`. The public archive hash and its completed checks are recorded in `publication/PUBLICATION_ARCHIVE_CHECK.json`.
