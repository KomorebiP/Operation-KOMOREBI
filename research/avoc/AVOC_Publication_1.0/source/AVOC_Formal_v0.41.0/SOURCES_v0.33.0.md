# AVOC v0.33.0 — source and dependency notes

This block does not rely on a new external empirical dataset or literature
claim.  It extends the cumulative AVOC source using the exact pinned Lean and
mathlib revisions recorded in `lean-toolchain`, `lake-manifest.json`, and
`REPRODUCE.md`.

The algebraic specialization reuses the inherited AVOC entry/minor rank proofs,
which in turn use mathlib's matrix rank and determinant infrastructure.  The
runtime regression uses exact locally generated GF(5) matrices and rational
model data under fixed seed `20260914`.

No production LLM traces, calibrated workload frequencies, measured cache
costs, or physical timing claims are introduced in this release.
