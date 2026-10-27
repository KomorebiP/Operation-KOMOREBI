# Komorebi Lean verification — Paper II component v1.1.1

Author: Komorebi P.  
Verification date: 2026-09-03  
Manuscript release: *Projector-Resolved Seed Calculus II*, v1.2.1  
Lean component: v1.1.1

This Lean 4/Mathlib component maps every item in the frozen 25-row Paper II
contract to compiled declarations. The exact declaration names, theorem
strengths, assumptions, certificate inputs, and exclusions are recorded in
[`LEAN_THEOREM_MAP_v1.1.1.md`](LEAN_THEOREM_MAP_v1.1.1.md).

“25/25 mapped” means that every contract item has a checked counterpart at the
scope stated in that map. It does not mean that Lean automatically constructs
every packet family, Fourier table, filtration, evaluated Bezout identity,
Smith normal form, or inverse witness that appears as an explicit hypothesis.
Within those boundaries, finite-graph transfer-zeta rationality and concrete
one-coordinate Smith arithmetic over `ZMod (p^L)` are now proved directly.

## Paper II modules

| Module | Principal contract coverage | Important boundary |
|---|---|---|
| `PaperII/NestedRefinement.lean` | Rows 1–5: generic finite-packet uniqueness, refinement absorption and reconstruction, transitivity, coordinate identity/symmetry/cocycle laws, typed coordinate-operator naturality, refined transfer blocks, and a direct row-5 trace wrapper including map reconstruction at both levels. | Finite algebraic projector families; coherence is an exact full-coordinate statement, not truncation or infinite packet convergence. |
| `PaperII/ResidueFourierCRT.lean` | Rows 6–9: residue projector algebra, finite-table Fourier realization over a commutative semiring, periodic extension from `omega^N = 1`, the field primitive-root corollary, polyphase refinement, CRT, and dyadic-odd factorization. | Over a general semiring the finite `N × N` orthogonality table is supplied; a primitive root constructs it only in the field specialization. |
| `PaperII/WeightedTransfer.lean` | Rows 10–11 and 24: finite and norm-convergent geometric inverses, explicit retained-word/pruned inverse formulas, multiplicative filtrations, exact precision pruning, minimum-edge-weight cutoffs, the proved `ceil(L/m)` cutoff inequality, and the full mapped diagonal-plus-transfer inverse specification. | The finite branch consumes diagonal-inverse, edge-expansion, and filtration certificates; the infinite branch requires a complete normed ring and a strict norm contraction. The Lean parameter `K` denotes the manuscript perturbation `H`. |
| `PaperII/TransferZeta.lean` | Rows 12–13 and 25: unrestricted finite walks and bounded-tuple counting, first-edge recurrence, weighted adjacency series, determinant/adjugate rationality for the enumerated `pathZeta`, and direct trace wrappers for rows 12 and 25, with the normalized certificate API retained. | Automatic rationality is finite-vertex and finite-edge, with strictly positive natural weights; repeated vertices and edges are allowed, so this is not simple-path enumeration. It is not an infinite-graph or analytic convergence theorem. |
| `PaperII/ResultantSeparation.lean` | Rows 14–16: minimal evaluated-Bezout numerator identities, quasi-idempotence and kernel actions, unit-aware denominator clearing for `r = u*pi^s`, upward-closed separation weights, least clearing exponent, upper bounds, and precision delay. | The module starts after polynomial evaluation; it does not construct a general polynomial resultant or a DVR valuation object. |
| `PaperII/SmithDyadic.lean` | Rows 17–18 and 22: concrete congruence fibres and exact counts over `ZMod (p^L)`, the general certificate/product API, the rational sign split, exact local denominator weights, the sign-factor resultant and its `2`-adic valuation, a direct row-17 trace wrapper, and Smith phase inversion. | The counted row-18 theorem has count base `p`; arbitrary-DVR count base `q` is certificate-explicit. Smith normal form construction remains input; the sign example proves exact rational and `p`-local endpoints rather than constructing completed `p`-adic spaces. |
| `PaperII/LinearDefects.lean` | Ring-valued all-power defect identities, raw and normalized norm bounds, and noncommutative inverse/resolvent identities. | The normalized ring-valued norm form explicitly assumes `NormOneClass`. |
| `PaperII/TypedLinearDefects.lean` | Rows 19–21: typed power and resolvent defects, zero-defect power and polynomial compatibility, the geometric power-defect majorant, and the continuous resolvent norm bound. | Continuous resolvent identities use exactly a right inverse for the fine shift and a left inverse for the coarse shift; no spectral or inverse-existence theorem is inferred. |
| `PaperII/KernelAudit.lean` | Fail-closed environment scan of every compiled `Komorebi.*` declaration, plus selected explicit reports. | This is a trust audit, not an additional mathematical contract row. |

The Paper II files reuse the existing `ProjectorCore.lean`,
`ExactCoordinates.lean`, `FibreRefinement.lean`, and
`ResidueProjectors.lean` foundations. In
particular, the residue analysis/synthesis algorithm contract is the exact
linear equivalence with the independently defined product of projector ranges,
not an inverse-by-definition.

## Reproduce the checks

With Elan available, run from this directory:

```bash
lake exe cache get
lake build
python scripts/verify_theorem_map.py
lake env lean -E warning KomorebiVerification/PaperII/KernelAudit.lean
```

The toolchain is pinned by `lean-toolchain` to Lean `v4.34.0-rc2`; the exact
Mathlib dependency graph is pinned in `lake-manifest.json`.

## Trust and interpretation

The Paper II sources contain no project-specific axiom declarations,
`sorry`, `admit`, or `unsafe` declarations. The kernel audit reports only
Lean/Mathlib foundations where applicable: `propext`, `Classical.choice`, and
`Quot.sound`; it reports no `sorryAx`.

Several distinctions are intentional:

- Exact coordinate refinement preserves the full object; its identity,
  symmetry, composition/cocycle, and coordinate-operator naturality laws do
  not by themselves justify discarding descendants.
- Weighted finite-precision inversion is proved after supplying a ring map and
  filtration-killing certificate. The full mapped diagonal-plus-transfer formula additionally
  consumes a two-sided inverse for `D` and an explicit weighted-edge expansion
  of the normalized transfer (called `Dinv*H` in the manuscript and `Dinv*K`
  in the Lean parameter names). Unrestricted convergence in an unspecified complete filtered
  algebra is not claimed.
- The typed power-defect norm theorem is for continuous linear maps between
  distinct normed spaces. The geometric majorant assumes both operator norms
  are bounded by the same real `rho`; it is not a spectral-radius or nonlinear
  estimate.
- Transfer-zeta coefficients are computed for a fixed start/target pair, with
  multigraph multiplicity represented by distinct parallel edges.
- `separationWeight` is the noncomputable least clearing exponent once finite
  existence is supplied; the evaluated denominator yields an upper bound and
  need not be minimal.
- Finite-graph `pathZeta` rationality is constructed from the transfer matrix,
  determinant, and adjugate; the older normalized `QZ=P` certificate route is
  retained for externally supplied presentations.
- Concrete Smith solvability and cardinality are proved for diagonal systems
  over `ZMod (p^L)`, with exact count base `p`. The general product interface
  remains certificate-driven, including an arbitrary supplied base `q`, and
  Lean does not construct general DVR coordinate facts or Smith normal form.
- The algorithm rows are mathematical correctness specifications. They are
  not extracted Python code, verified symbolic algebra, complexity analyses,
  or performance guarantees.

This component makes no claim about historical priority, novelty, external
review, or the numerical accuracy of the separate Python experiments. It also
does not formalize nonlinear operator trees, nonlinear obstruction packets,
or holonomy, which lie outside the Paper II contract.
