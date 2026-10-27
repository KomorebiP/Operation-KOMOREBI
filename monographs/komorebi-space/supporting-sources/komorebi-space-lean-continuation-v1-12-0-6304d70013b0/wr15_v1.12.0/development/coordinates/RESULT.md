# Coordinate covector development result

Production source: `formal/KomorebiSpace/CoordinateCovector.lean`.

Source SHA256: `151661fac5f9ef5e2212ef41d76bf179299b5da4c5df10bf07844f18e04decfe`.

The final production compile is `attempt_011`, exit 0. The full declaration-type
and axiom export is `attempt_013`, exit 0. Both use Lean 4.34.0-rc2 with `-j1`,
`-DwarningAsError=true`, and `-DautoImplicit=false`. The compiler command,
development import paths, original source snapshot, output log, source hash,
and exit status are preserved for each numbered attempt. These development
checks do not replace the parent task's authoritative clean integration build.

All 34 declarations in this module have successful full-type and axiom records.
Their axiom dependencies are limited to `propext`, `Classical.choice`, and
`Quot.sound`. There is no `sorry`, custom axiom, or `Lean.ofReduceBool` dependency
in the production source or the successful axiom export.

## Mathematical coverage

- A finite `Module.Basis` is a full basis of the correction space, with no
  orthonormality or nonemptiness assumption.
- `gram_posDef` and `gram_isUnit` derive positivity and invertibility from this
  full basis and the actual Hilbert inner product.
- `normalResidual_eq_pairings` proves that the literal matrix normal-equation
  residual is the covector of the already accepted Hilbert gradient.
- `gradient_eq_synthesis_inverse_normalResidual` and
  `gradient_norm_sq_eq_normalResidual` derive reconstruction and the squared
  Hilbert norm from the computed residual.
- `dotProduct_eq_euclidean_inner` identifies the scalar dot product with the
  Euclidean inner product. No coordinate maximum norm is substituted.
- `norm_sq_eq_zero_of_empty_basis` includes the empty full basis explicitly.
- `pairings_changedBasis`, `gram_changedBasis`,
  `operatorMatrix_changedBasis`, `computed_normalResidual_changedBasis`, and
  `computed_certificate_changedBasis` connect actual changed full bases to all
  matrix transformations and the invariant certificate. The changed basis is
  the invertible-matrix construction in `CoordinateBasisChange`.
- `protected_coordinate_certificate` is the consolidated ambient statement:
  its basis spans the whole `p.ker`, its matrices satisfy literally
  `S = dm * Bm` and `G = Bm.transpose * Bm`, its residual is computed from those
  matrices, and its vector is the existing restricted gradient. It proves the
  projected ambient formula, invertibility of `G`, ambient orthonormal
  coordinates `g = Bm * (G.inverse * q)`, and the squared original ambient norm.
- The identities allow every real regularization parameter; positivity is not
  needed for this coordinate statement.

## Preserved failed attempts

- `attempt_001`: adaptation to the new `Module.Basis` namespace was needed.
- `attempt_002`: inner-product finite-sum rewrites, one matrix API argument, and
  unused section-variable lint failures.
- `attempt_004`: development dependency-root layout did not yet contain the
  basis-change object; fixed by a local development copy.
- `attempt_005` and `attempt_007`: strict unused-variable or unused-simp lint
  failures; the mathematical goals had elaborated.
- `attempt_012`: the optional pretty-printer option `pp.width` was unavailable.
  The option was removed in `attempt_013`; the production source did not change.

The remaining numbered attempts passed. Failed snapshots and logs are retained
without replacement.

## Final self-review

Proofread: only the newly authored `CoordinateCovector.lean` source and its
mathematical docstrings, using the `proofread-math` self-review workflow.

- Routine edits during self-review: none.
- Mathematical-token changes during self-review: none.
- Unresolved issues: none found.
- Validation: final strict compile `attempt_011` and type/axiom export
  `attempt_013` passed.
- Scope: this production module; inherited modules were not edited.
