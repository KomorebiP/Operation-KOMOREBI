# Exact mean cancellation for residue norm characters

For a finite monoid `R`, a monoid homomorphism `N : R →* S`, a complex
multiplicative character `χ`, and a unit `u : Rˣ`, the new theorem proves

\[
\chi(Nu)\ne1\quad\Longrightarrow\quad
\sum_{a\in R}\chi(Na)=0.
\]

Multiplication by `u` is a permutation of the entire finite monoid, including
nonunits. Consequently the sum equals itself multiplied by `χ(Nu)`. Cancellation
in the complex field proves it is zero. This requires no surjectivity of `N`.

The condition is equivalently nontriviality of the pulled-back character on
`Rˣ`. Nontriviality of `χ` on `S` alone is deliberately not used: its restriction
to the norm image may be trivial.

`NormResidueCharacter.lean` specializes the result to the actual map

\[
N:\mathcal O_K/m\mathcal O_K\longrightarrow\mathbb Z/m\mathbb Z
\]

defined as the determinant of multiplication in `NormResidueArithmetic.lean`.
The character in this specialization has type `ZMod m →*₀ ℂ`. The theorem also
proves zero mean for `a ↦ χ(c·N(a))` for every fixed residue `c`, including the
negative sign factor. This provides the exact finite mean condition used in
the signed residue-lattice count.

The arithmetic specialization uses any finite enumeration of the quotient.
For `m ≠ 0`, the earlier theorem `integer_quotient_finite` supplies its
finiteness; this is independent of the character witness. The unit witness
remains an arithmetic input. This module does not prove its existence for
every nontrivial codomain character.

Compiler and axiom-check evidence is recorded in
`privatechecks/norm_residue_character_verification.json`. All previously frozen
Mellin modules are unchanged.

The corrected source passed the strict compiler in the coordinator's sequential
wave (`coordinator_a_NormResidueCharacter.log`, exit zero), with five theorems
and no definitions. The first compiler attempt failed on the permutation-sum
overload, the unit-coercion homomorphism name, and a deprecated tactic. These
API errors were corrected without changing mathematical hypotheses. The run
finished before a requested cancellation, so no interruption is claimed.
