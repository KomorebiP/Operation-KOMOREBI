# AVOC v0.22.0 — optimal costed retries under persistent reliability

This release adds a single-operation, fault-inclusive decision model and an
executed read-only advisor. It does not change the protected retry backend.
It builds on the v0.21 attempt ledger rather than rewriting its recovery semantics.

## 1. Exact retry control

At operational state s, a new attempt has probability p(s) of resolving the
operation, a declared resolution benefit G(s), and a cost c(s) paid on every
attempt, whether resolved or not. An unresolved outcome leads to f(s).
Abandonment has incremental value zero. Resolution terminates this subproblem.
Resolving an operation is NOT a proof admission: its actual receipt still has to
pass the existing checker and monitor.

Let e(s)=p(s)G(s)-c(s). With n attempts of planning horizon remaining,

    U_0(s) = 0
    U_(n+1)(s) = max(0, e(s) + (1-p(s))*U_n(f(s)))

when retry is enabled, and zero otherwise. The executable `retryValue` computes
this recurrence. `Retry.system` independently expresses it using the inherited
Guarded.System with abandonment and retry actions. Its stage reward is the
pre-integrated expected reward pG-c; resolution is absorbing. The value theorem
proves that both definitions agree. The executable selected plan is legal, attains
this Bellman value, and dominates every legal deterministic adaptive observation
tree of the same finite horizon. It does not assert general randomized constrained
or multi-mode retry optimality.

## 2. Why a threshold requires a hypothesis

`NoRevival` says e(s)<=0 implies e(f(s))<=0. Under this condition, induction proves
U_n(s)=0 for every n whenever e(s)<=0. Nonnegative continuation values imply that
e(s)>0 makes retry profitable at every positive horizon when enabled. Thus the
implemented tie-breaking rule is exactly

    retry iff enabled(s) and p(s)*G(s) > c(s).

At equality abandonment is optimal but need not be the only optimum. This is
not a universal myopic policy. A checked improving-service counterexample starts
with p=0, G=10, c=1, then reaches p=1 after the first fault. Its one-attempt net
value is -1, but its two-attempt value is 8. It violates NoRevival.

## 3. Bayesian persistent-reliability specialization

A finite hidden operational type theta has fixed resolve rate q(theta) in [0,1].
Attempts are conditionally independent given this persistent type. The type
space models operational reliability, not the truth of a theorem. The benefit
G>=0 and nominal retry fee c are fixed during this local decision problem.
Belief b is a normalized finite rational distribution. Its predictive rate is

    p = sum_theta b(theta) q(theta).

After a positive-probability operational fault,

    b'(theta) = b(theta)(1-q(theta))/(1-p).

The executable updater is total: if a fault has zero predictive probability its
mathematical fallback is b. The CLI rejects a supplied impossible fault instead
of presenting that fallback as observed evidence.

A finite weighted-variance proof establishes E[q^2] >= E[q]^2. Consequently,

    p' = (p-E[q^2])/(1-p) <= p

when 1-p>0. The same monotonicity holds for the total fallback. Since G>=0 and c
is fixed, p'G-c <= pG-c, giving NoRevival rather than assuming it. The threshold
is therefore optimal at every positive finite horizon under these hypotheses.
This does not cover service repair, improving availability, backoff, changing
providers, multiple fault signals, variable costs/benefits, or correlated
scientific/operational latent states without an extended model.

## 4. Budget and attempt limits

The operational state retains remaining nominal credit C and remaining attempt
slots N. Retry is enabled iff c<=C and N>0. The unresolved successor uses C-c
and N-1. With enabled retry these subtractions have exact accounting identities.
A zero fee still consumes an attempt slot.

The adapter derives C=limit.credits-ledger.charged and
N=limit.attempts-ledger.reserved from the existing safe v0.21 ledger. Enabledness
is proved equivalent to its `room` predicate. The inherited `renew` gate then
checks the current ticket, unpublished phase and terminal flag. Accepted advice
preserves ledger safety, adds exactly one fresh charge/generation, retains confirmed
fees, and fences the obsolete ticket. Applying the advice through AttemptRecovery
preserves the full scientific checkpoint, not merely a Boolean status field.
The reliability belief is a separate coordinate. No fault is inferred from an
unfinished intent or missing acknowledgement by this module.

## 5. Executable computation

The evaluator follows only the unresolved branch. `evaluate` returns the net
value, chosen action and a state-visit count. Its value equals the Guarded value,
its choice equals the executable optimal selector, and visits <= horizon+1.
The count excludes exact-rational bit complexity, model evaluation, parsing,
runtime initialization, proof checking and I/O.

Under the persistent-type theorem the action alone needs only the current
predictive mean and resource guard. The delivered advisor also evaluates the
finite-horizon value to expose and test its calculation. It is not a globally
optimal metareasoning algorithm or a calibration procedure.

## 6. Exact examples

* Prior 1/2 on types q=1/10 and q=9/10, G=4, c=1: predictive rate 1/2,
  optimal incremental value 1 at every positive horizon (when enabled initially).
  After one fault, fast-type posterior is 1/10, predictive rate is 9/50, and
  one-attempt expected net value is -7/25. Abandonment is then optimal.
* q=1/2 for both types (fresh i.i.d. success probability at every attempt), G=4,
  c=1: fault does not change the prior, and three affordable attempts have value
  7/4. Equal initial marginal success probabilities therefore do not determine
  repeated-attempt value.
* Improving-service counterexample above: a universal one-step stopping rule fails.
* An actual safe paid-attempt ledger produces a fresh paid retry; with the
  updated persistent-reliability posterior the same ledger produces terminal
  abandonment with no refund and no new confirmation.

## 7. Artifact and execution boundary

The Python wrapper calls the exact Lean advisor defined here. It returns advice
and a hypothetical next ledger, never mutates a database, never issues an
operation key, and never marks a proof as admitted. The existing explicit v0.21
backend is still responsible for publication checks, fresh authorization,
source identity, and actual proof rechecking. No successful end-to-end live
retry run is claimed for this new advisor in this release.

The reference G should be the incremental utility of resolution relative to
abandonment, with remaining relevant costs treated consistently. It is declared,
not estimated by Lean. Full physical fault/recovery/planning cost optimality and
empirical LLM effectiveness remain open.
