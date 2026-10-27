# AVOC v0.40.0: observation streams to certified policy issuance

The new block removes the previous theorem's supplied binomial count-law premise.
It derives that law from a primitive conditional-outcome contract and connects
it to an explicit sample-collection process. The contract's applicability to a
real provider is still a modeling assumption.

## Primitive outcome law

For identity k, fix a finite latent Boolean source of length N_k and a rational
probability p_k in [0,1]. On a finite rational probability space, the contract
requires that, for every specified pattern on a set of source positions, an
unseen position has success mass p_k times the mass of that pattern. This is a
multiplication identity; impossible histories need no conditional division.
It is a within-source independence contract. Cross-identity independence is not
required by the final formal theorem.

`ObservationStream.conditional_pattern_mass` proves by finite-set induction
that every complete vector with s successes has mass p^s(1-p)^(N-s).
`conditional_implies_product` extracts that product law. Counting the vectors
with exactly s successes produces choose(N,s), proving the binomial count law.
An explicit normalized Bernoulli product law is constructed as well.

Restriction to an initial n positions preserves the conditional contract.
Therefore several scheduled sample sizes can share one source without assuming
independent checkpoint counts. Equal success marginals alone are insufficient:
a proved correlated-pair example has both marginals 1/2 but no one-success
outcomes, unlike the binomial model.

## Recursive observation process

`ObservationReveal` stores a report list and a remaining source for each identity.
A report appends the next Boolean and consumes one source position. A checked
rejection appends false. A fault leaves the state unchanged. Every transition
preserves source = reports ++ remaining, so every stored report list is exactly
its source prefix. This is proved for arbitrary finite traces.

The trace can depend on the entire outcome space; the pathwise invariant does
not need independence of scheduling. The model does require that reporting
cannot skip a latent rejection. It does not prove that a physical timeout obeys
this latent accepted-report interpretation.

Fresh report/fault operations are related to the existing `CalibrationLog`
recorder by one-step theorems. Those require a fresh operation identifier and,
for a report, agreement with the next latent Boolean. Inherited recorder rules
handle identical replay and conflicting reuse before a new reveal step. A
universal host-log-to-machine refinement is not claimed.

## Fixed checkpoints and fail-closed issuance

Each checkpoint j fixes identity key_j, n_j <= N_key_j, positive grid size m_j,
and nonnegative error allocation alpha_j before observing its data. A checkpoint
is available when its identity has at least n_j checked reports; its count uses
only the first n_j. Later outcomes cannot alter that checkpoint's count.

The inherited exact rational cell-envelope interval has miss probability at
most alpha_j. Summing those fixed-prefix bad events bounds their union by
sum_j alpha_j. An available incorrect interval is a subset of that union,
regardless of the process's probability of completing each checkpoint.

Warm and cold checkpoint selectors can depend on the outcome, but must select
their respective target probability strata. `observedPlan` returns no plan if
either selected checkpoint is unavailable. When both are available, it installs
their learned bands in the existing quote model.

`ObservationPolicy.shared_stream_episode_coverage` and
`shared_stream_issued_failure_le` combine the entire chain. Their premises contain
primitive conditional source laws, the explicit reveal process, fixed schedules,
and valid deterministic setup/gross bounds. They do not assume binomial count
laws or a separate observed-count correspondence. The final conclusion is

    P(there is an issued plan without the stated episode certificate)
      <= sum_j alpha_j.

The certificate supplies the stated warm/cold probabilities, deterministic
setup/gross values, Q/value bounds, and expected whole-policy regret guarantee.
Its quote model remains fixed within the episode and its comparator uses the
same conservative upper-setup reservation policy as the inherited theorem.
No claim is made that data collection completes with high probability.

## Why conditioning on completion fails

Two fair latent outcomes suffice: always report the first, and report the second
only after the first succeeds. The gate does not inspect the second outcome.
Completion probability is 1/2. Conditional on completion, success counts have
probabilities (0,1/2,1/2), rather than the binomial (1/4,1/2,1/4).
`ObservationCensoring` proves this obstruction in a finite exact model.

The same issue can violate AVOC interval coverage, not just the count law. The
independent 1,024-path check takes ten fair outcomes, grid ten, alpha=1/10, and
permits the tenth report only after nine successes. Conditional miscoverage is
1/2, while unconditional bad issuance has probability 1/1024. This larger
interval-specific example is exact executable evidence, not an additional
kernel-checked theorem.

In general the conditional bound divides by completion probability. The formal
safe unconditional bound makes no division. It can remain useful even when
completion is rare, but says nothing about completion rate or productivity.

## Attempt probabilities and censoring

A separate primitive attempt law uses potential success probability p, retention
a for successes, and retention b for rejections. Its reported success probability
is p*a/(p*a+(1-p)*b), when retention has positive mass. Equal positive retention
preserves p; for interior p it is also necessary. These statements and a
success-only-retention counterexample are kernel checked.

This one-attempt theorem is distinct from proving a real multi-attempt system
has the accepted-source contract. Outcome-dependent consuming censoring can
break even unconditional calibration for attempted success probability. The
executable oracle includes an exact example and a log fixture illustrating why
a parser cannot authenticate that omitted rejections never occurred.

## Inherited foundation

The cumulative core retains exact rational calibration, adaptive finite-schedule
coverage, robust quote planning, competitor-only dominance, semantic/cost
artifact backends, guarded Bellman policies, and durable selected-only execution
rules. All 186 inherited non-audit mathematical modules are unchanged.
The v0.39 explanation is preserved under provenance/v0.39_release_top.
