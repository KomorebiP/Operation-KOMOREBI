# Block 15 formalization coverage

## Completed strict cold run

PASS: 82 expected-outcome tasks, 74 library modules,
655 theorem declarations, 225 definitions/abbreviations,
10 named instances. All 890 registered named declarations
were axiom-audited. Only Classical.choice, Quot.sound, propext occur. There are no
unexpected axiom dependencies, missing audited names, or changed accepted inputs.
Every library source compiled with warnings as errors. Positive control accepted;
false and placeholder controls rejected for their intended mathematical errors.

Six new modules add 64 theorem declarations and 12
definitions, with no new named instances. All 68 inherited modules are unchanged.
Counts include finite base identities and technical lemmas, not independent discoveries.

| Module | Universal checked content |
|---|---|
| BinaryThreeWeights | Exceptional binary diagonal weights, monotonicity, three top-degree inequalities, exact projected raising |
| BinaryThreeCoefficients | Actual low-order polynomials, absence of degree1, integer third-coefficient divisibility and finite induction bases |
| BinaryThreeEnvelope | All coefficients integral after normalization, exact diagonal span, digit invariance and actual partition orbit containment |
| BinaryThreeProjectors | Stability under coefficient projections and exact least projector-closed enlargement using integer recovery |
| BinaryThreeFinite | Actual finite residue envelope, precise vanishing, and universal square-root free-machine upper bound |
| BinaryThreeObstruction | Coupled 16c4+c6 obstruction, strict orbit/envelope distinction, and actual partition-series nonreachability witness |

## Proof boundary

The exact digit-only integer orbit lattice and universal intrinsic Smith law remain
UNRESOLVED. Least closure refers explicitly to the additional coefficient projectors.
The closed count of diagonal factors is written and finitely audited, while the
separately assembled universal Lean bound uses binaryThreeBudget. The precise
mod64 index-two description uses a written finite-cardinality proof and its instance
certificate; no specialized new Lean equivalence is claimed for that statement.
The polynomial obstruction is not an identity between raw partition coefficients.

Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
Mathlib pin: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Python implementation/certificate checker, external refereeing and novelty remain
outside the verified-executable/historical scope.
