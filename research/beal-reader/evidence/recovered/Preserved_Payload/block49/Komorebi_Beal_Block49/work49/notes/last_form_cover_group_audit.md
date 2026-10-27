# Independent finite-group audit of the final-form cover

Verdict: **implementation and finite assertion verified; no mathematical
blocker or coverage gap found within the finite-group scope.**

Audited on 2026-09-19: Sections 3–4 of
`notes/last_form_cover_frontier.md`, frozen at SHA-256
`a2036fc5656430cad7075fd991d91dcf42f37f2a6647ac7d712fccdea3d1680a`,
and the scripts and results listed below. Arithmetic-geometric realization,
descent, specialization and rational points were outside this audit.

## Checks and reproduction

Both scripts were rerun under Python 3.12.14, with outputs written only to
scratch paths. Each exited successfully and reproduced its archived result
byte for byte. The calculation uses exact arithmetic in
F_7[s]/(s^2−5), with determinant-one matrices modulo +/-I.

An additional independent, inline implementation imported neither audited
script nor its finite-field tables. Using direct polynomial arithmetic, it:

- enumerated all determinant-one matrices and obtained all 58,800 projective
  elements;
- filtered the full enumeration by the actual trace equations and matched
  all 48 recorded lifts for each beta, hence all 96 possibilities;
- reconstructed the centralizer of order 24, matched all four recorded
  orbits, and independently generated the full group from each representative;
- verified that the recorded subgroup of order 50 is the full normalizer
  of an explicitly recovered cyclic subgroup of order 25;
- verified centralizer order 25 and conjugacy-class intersection size two
  for order-five representatives from both beta roots, giving one fixed coset.

This supplementary implementation was executed directly for the audit and
was not retained as a separately reusable script. The archived scripts and
outputs remain the reproducible computational evidence.

The algebraic coverage check is independent of execution: after diagonalizing
A as diag(2,4), the trace equations force B's diagonal entries to be
2*beta−1 and 1−beta. Its off-diagonal entries satisfy
p*q=5*beta−4, which is nonzero. Thus there are exactly 48 candidates.
The determinant-one diagonal centralizer scales p by squares, producing two
orbits of 24. Since tr(A)=−1 is nonzero, a projective centralizer lift cannot
send A to −A. Since beta is nonzero, passage to projective matrices loses no
points in each fixed-trace slice. GL_2 conjugation normalizes PSL_2, so fixing
A loses no generation cases. Squaring an order-five element sends beta to
−1−beta, the other root, and preserves its fixed-point count.

The coset construction and permutation checks were read and reproduced.
The degree is 58,800/50=1176. The cycle types are 3^392, 1*5^235 and 7^168,
with defects 784, 940 and 1008. The generated group is transitive on its
cosets, and the permutation product is the identity. Consequently the
characteristic-zero branch-cycle genus is determined by
2*g−2=−2352+784+940+1008=380, hence g=191.

Terminology correction only: the sets gN are conventionally **left cosets**,
although the frozen script and its contract call them right cosets; the final
frontier note records the correction. The implemented left multiplication
action is correct; this wording does not affect any result.

## Checked SHA-256 hashes

| Artifact | SHA-256 |
|---|---|
| `computations/lastform_monodromy.py` | `5ec88e85d945e0766dbeb71f525341c734943c7effe0862c41fb9466521b785c` |
| `computations/lastform_normalizer.py` | `d4e29c74f6c23860236241430fa0f6fe0afbfaefdf645a4f6eb362d82951577b` |
| `verification/lastform_monodromy_run/result.json` | `babdfbb4f609e8cd14c7727f47c9392fb1efd0eae6059aaec9c2b319d6264458` |
| `verification/lastform_normalizer_run/result.json` | `9532e1563d356e2baa355f74e7f6646fc24e2d03e4e6f62a7c3fa07d45ae3e98` |

No audited script, result, or frontier note was modified by this reviewer.
