# Failures and corrections

## Mathematical corrections to the preceding brainstorm

1. Its printed row product (1,-1,3)(M-I)=(-24,6,84) was incorrect. The exact
   result is (0,0,-6). The quotient modulo six survives with explicit preimages.
2. Lattice coinvariants do not restrict the independent infinite-cyclic unit
   character. The semidirect-product abelianization has an additional Z factor.
3. A single mixed holomorphic commutator is gauge-dependent even when the
   real-cover restriction and cochain value at zero are preserved.
4. A trivial holomorphic line on the Stein cover can have a unit linearization
   with arbitrary phase at the conductor fixed point, even normalized at zero
   and inversion-symmetric. Equivariant flatness is stronger than triviality.
5. The actual extra-Eisenstein gamma cochain was not computed: it is outside
   the domain of the existing rank-three translation formula. Scalar F-ratios
   yield the trivial square commutator and cannot replace a gerbe cochain.

These failures do not refute the gamma special-value target. The repaired
compact-line and based-holonomy theorems are proved separately in PROOF.md.

## Tool execution

An attempted streaming container execution was rejected with
StreamingExecNotEnabledContainerError before the command ran. The identical
runtime assembly was then run synchronously and completed. Its combined
SHA256 matched the pinned archive. No result is attributed to the rejected call.

All four new Lean source modules compiled on their first executed versions.
The exact production checker and fresh isolated Lean audit passed. The checker
was subsequently extended to include the compact exterior-square calculation
and rerun successfully. The final replay uses the extended source.

The intentionally false arithmetic control is expected to fail and is not a
production mathematical failure. No inherited full replay or numerical gamma
computation was attempted in this release.
