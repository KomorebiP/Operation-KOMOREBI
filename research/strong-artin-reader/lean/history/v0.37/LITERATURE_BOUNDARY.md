# Source check

Checked 2026-09-12 against the installed Mathlib source at git revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Primary formal source: `Mathlib/NumberTheory/Padics/Hensel.lean`, theorem
`hensels_lemma`. Official documentation:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/Padics/Hensel.html

The required implication is: for an integral polynomial P and a in PadicInt p,
the strict inequality |P(a)|<|P'(a)|^2 supplies a root z with
|z-a|<|P'(a)|, preserves the derivative norm, and gives uniqueness within that
open ball. The actual theorem statement and its local source proof were read.
The new code invokes this exact theorem, with R=PadicInt p. It derives the
smaller closed-ball bound using the separately proved norm identity.

The second formal source is `Mathlib/NumberTheory/Padics/RingHoms.lean`,
`PadicInt.ker_toZModPow` and `PadicInt.cast_toZModPow`. These identify the
congruence balls and prove reduction compatibility. Degree valuations use
`Padic.valuation_natCast` and the p-adic norm formula. Diagonal matrix units
use `Matrix.isUnit_diagonal` and the product-ring unit criterion.

This is a formal corollary of the established Hensel mechanism, integrated with
the continuation problem. No exhaustive historical or novelty search was performed,
and no claim of historical novelty is made. The checked source application is
scalar. It supplies no noncommutative matrix Hensel theorem.
