# Self-review

Checkpoint: LEHMER-TREE-SHARP-01.

Primary verdict on the requested conjecture: **incomplete, with the uniform
arithmetic nonvanishing implication still missing**.

Primary verdict on the sharp dyadic boundary theorem: **proved as written**
in the accompanying elementary argument, subject to ordinary mathematical
review. This is self-review, not independent-agent review or Lean verification.

## Dependency graph

1. Definitions of V_n, W, c and J.
2. Integer geometry of equal-norm packets in one dyadic sector.
3. Exclusion of a squared difference norm 2 by distinct residues modulo 5.
4. Squared norm 4 has pattern (1,1,-1,-1,0), up to permutation.
5. Opposite Vandermonde signs force one of the eight crossing factors positive.
6. Orthogonal projection plus integrality gives the sharpened norm lower bound.
7. Three explicit vector families and one base case attain its integer ceiling.
8. Separate conservation argument excludes the sector-local finishing move.

The sharp boundary theorem itself does not depend on modular-form theory.
Only its interpretation as a decomposition of tau uses Han's classical formula.

## Obligation matrix

| Obligation | Verdict | Evidence |
|---|---|---|
| Quantified objects and sector relation | Passed | Definitions in Section 1 |
| J action, multiplicities and W sign | Passed | Direct permutation argument and exact checks |
| Midpoint integrality for k>=1 | Passed | 5M is even |
| Smallest difference vector and exceptional norm 2 | Passed | Residue contradiction |
| Eight unequal-coordinate pairs at norm 4 | Passed | Blocks of sizes 2,2,1 |
| Strict inequality converted to integer gap +1 | Passed | Integral midpoint and a |
| Projection denominator 2-delta^2/4 | Passed | ||d||^2=4, m perpendicular to d |
| Larger difference norms | Passed | Bound 15M^2/4 exceeds the required bound for M>=2 |
| Ceiling and k mod 3 cases | Passed | Powers of 2 modulo 7 |
| Witness congruences and norm | Passed | Explicit affine formulas, exact polynomial coefficients |
| Witness signs for all parameter values | Passed | Every linear factor keeps sign above the row minimum |
| Special k=1 case | Passed | Exact vectors in V_13 |
| Distinct J-orbits of witnesses | Passed | Opposite W signs, while J preserves W |
| Sector-local impossibility | Passed | Conservation and p=7 sector masses |
| Arbitrary non-J-invariant corrections | Scope clarified | Orbit masses remain fixed even if values change |
| Unique-minimum valuation mechanism | Refuted as automatic claim | Unit lemmas and p=31 |
| Universal nonvanishing from correction completeness | Not established | Exact equivalence shows further input is required |
| Han normalization | Passed | Theorems 1.1 and 1.2, arXiv:0805.1398v1 |
| Hecke recurrence and multiplicativity | Passed | Theorem 2.2, arXiv:2005.10345 retrieved PDF |
| Prior fourteen harmonic null polynomials | Not re-audited | Not needed for the new obstruction theorems |
| Lehmer for every prime | Not established | Remaining signed arithmetic cancellation |

## Finite computation review

The quadratic shell enumerator is exhaustive within each specified shell.
The last coordinates must have their prescribed sum and square sum, so their
difference is exactly one of the square roots enumerated by the script.
The independent four-coordinate enumerator confirms shells 1 through 32.

The direct product coefficient algorithm updates from a copied old coefficient
array for each factor (1-q^k)^24. It does not reuse the triangular recurrence.
Both agree through 512. Shell sums agree through 512 and at 737, 2411.

The report's first boundary for k=4 is established by the analytic lower
bound plus a witness at 737. The script does not claim to enumerate all shells
513 through 736. Larger first boundaries likewise rely on the proof, not an
unexecuted exhaustive search.

The manifest validator completed successfully. No failed mathematical assertion
was hidden or changed into a pass. The environment import failures occurred
in exploratory setup and are recorded in FAILURES.md.

## Final proofreading

Self-review covered the newly written note, the README and this audit.
Routine edit: corrected an article in the remaining-goal paragraph.
Mathematical-token changes during proofreading: none.
Unresolved mathematical issue: the original Lehmer target, explicitly retained.
No claim of independent review is made.
