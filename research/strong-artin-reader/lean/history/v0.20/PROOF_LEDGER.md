# Proof ledger — Strong Artin Lean v0.20

## Evidence label

Every result listed below is **Lean-checked as written** under the pinned Lean/mathlib environment.  These are algebraic theorems about finite-coordinate polynomial systems and residue-field Jacobians.  Arithmetic identification with an actual Strong Artin deformation/Hecke presentation remains open.

## `ScalarPowerDivisibility.lean`

- multiplication by an arbitrary scalar preserves filtration depth;
- products of depths `m` and `n` have depth `m+n`;
- coordinate evaluation preserves power divisibility.

## `PolynomialExpressionTaylor.lean`

- intrinsic polynomial-expression syntax from constants, variables, addition, negation, and multiplication;
- recursive evaluation and directional derivative;
- linearity of the directional derivative;
- polynomial increments preserve the input filtration depth;
- derivatives preserve the direction filtration depth;
- evaluations and derivatives vary with the same filtration depth as the base point;
- every first-order polynomial Taylor remainder gains one level for positive-depth corrections.

## `PolynomialSystemTaylor.lean`

- coordinatewise polynomial system evaluation;
- state-dependent derivative packaged as a linear map;
- coordinate equality between vector and scalar remainders;
- automatic `VariableRemainderRaisesOne` for every polynomial system;
- exact nonlinear solution under the v0.19 stable approximate-right-inverse hypotheses.

## `FiniteCoordinatePolynomialHensel.lean`

- entrywise matrix power divisibility;
- closure under matrix addition, subtraction, and multiplication by arbitrary finite matrices;
- conversion of an entrywise depth-one error into an explicit `pi`-multiple matrix;
- standard-coordinate Jacobian matrix;
- residual-fibre stability of the polynomial Jacobian matrix;
- compatibility between matrices and standard-basis linear maps;
- a base-point matrix inverse modulo `pi` remains an approximate right inverse throughout the residual fibre;
- exact polynomial solution from an entrywise lifted residual matrix right inverse.

## `ResidualMatrixRightInverseLift.lean`

- entrywise lift of a matrix over `R / (pi)`;
- a quotient-ring residual right inverse lifts with `pi`-divisible composite error;
- exact polynomial solution from a residual quotient matrix right inverse.

## `SurjectiveMatrixRightInverse.lean`

- a surjective linear map onto a finite standard-coordinate vector space over a field has a linear right inverse;
- a surjective matrix map over a field has a matrix right inverse.

## `SurjectiveResidueHomPolynomialHensel.lean`

- entrywise matrix lifting along an arbitrary surjective residue homomorphism;
- residual matrix right inverse lifting when the kernel is `(pi)`;
- capstone: a surjective residual Jacobian over the residue field lifts every residual polynomial solution to an exact solution over a nilpotent principal thickening.

## Declaration audit

New v0.20 source:

- theorem declarations: **50**;
- definitions: **9**;
- abbreviations: **1**;
- lemmas: **0**;
- structures: **0**;
- instances: **0**;
- `sorry`: **0**;
- `admit`: **0**;
- custom `axiom`: **0**;
- custom `opaque`: **0**.

Axiom reports are confined to ordinary Lean/Mathlib foundations:

- `propext`;
- `Classical.choice`;
- `Quot.sound`.
