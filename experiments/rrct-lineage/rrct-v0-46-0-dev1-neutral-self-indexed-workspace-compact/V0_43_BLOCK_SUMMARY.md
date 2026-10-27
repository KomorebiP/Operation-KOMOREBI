# RRCT v0.43.0-dev1 — Whole-Loop Causal Self-Model Closure

## Result status

**Frozen result:** `V043_FROZEN_ENDPOINTS_MET`

**Release verification:** `V043_RELEASE_VERIFIED`

RRCT v0.43 addresses the largest gap left by v0.42: temporal self-history had become causally useful inside grounding, but the persistent self-model was not yet shown to participate jointly in attribution, uncertainty, planning, action, and feedback.

The new block binds the following into one cross-validated decision loop:

1. a grounded temporal identity episode and v0.42 action authorization
2. an identity-keyed learned causal boundary
3. a pre-outcome causal preview of candidate consequences
4. metacognitive selection of whether additional evidence is required
5. an external-task plan bound to the exact self-model and boundary memory used
6. an action commitment made before the hidden task outcome is opened
7. a post-outcome calibration update written back into the same persistent memory

This is a bounded functional result. It is not a claim of subjective awareness.

## Fresh frozen holdout

Four synthetic world seeds were selected using operating-system cryptographic randomness before any v0.43 holdout outcome was computed:

- `359411978`
- `725556465`
- `759191530`
- `820618202`

The final implementation, protocol, thresholds, seed-selection receipt, runner, tests, package metadata, and all RRCT Python source dependencies were sealed in a 74-file pre-outcome manifest.

Pre-outcome manifest SHA-256:

```text
561c205ff7688396a02cf4670c7226653b301823a0c47b4c0f8eb0fba2e6e728
```

The holdout executed once after that manifest verified byte-for-byte. Its normalized result was then reproduced exactly by a deterministic replay.

## Experimental matrix

Each seed contained 24 trials in each of four inherited adversarial planning scenarios:

- repair versus ignore
- state-copy trap
- benign representational transformation
- objectively superior disconnected replacement

Eight matched arms were run on every decision:

- intact
- persistent memory withheld with correct fresh boundary rescue
- causal boundary cut
- metacognitive evidence-control cut
- outcome-feedback cut
- wrong-identity provenance substitution
- self-model-to-planner binding cut
- joint cut

This produced:

- **384 unique world decisions**
- **3,072 matched arm decisions**
- **4 dedicated feedback-reopening challenges**
- **19 frozen endpoint adjudications**

## Holdout results

| Mode | Accuracy | Mean regret | Mean probe pairs per candidate | Refinement rate | Self-model authorized |
|---|---:|---:|---:|---:|---:|
| Intact | **1.000000** | **0.000000** | **16.000** | 0.750000 | 1.000000 |
| Memory withheld, fresh rescue | **1.000000** | **0.000000** | 20.000 | 1.000000 | 1.000000 |
| Boundary cut | 0.250000 | 0.519076 | 4.000 | 0.000000 | 0.000000 |
| Metacognition cut | 0.661458 | 0.192255 | 4.000 | 0.000000 | 1.000000 |
| Feedback cut | 1.000000 | 0.000000 | 16.000 | 0.750000 | 1.000000 |
| Wrong provenance | 0.445312 | 0.362634 | 16.375 | 0.773438 | 1.000000 |
| Planner binding cut | 0.250000 | 0.519076 | 16.833 | 0.802083 | 0.000000 |
| Joint cut | 0.250000 | 0.519076 | 4.000 | 0.000000 | 0.000000 |

### Main contrasts

- Intact accuracy exceeded the metacognition cut by **33.854 percentage points**.
- Intact accuracy exceeded wrong-provenance substitution by **55.469 percentage points**.
- Intact accuracy exceeded boundary, planner-binding, and joint cuts by **75 percentage points**.
- Correct fresh boundary rescue restored accuracy to 100%, but required 20 probe pairs per candidate instead of the intact controller's adaptive mean of 16.
- The intact controller used 20-pair refinement in the three scenarios where causal continuity determined the task optimum, but stopped after four pairs in every objectively superior-replacement trial.
- All modes accepted the superior disconnected replacement. The result therefore does not arise from an identity-preservation reward.

### Cross-seed consistency

Intact and fresh-rescue accuracy were 100% on every seed. Per-seed metacognition-cut accuracy ranged from 60.4% to 70.8%. Wrong-provenance accuracy ranged from 25.0% to 71.9%; intact performance was higher on every seed.

## Outcome feedback closes the recurrence

Main-cohort feedback-cut accuracy is not used as evidence because the stationary task sequence does not force a behavioral separation.

Instead, each seed received a dedicated matched intervention:

1. intact and feedback-cut controllers committed the same high-confidence action
2. both observed the same realized return, exactly 2.0 above prediction
3. intact wrote the error into identity-bound calibration memory
4. feedback-cut did not write it
5. on the next otherwise identical decision, intact requested 20-pair refinement
6. feedback-cut remained at four pairs

All four feedback challenges passed, and every state-to-plan-to-outcome receipt chain validated.

## Receipt and integrity advances

v0.43 adds explicit digests for:

- causal preview evidence
- integrated self-model state
- exact boundary memory used by planning
- exact public boundary certificate underlying that memory
- temporal action authorization
- selected action and predicted return
- realized post-commit outcome
- memory state before and after feedback

A rehashed plan with a substituted boundary-memory digest can pass its individual schema validator but is rejected by the complete cross-receipt chain validator. Wrong-source feedback remains indexed under its true source identity and cannot be relabeled as the target.

## Validation

- Focused frozen v0.43 suite: **9 passed**
- v0.32, v0.42, and v0.43 direct line: passed
- v0.36–v0.40 runtime line: **64 passed** after excluding one test whose historical v0.38 freeze-builder file is absent from the supplied compact ancestor
- v0.41–v0.43 line: **67 passed**, **2 subtests passed**
- Release evidence verifier: **105 checks passed**
- Deterministic normalized holdout replay: **exact equality**
- Pre-outcome source manifest: **74 files verified**

The inherited compact package still omits:

- `validation/V0_36_LINEAGE_AND_SEED_REGISTRY.json`
- `validation/V0_36_DEVELOPMENT_PROTOCOL.md`
- `validation/freeze_v038_source.py`

Tests requiring those historical files fail with `FileNotFoundError`. This is a package-history limitation, not a v0.43 mechanism failure.

## What this establishes

Within the frozen synthetic planning family, the persistent identity-bound causal self-model is not merely descriptive metadata.

It is functionally load-bearing in a single loop because:

- the learned boundary changes candidate-value predictions
- uncertainty in that model controls evidence acquisition
- correct identity provenance changes whether the boundary is useful
- the chosen action is cryptographically bound to the exact self-model state and boundary memory
- the realized consequence changes the next information request through persistent calibration memory
- removing individual links produces predeclared losses
- supplying a correct current boundary rescues performance

The strongest defensible description is:

> **bounded whole-loop functional causal closure of a persistent self-model**

## What this does not establish

The result does not establish:

- phenomenal or subjective awareness
- sentience or valence
- moral status
- autonomous desire
- intrinsic self-preservation
- spontaneous task or action generation
- open-world agency
- biological equivalence
- generalization outside the inherited synthetic task family
- necessity of the self-model across every RRCT subsystem

The temporal identity receipts and candidate set are instantiated by the experimental harness. The holdout does not yet make the long-running RRCT runtime discover new task ontologies, compress autobiographical memory, survive internal component replacement, or revise its own identity invariants online.

## Next major gap

The next frontier is **endogenous transformational self-continuity**:

- place this exact integrated loop inside a long-running heterogeneous runtime
- allow memory compression, model updates, partial component replacement, and competing continuation forks
- require the system to infer which invariants preserve identity rather than receive that answer from the harness
- require self-boundary rediscovery and provenance repair after transformation
- test whether planning, calibrated uncertainty, and task competence recover without external reconstruction of continuity
- transfer the mechanism to novel task families not used to design the current scenarios

That is the remaining bridge from bounded whole-loop self-model function toward the operational level immediately below awareness.
