# AVOC v0.15.0 — exact proof boundary

## Proved in the new block

- Nonnegative finite joint world/observation L1, predictive contraction, and a prior-plus-channel joint-error bound.
- Total Bayes' scaled identity, including zero predictive mass.
- Probability-weighted posterior L1 at most twice the joint-law L1 error, without an evidence floor.
- Expected continuation comparison for bounded belief-Lipschitz observation-specific functions.
- Exact-metadata product-state adapter, with explicit matching state-dependent feasible actions and codec error.
- A uniform belief encoder bound implies the required expected codec bound when the raw updater is Bayes.
- Approximate value-table Bellman residuals imply reference constrained value and Q errors.
- Additional Q computation/compression and maximization errors give a complete deployed-policy regret bound.
- Specialization to the existing certificate-gated research controller preserves its dependency, certified-truth, pending-queue and budget invariant.
- Finite maxima of bounded linear belief rows have certified absolute bounds and Lipschitz constants.
- Exact rare-event and imperfect-model/backup examples, including refutations of pointwise relabeling, zero residual, and zero policy regret.

## Precise assumptions

- Finite hidden world and finite observation alphabet, rational probabilities, and normalized nonnegative channels.
- Finite nonempty state-dependent action sets. The full state or belief space is not required to be finite.
- Same observation labels permit pairing branches. Different observation alphabets require a separately proved coupling adapter.
- The compared raw/model feasible sets agree. Exact metadata agrees on corresponding branches.
- Prior, channel-row, codec and reward bounds hold on the declared modeled domain. They are not estimated by the theorem.
- The model successor's belief is the declared total Bayesian update. A raw/encoded successor must satisfy the stated average codec discrepancy.
- Continuation tables are bounded and belief-Lipschitz inside fixed metadata; model-backup residuals are bounded and the zero-horizon table is zero.
- Deployed choices are actually admissible, with the stated approximate-maximization guarantee.
- Research invariants still depend on the original protocol's actual checker-soundness/local-proof obligation.

## Not established

- No uniform posterior bound for every rare observation. The new result is weighted in expectation; pointwise instability remains.
- No inference that small belief L1 means small L1/TV between atomic laws on posterior states.
- No unconditional continuity of arbitrary state-dependent rewards, experiments, guard masks or optimal Q functions.
- No real LLM calibration, reward identification, likelihood correctness, context-token guarantee, or empirical effectiveness claim.
- No cheap universal procedure for constructing the approximate value table, proving all residual/regularity bounds, or optimizing context.
- No metareasoning-cost accounting beyond explicitly modeled fees. The existence of finite maxima is not an efficiency claim.
- No new latent worlds, robust model misspecification, dynamic AND/OR tasks, concurrency, or infinite horizon.
- No real candidate-to-receipt authentication. v0.14's pending-ID and modeled-receipt boundary is unchanged.
- No probabilistic replacement for the sound proof gate. Fallible external evidence and formal proof admission remain distinct.
- No universal constant-optimality or tightness claim for the new inequalities.
- No Shannon rate-distortion theorem and no claimed historical novelty.

## Verification scope

See `results/VERIFICATION_v0.15.0.md` and `AUDIT.json` for final current-source results. The local project is rebuilt against the pinned external dependency cache. This is not a fresh source rebuild of mathlib, an independent Lean kernel, or formal extraction of the Python regression. Counts include helpers and examples.

The 68 inherited non-audit modules are byte-identical to v0.14. The previous nine audit-only lemmas are retained separately in their original audit package and are not counted as new release results here.
