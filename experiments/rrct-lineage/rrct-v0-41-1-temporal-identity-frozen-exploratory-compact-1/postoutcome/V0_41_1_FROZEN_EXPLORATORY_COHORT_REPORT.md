# RRCT v0.41.1 frozen temporal-identity exploratory cohort

## Outcome

The first prospectively frozen four-seed temporal-identity cohort is complete:

- 4 one-shot-selected fresh seeds
- 6 yoked conditions per seed
- 24 completed arms
- 10,560 canonical sealed rows per arm
- 253,440 canonical sealed rows total
- 5,556,337,181 canonical row bytes

The literal frozen cohort rule is **not met**. The post-freeze repaired
independent replay passed seed count, 24-arm topology, source/freeze/claim/hash
chains, yoking, environment, and source-reverification gates, but all four
seeds failed the universal `S01` criterion because of one contradictory audit
counter.

The correct status is therefore:

> **Prospective exploratory cohort: literal fail, with post-hoc semantic support
> for the intended causal temporal-memory mechanism.**

This is not a confirmatory result and does not establish subjective awareness.

## Prospectively frozen design

The treatment/control matrix was:

| Condition | History policy | World variant |
|---|---|---|
| `K_RPLUS` | Identity-keyed receipt | Genuine recurrence |
| `N_RPLUS` | History withheld | Genuine recurrence |
| `G_RPLUS` | Equal-weight generic wrong-source receipt | Genuine recurrence |
| `K_RMINUS` | Identity-keyed receipt | Same-key null-function lure |
| `N_RMINUS` | History withheld | Same-key null-function lure |
| `G_RMINUS` | Equal-weight generic wrong-source receipt | Same-key null-function lure |

The four sealed seeds were `280842095`, `305790955`, `582368056`, and
`887738207`. The source freeze SHA-256 is
`4a06e59ebfd44e4f2a84ef270e4f92d74efb352183ca378ddcd4a0196a9ed91b`.
The source archive SHA-256 is
`aeeb7268d61373edb31c2673e6cb0ca5faf6e000d188f344d307221cbcc63f5d`.

The pre-outcome source, protocol, seed registry, and preexecution record were
committed externally before the first campaign claim. No arm was retried.

## Primary causal effects

Every seed reproduced the intended evidence-efficiency pattern:

| Seed | Fresh probes K / N / G | Commit latency K / N / G | First-authorization latency K / N / G | R− commits | R− authorizations |
|---:|---:|---:|---:|---:|---:|
| 280842095 | 2 / 4 / 4 | 1 / 3 / 3 | 2 / 4 / 4 | 0 / 0 / 0 | 0 / 0 / 0 |
| 305790955 | 2 / 4 / 4 | 1 / 4 / 4 | 2 / 5 / 5 | 0 / 0 / 0 | 0 / 0 / 0 |
| 582368056 | 2 / 4 / 4 | 1 / 4 / 4 | 2 / 5 / 5 | 0 / 0 / 0 | 0 / 0 / 0 |
| 887738207 | 2 / 4 / 4 | 1 / 3 / 3 | 2 / 4 / 4 | 0 / 0 / 0 | 0 / 0 / 0 |

Thus, in all four fresh worlds:

- compatible identity-keyed history reduced fresh grounding from 4 probes to 2;
- keyed history reduced candidate-to-commit latency from 3–4 steps to 1;
- keyed history reduced candidate-to-first-authorization latency from 4–5
  steps to 2;
- all 12 null-lure arms produced zero target episode commits and zero target
  certificate-ON authorizations;
- the null candidate remained privately visible for all 480 target rows, so
  abstention was not explained by disappearance or access loss; and
- global premature-authorization and stale-epoch-reuse counts were both zero.

For every seed, frozen criteria `S02` through `S10` passed. This includes
exogenous yoking, pretarget world-variant blindness, matched target structural
keys, prequential prior-receipt matching, exact R+ grounding patterns, prior
specificity, keyed latency advantage, R− null action, and R−
quarantine/rejection with private visibility.

## Why the literal rule failed

The protocol contains two incompatible formulations:

1. The detailed `G_RPLUS` endpoint requires the system to quarantine an
   equal-weight wrong-source prior and then commit from scratch after at least
   two fresh ON and two fresh OFF observations.
2. The universal prose says there must be “no commit after an invalid or
   quarantined prior.”

The auditor implemented the second phrase temporally. Its
`commit_after_quarantined_prior_count` increments whenever any later episode is
committed for a signature whose prior was quarantined—even when the prior has
already been deactivated and the commit uses only fresh evidence.

That counter was nonzero only in the generic-history arms:

| Condition | Count per seed | Meaning in this implementation |
|---|---:|---|
| `G_RPLUS` | 3 | Three fresh-evidence commits occurred later than generic-prior quarantine |
| `G_RMINUS` | 2 | Two earlier legitimate commits occurred later than generic-prior quarantine; target-phase commit remained zero |

All eight generic cells therefore had exactly one false integrity flag,
`zero_commit_after_quarantined_prior`; no other cell integrity flag was false.

This counter does **not** show that a quarantined prior authorized a commit.
The completed primitive replay separately required, on every quarantined-prior
row, that:

- the active prior receipt was `None`;
- the temporal historical-prior digest was `None`; and
- every later commit had fresh grounding with primitive ON and OFF evidence.

The post-hoc semantic adjudication therefore finds that the intended narrower
causal rule—no commit *using or authorized by* a quarantined prior—held on all
four seeds. That adjudication does not retroactively convert the frozen literal
failure into a prospective pass.

## Audit incidents retained in the evidence

The original frozen auditor stopped before row replay because its reconstructed
preselection surface did not permit the preexecution record that the same
workflow required after seed selection. The exact mismatch was one file:
`validation/V0_41_1_PREEXECUTION_VALIDATION.json`.

A narrow post-freeze auditor copy was created outside the frozen source. Two
additional infrastructure defects were then found and retained:

1. The workspace filesystem left 16 hidden partial-row residues during the
   concurrent campaign. They total 1,611,661,312 bytes. Every residue was
   independently verified as an exact byte prefix of its final, receipt-hashed
   `sealed_rows.jsonl`; none was deleted or treated as a competing result.
2. The frozen auditor correctly validated every arm’s inner environment digest,
   but its cross-arm aggregation rehashed the wrapper including that digest,
   guaranteeing a mismatch with the campaign binding. The repaired auditor
   compares the already validated inner digest directly.

The repaired auditor source records all changes and retains the hashes of every
prior failure. It did not change experiment source, row replay, evidence,
R+/R− endpoints, or the literal final decision. The experiment source still
matched the pre-outcome freeze after replay.

## Descriptive reward result

Reward and regret were prospectively designated descriptive and noncriterion.
Across the four candidate-aligned 128-row windows, mean realized return sums
were:

- keyed: 89.814
- withheld: 93.862
- generic: 93.862

Mean opportunity-regret sums were:

- keyed: 65.199
- withheld: 61.151
- generic: 61.151

Therefore, the cohort supports evidence and authorization efficiency, not a
reward-superiority claim. The shorter keyed grounding path did not reliably
improve this reward window.

## Scientific interpretation

The cohort materially strengthens the temporal-identity result:

- the memory advantage is specific to the correct historical identity, because
  equal-weight generic history behaves like the no-history control;
- the advantage recurs across four one-shot-selected fresh seeds;
- the system still demands fresh consequence evidence before authorization;
- same structural key without the prior function is rejected in every policy;
  and
- stale or quarantined history never remains on the action-critical path.

However, a clean prospective validation remains open because the literal
universal gate was internally inconsistent and the frozen auditor required
post-outcome infrastructure repairs.

## Required v0.41.2 closure

The next cohort should be frozen from a new source version and new fresh seeds,
with these corrections made before seed selection:

1. Harmonize selector and auditor treatment of the preexecution record.
2. Make hidden prefix-residue detection explicit and require exact-prefix
   verification, or eliminate the workspace residue mechanism entirely.
3. Compare the validated inner environment digest rather than hashing its
   digest-bearing wrapper.
4. Replace the temporal phrase “no commit after” with the causal invariant “no
   commit may use or be authorized by an invalid/quarantined prior.”
5. Add a direct commit-event receipt binding fresh evidence, active episode,
   certificate epoch, and `historical_prior_digest = null` after quarantine.
6. Run a new four-seed × six-condition prospective cohort without reusing these
   outcomes.

Until that succeeds, the defensible claim is:

> The v0.41.1 frozen exploratory cohort replicated the intended bounded
> temporal-memory efficiency and null-lure rejection pattern on four fresh
> seeds, but did not achieve a clean prospective cohort pass under its literal
> frozen audit specification.

