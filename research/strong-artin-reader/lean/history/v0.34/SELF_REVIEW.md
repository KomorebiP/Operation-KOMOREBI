# Self-review — v0.34

Review type: same-author mathematical review plus Lean checking and independent exact modular arithmetic. Not an independent specialist report or independent kernel.

1. The upper ring is genuinely Z/(m*p), not a dual-number substitute. The reduction and residue maps are ZMod.castHom maps with their divisibility proofs.
2. layerEmbedding is an additive map induced from integers. Injectivity uses m != 0 and cancellation in Z, not cancellation in the upper ring.
3. The kernel characterization is proved in both directions. No dimension/cardinality heuristic substitutes for it.
4. p|m is essential to square-zero multiplication. r=0 in the prime-power specialization is deliberately excluded.
5. The kernel-coordinate equivalence does not extend to a coefficient-ring splitting. The no-retraction theorem is a negative control.
6. The actual left/right multiplication laws prove equivariance. The residual adjoint is not supplied as an unexplained model assumption.
7. No image-order invertibility, diagonalization or semisimplicity is assumed by the prime-power criteria.
8. Every prescribed mismatch is defined from U and F^d in the actual kernel. The previous layer is preserved modulo m, not only modulo p.
9. The inherited simultaneous criterion retains one shared x and distinct local z_i. The incompatible family tests the difference.
10. All layer depths are covered by the coordinate theorem, but this is not a compatible existence theorem for a tower. The scalar mod9-to-mod27 obstruction remains a test against that inference.
11. No automorphic object, global arithmetic localization or new Strong Artin case is claimed.
12. The direct dependencies are immutable copies with provenance. Every accepted new constant is listed for axiom auditing. Cached Mathlib objects are reused and trusted at the pinned revision.
