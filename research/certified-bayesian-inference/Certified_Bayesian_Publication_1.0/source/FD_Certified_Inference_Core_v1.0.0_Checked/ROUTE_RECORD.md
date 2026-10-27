# Release-completion route record

Base: v13, SHA256 8f6bde58df0b6b18388f60adff4a22e5fed0a69d0a8f66321922452950cf3ba7.
Target: finish the scoped one-update research release by implementing checked
incremental bookkeeping, measuring full costs, assessing rounded selective updates,
reproducing the active build, and completing a bounded literature comparison.

1. Cache all output residuals and scores; replace only the selected entry.
   Implemented and proved. The new total is old total minus old selected energy
   plus new selected energy. The actual cached trajectory equals v13's gains.
2. Reuse cached exact score to avoid repeated full rounded verification.
   Implemented and proved. Stop at epsilon^2/4, then invoke the rounded evaluator
   with its sufficient fallback. Actual program termination and output are checked.
3. Independently round the cached residual and gain after each step.
   Refuted by a scalar exact counterexample. Stored score zero can coexist with true
   score two. Final verification still rejects. Reopening requires propagated cache
   error enclosures and a selection/forcing-error analysis.
4. Infer practical superiority from reduced matrix work.
   Rejected as an inference. Seven bounded benchmark cases show cheaper iteration
   versus recomputation but little total benefit, and no overall advantage over an
   efficient full Richardson baseline. Proof checking is measured separately.
5. Assert novelty from the combination's vocabulary.
   Rejected. Primary sources show established block greedy selection, caching,
   pathwise Gaussian/Wasserstein analysis and formally checked interval arithmetic.
   The artifact's integrated theorem is delivered without a priority claim.

The first-release scope is frozen in RELEASE_SCOPE.md. Large-scale efficiency,
rounded selective iteration, changing packet geometry, sequential filtering and
sampling remain separately named extensions rather than unannounced release gates.
