# AVOC v0.23.0 — protected, cost-accounted component improvement

## 1. What changed

The predecessor supplies research control, proofs, recovery, paid retries and an
optimal retry advisor for a declared reliability model. It does not supply an
update gate that allows the research machinery itself to be replaced. This block
formalizes that gate and executes one genuine algorithm substitution from an
immutable compiled catalogue.

There are three separate claims:

1. A candidate preserves the component's semantic contract.
2. Its declared utility improves under one fixed evaluation objective.
3. The entire improvement campaign, including rejected trials, has worthwhile net
   return. The first two do not imply the third.

## 2. Protected authority

Fix a type V of version identities. The authority supplies:

- a contract `Contract : V -> Prop`;
- an executable check and a proof `check v = true -> Contract v`;
- one utility `J : V -> Int`, with valid lower and upper bounds L,U;
- nominal evaluation and switching charges;
- a funding limit B and positive promotion margin mu;
- fixed core and objective identifiers.

The soundness obligations are explicit. Arbitrary JSON values are not evidence of
these obligations. In the concrete catalogue, the contract checker is proved and
the utility bounds are exact computational values, not estimated confidence bounds.
Integer utility is a declared common accounting scale, not automatically money,
wall time or scientific value.

## 3. Candidate binding and promotion

A request contains its candidate, incumbent identity, incumbent revision, protected
core ID and objective ID. It cannot supply its own fee, utility score or approval.
A funded trial pays its evaluation charge even if stale, unprofitable or invalid.
Promotion additionally requires:

    request.parent = state.active
    request.revision = state.revision
    request.core = authority.core
    request.objective = authority.objective
    check(candidate) = true
    U(active) + switching_charge + mu <= L(candidate)

and enough budget for the switch. The active version and revision change only on
promotion. An unfunded request leaves state unchanged. A funded rejected request
leaves the active version unchanged but retains its charge.

Bound soundness immediately gives:

    J(candidate) >= J(active) + switching_charge + mu.

Because mu>0, an accepted upgrade has strictly higher declared utility. This is
relative to the fixed objective; not a theorem that all workloads improve.

## 4. Campaign invariant

Write E for all funded evaluation charges, S for all switch charges, r for the
revision/promotion count, and M for accumulated minimum gains. The invariant is:

    Contract(active)
    E + S <= B
    J(initial) + S + M <= J(active)
    M = r * mu
    r <= funded_trial_count.

`step_safe`, `run_safe` and `adaptive_campaign_safe` prove this invariant for each
step, finite sequence, and state-dependent adaptive proposer. The proposer sees
the current accepted version and ledger and may be learned or adversarial. These
are preservation results, not a guarantee that the proposer finds an upgrade.

The exact trace accounting theorems equate E and S to their respective charged
transition sums. Failed funded trials cannot disappear from the accounting.

Define net endpoint gain:

    Net = J(active) - J(initial) - E - S.

Then:

    Net >= M - E.

If M>E the modeled campaign is profitable. Otherwise the bound does not guarantee
profit. A promoted version can be better while the campaign is net-negative.
This objective compares the final deployment score with the initial one after all
recorded search/switch tariffs; it is not the cumulative production reward over
time spent operating each intermediate version.

## 5. The actual component specialization

The catalogue contains `dynamic`, `threshold`, and `always_retry`.

`dynamic` executes the existing `Retry.evaluate` then projects its Boolean action.
`threshold` handles zero horizon with false, and at positive horizon returns:

    enabled(s) && (0 < p(s)*G(s)-c(s)).

Its contract is universal over all declared retry models satisfying NoRevival:

    immediate(s)<=0 -> immediate(afterFault(s))<=0.

The inherited threshold theorem proves equality with the dynamic-program action.
The new adapter proves the replacement contract and that its counted state visits
are no larger than the old evaluator's on any input. The latter comparison is a
state-visit counter, not complete physical execution cost.

`always_retry` is cheap but violates the zero-horizon contract. Its failed contract
is proved, and the promotion check rejects it. Evaluation success or a favorable
benchmark cannot override the contract gate.

This is an ACTION-ONLY interface. The original retry report also returns an exact
lookahead value; the threshold does not provide that value and is not presented as
a compatible replacement for the full report.

## 6. Fixed-workload demonstration

The exact protected workload has horizons [0,1,2,4,8,16,32] on a constant, enabled
retry model with resolution probability 1/2, benefit 4 and fee 1.
The baseline visits n+1 states; the threshold visits one. Thus total visits are:

    dynamic: 70
    threshold: 7.

Utility is negative visits. Nominal evaluation tariff is 3, switching tariff 1,
and required margin 8. These tariffs are illustrative, not calibrated cost data.

First reject `always_retry`, paying 3. Then promote `threshold`, paying another 3
and switching tariff 1. The final utility improves by 63, and net endpoint gain is:

    63 - 6 - 1 = 56.

The universal campaign lower certificate is M-E = 8-6 = 2. It is conservative.

In another fully checked sequence, 24 bad funded candidates precede that same
promotion. Search charges become 75 and net endpoint gain becomes:

    63 - 75 - 1 = -13.

The improvement is real in the declared work metric. Campaign profitability is
not automatic. `expensive_search_reachable` also proves the costly pre-state comes
from replaying 24 actual rejected transitions; it is not just an invented ledger.

## 7. Executable boundary

The Lean runtime constructs a `CertifiedResult` whose state carries `Safe` evidence.
It then executes the selected active component on the workload. The Python wrapper
rejects unknown fields, candidate-provided scores/fees, duplicate keys, and arbitrary
source paths. It checks pinned sources and current compiled-target fingerprints
before and after evaluation under a protected host.

The runtime is read-only and starts a fresh logical campaign from the fixed baseline
for each input. It does not install source, authorize retries, edit existing stores,
or persist a globally authoritative campaign ledger. A replayed stale proposal
cannot promote again, but a newly evaluated stale proposal is still charged within
that campaign. This is not an idempotent payment or crash-recovery API.

## 8. Relation to recursive improvement

The generic adaptive theorem permits an incumbent-dependent proposer while keeping
the authority fixed. This supplies a checked update rule for a possible recursive
improvement loop. The example is an authored, precompiled specialization, not a
candidate discovered by an autonomous model. No multi-generation gain, learning in
model weights, unbounded capability growth or historical novelty is established.
