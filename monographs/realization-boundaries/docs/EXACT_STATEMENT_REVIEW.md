# Exact statement review — v0.6.0

The new source interfaces were compared with the unchanged final monograph's Chapter 6 LaTeX, labels `thm:rootfiber` and `thm:quotientformula`. This is an internal statement review, not external peer review.

## Objects and hypotheses

`RootFiber W m x` is the subtype of actual elements y of the original infinite group `preimage W` satisfying `m • y = x`. `rootKernel W m` is the kernel of that actual integer-multiplication homomorphism. No root count is supplied as data. The general theorems quantify over every rational subspace W, which includes every paired selector's rational line.

Positive-multiplier hypotheses are visible on all finite-cardinality theorems. `primeRadical m` is the product of the finite set `m.primeFactors`, not the original multiplier and not a list with repetitions. The product convention at zero yields one, but no root-count theorem uses it at zero.

## Proposition 6.2

`rootFiberTranslation` is an equivalence of sets from the kernel to the full fiber, by adding the supplied root. It is intentionally not an additive equivalence onto a nonzero fiber. Both inverse laws are checked. `rootFiber_coset_iff` asserts the literal difference criterion.

`rootKernelEquiv` is an additive equivalence to actual divisor coordinates. Its inverse is extension by zero into the infinite ambient product, with a proved finite-support certificate and a proved integer-annihilation equation. The inverse laws exclude both missing kernel points and spurious parameters. `rootFiberEquiv_symm_apply` preserves the explicit ambient solution formula.

`divisorCoordinates_card` derives the cardinal by a finite product, identifying the actual prime-divisor subtype with the distinct-prime-factor finite set. `rootFiber_finite` proves finiteness separately, preventing a misuse of `Nat.card`, whose value is also zero on infinite types. `rootFiber_card_of_solvable` and `rootFiber_card` give the exact radical-size and empty-fiber branches. The prime-power result proves that p^k contributes p solutions whenever the equation is solvable.

## Theorem 6.3

`divisorCrtEquiv` invokes Mathlib's proved CRT after deriving pairwise coprimality from distinct actual primes and identifying the product modulus with the radical. It is a ring equivalence on the finite coordinate target. `cyclicIntegerQuotientEquiv` composes it with the previously checked quotient by the actual multiple subgroup.

`cyclicIntegerQuotientEquiv_coordinates` and the representative theorem ensure this is not an arbitrary same-cardinality equivalence. `quotientRestriction` is the genuine quotient homomorphism induced by the identity of H_W. The commuting square is proved for every quotient element and identifies the transition with canonical modular reduction. `multiples_eq_radical` states equality of the original subgroups.

`finiteTargetCyclicFactor` factors an arbitrary map to a finite additive group; commutativity of the target is not assumed. Under surjectivity, target cyclicity and squarefreeness are proved. The converse constructs an actual surjection onto any finite cyclic squarefree target. `finite_surjection_ker` identifies its literal kernel as `multiples W (Nat.card F)`, not just a subgroup of equal index.

## Normalization and zero

`normalizedRoot` explicitly specifies coordinate division, with zero at the divisor primes. Uniqueness is conditional on that normalization. By contrast `unique_root_iff_one` proves that a solvable positive-multiplier equation has a unique unrestricted root exactly at multiplier one.

`zeroRootFiberEquiv` identifies the zero-at-zero fiber with the whole original infinite group. The proofs of infinitude, nonemptiness and natural-cardinal zero coexist deliberately. Zero multiplication at a nonzero target is separately empty. These distinguish zero cardinal from emptiness and prevent deleting positivity.

## Remaining algorithm boundary

The mathematical count, parameterization and normalized-root coordinate formula are checked. They do not formalize the oracle-copy semantics, an extraction of the Python arithmetic engine, its runtime bounds, or the monograph's specific finite denominator-support implementation. Entry 6.1 therefore remains CORE_COMPLETE.

All inherited production modules and publication artifacts are preserved unchanged. Exact exported types and declaration dependencies are recorded in the accepted audit and new-type inventory.
