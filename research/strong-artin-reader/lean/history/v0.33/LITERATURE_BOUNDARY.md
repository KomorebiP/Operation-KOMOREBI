# Literature and overlap boundary

Checked official Mathlib documentation on 2026-09-12:
- Mathlib.Algebra.Ring.GeomSum: geom_sum_mul_neg gives S_d(T)(1-T)=1-T^d, valid in noncommutative rings.
- Mathlib.Algebra.CharP.Lemmas: characteristic-prime-power polynomial identities.

Online documentation is a source orientation, not the compilation pin. The exact compiler pin remains Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 and the byte-preserved v0.32 operator proofs.

No external unproved arithmetic theorem is imported to prove the new statements. The common-correction criterion is proved directly in Lean. No historical novelty search was completed and no novelty claim is made.
