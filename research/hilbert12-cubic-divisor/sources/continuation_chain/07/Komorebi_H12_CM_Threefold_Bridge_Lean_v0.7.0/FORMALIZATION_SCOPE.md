# Formalization scope: 44 new kernel-checked theorem constants

| Module | Count | Actual formal scope |
|---|---:|---|
| H12ConjugationOrder | 25 | Explicit integer coefficient algebra; conductor characterization for all coefficients and all multipliers; two-branch residue tests and lifts; conjugation/rotation; Jacobi pair and unit action |
| H12ConjugationRelations | 8 | Exact Z^2 exponent maps; rotation quotient Z/3; combined rotation and twisted-conjugation relation lattice is all of Z^2 |
| H12CMThreefold | 11 | Eisenstein coefficient identities for the original/companion matrices, complete fixed-point parameterizations, and the oriented seven-line carries |

All 44 are freshly compiled with the pinned Lean 4.34.0-rc2 compiler and its
bundled Std. No Mathlib dependency is used in this block. All theorem axiom
reports are audited; only propext, Classical.choice, Quot.sound are permitted.
A false integer theorem must be rejected.

The concrete coefficient model is explicit; its faithful interpretation in
Q(r,omega) and its complex-torus applications are ordinary mathematics. This
release does not formally define elliptic curves, their analytic uniformization,
the geometric fixed-group exact sequence, or elliptic-gamma descent. The phase
character application of the exponent relations is an ordinary conditional
argument. It is not an actual analytic comparison character.

The cumulative source inventory is 216 (172 inherited, 44 new). The inherited
172 sources and their previously reported evidence are preserved in the prior
ZIP. A fresh complete replay of 216 is NOT claimed. Full runtime extraction
hit the tool cap twice; the new Std-only checks succeed without Mathlib.

No theorem proves or assumes as a project axiom Im(C_pol*U_Gamma^3)=0,
U_Gamma^3=U_alg^3, or U_Gamma=U_alg. The remaining scalar comparison is explicit.
