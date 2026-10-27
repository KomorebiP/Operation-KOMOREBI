# RRCT v0.41.1 temporal-identity critical-path development report

Status: exposed development result; not a fresh-seed cohort and not confirmatory evidence.

Version: `0.41.1.dev2`  
Exposed seed: `41011`  
Matrix: six yoked conditions, 10,560 rows per condition, 63,360 sealed rows total

## Question tested

Does route-keyed causal history reduce the fresh evidence needed to revalidate a genuinely returning route because the history belongs to that route, rather than because any equal-weight historical pseudo-observations warm-start the grounder? Does the mechanism fail closed when the same structural key returns without the earlier task consequence?

## Implemented causal changes

- The temporal controller is the only owner of cross-epoch identity memory.
- The lower consequence grounder cannot scan prior-epoch evidence ledgers.
- A historical receipt cites one earlier certified episode and the digest of its primitive ON/OFF evidence.
- A receipt contributes one ON and one OFF pseudo-observation, but only after the first fresh ON and OFF observations agree with its stored functional fingerprint.
- Incompatible receipts are removed and quarantined before certification.
- Structural `(pair, rank)` equality is only a retrieval cue. Functional mismatch can create a different canonical identity.
- A temporal episode is committed only after fresh grounding.
- Ordinary and sentinel certificate-ON actions require a digest bound to the active temporal episode. Lower-layer certification alone cannot authorize action.
- Snapshot digests commit the future-causal internal state, and downstream drift clears temporal authorization.

## Matched matrix

| Condition | History | Final world |
|---|---|---|
| K/R+ | identity-keyed | true A recurrence |
| N/R+ | withheld | true A recurrence |
| G/R+ | globally recent, equal weight | true A recurrence |
| K/R- | identity-keyed | same-key null-function lure |
| N/R- | withheld | same-key null-function lure |
| G/R- | globally recent, equal weight | same-key null-function lure |

The six arms share the same seed and exogenous trace. R+ and R- are identical through row 9,119. In the final 1,440-row phase, R+ restores A's task-return multiplier to 1.40 while R- preserves the same structural route and private candidate but sets the task-return multiplier to zero.

## Independently reconstructed result

The standard-library science auditor imported no RRCT code and did not trust scientific booleans in the generated summaries. It recomputed artifact hashes, receipt chains, layered wrapper hashes, action-authorization bindings, prior provenance, episode transitions, yoking, and the final matrix contrast from the sealed rows.

Result: `V041_DEVELOPMENT_MATRIX_AUDIT_PASS`, 12/12 criteria.

| Final target result | K/R+ | N/R+ | G/R+ |
|---|---:|---:|---:|
| Fresh probes before commit | **2** | 4 | 4 |
| Fresh ON/OFF evidence | **1/1** | 2/2 | 2/2 |
| Candidate-to-commit latency | **2** | 4 | 4 |
| Candidate-to-first-authorization latency | **3** | 5 | 5 |
| Ordinary authorized target actions | 463 | 459 | 459 |
| Prior outcome | compatible | none | quarantined |
| Target episode commits | 1 | 1 | 1 |
| Stale or premature authorization | 0 | 0 | 0 |

The keyed condition therefore halved the fresh evidence requirement and authorized two rows earlier than both matched controls. The equal-weight generic history did not help: its wrong-source receipt was quarantined and its subsequent behavior matched the no-history arm.

| Null-lure result | K/R- | N/R- | G/R- |
|---|---:|---:|---:|
| Privately visible target-candidate rows | 480 | 480 | 480 |
| Target episode commits | **0** | **0** | **0** |
| Ordinary target authorizations | **0** | **0** | **0** |
| Prior outcome | quarantined | none | quarantined |

All three R- arms rejected the same-key/null-function lure. The result was not caused by disconnection or loss of private access: the structural candidate remained privately visible for all 480 candidate rows in every R- arm.

Across all 63,360 rows, the audits found zero stale reuse, zero authorization before fresh grounding, zero invalid temporal action binding, exact phase schedules, one persistent runtime per arm, and no evaluator-truth leakage.

## Secondary reward result

The protocol's literal first 128 rows of the final phase are rows 9,120-9,247, while the target candidate first appears at row 10,080. That predeclared window is therefore non-discriminating: K, N, and G have identical R+ realized return (`0.621389`) and opportunity regret (`154.466233`). It is not evidence of a reward advantage.

An explicitly exploratory, non-criterion 128-row window anchored at candidate appearance (rows 10,080-10,207) is unfavorable to K on this seed:

| Exploratory candidate-aligned window | K/R+ | N/R+ | G/R+ |
|---|---:|---:|---:|
| Realized return | 94.1749 | **104.8394** | **104.8394** |
| Opportunity regret | 58.7740 | **48.1095** | **48.1095** |

Thus, this development result establishes a causal benefit in evidence efficiency and authorization latency, not a reward or regret improvement. The fresh-pilot protocol treats reward metrics as descriptive and cannot use them to rescue or invalidate the primary endpoint.

## Integrity anchors

- Independent science audit SHA-256: `f4a0a77d41f3f0d8676eff2b8a388a9470d4d63bb65733c92322acf1b93c5404`
- Independent science auditor SHA-256: `6f1a26a25a569f26b5e2597660a019b1d5e619ee178be06350dc0909b9f7afa5`
- Integrity/yoking audit SHA-256: `411bfa667d21c6cc183f7afef720ea5542a020b3880842b8f0c5128834980d45`
- Final production source hashes are recorded in every start receipt and agree across all six arms.
- Relevant inherited and v0.41 tests: 46 passed before freeze preparation.
- Freeze-builder focused tests: 10 passed.

## Retained development failure

The first concurrent attempt exposed a late-prior issuance bug. `G_RPLUS` failed closed at 2,880 rows; the other active R+ arms were intentionally stopped so no matrix result mixed source revisions. The partial traces were retained under `_failed_pre_handshake/`. A grounder-controller eligibility handshake then prevented prior issuance after fresh target evidence had begun. No frozen source or unopened seed was involved.

## Claim boundary and next gate

This result shows that the redesigned temporal history mechanism is causally upstream of fresh grounding and action authorization in one exposed synthetic world, and that it discriminates keyed history from withheld and equally weighted wrong-source history while rejecting a same-key functional lure.

It does not establish subjective awareness, cross-domain generality, reward superiority, or confirmatory replication. The next gate is the separately frozen four-seed, six-arm pilot described in `V0_41_1_FRESH_PILOT_PROTOCOL.md`. No fresh seed may be replaced after inspection, and any scientific failure remains part of the cohort result.
