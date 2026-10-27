# Changelog

## 1.2.1 — 2026-09-03

- Narrowed the counted Smith congruence theorem to the directly proved
  `ZMod (p^L)` case with residue cardinality `p`; the arbitrary-DVR,
  residue-size-`q` statement is now explicitly classical/certificate-driven.
- Added a Lean proof that the executable cutoff `N = ceil(L/m)` satisfies
  `L <= m*N` for `m > 0`.
- Added direct Lean traceability declarations for transfer-block refinement,
  finite-graph transfer-zeta rationality, the dyadic sign comparison, and the
  transfer-zeta coefficient algorithm.
- Made separation-weight notation lattice-dependent and existence-explicit,
  clarified rank-deficient Smith factors and reduction modulo two, and
  consistently described the graph objects as walks rather than simple paths.
- Corrected the finite-precision inverse notation, removed the fraction-field
  and perturbation-symbol collision, repaired the shifted-operator subscript,
  and added the Paper I citation.
- Released the manuscript and Python companion as 1.2.1 and the Lean component
  and theorem map as 1.1.1.
- Made the inherited `ProjectorCore` load banner version-neutral so build logs
  do not advertise a competing component version.

## 1.2.0 — 2026-09-03

- Strengthened nested refinement with a generic finite-packet uniqueness
  theorem, coordinate identity/symmetry/cocycle laws, and typed
  coordinate-operator naturality.
- Reduced the general Fourier hypothesis to a finite `N × N` orthogonality
  table over a commutative semiring plus `omega^N = 1`, and proved the
  all-exponent statement by periodic reduction.
- Exposed the finite-precision inverse as an explicit retained-word sum and
  added the sharper cutoff obtained from a positive minimum edge weight.
- Constructed the finite-graph transfer-zeta denominator and numerator from
  the transfer matrix, determinant, and adjugate; proved that the enumerated
  `pathZeta` equals this matrix solution and is therefore rational without a
  supplied `QZ=P` certificate.
- Factored the separation development into minimal evaluated-Bezout lemmas,
  added unit-aware clearing for `r = u*pi^s`, and proved upward closure and
  the resulting least-weight bounds under explicit lattice hypotheses.
- Proved concrete one-coordinate solvability and exact fibre cardinality over
  `ZMod (p^L)`, while retaining the abstract certificate API for general
  Smith-diagonal products.
- Added exact `p`-local sign-projector denominator weights, computed the
  sign-factor resultant as `2`, and linked its dyadic valuation to the exact
  local weight.
- Added zero-defect polynomial functional-calculus compatibility, the
  `n * rho^(n-1) * norm Delta` power-defect majorant, a continuous resolvent
  identity from the necessary one-sided witnesses, and its operator-norm bound.
- Replaced representative-only trust checks with a fail-closed audit of every
  compiled `Komorebi.*` declaration and added an executable theorem-map
  consistency check.
- Released the manuscript and Python package as 1.2.0 and the strengthened
  Lean component and theorem map as 1.1.0.

## 1.1.0 — 2026-09-03

- Froze a 25-item theorem-and-algorithm completion contract with stable labels.
- Added a Lean 4/Mathlib formalization, kernel audit, and item-by-item theorem map.
- Repaired the root-of-unity statement by separating an explicit orthogonality
  certificate from the primitive-root field corollary.
- Split weighted inversion into finite nilpotent and complete normed-contraction
  results; made finite-precision pruning depend on multiplicative filtration and
  quotient certificates.
- Recast transfer-zeta rationality as a checked `QZ=P`, `Q(0)=1` certificate and
  proved the finite coefficient algorithm and induced recurrence.
- Replaced the spectral-separation argument with evaluated commuting Bézout data
  and an explicit `FG=0` certificate.
- Made Smith-coordinate solvability conditional, with zero solutions for an
  inadmissible coordinate and a product count only for admissible fibres.
- Typed and formalized the power-defect, norm, and resolvent-defect identities.
- Expanded the Python suite from 21 to 32 tests, added invalid-input contracts,
  generated-record consistency checks, and an isolated wheel smoke test.
- Corrected the filtered-depth and proof-dependency figures and added a local
  bibliography, reproducibility records, and precise claim boundaries.

## 1.0.0 — historical baseline designation

The recovered pre-revision archive is retained only as the historical baseline
for lineage and comparison. It is not the Lean-complete release.
