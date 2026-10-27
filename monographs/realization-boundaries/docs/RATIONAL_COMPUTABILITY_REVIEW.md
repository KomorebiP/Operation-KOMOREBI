# Independent review: native rational arithmetic and prime reduction

## Normalized claim and verdict

**Verdict: proved as written. No mathematical defect found.**

Source: `RealizationBoundaries/RationalComputability.lean`.
Reviewed SHA-256: `a912908e18e654ef13c6a267b837480198183af843cb13b13f6b0e6c5ceec788`.
Compiler receipt: `verification/development/RationalComputability_005.json` (exit 0, warnings as errors, autoImplicit false).

For every native rational code `((u,v),d)`, its meaning is `(u-v)/(d+1)` in the actual rational field. Addition, negation and equality of these meanings are implemented by actual primitive recursive operations on natural-number products. Native normalization fields are proved equal to the literal reduced `Rat.num` and `Rat.den`. For every prime `p`, the total natural-number `primeResidue` agrees with the actual total Rat-to-`ZMod p` cast, including normalized denominator primes.

The primitive-recursion assertions concern the concrete natural-number arithmetic and bounded searches, rather than a newly introduced predicate that simply labels a classical definition computable.

## Dependency graph and critical checks

1. `value_eq` identifies each raw code with its rational fraction, with a strictly positive denominator.
2. Cross multiplication proves `equal_iff`; polynomial identities prove `value_add` and `value_neg`. The denominator predecessor in the result of addition is safe because the product of positive denominators is positive.
3. `primrec_nat_gcd` derives the actual gcd from bounded greatest-common-divisor search. The bound is the sum of the two inputs, and the both-zero case is handled separately.
4. `normal_fields` derives the actual reduced numerator and denominator from that gcd. It splits positive and negative differences, using divisibility of the numerator magnitude by the gcd before rewriting division of a negative integer. It does not incorrectly assume that arbitrary Euclidean division commutes with negation.
5. `numeratorResidue_cast` proves the signed numerator residue. The added modulus makes the natural subtraction safe: the negative-part residue is strictly less than the positive modulus and therefore at most the positive-part residue plus the modulus.
6. `primeResidue_cast` splits at divisibility of the **normalized** denominator. In the zero branch the actual total Rat cast is zero. Otherwise Fermat inversion is proved to equal the multiplicative inverse in `ZMod p`. Prime 2 is included: exponent `p-2` is zero, and the only nonzero denominator residue is one.
7. `primeResidue_lt` gives a canonical residue below the prime; `primeResidue_eq_val` identifies it with the actual field element's natural representative.

All arithmetic, normalization and modular-power computations have explicit `Primrec` proofs built from native arithmetic, composition, pairing and bounded search. The production prime predicate and counting dependencies are similarly derived in `PrimeComputability.lean`.

## Obligation matrix

| Obligation | Verdict | Evidence |
|---|---|---|
| Denominator never zero | Passed | `denominator_pos` |
| Every rational has a native code | Passed | `value_surjective` |
| Arithmetic and equality preserve actual rational meaning | Passed | `value_add`, `value_neg`, `equal_iff` |
| Raw numerator cancellation handled | Passed | `normal_fields` |
| Negative numerator normalization exact | Passed | Negative branch of `normal_fields`, with gcd divisibility |
| Zero numerator gives normalized denominator one | Passed | Included in `normal_fields` and finite checks |
| Native normalization is genuinely primitive recursive | Passed | Actual `primrec_nat_gcd` and field-projection composition proofs |
| Residue subtraction has no underflow | Passed | Explicit bound in `numeratorResidue_cast` |
| Exceptional branch uses the reduced denominator | Passed | `primeResidue_cast` rewrites by `normal_fields` |
| Nonexceptional inversion includes prime 2 | Passed | Fermat inverse identity under the actual prime hypothesis |
| Correctness for composite or zero moduli | Out of scope | Operations are total there, but the field-correctness theorem explicitly assumes primality |
| Polynomial-time or bit-complexity claim | Out of scope | No such claim is made |

## Independent finite checks

Log: `verification/development/RationalComputability_independent_review.log`, exit 0.

A complete finite range of 288 raw codes was checked: positive and negative numerator parts from 0 through 5 and raw denominators from 1 through 8. All five aggregate checks returned true:

* literal normalized `Rat.num`/`Rat.den` fields for every code;
* all 1,152 prime reductions at primes 2, 3, 5 and 7, compared directly with the actual Rat-to-ZMod cast's `.val`;
* all 82,944 ordered code-pair equality decisions compared with actual rational equality;
* all 82,944 ordered code-pair additions compared with actual rational addition;
* all 288 negations compared with actual rational negation.

Explicit branch checks returned:

| Raw fraction | Prime | Result | Reason |
|---|---:|---:|---|
| `2/2` | 2 | 1 | Cancellation removes the raw denominator prime |
| `-3/6` | 2 | 0 | Reduced denominator is 2, so this is exceptional |
| `-3/6` | 3 | 1 | Reduced fraction is `-1/2`; raw denominator divisibility by 3 must not force zero |
| `6/15` | 3 | 1 | Reduced fraction is `2/5` |
| `-6/15` | 3 | 2 | Signed residue is retained after cancellation |

These checks exercise cancellation, signs, zero and the smallest prime. They are sanity checks, not a replacement for the universal Lean proofs.

The reviewed source's existing kernel replay passed (`RationalComputability_replay.log`). Explicit axiom inspection of `normal_fields`, `primrec_primeResidue`, `primeResidue_cast` and `primrec_nat_gcd` reports only `propext`, `Classical.choice`, `Quot.sound`.

## Remaining gap and provenance

No missing implication was found in this module's stated arithmetic/reduction contracts. This does not by itself prove the complete oracle-computable presentation theorem; that also needs the native group-code equality/addition bridge, the actual oracle-recursion proofs, and the conversion from redundant codes to a bijective natural-domain copy.

Review provenance: separate-agent source derivation and finite runtime checks. The pinned imported Lean/mathlib implementation remains part of the project's recorded trust boundary.
