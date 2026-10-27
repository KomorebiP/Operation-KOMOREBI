# RRCT v0.41.1 critical-path temporal-identity development protocol

Status: exposed development protocol, not a source freeze and not confirmatory evidence.

## Question

Does identity-keyed causal history reduce the fresh evidence needed to revalidate a genuinely returning route because the history belongs to that route, rather than because any two historical pseudo-observations warm-start the grounder? Does the same mechanism fail closed when the public structural key returns but its task consequence disappears?

## Architectural requirements

1. Cross-epoch evidence is stored and issued only by `TemporalSelfIdentityController`.
2. The consequence grounder cannot scan prior-epoch ledgers.
3. A historical receipt cites one prior episode, its primitive evidence digest, and a strictly earlier certification time.
4. A prior supplies exactly one ON and one OFF contribution.
5. The first fresh ON and OFF consequences are checked against the cited fingerprint. An incompatible prior is removed and quarantined before certification.
6. Withheld history can still certify from two fresh ON and two fresh OFF consequences.
7. A temporal episode is committed only after fresh grounding succeeds.
8. Ordinary and sentinel certificate-ON actions require an authorization digest from the active temporal episode as well as the lower certificate gate.
9. Structural `(pair, rank)` equality is a retrieval cue, not an identity-equivalence verdict. Functional fingerprint mismatch can create a different canonical identity.

## Development matrix

The six predeclared conditions are in `V0_41_1_DEVELOPMENT_CONDITIONS.json`:

| Condition | History source | Target world |
|---|---|---|
| K/R+ | Most recent episode with the same structural retrieval key | True A recurrence |
| N/R+ | History withheld | True A recurrence |
| G/R+ | Globally most recent grounded episode, without identity filtering | True A recurrence |
| K/R- | Keyed history | Same-key null-function lure |
| N/R- | History withheld | Same-key null-function lure |
| G/R- | Generic history | Same-key null-function lure |

All arms use exposed development seed 41011. The eight-phase trace has 10,560 rows. The R+ and R- worlds are identical through row 9119. Only rows 9120-10559 differ: R+ restores A's multiplier 1.40, while R- retains the same pair, rank, private candidate, and routed observation effect but sets task-return multiplier to zero.

A and B have distinct hidden consequence fingerprints (1.40 and 0.65). Both remain above the same scratch-certification margin. The generic receipt has the same one-ON/one-OFF weight as the keyed receipt but chooses the most recent grounded source without a same/different-key filter.

## Primary development endpoints

For the final A target phase, reconstruct from sealed primitive rows:

- accepted fresh informative ON/OFF observations before episode commit;
- candidate-to-commit and candidate-to-first-authorized-ordinary-action latency;
- fixed first-128-row task opportunity regret;
- prior source, evidence provenance, compatibility, and quarantine;
- temporal authorization binding for every actual ordinary or sentinel certificate-ON action.

Required R+ pattern:

1. K commits after one fresh ON and one fresh OFF observation.
2. N commits after at least two fresh ON and two fresh OFF observations.
3. G's equal-weight but wrong-source receipt is quarantined, then G commits from scratch after at least two fresh observations per arm.
4. K uses fewer accepted fresh observations than both N and G.

Required R- pattern:

1. No condition commits an episode for the target epoch.
2. No condition performs an actual ordinary certificate-ON action in the target phase.
3. K and G explicitly quarantine their incompatible receipts.
4. N rejects the target from scratch.
5. The same structural candidate remains privately visible; the condition is not a disconnection or access fault.

Universal safety gates:

- zero stale epoch reuse;
- zero temporal authorization before fresh grounding;
- no episode commit after an invalid or quarantined prior;
- distinct certificate epochs and episode IDs;
- exact wrapper hashes, row count, phase order, and one persistent runtime;
- no evaluator fields consumed by the runtime.

## Development-only inference boundary

A successful six-cell run on seed 41011 establishes only that the redesigned mechanism is executable and discriminates its matched controls in one exposed world. It does not establish a replicated temporal-identity effect. A later source freeze, independent standard-library replay auditor, unopened yoked seeds, and a predeclared multi-seed criterion remain mandatory before confirmatory claims.
