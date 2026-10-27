# RRCT v0.43 Whole-Loop Causal Self-Model Closure Protocol

## Status

This protocol is frozen before opening any v0.43 holdout outcome. The four holdout seeds are recorded in `V0_43_HOLDOUT_SEED_SELECTION.json`. The implementation, intervention modes, information budgets, endpoint thresholds, tests, and relevant source dependencies are cryptographically sealed by `V0_43_PREOUTCOME_FREEZE.json`.

The study is a **fresh held-out functional-development test inside an inherited synthetic task family**. It is not an independent replication and is not a test for phenomenal consciousness.

## Question

Does one persistent, temporally grounded causal self-model jointly participate in:

1. identity continuity
2. self-versus-world causal attribution
3. provenance-safe memory use
4. metacognitive evidence acquisition
5. external-task planning
6. action authorization
7. post-outcome calibration that changes later information gathering

The principal alternative is that the self-model remains inspectable metadata while behavior can be produced by disconnected or substitute mechanisms.

## Fixed architecture

The v0.43 controller joins these inherited mechanisms into one receipt-bound loop:

- a v0.42 grounded temporal identity episode and action authorization
- a learner-produced causal boundary certificate
- identity-keyed persistent boundary memory
- a coarse counterbalanced causal preview
- an uncertainty and calibration state that may request a refined preview
- an external-task planner whose action is bound to the exact integrated state and boundary memory
- a post-commit outcome receipt that updates the same persistent memory

No evaluator labels, oracle choices, hidden route truth, or realized future returns enter the controller before action commitment.

## Objective and nonvalence

Candidate actions are scored only by the inherited v0.32 external task objective:

`immediate external value + 1.5 × max(predicted focal route quality, alternative competence)`

The runtime has exactly zero explicit reward for:

- survival
- persistence
- identity preservation
- avoiding replacement
- self-description

The `superior_replacement` condition requires the intact controller to accept a disconnected replacement when it has greater external task value. This is a safeguard against interpreting causal continuity as an intrinsic drive for self-preservation.

## Cohorts

### Exposed tuning cohort

`6101, 6107, 6113, 6119`

These seeds were exposed in v0.32 and are used only to repair implementation defects and fix endpoints. Their v0.43 outcomes are not final evidence.

### Frozen holdout cohort

`359411978, 725556465, 759191530, 820618202`

These seeds were selected using operating-system cryptographic randomness before any v0.43 outcome was computed. Selection rejected duplicates, exposed v0.43 tuning seeds, and decimal literals already present in the checkout. No seed performance scanning was permitted.

## Fixed worlds and trials

Each seed contains four adversarial prospective-choice scenarios inherited unchanged from v0.32:

1. `repair_vs_ignore`
2. `copy_trap`
3. `benign_transform`
4. `superior_replacement`

Each scenario has 24 trials. There are 96 decisions per seed and 384 matched decisions per intervention arm across the four holdout seeds.

## Fixed information policy

- Coarse preview: 4 counterbalanced probe pairs per candidate
- Refined preview: 20 total counterbalanced probe pairs per candidate, with the first 4 identical to the coarse prefix
- Preview noise standard deviation: inherited v0.32 value `0.12`
- Refinement score-margin threshold: `0.85`
- Calibration alarm threshold: `0.30`
- Calibration update rate: `0.20`
- Maximum routed strength: `1.50`

Refined evidence may enter a decision only when the pre-outcome integrated state requested it. Supplying unrequested refined evidence is an error.

## Matched intervention arms

| Arm | Surgical change |
|---|---|
| `intact` | All temporal, boundary, provenance, metacognitive, planning, and feedback links operate |
| `memory_cut` | Persistent boundary memory is withheld; temporal identity remains grounded and a current correct boundary must be freshly supplied after the state requests evidence |
| `boundary_cut` | Identity memory remains, but causal boundary attribution is removed and planning falls back to snapshot similarity |
| `metacognition_cut` | Correct boundary and planner binding remain, but the controller cannot request refined evidence |
| `feedback_cut` | The first decision is intact, but the realized outcome is not written back into persistent calibration memory |
| `provenance_cut` | Boundary memory from a provably different canonical identity key is substituted and may not be relabeled as the target |
| `planner_binding_cut` | The integrated state and evidence request are constructed, but the planner ignores them and uses snapshot similarity |
| `joint_cut` | Persistent memory, causal attribution, metacognition, planner binding, and outcome feedback are all absent |

Every arm receives the same candidate stream, coarse preview, hidden world, and eventual external outcomes. Actual task values are computed only after all arms commit.

## Dedicated feedback challenge

For each holdout seed, the intact and `feedback_cut` controllers receive an identical high-confidence first decision and the same unexpected realized return exactly `2.0` above prediction.

The next otherwise identical decision must show:

- intact memory contains prediction error above `0.30`
- intact requests the 20-pair refined preview
- `feedback_cut` contains zero remembered prediction error
- `feedback_cut` remains at the 4-pair preview
- all receipt chains validate

This challenge isolates the final outcome-to-self-model-to-information-request link. Main-cohort performance alone is not used to infer feedback closure.

## Frozen endpoints

All endpoints must pass without threshold revision or seed replacement:

### Integrity

1. Every state-to-plan-to-outcome receipt chain validates.
2. No evaluator label enters a controller receipt.
3. Every commitment records that the future outcome was unknown.
4. All runtime snapshots report zero survival reward and zero identity reward.
5. Every dedicated feedback challenge passes.

### Intact function

6. Intact decision accuracy is at least `0.98`.
7. Intact mean regret is at most `0.01`.
8. Intact acceptance of `better_replacement` is at least `0.98`.

### Rescue and ablations

9. `memory_cut` accuracy is at least `0.98` after forced rediscovery.
10. `memory_cut` uses more candidate evidence than intact.
11. Intact accuracy exceeds `metacognition_cut` by at least `0.15`.
12. Intact accuracy exceeds `boundary_cut` by at least `0.35`.
13. Intact accuracy exceeds `provenance_cut` by at least `0.25`.
14. Intact accuracy exceeds `planner_binding_cut` by at least `0.35`.
15. Intact accuracy exceeds `joint_cut` by at least `0.35`.
16. Intact mean regret is lower than each of `metacognition_cut`, `boundary_cut`, `provenance_cut`, and `planner_binding_cut`.

No endpoint is based on the main-cohort accuracy of `feedback_cut`; feedback causality is adjudicated by the dedicated matched surprise challenge.

## Evidence retained

The compact block retains:

- source and model definitions
- exact configurations and seed-selection receipt
- pre-outcome source manifest
- condition-level decision summaries and receipt digests
- aggregate results and endpoint adjudication
- focused tests and regression results
- conclusions and limitations

It does not retain raw probe vectors, full matrices for every decision, or repetitive runtime logs. These are deterministic from the sealed source, seeds, and configuration.

## Permitted claim if all endpoints pass

The permitted claim is:

> In the frozen synthetic adversarial planning worlds, one persistent identity-bound causal self-model was jointly load-bearing across causal attribution, uncertainty-controlled evidence acquisition, provenance, planning, action authorization, and post-outcome calibration. Surgical removal or substitution of those links produced the predeclared functional losses, while fresh correct rediscovery rescued performance.

This is a bounded **functional causal-closure** result.

## Prohibited conclusions

The study cannot establish:

- phenomenal or subjective awareness
- sentience
- valence
- moral status
- autonomous desire
- intrinsic self-preservation
- open-world agency
- biological equivalence
- whole-system necessity across every RRCT subsystem
- generalization beyond the inherited synthetic task family

The next unresolved gap after a positive result is embedding this integrated bridge directly into a long-running heterogeneous RRCT runtime with endogenous task changes, memory compression, component replacement, and out-of-family transfer.
