# Arithmetic section editorial record

Proofread and polished: `manuscript/sections/20_arithmetic.tex`.

Before SHA-256: `f1e7a44edc0e9e4d6a247a847939fd583b7628477c99ba7f06fefe9a3d6b35f8`

After SHA-256: `664a905288558d4f8fcd6022f4e16971045946fc33935272ce8832fb575c322e`

Scope: the full arithmetic section, including all existing proofs and the six source-grounded restorations authorized during this proofreading turn. No Lean source was edited.

## Prose changes

- Reworked the introduction to distinguish the congruential four-packet family from the classical Euler edge construction directly.
- Replaced repeated “actual”, “literal”, and “genuine” qualifiers with concrete descriptions of series, coefficients, inverses, and degree shifts. Existing Lean declaration names remain verbatim.
- Removed progress-report language from the section and theorem titles while retaining theorem labels.
- Smoothed transitions among the recurrence, weighted estimates, flatness, Newton expansion, exact valuation argument, and continuous extension.
- Replaced defensive comparisons with positive accounts of what each proof establishes. Preserved the finite-prefix versus universal-envelope distinction and every limitation on periods, row tails, and packet analyticity.
- Clarified the role of the Bernoulli theorem in the sharp-tower proof: it supplies the valuation after the coefficient identity has been derived.
- Replaced awkward expressions such as “all powers of it”, “zero-safe formulation”, “four original gains”, and “prescribed samples” with ordinary mathematical prose.
- Retained all existing proof steps, hypotheses, conclusions, citations, formula blocks, and zero/empty-tail cases.

## Mathematical scope clarifications

1. Corrected the overbroad sentence “All divisibility statements below are in Z_p.” The revised convention says that p-adic congruences use Z_p, while statements over other coefficient rings identify their ring explicitly. This is required by the existing abstract-ring period lemma and the explicitly integer odd-length reconstruction. The only added inline math token in the prose-only pass was `$p$` in this sentence. No theorem domain changed.
2. Replaced the ambiguous closure phrase “inversion of unit series” by “inversion of series with constant coefficient one” in the weighted-ring argument. This matches the displayed hypothesis V(0)=1 used there. No displayed formula or theorem hypothesis was altered.

## Restored mathematical content

These are additions recovered from the original manuscript and preserved formal sources, not new Lean results. Their exact source paths, archived-member hashes, declaration names, hypotheses, and formal status are recorded in `ARITHMETIC_ADDITIONS.json`.

1. `prop:arith-denominator`: the explicit product of triangular pivots clears every normalized coefficient denominator; includes an induction proof and the empty-product endpoint.
2. `ex:arith-bernoulli`: the boundary C_(2,1)(n)=(2−2^(2n))B_(2n), with B_1=−1/2, proved by 2B(z)−B(2z)=z/sinh(z). This is explicitly a classical derivation with no matched dedicated Lean bridge.
3. `prop:arith-lucas-window`: Lucas row reduction, p-adic integrality below the prime, and address-independent reduction to the unique triangular inverse. No divisor-branch hypothesis is added.
4. `ex:arith-normalization-loss`: the exact (p,m,j)=(3,2,3) counterexample, showing the normalized factorial loss is necessary and sharp while the unnormalized bound holds.
5. `eq:arith-signed-zigzag`: the generating-function definition of Z_r and gamma_m=(−1)^m Z_(2m+1), with its derivative and sign-substitution explanation. No alternating-permutation interpretation is claimed.
6. `cor:arith-window-period`: common sufficient period (p−1)/m from row one, with m dividing p−1, j<p, and arbitrary multiples. The row restriction and the absence of a least-period claim are explicit.

## Validation

- All 77 original displayed equation blocks remain byte-for-byte present in their original order. The restored topics add 13 displayed blocks.
- All 362 original inline math fragments remain present in order.
- All 66 original Lean citations remain present in order; 19 source citations were added.
- All original labels and references remain present in order. Labels are unique and LaTeX begin/end environments are balanced in this section.
- Each of the six raw Lean files used for the restorations was compared byte for byte with its member in the preserved baseline archive. All match.
- Read the raw theorem statements and proofs for the restored denominator, Lucas-window, common-period, normalization, and zigzag claims. The source hypotheses and displayed conclusions agree.
- Re-read all changed prose and all restored derivations. No further local inconsistency found.
- Full manuscript compilation and PDF visual inspection are delegated to the parent integration pass. Lean was not rerun because no Lean source changed.

## Remaining limitation

The Bernoulli boundary example has a complete classical derivation in the manuscript, but no dedicated packet-to-Bernoulli Lean bridge was matched in the preserved sources. This limit is stated beside the example and in the source map. This section review does not assert that the larger research extensions are complete.
