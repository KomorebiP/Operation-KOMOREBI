# Manuscript crosswalk — Strong Artin Lean v0.8.0

Target manuscript family: **Finite Trace Alphabets, Residual Realization, and the Strong Artin Gate**, together with the adjacent cyclic-descent finite algebra used by that paper.

## 1. Cyclic extension spectra and finite attachment algebra — checked

Lean now checks:

- cyclic label rotations and their group law;
- alignment sets and their exact coset/stabilizer structure;
- uniqueness from one aperiodic stable spectrum;
- actual complex DFT on `ZMod p`;
- Fourier twist law and Fourier attachment equivalence;
- matrix coefficient rotation `e_k(cA)=c^k e_k(A)`;
- signed characteristic-polynomial coefficient identification;
- one active coefficient degree not divisible by `p` separates all cyclic twists;
- rank-prime power-label injection.

These formalize the finite spectrum criterion machinery.  They do **not** by themselves assert automorphic attachment.

## 2. Galois extension torsor — checked on isomorphism classes

The formalization now proves the literal quotient-character torsor statement at the level of representation isomorphism classes.

For a normal subgroup `H <= G`, if two extensions have equivalent irreducible restrictions, Lean proves

`exists! chi_bar : G/H -> K^×, Nonempty ((rho tensor chi_bar).Equiv sigma)`.

The proof has both halves internally:

- **transitivity:** transport the second extension to the first realization, apply Schur to the scalar-ratio operators, and factor the resulting character through `G/H`;
- **freeness on isomorphism classes:** an equivalence between two quotient twists yields a self-twist by the ratio character; the previously checked Schur self-twist obstruction forces that ratio character to be trivial.

Thus the manuscript statement that the Galois extension fibre is a quotient-character torsor no longer depends on a fixed common vector-space normalization.

## 3. Determinant selector — checked on the Galois side

Lean proves the literal representation identity

`det((rho tensor chi)(g)) = chi(g)^dim(rho) * det(rho(g))`.

For `G/H ~= C_p` and `p ∤ dim(rho)`, the `n`th-power map on quotient characters is injective.  Consequently:

- quotient twists have distinct determinant characters;
- in the fixed-space extension torsor, equal determinant functions force equal extensions;
- in the natural different-space formulation, equivalent irreducible restrictions plus equal determinant functions force representation equivalence.

The automorphic central-character analogue still depends on the external automorphic twisting/base-change formalism.

## 4. Galois trace separator — checked end-to-end

Over `C`, Lean proves:

- a nontrivial quotient self-twist is impossible when the restriction is irreducible;
- therefore some element outside `H` has nonzero trace;
- a canonical faithful character of the model `C_p` pulls back through `G/H`;
- one such off-`H` nonzero trace separates **all `p` quotient twists**.

This formalizes the manuscript's degree-one Galois separator theorem in the finite-group setting.  The Chebotarev step turning the group element into an unramified Frobenius place remains external.

## 5. Quotient-prime scalar and `C_p` collapse — checked

In characteristic `p`, Lean proves:

- scalar `p`-torsion collapses: `x^p = 1 -> x = 1` in the field/reduced setting used here;
- every irreducible `C_p` representation is trivial;
- every semisimple `C_p` representation is trivial;
- equal-dimensional semisimple `C_p` representations are equivalent;
- the characteristic-`p` simple-label collapse is implemented through the group-algebra Jacobson radical.

## 6. Moving induced blocks — checked

For finite-index `H <= G` and a scalar character trivial on `H`, Lean constructs an actual representation equivalence

`Ind_H^G(tau) ~= Ind_H^G(tau) tensor chi`.

The proof goes through Mathlib's concrete coinduction model and the finite-index `Ind ~= Coind` equivalence.  This formally closes the moving-block twist-blindness calculation.

## 7. Modular Clifford structure — substantially strengthened in v0.7

New checked theorems include:

- every `C_p` orbit has size `1` or `p`;
- in characteristic `p`, restriction across a prime-cyclic quotient is injective on **irreducible representation classes**;
- more strongly, a nonzero `H`-intertwiner between irreducible ambient representations forces ambient equivalence;
- **modular Clifford semisimplicity:** an irreducible finite-dimensional `G` representation restricts semisimply to every normal subgroup.

The last theorem is proved through the Jacobson radical of `K[H]`: normality makes the radical-generated subspace `G`-stable, irreducibility plus Nakayama forces it to vanish, and the action then factors through the semisimple quotient `K[H]/J(K[H])`.

### Exact remaining semisimple-collapse boundary

The source does not yet contain a single theorem that starts only from two arbitrary semisimple `G` representations with equivalent restrictions to `H` and returns their equivalence.  The remaining step is finite semisimple multiplicity bookkeeping/cancellation: lift the newly checked irreducible restriction-injectivity theorem from simple summands to arbitrary finite semisimple sums.

This is now the remaining internal modular representation-theory assembly step; the earlier radical, orbit, stable-block and moving-block mechanisms are all checked.

## 8. Finite trace image bound — checked

Lean proves the manuscript theorem

`|Gamma| <= t^(n^2)`

under the stated finite semisimple matrix-image hypotheses.  The formal chain includes:

- faithful semisimple image algebra has zero Jacobson radical;
- finite-dimensional semisimple image algebra admits a Wedderburn matrix-block decomposition;
- matrix trace pairing is nondegenerate;
- multiplicity-weighted block trace pairings remain nondegenerate when the multiplicities are nonzero in the field;
- finite direct sums preserve nondegeneracy;
- a basis can be selected from the spanning group image;
- trace coordinates give an injection;
- the image algebra has dimension at most `n^2`.

## 9. Finite cyclotomic alphabets and separating primes — checked

Lean constructs the bounded torsion-root alphabet and the associated finite degree-`n` split-polynomial alphabet, proves its exact multiset/binomial cardinality, and proves that finite-image characteristic polynomials land in it.

For a finite polynomial alphabet over a Dedekind domain, Lean proves all but finitely many prime ideals are separating: two distinct integral polynomials can collide modulo only finitely many prime ideals.

## 10. Large residual realization funnel — checked around one external theorem

Checked internally:

- trace bound plus `t^(n^2) < ell` implies `ell ∤ |Gamma|`;
- finite-image characteristic-zero lift polynomials lie in the bounded cyclotomic alphabet;
- separating reduction upgrades residual polynomial equality to exact characteristic-zero equality;
- the complete post-lift recovery funnel is assembled.

Still imported: **Brauer/Nesbitt cross-characteristic lifting itself**.  The pinned Mathlib revision does not expose the needed modular-to-characteristic-zero lifting theorem, so it is not encoded as a custom axiom.

## 11. Quotient-prime polynomial algebra — checked

Lean proves the root-power/Frobenius identity in characteristic `p` and injective cancellation through Frobenius on reduced rings.  This is the polynomial algebra used in the nonsplit quotient-prime congruence argument.

Global residual automorphy and automorphy lifting remain external.

## 12. Local Artin descent — group-theoretic core checked

Lean proves: finite image on a finite-index subgroup implies finite image on the whole group.

The local Langlands/base-change identification needed to apply this to Weil--Deligne parameters remains external.

## 13. Explicitly external / open

This formalization does **not** prove Strong Artin.  The following remain external or open:

- the final semisimple multiplicity-reflection assembly noted in §7;
- Brauer/Nesbitt cross-characteristic lifting;
- Chebotarev density/global Frobenius identification;
- automorphic induction and cyclic base change;
- local Langlands compatibility;
- unrestricted residual or `l`-adic Galois realization;
- pseudocharacter/eigenvariety occurrence theorems outside currently established ranges;
- quotient-prime automorphy lifting;
- global nonemptiness of the cyclic alignment intersection;
- full Strong Artin.

No such global/open statement is introduced as a custom Lean axiom.

## 14. v0.9 prime-field characteristic-polynomial propagation — checked

The new theorem `linearMap_charpoly_pow_prime` proves over `F_p` that

\[
\chi_{f^p}(T)=\chi_f(T).
\]

For a normal subgroup `H` with `G/H ~= C_p`, the theorem
`charpoly_eq_of_restriction_equiv_cp` then proves

\[
\operatorname{Res}_H\rho \simeq \operatorname{Res}_H\sigma
\quad\Longrightarrow\quad
\chi_{\rho(g)}(T)=\chi_{\sigma(g)}(T)
\quad\text{for all }g\in G
\]

over the prime field.

This sharpens the remaining internal residual-collapse boundary considerably.  The missing
statement can now be isolated as the semisimple Brauer--Nesbitt property represented in Lean by
`SemisimpleCharpolyRigidityFp`:

\[
\bigl(\forall g,\ \chi_{\rho(g)}=\chi_{\sigma(g)}\bigr)
\Longrightarrow
\rho\simeq\sigma
\]

for finite-dimensional semisimple `F_p` representations.  The checked theorem
`semisimple_residual_collapse_of_charpoly_rigidity` proves that this one property would close the
semisimple quotient-prime residual-collapse theorem immediately.

The property is **not** asserted as an axiom or instance in the source.
