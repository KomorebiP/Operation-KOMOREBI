# Sequential lower discrepancy certificate

Self-review verdict: proved as written for Proposition 68, conditional on the exact simultaneous residual event stated in Proposition 66. This record does not claim a proof of Proposition 66 or its concentration probability.

## Target and inputs

The authoritative target is Proposition 68 and the immediately preceding observation-law inequality in unchanged `source/FOUNDATIONS_1.0.0.md`, Sections 74 to 76. `P68_RESULT.json` records the input and output hashes. The proof has no finite-alphabet or finite-support restriction. It uses actual probability measures on an arbitrary measurable observation space, with measurable tests taking values in `[0,1]`.

The time index in the source file starts at zero, so `Finset.range t` stores the manuscript's first through t-th observations. Every true and proposed law is evaluated on the same supplied actual history and action. There is no shared latent state or common model cone assumption.

## Actual total variation, rather than a numerical surrogate

`lawTV P Q` is one half the mass of the Hahn–Jordan total variation of the actual signed measure `P.toSignedMeasure - Q.toSignedMeasure`. Mathlib's `SignedMeasure.totalVariation_eq_variation` identifies this with the vector variation defined by supremum over finite measurable partitions. Thus this is the standard probability convention, not an arbitrary numerical upper envelope.

`lawTV_nonneg`, `lawTV_self` and `lawTV_le_one` verify its normalization. `lawTV_dirac_eq_one` proves that distinct point masses have unit distance when singleton sets are measurable.

## Dependency and obligation checks

1. Bounded measurable tests are integrable under each probability law. `bounded_test_integrable` derives this from the `[0,1]` range.
2. The ordinary integral difference is the signed-measure integral of the centered test `φ - 1/2`. Constants cancel because both measures have total mass one. The proof explicitly transfers between ordinary Bochner integrals and vector-measure integrals; it does not postulate this identity.
3. The centered test has absolute value at most one half. Mathlib's actual variation bound on the vector-measure integral therefore proves `bounded_test_integral_le_tv`. This establishes the manuscript's load-bearing law-error comparison on general measurable spaces.
4. `residual_excess_le_abs_drift` derives the positive-part bound from the exact event `|R-D| ≤ boundary` using the triangle inequality and nonnegativity of absolute value.
5. `abs_drift_le_tv_sum` bounds the actual finite sum of integral differences by the actual finite sum of law TV distances.
6. `sequential_lower_certificate` combines these facts and divides by the positive sample count. No numerical law-error domination appears among its assumptions.
7. `simultaneous_sequential_lower_certificate` applies the theorem at every positive time and every rule on one supplied simultaneous event. That event is precisely the mathematical antecedent supplied by Proposition 66.

All seven obligations passed self-review and pinned Lean compilation with warnings treated as errors. The only external theorem leaves are kernel-checked Mathlib integration and variation APIs. No new axiom, approximation or unproved law-distance inequality was introduced.

## Controls and limitations

`zero_test_misses_disjoint_laws` gives a positive check of the manuscript's warning: the constant-zero test has residual zero even when two actual observation laws have TV distance one. Failure to cross is not an upper-error certificate.

Two negative controls reject with mathematical `False`. `SequentialLowerUnboundedTest` drops the `[0,1]` bound and uses a test with value two on two distinct point laws. `SequentialLowerFalseUpper` incorrectly infers an upper TV bound from a zero residual. Neither control fails because of an unknown symbol or missing import.

The initial source diagnostics concerned local-instance lint style, function-subtraction elaboration in integrability statements, an explicit local signed-measure definition, parentheses in finite-sum notation and a tactic-sequencing lint. These were implementation issues. The target and mathematical assumptions were not weakened to address them. Development snapshots and logs are retained here.

The coordinator must still integrate the module/import inventory, run the cumulative axiom audit and kernel replay, and reconcile the monograph status. Those execution stages are not claimed by this scoped record. The probability of the simultaneous event, predictable-test conditions needed to obtain that event and action coverage remain obligations of their own propositions.
