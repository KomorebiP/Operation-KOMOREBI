# AVOC v0.39.0: finite-sample quote calibration

This block connects exact logged counts to a rational confidence procedure and
then to AVOC's existing fixed-episode Bellman and policy-regret guarantees.
The statistical model is explicit. A parsed log does not prove that model true.

## Exact finite-sample interval

Fix a sample size n, grid size m>0, and error allowance alpha. For count k and
rational success probability p, write

    b(n,k,p) = choose(n,k) p^k (1-p)^(n-k).

Lean proves these count masses are nonnegative for 0<=p<=1 and sum to one.
For every cell [i/m,(i+1)/m], calculate the exact rational envelope

    E(n,k,i) = choose(n,k) ((i+1)/m)^k (1-i/m)^(n-k).

Retain cell i when E(n,k,i)>alpha/(n+1). Return the hull of the retained cells,
or [0,1] if none remain. The grid covers every rational parameter in [0,1];
the parameter need not be a grid point. The envelope bounds b throughout its
cell because both nonnegative power factors increase to their chosen bounds.

If the returned interval excludes p, the cell containing p was not retained.
Therefore b(n,k,p)<=alpha/(n+1). There are n+1 possible counts, so summing their
excluded masses proves

    P_p(p outside the returned interval) <= alpha.

This is `FiniteCalibration.missMass_le`. The theorem derives the coverage
bound from the procedure, not from a supplied confidence certificate. The
formal probability domain is rational, as in the inherited AVOC model.
The method is conservative; no shortest-interval or optimal-width claim is made.

Ten successes in ten trials, with ten grid cells and alpha=1/10, give [3/5,1].
Ten failures give [0,2/5]. Both are kernel-checked examples. At n=1,p=1/2,
the singleton empirical estimate misses with probability one; this is also
proved, rather than merely warned about.

## Fixed schedules and adaptive selection

A finite schedule fixes each sample count, grid, operation stratum, and error
allowance before the outcomes used for calibration. The Lean model is a finite
rational probability space with each scheduled count having the stated binomial
marginal distribution. Checkpoints may be arbitrarily dependent.

A finite union bound proves that all scheduled intervals are simultaneously
valid with probability at least 1-sum(alpha_j). Any selection among those
checkpoints, including a selection depending on all observed data, inherits
that bound. All selected warm and cold checkpoints belong to the same budgeted
schedule. No extra independence premise or hidden second error allocation is
used. This is a finite-schedule result, not unrestricted optional stopping.

`CalibrationSchedule` proves the count-law bridge, simultaneous coverage,
adaptive selection, and transfer to a pointwise proved conclusion. Its fair
binary counterexample shows why replacing the scheduled sum by one individual
error allowance is false.

## Composition with the controller

`CalibratedPolicy.learned_episode_coverage` constructs the actual learned
probability-band objects and proves the following integrated statement.
Except on data outcomes of total probability at most sum(alpha_j), the fresh
quote model has a compatible realization with the specified warm/cold true
probabilities, setup costs, and gross values, and it satisfies the full inherited
Q/value bounds and expected whole-policy regret theorem.

The deterministic setup/gross memberships remain supplied assumptions. The
selected bands are fixed for the entire subsequent policy episode. The
controller may adapt its actions to operational observations within that fixed
model, but this theorem does not update its probability bands mid-episode.
The regret benchmark uses the inherited conservative upper-setup reservation
guard. It is not a comparison with a larger exact-cost feasible action set.

`CalibrationBridge` also corrects an unnecessarily restrictive dominance
condition. The chosen action is compared with distinct feasible competitors.
Its own true Q is equal to itself, so comparing its lower endpoint with its own
upper endpoint was unnecessary and forced zero selected-action radius. Both
the corrected proposition and executable checker are proved sound.

## Logs, identity, and refresh

`CalibrationLog` defines exact identity strata, binary checked outcomes,
idempotent identical replay, and rejection of conflicting operation-id reuse.
Faults and unfinished intents create no binary observations. Events from another
identity do not alter a stratum's sample list. An unresolved intent blocks quote
refresh. These are pure formal rules; the Python adapter is tested against them,
not universally derived from them.

Probability replacement preserves source, workload, authority identity, setup,
and gross bands. It changes the exact quote evidence. The formal bridge proves
that changed bands obstruct acknowledgement of an authentic old intent. New
bands must therefore be authorized for a fresh episode. The adapter exports a
new plan rather than modifying a durable active checkpoint.

## Executable example

The included synthetic example fixes grid size 1000, n=500, and alpha=1/100,
then supplies 400 successes. The actual Lean calibration evaluator returns

    [361/500, 433/500].

The actual Lean planning evaluator changes the inherited uncertain example's
robust choice from cold generation to warm inspection. The corrected dominance
checker can certify the selected warm action despite a positive Q radius.
This demonstrates the implementation under supplied synthetic data. It is not
an empirical estimate of any deployed provider's success probability.

The cumulative v0.38 source remains included. Its exact theory and documentation
are preserved under `provenance/v0.38_release_top`.
