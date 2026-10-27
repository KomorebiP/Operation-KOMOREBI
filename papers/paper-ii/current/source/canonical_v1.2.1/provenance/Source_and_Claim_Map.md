# Source and Claim Map

## Constructed and kernel-checked in the release

- Exact nested packet refinement, absorption, reconstruction, uniqueness,
  transitivity, coordinate identity/symmetry/cocycle laws, typed
  coordinate-operator naturality, and transfer-block aggregation.
- Residue-selector algebra, polyphase refinement, finite-table Fourier
  realization over commutative semirings, periodic extension from
  `omega^N = 1`, primitive-root field specialization, CRT coordinates, and the
  dyadic–odd specialization.
- Finite nilpotent and complete normed-contraction inverse formulas; exact
  finite-quotient pruning as an explicit retained-word sum, with both the
  general weight cutoff and the sharper minimum-edge-weight cutoff.
- Finiteness and correctness of the positive-weight walk coefficient algorithm;
  first-edge recurrence; equality with the transfer-matrix solution; automatic
  determinant/adjugate rationality and its coefficient recurrence.
- Minimal evaluated-Bézout numerator identities and kernel action,
  quasi-idempotence under the needed commutation/annihilation assumptions,
  unit-aware lattice clearing, monotone and least separation weights, precision
  delay, and the explicit dyadic sign example.
- Concrete Smith-coordinate solvability and exact conditional product counts
  over `ZMod (p^L)`, where the count base is `p`, plus an abstract certificate
  interface for other fibres and arbitrary residue-cardinality parameters.
- Exact rational and `p`-local sign-projector weights, the sign-factor resultant
  and its dyadic valuation, typed polynomial/power/resolvent defect identities,
  geometric and resolvent norm bounds, and the Smith-phase identity.

The precise declaration-level map and assumptions are recorded in
`formalization/lean/LEAN_THEOREM_MAP_v1.1.1.md`.

## Supplied certificates or classical inputs

- Complete orthogonal-idempotent packet data.
- A finite `N × N` root-of-unity orthogonality table and `omega^N = 1` in the
  general commutative-semiring branch; the primitive-root field corollary is
  proved from Mathlib hypotheses, and no division by a nonunit is hidden.
- CRT equivalences and elementary finite-set/cardinality infrastructure.
- A nilpotence or strict norm-contraction certificate for an inverse.
- For the separator branch, an evaluated `UF+VG=rI`; the additional `FG=0`,
  commutation, nonvanishing, unit factorization, and lattice-preservation data
  are required only by conclusions that use them. General polynomial
  resultant construction is not claimed.
- Smith diagonalization itself. Once diagonal weights and targets over
  `ZMod (p^L)` are given, the divisibility and fibre-count calculation is proved
  directly; the abstract product theorem can instead consume coordinate data.
  The arbitrary-DVR one-coordinate solvability and `q`-based cardinality facts
  are classical or supplied certificates, not constructed in this release.
- Concrete inverse witnesses for resolvent identities and diagonal weighted
  transfer; these theorems do not infer spectral invertibility.

## Executable certificates

The Python companion checks finite residue/CRT/Fourier realizations, refinement
transitivity and blocks, filtered modular inverses, weighted walk counts, dyadic
sign packets at several odd primes, Smith fibre counts, typed defect identities,
Smith-phase geometry, invalid inputs, and stored JSON/CSV consistency. These 48
tests support the implementation but do not replace the formal proofs.

## Claims deliberately not made

- No novelty or priority claim is inferred from formalization.
- No universal convergence theorem for arbitrary complete filtered algebras.
- No infinite-graph transfer-zeta rationality theorem, general polynomial
  resultant constructor, or Smith normal-form constructor. The finite-graph
  denominator is constructed internally by determinant/adjugate algebra.
- No assertion that a resultant valuation is always the minimal lattice weight.
- No nonlinear packet-tree or obstruction theory; those remain outside Paper II.
- No external certification or peer-review claim.
