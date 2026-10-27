# Native rational arithmetic and prime reduction: checked return

Owner: `/root/reachability`. Parent: checked Lean v0.6.0 archive SHA-256 `032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.

Production artifact: `RealizationBoundaries/RationalComputability.lean`.
Source SHA-256: `a912908e18e654ef13c6a267b837480198183af843cb13b13f6b0e6c5ceec788`.

## Encoding and exact arithmetic

`RationalCode := (ℕ × ℕ) × ℕ` uses the ordinary native primitive-codable natural product. Code `((a,b),d)` decodes to `(a-b)/(d+1)` by actual `mkRat`. Codes are deliberately redundant; the coordinator's computable normal-code interface supplies canonical names. This module does not treat redundant codes as a group copy with decidable code identity.

- `RationalCode.value_surjective`: every actual rational is decoded by a code.
- `value_add`: raw `add` decodes to actual rational addition.
- `value_neg`: raw `neg` decodes to actual rational inverse.
- `equal_iff`: the native Boolean cross-multiplication test is true exactly when the actual decoded rationals are equal.
- `primrec_add`, `primrec_neg`, `primrec_equal`: these algorithms are primitive recursive in Mathlib's native recursion semantics.

## Literal normalized fields

`primrec_nat_gcd` is proved by bounded greatest-common-divisor search, including the both-zero branch. Define the absolute numerator magnitude by `(a-b)+(b-a)`, divide its two signed parts and the positive denominator by their gcd, and obtain:

`normal_fields c : (value c).num = (normalPositive c : ℤ) - (normalNegative c : ℤ) ∧ (value c).den = normalDenominator c`.

All three field algorithms have explicit native `Primrec` proofs. The fields are the literal reduced `Rat` fields, not an unnormalized surrogate. Zero numerators, negative numerators, and cancellation of denominator primes are covered.

## Exact total prime reduction

`primeResidue c p : ℕ` uses the native normalized numerator and denominator. It returns zero if the normalized denominator is zero modulo `p`; otherwise it uses the natural Fermat-power inverse `den^(p-2)` and reduces the product modulo `p`.

- `primrec_primeResidue : Primrec₂ RationalCode.primeResidue` holds for this total natural-number function.
- `primeResidue_cast c {p : ℕ} [Fact p.Prime]` proves its cast to `ZMod p` is the literal cast of `value c`.
- `primeResidue_lt c (hp : p.Prime)` proves the emitted value is below `p`.
- `primeResidue_eq_val` identifies it with the literal finite-field cast's canonical `.val`.

This matches the actual rational sections, including their exceptional denominator-prime zero branch. The modular inverse proof uses Fermat's theorem in the finite prime field. The implementation is an exact terminating algorithm, with no efficiency claim.

## Verification

- `verification/development/RationalComputability_005.json`: exit 0, warnings as errors, autoImplicit false, 3.37 seconds, final source hash above.
- `verification/development/RationalComputability_replay.log`: kernel replay exit 0.
- `verification/development/RationalComputability_contract.log`: exact type checks, allowed-axiom reports, and executable smoke evaluations exit 0.
- Headline native and interpretation theorems depend only on `propext`, `Classical.choice`, `Quot.sound`.
- Preliminary failures 001–002 and 004 are retained as development records. They involved elaboration/rewrite details, current proof-style/deprecation linters, and the need to place `Fact p.Prime` in scope before elaborating a rational-to-field cast. Record 003 checked the core arithmetic; 005 checks the full final module.

Executable boundary checks emitted:

| Input | Output |
|---|---|
| normalized denominator of `(3-1)/2` | `1` |
| residue of `(3-1)/2` modulo `2` | `1` |
| residue of `1/2` modulo `2` | `0` |
| residue of `1/2` modulo `5` | `3` |
| residue of `-1/2` modulo `5` | `2` |
| equality of `1/2` and `2/4` | `true` |
| decoded raw addition `1/2 + 1/3` | `5/6` |

The cancellation example guards against applying the exceptional zero branch to an unnormalized denominator.

## Integration boundary

The computable-normal-code owner has been notified and is reusing this exact API. Add `RationalComputability` after `PrimeComputability` and before the native normal-code presentation module in the build/import list. This module closes the native rational arithmetic dependency of 8.1. Full oracle presentation semantics and the computable copy theorem remain the presentation work package's integration obligations.
