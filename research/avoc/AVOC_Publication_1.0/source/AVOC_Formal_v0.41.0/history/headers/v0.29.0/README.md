# AVOC Formal v0.29.0 — certified affine factorization

Cumulative semantic-feedback branch, extending v0.28 without changing its 140 non-audit Lean modules.

This release adds a checked rank-factorization certificate over fields, minimum two-stage dense-tariff selection, and a metered GF(5) candidate generator. The proposer is Python; the acceptance and optimality contract is proved in Lean and its checker is executed on every accepted candidate.

Start with `FORMAL_THEORY.md`, `PROOF_BOUNDARY.md`, and `REPRODUCE.md`.

- 49 new theorem/lemma declarations; 1,548 cumulative (includes helpers/examples).
- 161 local compilation targets checked against the pinned dependency cache.
- 80 substantive negative proof tests; 960 exact runtime requests.
- Read-only: no deployment, durable promotion, external proof registry, or arbitrary-code execution.

Run `python tools/factor_affine.py examples/factorization/rank_one.json` after the documented build. Runtime binaries/caches are not included. Exact minimum width is not a globally cheapest arbitrary circuit or a measured physical speedup.
