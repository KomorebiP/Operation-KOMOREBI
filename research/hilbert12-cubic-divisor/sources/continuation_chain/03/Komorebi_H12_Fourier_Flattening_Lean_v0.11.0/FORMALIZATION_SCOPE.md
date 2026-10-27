# Formalization scope: 28 new kernel-checked theorem constants

| Module | Count | What Lean checks |
|---|---:|---|
| H12OrbitAntidifference | 14 | Universal finite integer prefix summation, telescoping, finite-support solvability with both endpoints, charge conservation under gauges, and uniqueness |
| H12DualFourier | 9 | Actual transpose unit/inverse, pairing identity, injectivity, all natural-iterate conductor residues, cubic matrix relation, and winding-gauge residue |
| H12FourierExtension | 5 | Explicit denominator-six flat-character numerator, its compatibility identity, the based cubic exponent, and finite-grid phase coefficient |

The pinned compiler is Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Only bundled Std is used. All new theorems are compiled in a clean directory with
one worker and warnings as errors. Their transitive axiom dependencies are
inspected. Only propext, Classical.choice, and Quot.sound are permitted where
needed. No sorry/admit, custom axiom, native_decide, or unsafe declaration is
accepted. A deliberately false integer equality must be rejected.

Not formalized: the global smooth or holomorphic Fourier expansion; the
adapted-norm convergence proof; existence of a smooth/holomorphic logarithm;
exponentiation and line-bundle compactification; the conjugation-only analytic
criterion; or its application to actual gamma/model cochains.

Those results have ordinary proofs with their hypotheses in PROOF.md. No
relative gamma multiplier has been constructed, no actual gamma orbit sums
have been evaluated, and no special-value power equality is supplied as an
axiom. Finite integer statements are not advertised as a formal analytic theory.

The 360 inherited declarations are preserved with their historical evidence in
the predecessor ZIP. They are not freshly recompiled. The new source inventory
would be 388 if counted cumulatively; this release claims 28 fresh checks only.
