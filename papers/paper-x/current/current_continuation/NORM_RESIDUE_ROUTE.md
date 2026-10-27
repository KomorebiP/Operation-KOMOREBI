# Arithmetic norm residues

The target is an actual finite residue map for the norm of an algebraic integer, followed by an exact residue test for an ideal obtained by dividing a principal ideal by a fixed representative.

For a finite free commutative integral algebra S with basis b, reduce the multiplication matrix of x modulo m. Its kernel contains the principal ideal mS. The induced matrix representation of S/mS has a determinant monoid homomorphism. The theorem `quotientNorm_mk` identifies its value with the reduction of `Algebra.norm ℤ x`, and `quotientNorm_basis_independent` removes the auxiliary choice of basis.

For S=O_K this yields `integerQuotientNorm K m`. When m is nonzero its source is finite; its cardinality is exactly m^[K:Q]. Signed norm congruence is an output of the construction. No polynomial congruence predicate is assumed.

Absolute principal ideal norm is treated separately. If the element norm is nonnegative, its residue equals the quotient norm. If the element norm is nonpositive, its residue is the negative of the quotient norm. The `Bool` sign interface `normSign` includes zero in both signs, which is harmless for the identity. Nonzero fundamental-cone points are partitioned by their strict signs in the separate geometric lane.

`idealResidueTarget K m positive J c` is the subset of the actual quotient consisting of q with signedResidue(q)=c*absNorm(J) modulo m. For actual ideals satisfying I*J=(x), and the indicated norm sign, the theorem `ideal_norm_residue_iff` states that absNorm(I)=c modulo m if and only if [x] lies in this target, provided absNorm(J) is a unit modulo m. The variant `_of_coprime` expresses this hypothesis as coprimality. The intermediate product identity does not assume invertibility.

The target is allowed to be empty. Neither surjectivity of the norm on residue units nor nontriviality of a character pulled back along the norm is inferred.

The boundary example uses actual principal ideals in ℤ. The elements -1 and 2 agree modulo 3 and have equal signed norm residues, but their principal ideal norm residues are 1 and 2. Thus forgetting the sign is false even over the rational integers.

Verification and corrections:

- NormResidueAlgebra passed strict Lean after removing a redundant explicit ℤ-algebra instance that caused a module-instance diamond, and correcting the matrix natural-cast lemma name.
- NormResidueArithmetic passed strict Lean after correcting the qualified rank theorem and making integer-to-ZMod casts explicit. No hypotheses were weakened or added by these corrections.
- An early NormResidueIdealFilter invocation was started before its arithmetic dependency had passed and is excluded from the final evidence. One output log collided with another agent’s generator-attachment log and is not accepted as independent per-module evidence. The final coordinator invocation passed with exit code 0. The only proof-file correction needed at that stage was the strict style-linter change `letI` to `let` in a proposition.
- The first boundary attempt stopped at closed ZMod numeral goals. Kernel `decide` was added to discharge those finite calculations, and the strict rerun passed with exit code 0.

This block does not prove arithmetic Frobenius coverage, norm-residue surjectivity, ray-class character cancellation, or an Euler-product identity. Full Claim 9.1 remains partial.

Final verification: all four modules passed strict compilation; they contain 22 theorem declarations and 8 definitions. Source and object SHA-256 values are recorded in `privatechecks/norm_residue_hashes.json`. The final filter check was run by the root’s sequential compiler coordinator and recorded in `privatechecks/coordinator_a_NormResidueIdealFilter.json`. Temporary stalls were diagnosed as object-import I/O contention. Both pending own jobs had already finished before the requested interruption, so no own compiler process was killed. No optional new compiler runs were launched after the final pass.
