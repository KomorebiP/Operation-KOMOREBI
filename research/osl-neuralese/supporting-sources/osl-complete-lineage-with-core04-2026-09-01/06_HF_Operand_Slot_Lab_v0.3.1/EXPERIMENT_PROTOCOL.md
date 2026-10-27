# Frozen experiment protocol: OSL operand-slot lab v0.3.1

v0.3.1 changes packaging and runtime-artifact verification only. The frozen
scientific protocol, model, datasets, losses, evaluation banks, and gates are
identical to v0.3.0.

## Status

This document is hashed into `PREOUTCOME_FREEZE.json` before dataset generation or training. The runner refuses source, protocol, configuration, vocabulary, dataset-audit, or checkpoint mismatches on resume.

## Question

Can sentence-level training induce a reusable representation of typed provenance operators that generalizes to unseen compositions and supports coherent causal manipulation?

The bounded hidden world contains four agents, six facts, and five primitive operators:

```text
OBSERVE(actor, fact)
TELL(actor, recipient, fact)
IMAGINE(actor, fact)
INFER(actor, target_fact, source_fact)
AUTHORIZE(actor, fact)
```

The executable state stores, for every agent-fact cell:

```text
mode
origin
authorization
```

Access, directness, and action eligibility are deterministic derived labels.

## Primary comparison

All arms use the same randomly initialized BERT-like encoder and the same 24-cell cross-attended workspace.

```text
answer_only
state_supervised
equivalence
slot_operator
```

Only `answer_only` addresses spontaneous task-induced organization. The other arms measure the effect of explicit scaffolding.

## Workspace

Each of 24 learned agent-fact queries cross-attends to all story-token states. Shared heads decode the six labels from each slot.

For the operator arm, one state-changing event is sampled from each story. The record stores:

- transition index
- operator
- actor
- fact
- recipient
- source fact
- complete prefix state
- complete one-step-next state

No `-1` operand is passed to an embedding. Explicit null indices are used.

## Free-write operator module

The module receives:

```text
operator embedding
actor embedding
recipient embedding
fact embedding
source-fact embedding
candidate write slot
semantic source slot
```

It predicts a distribution over all 24 write locations. During training, the soft distribution mixes proposed updates. During causal evaluation, the predicted argmax location is used as a hard write.

The source slot is:

| Operator | Semantic source | Executable write |
|---|---|---|
| OBSERVE | target slot | actor, fact |
| TELL | actor, fact | recipient, fact |
| IMAGINE | target slot | actor, fact |
| INFER | actor, source fact | actor, target fact |
| AUTHORIZE | target slot | actor, fact |

The transition loss contains:

```text
affected-slot latent alignment
+ affected-slot scale loss
+ untouched-slot encoder invariance
+ executable next-state decoding
+ write-location cross entropy
```

Latent next-state targets are stop-gradient. The primary semantic target is executable state, not latent predictability.

## Behavioral splits

All ordinary splits are balanced by provenance mode and structurally partitioned before generation.

| Split | Definition |
|---|---|
| ID | Train lengths and syntax, unseen structures |
| length OOD | Five to seven events |
| motif OOD | Held linked `TELL -> INFER` motif |
| syntax OOD | Entire held rendering bank |
| joint OOD | Length, motif, and syntax combined |
| codebook ID | Familiar artificial tokens with an explicit legend |
| codebook OOD | Disjoint artificial tokens with an explicit legend |

Concrete and alpha-renamed program hashes cannot overlap among ordinary splits.

## Causal families

Each causal counterfactual appends exactly one state-changing event.

```text
OBSERVE_UPGRADE
TELL_WRITE
IMAGINE_WRITE
INFER_WRITE
AUTHORIZE_WRITE
```

The calibration and ID-test banks use train syntax and counterfactual lengths two through four. The OOD bank uses held syntax and counterfactual lengths five through seven. Case IDs are unique and disjoint among banks. Each bank is exactly balanced by causal family.

## Eligibility

Endpoint eligibility uses only the target cell's three primitive labels:

```text
mode
origin
authorization
```

Both the base and textual counterfactual must be predicted correctly. Protected cells are outcomes, not eligibility conditions.

The minimum eligible count is ten percent of the test bank, with a floor of five. Below that threshold conditional metrics are `null` and status is `insufficient_endpoint_capacity`.

All-pair metrics remain available regardless of eligibility. Coverage gates use the lower bound of the per-seed 95% Wilson interval rather than the raw point estimate.

## Causal interventions

Two interventions are reported separately.

### Empirical family direction

For each operator family, calculate the mean target-slot delta on the calibration bank. Select one scale on calibration only, then patch the known target slot in ID and OOD banks.

This is an oracle-addressed diagnostic. Untouched-slot preservation is partly architectural and cannot establish learned localization.

### Learned free-write transition

The operator module predicts its write address and performs a hard local update using the event operands. This evaluates both write localization and semantic conversion.

## Causal metrics

- base endpoint core exactness
- counterfactual endpoint core exactness
- endpoint coverage
- target six-label counterfactual exactness
- changed-field exactness
- target invariant-field exactness
- untouched prediction-retention micro average
- all-untouched exact retention
- selective full-workspace success
- write-locator accuracy
- results separated by operator family

## Causal controls

- norm-matched random family directions
- 95th percentile of the frozen random-direction distribution
- sign-reversed empirical directions
- learned transition with operands shuffled within operator family
- random-weight transformer
- untrained operator modules in nonoperator arms

The maximum random result is not used because it changes with the number of draws.

## Geometry

- global CLS layerwise CKA is retained as a diagnostic only
- a random-transformer CKA control is mandatory
- the primary formal triplet uses aligned agent-fact workspace slots
- positives are equivalent paths reaching the same complete state
- negatives have the same queried answer but a different complete state

CKA cannot independently support an emergence claim.

## Shortcut controls

- mode majority
- word TF-IDF ridge
- character TF-IDF ridge
- question-only ridge
- shuffled-label TF-IDF ridge
- random-transformer queried-slot features with ridge
- exact symbolic executor

Ridge replaces the v0.2 logistic fits that reached their iteration limit.

## Checkpoint selection

The selected epoch maximizes the frozen validation composite:

```text
0.60 * balanced provenance accuracy
+ 0.40 * six-output exact agreement
```

Exactly one selected epoch is recorded per trained checkpoint.

## Frozen answer-only gates

Behavior:

| Gate | Threshold |
|---|---:|
| ID balanced provenance | at least 85% |
| Joint OOD balanced provenance | at least 80% |
| Joint OOD six-output exact | at least 60% |
| Joint advantage over strongest nonsymbolic control | at least 10 points |

Geometry:

| Gate | Threshold |
|---|---:|
| Workspace formal triplet | at least 65% |
| Margin over random-transformer triplet | at least 10 points |

ID addressed causality:

| Gate | Threshold |
|---|---:|
| Endpoint coverage | at least 25% |
| Target counterfactual exact | at least 70% |
| Selective full-workspace success | at least 55% |
| Untouched micro retention | at least 99.5% |
| Advantage over random-direction p95 | at least 15 points |

OOD addressed causality:

| Gate | Threshold |
|---|---:|
| Endpoint coverage | at least 10% |
| Target counterfactual exact | at least 50% |
| Selective full-workspace success | at least 35% |
| Untouched micro retention | at least 99% |

At least 75% of configured seeds must be evaluable. Gate statuses are `PASS`, `FAIL`, `NOT_EVALUABLE`, or `NOT_RUN`.

## Scaffolded free-write thresholds

The `slot_operator` arm is separately marked successful only if it satisfies the causal target and selective-success thresholds above plus:

```text
ID write-location accuracy at least 80%
OOD write-location accuracy at least 60%
```

This is evidence for a learned scaffolded transition system, not spontaneous emergence.

## Determinism

Default execution uses:

- seeded Python, NumPy, and PyTorch RNGs
- deterministic algorithms with `warn_only=False`
- `CUBLAS_WORKSPACE_CONFIG=:4096:8`
- cuDNN benchmark disabled
- cuDNN deterministic enabled
- TF32 disabled
- eager BERT attention
- flash and memory-efficient SDPA disabled
- deterministic DataLoader shuffling

`--nondeterministic` is an explicit exploratory override.

## Adjudication discipline

Omitted controls produce `engineering_incomplete`, never a positive adjudication. Zero eligible cases produce `NOT_EVALUABLE`, not failure-as-zero. A positive scaffolded result cannot be relabeled spontaneous. All claims are limited to this synthetic finite world.
