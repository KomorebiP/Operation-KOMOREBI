# Komorebi Lean verification report — Paper II

Author: Komorebi P.  
Lean component: v1.1.1  
Manuscript release: *Projector-Resolved Seed Calculus II*, v1.2.1  
Verification date: 2026-09-03

## Outcome

The aggregate Lean 4/Mathlib project and the dedicated Paper II kernel audit
complete successfully. All **25/25 items** in the frozen Paper II contract have
compiled counterparts at the precise scopes recorded in
[`LEAN_THEOREM_MAP_v1.1.1.md`](LEAN_THEOREM_MAP_v1.1.1.md).
The map resolves **160 unique declarations**, and the fail-closed environment
scan accepts all **1,034 compiled `Komorebi.*` declarations**.

This is a mapped, scope-explicit completion result. It is not a claim that
every row is unconditional or that Lean constructs every object mentioned in
the mathematical motivation. Theorem-map classifications, hypotheses, and
exclusions are part of the reported result. Version 1.1.1 of the Lean component
also closes several boundaries left certificate-only in its predecessor:
finite-graph `pathZeta` rationality and concrete diagonal Smith arithmetic over
`ZMod (p^L)` are derived internally.

| Contract rows | Verified subject | Scope summary |
|---:|---|---|
| 1–5 | Nested projector refinement | Finite algebraic projector families; generic packet-decomposition uniqueness; exact child sums, absorption, transitivity, coordinate identity/symmetry/cocycle laws, coordinate-operator naturality, source/target block refinement, and a direct composite trace declaration. |
| 6–9 | Residue, Fourier, polyphase, and CRT selectors | Division-free residue algebra; a finite `N × N` Fourier table over a commutative semiring extended to all exponents using `omega^N = 1`; field primitive-root specialization; positive coprime and dyadic-odd CRT. |
| 10–11 | Weighted transfer inversion | Finite noncommutative geometric inversion from nilpotence; complete-normed contraction specialization; an explicit retained-word/pruned inverse, a minimum-edge-weight cutoff, a proved ceiling-cutoff inequality, and a full mapped diagonal-plus-transfer inverse from filtration and diagonal-inverse certificates. |
| 12–13 | Transfer-zeta series | Exact finite positive-weight walk enumeration and first-edge recurrence; transfer-matrix determinant/adjugate construction; automatic rationality and a denominator-induced recurrence for the enumerated `pathZeta`; and a direct composite trace declaration. |
| 14–16 | Evaluated separation | Minimal evaluated-Bezout hypotheses give numerator identities and kernel actions; commutation/annihilation give quasi-idempotence; `r = u*pi^s` with lattice-unit control gives clearing, an upper bound, upward closure, and precision delay. |
| 17–18 | Dyadic sign split and Smith fibres | Concrete solvability and exact `p`-based fibre counts over `ZMod (p^L)`; exact rational sign matrices and local denominator weights; the sign-factor resultant and its dyadic valuation; a direct sign-comparison trace declaration; and general global Smith products from coordinate certificates. The arbitrary-DVR, residue-size-`q` extension is certificate-explicit. |
| 19–21 | Linear defects | Typed power/resolvent identities between different modules; zero-defect polynomial compatibility; a geometric power-defect majorant; a continuous resolvent norm bound; ring-valued specializations. |
| 22 | Smith phase identity | Algebraic inversion identity over fields in which `2` is nonzero. |
| 23–25 | Algorithm specifications | Exact packet analysis/synthesis, bounded weighted inversion, and finite walk-coefficient enumeration; mathematical specifications rather than extracted software. |

## Source modules

Eight substantive Paper II modules supply the contract, with one audit module:

| Module | Principal declarations and role |
|---|---|
| `NestedRefinement.lean` | `finitePacket_decomposition_unique`, the `Refines` absorption/reconstruction/transitivity family, coordinate identity and cocycle laws, `coordinateOperator_naturality`, transfer-block refinement, and `transferBlock_refinement_and_reconstruction`. |
| `ResidueFourierCRT.lean` | Residue projector algebra, `FiniteRingFourierOrthogonalityCertificate.toRingCertificate`, finite-table and field Fourier realizations, `polyphase_refinement`, CRT equivalences, and `residueProj_dyadicOdd`. |
| `WeightedTransfer.lean` | Explicit two-sided inverses, finite and analytic geometric inverse specifications, `prunedWordInverse`, minimum-weight cutoff theorems, `le_mul_ceilDiv`, multiplicative filtrations, and the mapped diagonal-plus-transfer inverse. |
| `TransferZeta.lean` | Exact walks, bounded-tuple enumeration, first-edge decomposition, weighted adjacency series, transfer determinant and adjugate, `pathZeta_eq_matrixPathZeta`, automatic `finite_graph_pathZeta_rationality`, direct composite trace wrappers, and the retained `RationalCertificate` API. |
| `ResultantSeparation.lean` | Minimal evaluated-Bezout separator identities, quasi-idempotence and kernel actions, scalar/lattice-unit preservation, unit-aware clearing, upward-closed and least separation weights, and precision delay. |
| `SmithDyadic.lean` | Concrete `SmithZModFiber` solvability/counting, the general split certificate API and global product theorems, explicit sign matrices, exact local denominator weights, `signFactors_resultant`, valuation endpoints, `oddAdicVersusDyadicSignBehavior_trace`, and Smith phase inversion. |
| `LinearDefects.lean` | Ring-valued all-power telescoping, raw and normalized norm bounds, inverse sandwich, and noncommutative resolvent identity. |
| `TypedLinearDefects.lean` | Genuinely typed fine/coarse modules, all-power identity, power and polynomial compatibility at zero defect, continuous geometric majorant, one-sided-witness resolvent identity, and resolvent norm bound. |
| `KernelAudit.lean` | Imports every substantive Paper II module and rejects any compiled `Komorebi.*` declaration that is unsafe or depends on an unapproved axiom. |

The modules reuse the earlier `ProjectorCore.lean`, `ExactCoordinates.lean`,
`FibreRefinement.lean`, and `ResidueProjectors.lean` foundations.
`KomorebiVerification/PaperII.lean`
is the Paper II aggregate import, and `KomorebiVerification.lean` imports that
aggregate into the full component.

## Reproducible build and kernel audit

Run from `formalization/lean`:

```bash
lake exe cache get
lake build
python scripts/verify_theorem_map.py
lake env lean -E warning KomorebiVerification/PaperII/KernelAudit.lean
```

The project pins Lean `v4.34.0-rc2` in `lean-toolchain` and pins Mathlib plus
its dependency graph in `lake-manifest.json`. Both the aggregate build and the
standalone audit command exit successfully in the recorded environment.

The theorem-map checker verifies that all mapped names exist in the compiled
environment. The fail-closed kernel audit traverses every compiled
`Komorebi.*` declaration and rejects unsafe declarations or dependencies on
anything outside the approved Lean/Mathlib foundations:

```text
propext
Classical.choice
Quot.sound
```

No audited declaration reports `sorryAx`.

## Certificate boundary

The following inputs are explicit rather than hidden behind informal phrases:

| Branch | Supplied input | Kernel-checked consequence | Not constructed by this component |
|---|---|---|---|
| Fourier | `omega^N = 1` and a finite `N × N` orthogonality table over a commutative semiring, or a primitive root over a field. | Periodicity extends the table to arbitrary exponents, and the Fourier average equals the coefficient residue selector. | A primitive-root or orthogonality solver for arbitrary semirings. |
| Finite weighted inverse | A two-sided inverse for `D`, nilpotence or a filtration-killing ring map, positive edge weights, edge filtration memberships, and an equality identifying the normalized perturbation with the edge sum. | Equality with an explicit retained-word sum, exact high-weight pruning, the ceiling choice for a minimum-weight cutoff, and a full two-sided inverse after mapping the diagonal-plus-transfer operator. | A quotient/DVR implementation, basis-level matrix inverse routine, or unrestricted adic convergence theorem. |
| Analytic weighted inverse | Complete normed ring and a strict norm bound on the normalized perturbation. | The Neumann sum is a two-sided inverse. | An effective convergence rate or executable infinite sum. |
| Transfer zeta | A finite vertex/edge multigraph with strictly positive natural weights. | The enumerated series satisfies the first-edge matrix equation, equals the determinant/adjugate solution, and has a nonzero normalized polynomial denominator and induced recurrence. | Infinite-graph rationality or analytic convergence. The separate `RationalCertificate` API remains available for supplied presentations. |
| Evaluated separator | An evaluated Bezout equation; additional commutation/annihilation only where quasi-idempotence or the complementary kernel action needs them; lattice preservation for integral conclusions. | Minimal numerator identities and `ker F` action, quasi-idempotence, normalized idempotence, exact kernel actions, and precision delay. | A general polynomial Bezout/resultant constructor, characteristic factorization, or Cayley-Hamilton instantiation. |
| Separation weight | A factorization `r = u*pi^s`, lattice preservation by the relevant unit actions, and existence of at least one clearing exponent for the least-weight definition. | Unit-aware clearing, upward closure when `pi` preserves the lattice, a noncomputable least exponent, and the bound `separationWeight <= s`. | A general DVR valuation object, search algorithm, or proof that every displayed resultant valuation is minimal. |
| Smith fibres | For the concrete branch, a diagonal system over `ZMod (p^L)` with `1 < p`; for the abstract product branch, per-coordinate solvability/cardinality certificates and a supplied base `q`. | Concrete divisibility solvability and exact `p^min(s,L)` fibre count, including the inadmissible zero branch globally; abstract coordinatewise product assembly. | General-DVR coordinate arithmetic, Smith normal form, or diagonalization of a supplied matrix. |
| Defect bounds | Typed continuous linear maps over a nontrivially normed field, with common norm bound `rho` for the geometric majorant. | `n * rho^(n-1) * norm Delta` power bound, zero-defect polynomial compatibility, and the resolvent norm bound. | Spectral-radius, nonlinear, or inverse-existence results. |
| Resolvents | For the algebraic identity, two-sided inverse witnesses; for the continuous identity, only a right inverse for the fine scalar shift and a left inverse for the coarse scalar shift. | Typed resolvent-defect identities, zero-defect compatibility, and `norm(Rc) * norm(Delta) * norm(Rf)` control in the continuous case. | Spectral membership or analytic construction of resolvents. |

## Precise limitations

- All projector-index sums, tuple enumerations, CRT label sets, and Smith
  coordinate products in the contract are finite.
- Exact coordinate refinement is an invertible change of full packet
  coordinates with checked identity, symmetry, cocycle, and naturality laws.
  It does not justify discarding descendants.
- The full mapped diagonal-plus-transfer inverse is certificate-explicit: it requires a
  supplied two-sided inverse for `D`, an identity equating the normalized
  perturbation with the edge sum, a
  filtration-killing ring map, positive weights, and edge memberships. It is
  a ring-level theorem, not an executable basis-level modular matrix program.
- Transfer-zeta enumeration uses one fixed start and target vertex for each
  scalar series. Parallel edges represent multigraph multiplicity. Automatic
  determinant rationality requires finite vertex and edge types and positive
  natural edge weights.
- The odd-prime sign result is an exact rational-entry `p`-integrality theorem.
  It does not construct a completed `p`-adic field or identify an arbitrary
  completed lattice.
- The typed norm-defect theorems are operator-norm estimates for continuous
  linear maps between distinct normed spaces over a nontrivially normed field.
  They include the common-`rho` geometric majorant and the explicit resolvent
  bound, but not a spectral-radius, sharpness, nonlinear, or inverse-existence
  result.
- The Smith phase theorem checks the algebraic fractional formula; it does not
  formalize the complex Smith disk, physical impedance, or radius preservation.
- No row verifies the separate Python source, numerical residuals, test count,
  code extraction, symbolic factorization, complexity, or benchmark claims.

## Final scope statement

Lean component v1.1.1 verifies the 25-item Paper II contract at the scopes in
the theorem map. It does not establish historical priority, novelty, external
review, executable certificate construction, unrestricted universality, or
the nonlinear operator-tree and obstruction theory reserved for Paper III.
