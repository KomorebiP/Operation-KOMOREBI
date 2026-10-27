# Paper IX: singular-residue algebra attempt

Author: Komorebi P.

This is a partial research checkpoint, not Paper IX completion. The global all-residue Theorem 7.5 remains unproved in this package. Previous full-item coverage remains 23/24.

The new route works in the integral cyclic group ring. It first proves that I=(p,z-1), z^p=1, satisfies I^p <= p I and I^q <= (p^v_p(q!)). Each consecutive p-block of a falling factorial lies in I. This yields a uniform denominator estimate before any division in a p-adic field.

The attempted modules connect this to cyclic coefficients and the actual exp/log substitution. Read their compiler records individually. Probe.lean and inactive development drafts are NOT proof modules. No result in this checkpoint should be interpreted as a completed proof of the singular-ratio estimate or the all-residue theorem.

The toolchain and pinned Mathlib are external, supplied by the existing portable kit. Run check_low_memory.py for each module in dependency order: CyclotomicFiltration, PrimeBlockPolynomial, CyclicAmiceCoefficients, BinomialLogSeries. The imported pinned Mathlib cache is not rechecked from source.

No new axiom audit is asserted by this checkpoint README. Compilation and full dependency auditing are different checks.
