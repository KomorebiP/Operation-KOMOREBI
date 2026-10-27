# AVOC v0.26.0 — failures, repairs, and excluded evidence

No mathematical or implementation failure is hidden by counting a timeout or stale record as success.

1. **Unsupported session launch.** An initial container call requested an interactive session unsupported in this environment. It failed before the intended command ran; subsequent work used normal bounded calls.
2. **API probes.** Guessed finite-list lemma names were absent in the pinned runtime. A small scratch API probe failed and was retained as `development/API_PROBE.txt`; it is not part of the positive library. Proofs were rewritten with the actual available primitives.
3. **Induction generalization.** The first recursive-coverage script did not generalize its candidate expression sufficiently. Explicit induction generalization repaired the statement's proof, not its hypotheses.
4. **Branch and arithmetic simplification.** Uniqueness proofs needed the unfolded signature-match guard; probe accounting required normalization of zero-plus terms; arithmetic used the available multiplication lemma names. Warnings-as-errors exposed unused arguments and prompted explicit omission/removal.
5. **Dependent budget expressions.** Reducing the generated layer through local let-bindings did not initially expose the required charge equation. Explicit unfolding supplied the equalities, with no weakening of the credit invariant.
6. **Intermediate build state.** During development, a dependent draft could run against the last compiled parent after a parent draft failed. Such a result was not used as final evidence. Final records verify current source and direct-import output hashes for every local target, and descendants were recompiled after repaired parents.
7. **Tariff correction before the benchmark.** The per-node tariff was increased from nine to ten to include both size traversals alongside eight semantic traversals. All reported experiments and final proofs use ten. This remains a declared incomplete structural cost model, not an exact machine instruction model.
8. **CLI status handling.** A legitimate funded-search/unfunded-query result is `query_unfunded`, not a generic execution failure. The entrypoint's accepted status list was corrected before final wrapper and oracle tests.
9. **Negative-suite interruption.** A long batch was terminated by an outer execution limit after its first completed files. No unfinished record counted as rejection. After confirming no prior child remained, the rest were rerun in bounded groups and all 67 final records were checked individually for substantive errors and no timeout/setup failure.
10. **Final collection.** The final collector validates exact theorem names, source/import/output/log hashes, immutable inherited modules, current test pins, and negative diagnostics. Successful old version records are not substituted for this run.

All final local proof modules, audit, negative tests, oracle comparisons, and CLI cases passed. The external dependency cache and physical runtime remain trusted. Older live filesystem/recovery suites were not rerun in this block.
