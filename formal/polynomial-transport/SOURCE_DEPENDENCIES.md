# Pinned mathematical source dependencies

**Checked 4 November 2026 · Komorebi P.**

Check type: exact theorem verification and notation translation. The primary source is the Mathlib project at revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. These source files were read from the pinned local dependency checkout. The replay checks the dependency revision and tracked cleanliness before compilation.

The table identifies the principal inputs and their application. The imported environment also contains their transitive dependencies. The full dependency revision is fixed by the Lake manifest.

| Primary source | Results used | Application and hypotheses | SHA-256 |
|---|---|---|---|
| [Algebra/Polynomial/Basic.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Algebra/Polynomial/Basic.lean) | `Polynomial.coeff`, `Polynomial.ofFinsupp`, `Polynomial.monomial_mul_monomial`, `Polynomial.induction_on'` | Finite-support polynomial representation and actual polynomial induction. | `6cf18c0562bd1ce27fe5a018e1a1a897e7ddaaa1b1f9dbd1d7ff72d50842284a` |
| [Algebra/Polynomial/Basis.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Algebra/Polynomial/Basis.lean) | `Polynomial.basisMonomials`, `Polynomial.coe_basisMonomials` | The ordinary monomial basis. | `75b326d7f4d3216da9e58dce0bd38d97bd55c41ab016e6deafd74eb82e7bca8d` |
| [LinearAlgebra/Basis/Defs.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/LinearAlgebra/Basis/Defs.lean) | `Module.Basis.repr`, `Module.Basis.equiv`, `Module.Basis.equiv_apply` | Finitely supported coordinates and the correctly oriented basis equivalence. | `89865e3cbfcee915d186b3448eb18c070b0601e4e30c4d0d661bd4862b723d29` |
| [Algebra/Polynomial/Sequence.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Algebra/Polynomial/Sequence.lean) | `Polynomial.Sequence.basis`, `Polynomial.Sequence.basis_eq_self` | An integral-domain polynomial sequence with unit leading coefficients gives a basis, applied only to ℚ. | `c0f1be67db5c11f3326a8bc80140fee079ba0a4dabf8d2986d88c9cdcb7a9503` |
| [RingTheory/Polynomial/Pochhammer.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/RingTheory/Polynomial/Pochhammer.lean) | `descPochhammer`, `monic_descPochhammer`, `descPochhammer_natDegree`, `descPochhammer_eval_eq_descFactorial` | Descending-product convention, monicity, degree and natural-argument evaluation. | `ad7f0f7072531ab4cbfb55f10764fb0753d0f0daf5cdce3e39675c3b939894f0` |
| [Algebra/Polynomial/Degree/Lemmas.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Algebra/Polynomial/Degree/Lemmas.lean) | `Polynomial.natDegree_sum_eq_of_disjoint` | Distinct degrees of the nonzero supported summands preserve the leading term. | `70e1ffe5c24fbf372293c2853dd3168169c023cf0d36e91402b5273f803181dc` |
| [Combinatorics/Enumerative/Stirling.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Combinatorics/Enumerative/Stirling.lean) | `Nat.pow_eq_sum_stirlingSecond_mul_descFactorial` | Classical second-Stirling expansion at all natural evaluation arguments. | `135208f89b047336d78bacd537d145d8d75a76890146f639f1058cf88e8474df` |
| [Algebra/Polynomial/Roots.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Algebra/Polynomial/Roots.lean) | `Polynomial.eq_of_infinite_eval_eq` | Equality at infinitely many rational addresses implies polynomial equality. | `fe8cd6724459d2461098ff4f246f3496115210a1e36802c33565f2f73fa1640c` |
| [RingTheory/RootsOfUnity/Complex.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/RingTheory/RootsOfUnity/Complex.lean) | `Complex.isPrimitiveRoot_exp`, `Complex.isPrimitiveRoot_I` | Exact primitive roots for positive orders and the order-four sign control. | `a403d79d20137cc03f3e8899594a4c5c63333a690cfb4b77b066018dc3925a53` |
| [RingTheory/RootsOfUnity/PrimitiveRoots.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/RingTheory/RootsOfUnity/PrimitiveRoots.lean) | `IsPrimitiveRoot.pow_inj`, `IsPrimitiveRoot.ne_zero`, `IsPrimitiveRoot.eq_orderOf` | Primitive-root order, nonzero value and injectivity within canonical residue range. | `226fe247c20101f787ea6fb3bfafb92bf73fd62674150eb7b8207342354a8efb` |
| [Algebra/Field/GeomSum.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Algebra/Field/GeomSum.lean) | `geom_sum_eq` | The finite geometric-sum formula for a ratio unequal to one, applied in ℂ. | `38203fde4e073b2af47fb14acccaa5d46bf0ba50e86d2f8d96eda1803f08b8c0` |
| [Algebra/Polynomial/Eval/Degree.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Algebra/Polynomial/Eval/Degree.lean) | `Polynomial.comp_C_mul_X_coeff` | Coefficients of the actual substitution p(cX). | `81f41446155dd6c8a79d8090cd080bacfc6529e11b32a8dbf54d4399e5fc43c0` |
| [Algebra/BigOperators/Ring/Finset.lean](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Algebra/BigOperators/Ring/Finset.lean) | `Finset.sum_mul_sum` | Finite distributivity in complete packet convolution. | `3260deb025880a9c56b258bc0d9c53106aab2452599141b1e1c8f5bb0f589aa3` |

## Exact application checks

- The polynomial-sequence basis constructor is used over the integral domain ℚ. Monicity gives unit leading coefficients at every degree. The monomial basis is the source of `Basis.equiv`, and the falling basis is its target.
- `Basis.repr` has finitely supported coordinates. Its inverse laws give the actual linear equivalence on finite polynomials.
- Degree preservation uses the distinct degrees of the nonzero supported summands. The zero polynomial is handled separately for its degree ⊥.
- The second-Stirling identity is proved for natural-number evaluations and then lifted to ℚ[X] using infinitely many distinct rational addresses. This repeats the earlier reader companion’s classical helper.
- Primitive-root power injectivity is used only with canonical exponents below N. Powers outside that range are reduced modulo the exact order.
- The character proof rewrites to a quotient of powers, so k < r introduces no truncated natural subtraction. The geometric-sum branch has a proved ratio unequal to one and a proved N-th power equal to one.
- Positivity and the canonical residue bound exclude zero modulus. The latter already implies positivity, although both premises are retained explicitly in the Fourier signatures.
- The coefficient lemma applies to actual polynomial composition with C(ζ^ℓ) X. Polynomial extensionality supplies the universal identity, without a finite sample cutoff.
- Rational coefficient extension is a ring map. The comparison with falling coordinates occurs after that extension in ℂ[X].

## Additional inspected primitives

The review also inspected `Polynomial.comp` in `Mathlib/Algebra/Polynomial/Eval/Defs.lean`, `pow_mod_orderOf` in `Mathlib/GroupTheory/OrderOfElement.lean`, and the integer-power identities `zpow_neg`, `zpow_natCast`, and `inv_pow`. Their instances are applied to complex numbers in the compiled source.

**Implication verdict:** verified for the types and hypotheses instantiated in the companion. The source identities, literal statements, and applications were checked separately. The complete source-to-claim list is in [CLAIM_MAP.json](CLAIM_MAP.json).
