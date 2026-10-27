# Literature and API boundary

No historical novelty claim. The mechanism is the Hensel/implicit-function argument for a matrix power map, using the checked norm differential, plus the standard inverse-limit description of p-adic integers.

The pinned local Mathlib `Mathlib/NumberTheory/Padics/RingHoms.lean` was inspected. The accepted proof uses `PadicInt.isCauSeq_padicNorm_of_pow_dvd_sub`, `PadicInt.toZModPow_ofIntSeq_of_pow_dvd_sub`, `PadicInt.ext_of_toZModPow`, and `PadicInt.cast_toZModPow`. The coefficient target is Mathlib's actual PadicInt, not a newly named surrogate limit.

Public documentation checked September 12, 2026:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/Padics/RingHoms.html

The cofiltered finite-limit documentation was also inspected as an alternative route but is not imported into the accepted proof:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/CofilteredSystem.html

The compiled result is against the pinned local revision, not against a presumed current documentation version. No automorphy or global arithmetic theorem is imported or inferred by this block.
