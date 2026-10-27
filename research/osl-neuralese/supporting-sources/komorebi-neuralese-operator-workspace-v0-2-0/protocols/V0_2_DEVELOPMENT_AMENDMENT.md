# V0.2 development amendment: composition anti-collapse boundary

**Written after the first development-only smoke run and before any test-split
evaluation:** 2026-09-02 UTC

The first development sweep showed that every arm with composition weight at or
above 0.03 converged toward a near-zero operator encoder. Terminal loss remained
near chance, the composition and shuffled-composition arms were indistinguishable,
and the learned metric could not rescue the zero-code stationary point. This is
a negative result for the original unbounded symmetric consistency loss.

The composition target is now treated as a stop-gradient moving target, and the
relative squared residual is passed through `log1p`. The first change removes the
direct incentive to shrink the independently encoded target. The second bounds
the influence of badly mismatched products early in optimization so that closure
pressure cannot overwhelm the terminal objective. No state labels, canonical
operator identities, coordinate permutations, D4 relation names, development
outcomes, or test-partition examples enter the target.

The original smoke result remains immutable under
`results/v0.2.0/smoke_noninferential`. A second development protocol will use a
new output directory and a new code digest. Primary weights and gates will be
locked only after that second development run, and before the test partition is
opened.
