# Komorebi Sufficient Resolution v0.16.0

Cumulative Lean 4/Mathlib formalization of exact/approximate sufficient representation,
hidden-return dynamics, globalization obstruction, reconstruction and regularization,
discrepancy certification, uncertain forward operators, source-bound-free discrepancy,
and calibration-generated operator-error certification.

Current inventory: **998 theorem/lemma declarations, 93 production proof modules,
1159 enumerated named declarations**. Counts include helpers/examples and are not novelty
counts. See `PROGRESS.md`, `BLOCK_16_THEOREMS.md`, and `VERIFICATION_SUMMARY.md`.


## Final-edition replay and provenance

All 93 production Lean files are unchanged from the frozen checkpoint. The generic
verification driver and top-level metadata are amended for this paper edition.
Read `PORTABLE_REPLAY.md` and the current `VERIFICATION_SUMMARY.md`. Original
metadata and the original generic driver are preserved in `inherited_provenance`.
Current bounded finite evidence is in the release-level `verification` directory.
No fresh Lean build is claimed because the separately required runtime could not
be recovered in this session.
