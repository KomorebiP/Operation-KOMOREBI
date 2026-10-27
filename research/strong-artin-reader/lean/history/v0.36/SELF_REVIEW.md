# Self-review — v0.36

This is self-review plus Lean checking, not independent specialist review.

## Critical checks
- Koenig is applied to subtypes of actual finite levels with proved reduction
  stability. Nonemptiness at every level is an explicit hypothesis.
- The prefix is encoded by every available reduction to its depth; missing lower
  levels are filled by projection from max(prefix depth, requested depth).
- The p-adic limit uses inherited constructions for both matrices and inverse
  matrices. Equality is checked by every positive coefficient reduction.
- Simultaneous nodes contain the shared Frobenius AND every conjugator. These
  witnesses are never selected independently by incompatible limit procedures.
- Local conjugators are identity modulo p and one fixed matrix per prescription.
- No nonresonance or norm surjectivity hypothesis appears in the new capstones.
- No finite test is promoted to all-depth solvability.
- The finite-horizon proof chooses obstruction depths for the finitely many dead
  prefixes, then takes a maximum. Its non-effectivity is recorded explicitly.
- Degree zero, empty matrix index, and empty local family are permitted by the
  formal hypotheses; the generic branch construction does not discard them.
- Direct source provenance is checked byte-for-byte against the exact parent.

## Tests
New Lean controls distinguish multiple genuine branches from a dying finite
branch. The Python checks exhaust their declared finite domains and do not decide
infinite branch existence. Full source replay uses the pinned Mathlib cache.
