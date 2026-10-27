# Basis-change development result

The source `formal/KomorebiSpace/CoordinateBasisChange.lean` passed strict Lean
compilation in attempt 005 with one compiler thread, warnings as errors, and
implicit undeclared variables disabled. The compiler log is empty. The source
SHA-256 is recorded in `attempt_005/result.json`.

The module defines the printed coordinate normal-equation residual and proves:

- Gram congruence and observation-matrix transport.
- Preservation of the ambient correction under inverse coordinate transport.
- Uniqueness of those coordinates for independent columns.
- Covector covariance derived from the changed normal equation.
- Reverse-order inverse-Gram transport.
- Invariance of the inverse-Gram quadratic certificate, including the
  certificate obtained directly from the changed normal equation.
- The zero scalar value for empty coefficient spaces.
- An actual full basis for every invertible coordinate matrix, its transformed
  columns and synthesis map, and inverse coordinate transport for every fixed
  vector in the full space.

All change-of-basis conclusions quantify over arbitrary invertible real square
matrices using `IsUnit C`. No orthonormality, positive dimension, or nonempty
index assumption is present. Generic inverse-Gram transport uses the total
matrix inverse and is valid even for singular metrics. The actual Hilbert-space
Gram invertibility and normal-residual identification belong to the companion
`CoordinateCovector` module; this module alone does not close WR15.

Attempts 001–005 preserve source, command, environment, log, and hashes. Attempt
001 was a source-root invocation error; attempt 002 found two unused section
instances; attempt 003 found placement errors for `omit` commands and one
further unused section instance. Attempt 004 succeeded for the generic matrix
part. Attempt 005 added and successfully checked the full-basis construction
and its four transport theorems. No failed source was discarded or overwritten.

The attempt-004 development object was subsequently moved out of the formal
source overlay. `object_relocation.json` records the unchanged digest and both
paths. Attempt 005 and future local attempts use `development/basis_change/build`.

## Mathematical proofreading self-review

Scope: the complete new `CoordinateBasisChange.lean` source and its theorem
documentation, using the proofread-math skill in self-review mode.

- Routine edits: compiler-safe placement of section-variable omissions.
- Mathematical-token changes during proofreading: none.
- Unresolved proofreading issues: none.
- Validation: strict Lean attempt 005 succeeded.
- Mathematical scope checked: matrix dimensions, inverse multiplication order,
  covector transpose convention, exact normal-equation definition, and absence
  of nonemptiness restrictions.

Independent full-type/axiom review and cumulative clean replay remain the
integration verifier's responsibility.
