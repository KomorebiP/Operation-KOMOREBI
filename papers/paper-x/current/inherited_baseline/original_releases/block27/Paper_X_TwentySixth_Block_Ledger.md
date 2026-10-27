# Paper X — Twenty-sixth block ledger

**Source accounting: 17 checked / 3 partial.** No source claim is promoted in this block. The remaining partial claims are 9.1, 9.2, and 11.1. Claims 8.2 and 11.2 retain their checked conditional scopes and their unproved arithmetic application premises.

| Obligation advanced | Formal result | Exact scope |
|---|---|---|
| Actual absolute-Galois quotient | `AbsoluteGaloisRestriction.restriction_surjective`, `restriction_continuous` | Restriction through an actual embedding into $\overline{\mathbb Q}$; normality for surjectivity and finite degree for continuity. |
| Actual representation descent | `SurjectiveRepresentationPullback.nonempty_equiv_iff`, `isIrreducible_iff`, `subrepresentationOrderIso` | Surjective acting homomorphism; actual equivariant isomorphisms and invariant subspaces. No characteristic-zero or finite-group requirement for this transfer. |
| Independence from the global lift | `CyclotomicAbsoluteSamples.pullback_on_lift` | Full operator equality for representations factoring through the fixed cyclotomic field. |
| Continuity and common separator | `CyclotomicAbsoluteSeparation.pullback_action_continuous`, `finite_absolute_system_separator` | Actual $G_{\mathbb Q}$ systems with a common cyclotomic factor, arbitrary finite exclusions, and coefficient-specific good-place conditions. |
| Actual valuation inertia triviality | `CyclotomicInertiaBridge.restriction_eq_one_of_coprime_inertia`, `pullback_trivial_on_inertia` | Valuation inertia of $\overline{\mathbb Q}$, residue characteristic $p$, and $p\nmid n$. |
| Recognition of arithmetic valuation Frobenius | `CyclotomicInertiaBridge.restriction_eq_primePower_of_coprime_residue`, `pullback_on_arithmeticFrobenius` | Supplied decomposition element with $p$-power residue action; equality of entire operators. |
| Failure without surjectivity | `SurjectivePullbackBoundary.representations_not_equivalent`, `collapsed_pullbacks_equivalent` | Inequivalent rational irreducible sign/trivial representations become equivalent after constant $C_2\to C_2$ restriction. |
| Failure of full coverage from one quotient | `SurjectivePullbackBoundary.projected_samples_coverage`, `quotient_samples_coverage_fails` | Samples $(g,1)$ cover the first $C_2$ quotient but fail coverage in $C_2\times C_2$. |
| Necessity of the unit hypothesis | `CyclotomicInertiaBridge.twoAdic_distinct_roots_same_residue`, `twoAdic_order_not_unit` | Distinct square roots $1,-1\in\mathbb Z_2$ have equal residues and root order $2$ is not a unit. |
| Absolute arithmetic Frobenius existence | `AbsoluteIntegralFrobenius.exists_frobenius_at`, `exists_frobenius` | Constructs actual prime ideals above every rational prime and stabilizer elements with $p$-power residue action. No supplied Frobenius or residue-surjectivity premise. |
| Actual ideal inertia and Frobenius restriction | `CyclotomicIntegralFrobenius.restriction_eq_one_of_inertia`, `restriction_eq_primePower_of_residue`, `pullback_trivial_on_inertia` | Actual integral-closure ideal model, a prime above $(p)$, and $p\nmid n$. |
| Arithmetic separator assembly | `CyclotomicAbsoluteArithmeticSeparation.finite_arithmetic_system_separator` | Constructs distinct permitted rational primes, actual absolute prime ideals and Frobenius elements, ideal inertia triviality for every member, and a common invertible trace matrix for the factored systems. |

The ideal and valuation constructions use their respective actual local objects. No identification between the models is asserted.

The fixed root order $n$ is not asserted to be the field's minimal conductor. Arithmetic Frobenius means $p$-th powering on residues. Ordinary trace comparison retains each coefficient member's good-place condition. The arbitrary `liftSample` choices are not asserted to be local decomposition Frobenius elements; the final arithmetic theorem constructs its own actual witnesses. No full absolute-group density follows from coverage of one quotient.

General arithmetic prime coverage for arbitrary finite Galois quotients and actual Hodge–Tate/Weil–Deligne attachment remain unproved here.

**Release verification passed.** All 170 production modules passed the clean build. The 1,989 named declarations passed the transitive axiom audit using only Classical.choice, Quot.sound and propext. The block adds 63 theorem/lemma declarations and 22 other named declarations; the cumulative theorem/lemma count is 1,396. Eleven positive controls passed, and 25 false claims plus the placeholder were rejected as intended. All 161 predecessor source and rebuilt proof-object hashes match Block 25. Fresh archive replay reproduced all nine new proof objects and the retained Block 22 exact regression. Independent exact-source review of all nine modules and manuscript review passed.

The target contract is `BLOCK26_TARGET_CONTRACT.md`. Repaired development errors and proved mathematical boundaries are distinguished in `DEVELOPMENT_BLOCK26.md`.
