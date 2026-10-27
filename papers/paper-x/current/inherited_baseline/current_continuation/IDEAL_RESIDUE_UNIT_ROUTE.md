# Unit permutations on actual ideal residues

## Target

An average of norm-character weights over the whole ring `𝓞 K/m𝓞 K` does not
in general determine the average of their pullback to an ideal quotient. The
construction here proves cancellation directly on the actual ideal residue set.
It never assumes that its map to the ambient residue ring is surjective.

## Actual permutation

`IdealResidueUnitAction.lean` works with the actual lattice quotient
`IdealResidues K M J`, meaning `J/(J∩M)`, and hence `J/M` when `M≤J`.
Every residue is represented by an actual integer of `J` via `idealPointEquiv`.
Multiplication by any algebraic integer preserves `J` and respects congruence
modulo `M`, so it descends to a map on these residues.

Suppose `mJ≤M` and `u` is a unit of `𝓞 K/m𝓞 K`. Choose actual integer lifts `a`
of `u` and `b` of `u⁻¹`. For every `x∈J`,

\[
a(bx)-x=(ab-1)x\in(m\mathcal O_K)J\subseteq M.
\]

The two multiplication maps are therefore inverse permutations. The Lean
construction retains the permutation and proves its inverse laws. It also proves
that, when `M≤m𝓞 K`, the actual residue norm obeys

\[
r(u\cdot c)=N_m(u)r(c).
\]

Both sides use the already constructed determinant norm on the ring-of-integers
quotient. No abstract substitute for the arithmetic norm is introduced.

## Finite mean

`IdealResidueUnitActionMean.lean` is independent of geometric counting modules.
For a complex multiplicative character `χ`, a supplied unit `u` satisfying

\[
\chi(N_m(u))\ne1,
\]

and any fixed residue `s`, permutation of the finite actual ideal residue set gives

\[
\chi(N_m(u))\sum_c\chi(s\,r(c))=\sum_c\chi(s\,r(c)),
\qquad
\sum_c\chi(s\,r(c))=0.
\]

Choosing `s=1` or `s=-1` supplies the two finite means needed by positive and
negative norm-sign geometry. The proof is a finite permutation argument; it does
not require the unit multiplication to preserve an individual geometric sign
region.

The module also constructs the actual nonzero ideal `mJ` for every `m≠0`, proves
`mJ≤J` and `mJ≤m𝓞 K`, proves `J/mJ` finite, and specializes the mean theorem to
that actual quotient. No coprimality condition on `J` is needed for this result.

## Scope boundaries

The unit witness `χ(N_m(u))≠1` is explicit. This block does not derive such a
witness from nontriviality of `χ` on a larger codomain.

Cancellation of the finite ideal-residue mean does not by itself identify the
final ideal character sum. When a principal-generator count has weight
`χ(NI·NJ)=χ(NI)χ(NJ)`, recovering a bound for `χ(NI)` still requires canceling
`χ(NJ)`. If that value is zero, the principal-weight bound may be trivial. A
coprime class representative or another nonvanishing argument remains relevant
to that later transfer.

## Verification

- The first action compiler attempt rejected quotient-constructor unfolding,
  a deprecated/incorrect norm multiplication API, and one strict style lint.
  These were repaired by explicit constructor reduction and `map_mul`.
- `privatechecks/ideal_unit_action_attempt2.log`: strict compilation exit 0.
- `privatechecks/ideal_unit_mean_attempt1.log`: strict compilation exit 0.
- `privatechecks/ideal_unit_hashes.json`: frozen source and proof-object SHA-256 hashes.
- `privatechecks/ideal_unit_axioms.log`: all thirteen named declarations passed
  axiom inspection, exit 0, using only `propext`, `Classical.choice`, and `Quot.sound`.

The two modules add nine theorems, three definitions and one finite-instance proof.
No predecessor source was modified.
