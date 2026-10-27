# Fixed-presentation polynomial obstruction and shared compatibility

Author: Komorebi P.

## Result and scope

`PolynomialObstruction.lean` defines evaluation and the actual partial-derivative
Jacobian for an arbitrary finite list of multivariable integer polynomials.
For every positive natural modulus q, depth L at least one, and actual root x
modulo q^L, it constructs the exact integer residual r with F(x)=q^L r. The finite
cokernel of the reduced Jacobian contains an obstruction class [r]. Its vanishing
is equivalent to the existence of an actual root y modulo q^(L+1) with
y congruent to x modulo q^L. The proof imports the checked polynomial Taylor
remainder theorem. No Taylor estimate, surjectivity, or correcting-vector
existence is assumed in the final finite-obstruction theorem.

The modulus may be composite or equal one. The number of unknowns and the number
of equations may be zero. The proof does require L >= 1. No prime-field rank or
lift-cardinality claim is included.

`PolynomialShared.lean` applies the common quotient to two actual polynomial
blocks F and G on the same unknown vector. Write J and K for their reduced
Jacobians. The finite quotient is U/(ker J + ker K), with U the integer correction
module. Given individually successful corrections u and v, an actual common
next-level root exists if and only if [u]=[v] in that quotient. The two labels are
independent of the chosen individual corrections. The final unconditional
criterion includes both individual solvability and equality of labels in its
right-hand side.

These results concern fixed polynomial presentations and one lifting step.
They do not establish invariance under changes in the list of defining
equations, an infinite compatible tower, global integer descent, or the full
native conjectures 13.2 and 13.3.

## Verification

Runtime: portable Lean 4.34.0-rc2, checked with the low-memory runner using
one compiler thread and `-DwarningAsError=true`.

- `logs/definitions_01.log`: initial actual evaluation/Jacobian and residual
  definitions compiled successfully.
- `logs/full_01.log`: initial complete obstruction compile failed on a function
  representation mismatch inside polynomial evaluation. It generated no
  accepted complete proof. An explicit equality between the pointwise shifted
  vector and its lambda expression repaired the elaboration issue.
- `logs/full_02.log`: final obstruction module passed. All 12 explicitly audited
  declarations use only `propext`, `Classical.choice`, and `Quot.sound`.
- `logs/shared_01.log`: final shared module passed on its first full compile.
  All nine explicitly audited declarations use only the same standard axioms.

The two modules contain 21 audited declarations: 17 theorems, three definitions,
and one abbreviation. This counts support statements, not independent research
discoveries. Compiled modules are development products under `build/`; the
source modules and verification logs are the authoritative deliverables for a
fresh cumulative replay.

Independent review and cumulative statement-contract tests are coordinated by
the parent task and recorded separately in the release audit.
