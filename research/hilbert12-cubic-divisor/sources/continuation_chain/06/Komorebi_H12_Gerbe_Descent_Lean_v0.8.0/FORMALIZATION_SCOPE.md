# Formalization boundary — 51 freshly checked theorem constants

| Module | Count | Kernel-checked content |
|---|---:|---|
| H12GerbeDescent | 29 | Explicit 20-coordinate exterior-cube operator; 400 exact minors; eighteen elimination certificates; universal invariant normal form; explicit Hodge projection obstruction; conjugation parameter constraints |
| H12FlatGerbeAction | 9 | Explicit 15-coordinate exterior-square operator; 225 exact minors; six-coordinate integral Hodge projection and right inverse; cofactor intertwining; inverse/opposite twist and parameter identities |
| H12WeilCharacter | 13 | Finite residue pairing and nondegeneracy; product-polarization distinction; exact Jacobi/Gauss group-algebra coefficients; fifth-smoothing determinant |

All files use the pinned Lean 4.34.0-rc2 and bundled Std, with one worker and
warnings as errors. Every named theorem's transitive axioms are audited. Only
propext, Classical.choice, and Quot.sound are allowed where required. There
are no admitted proofs, project axioms, native_decide calls, or unsafe code.
A separate false integer equality must be rejected.

The exterior/Hodge matrices are concrete coefficient presentations. Their
identification with singular cohomology and complex Hodge projection is an
ordinary proof. No Lean definitions of holomorphic gerbes, analytic sheaf
cohomology, the exponential exact sequence, Cartan vanishing, or quotient
stacks occur here. The analytical gerbe theorems apply the coefficient results
through that explicitly disclosed dictionary. The finite Gauss certificate
is in the integral Eisenstein group algebra; its interpretation at an actual
complex root is an ordinary algebraic evaluation.

The geometric statement counts pullback-fixed ISOMORPHISM CLASSES, not chosen
equivariant structures or gamma special values. No new theorem asserts an
actual gamma descent, chooses its class, or proves the polarized reality
condition.

The cumulative source inventory is 267 (216 inherited plus 51 new). The 216
predecessor declarations are retained, with prior evidence, in the unchanged
predecessor ZIP. No complete fresh 267-theorem replay is claimed.
