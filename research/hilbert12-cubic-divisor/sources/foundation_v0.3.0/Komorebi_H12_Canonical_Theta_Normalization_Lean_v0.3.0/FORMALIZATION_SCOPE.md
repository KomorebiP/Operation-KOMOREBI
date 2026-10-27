# Formalization scope: 109 audited theorem constants

The inherited 83 statements and proofs are unchanged. Their original source hashes are in `evidence/predecessor.json`.

The 26 new statements comprise:

- `H12CoprimeNormalization` (8): abstract commutative-group reconstruction from third and eighth powers, uniqueness, and exact scalar norm constraints.
- `H12FifthTorsionAlgebra` (8): field-polynomial consequences of explicitly supplied tangent, curve, and duplication equations.
- `H12CanonicalTheta` (10): the normalized rational coordinate, unordered-kernel symmetry, scale invariance, exact field normalizer, and discriminant formula.

Every theorem is compiled with the pinned external Lean 4.34.0-rc2 runtime and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The all-theorem audit rejects any transitive dependency outside propext, Classical.choice, Quot.sound. No custom axiom, admitted proof, native_decide, or unsafe declaration is allowed. Warnings are errors; a false arithmetic control must fail.

## Not formalized

The analytic definitions and convergence of theta/gamma, the meromorphic divisor argument, the identification of actual fifth-torsion points with the polynomial hypotheses, multiplication-norm identities as analytic statements, the geometric order-five curve normalization, and the gamma-to-arithmetic comparison are not formalized here.

The ordinary proof derives the norm and elliptic torsion inputs before applying the formal algebra. The new normalizer theorem is conditional on its two displayed power identities; those identities are not postulated as project axioms. No statement asserts U_Gamma=U_alg or equality of their powers.
