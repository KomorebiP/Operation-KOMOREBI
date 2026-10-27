# Unified Inference Lean v0.6.0 — Checked

This release extends v0.5 with the first fully stochastic Brownian-driven theorem block.

All source compiles under the preserved Komorebi Lean 4.34.0-rc2 + pinned Mathlib runtime with warnings treated as errors.  The new affine Itô process uses Mathlib's actual Brownian-motion law and independence machinery.

The result is deliberately scoped: it closes the scalar additive-noise constant-coefficient case (`A=0`) end-to-end.  It does not claim the general matrix linear SDE theorem is already derived from a stochastic integral.

See `STATUS.md` and `logs/` for the exact boundary and audits.
