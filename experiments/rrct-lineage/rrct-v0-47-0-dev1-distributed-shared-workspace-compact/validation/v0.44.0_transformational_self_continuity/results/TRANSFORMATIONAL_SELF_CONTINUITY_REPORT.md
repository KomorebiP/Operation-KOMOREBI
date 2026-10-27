# RRCT v0.44 Transformational Self-Continuity Report

**Cohort:** `frozen_holdout`

**Seeds:** 973948357, 903438047, 119520877, 251222378

**Frozen endpoints met:** `True`

## Matched intervention results

| Mode | Relation accuracy | Group accuracy | Task accuracy | Mean regret | Mean evidence cost |
|---|---:|---:|---:|---:|---:|
| intact | 1.000000 | 1.000000 | 0.991319 | 0.000179 | 142.556 |
| snapshot_only | 0.074074 | 0.111111 | 0.829861 | 0.130903 | 125.156 |
| causal_only | 0.777778 | 0.777778 | 0.991319 | 0.000179 | 146.000 |
| memory_only | 0.672164 | 0.477431 | 0.991319 | 0.000179 | 129.861 |
| metacognition_cut | 0.509259 | 0.111111 | 0.991319 | 0.000277 | 111.667 |
| transfer_cut | 1.000000 | 1.000000 | 0.991319 | 0.000179 | 164.556 |
| binding_cut | 1.000000 | 1.000000 | 0.222222 | 0.632580 | 142.556 |
| joint_cut | 0.074074 | 0.111111 | 0.048611 | 0.756769 | 65.222 |

## Persistent multigeneration lineage

| Seed | Final generation | Lineages | All checks |
|---:|---:|---:|---:|
| 973948357 | 5 | 6 | PASS |
| 903438047 | 5 | 6 | PASS |
| 119520877 | 5 | 6 | PASS |
| 251222378 | 5 | 6 | PASS |

## Frozen endpoint adjudication

- `intact_relation_accuracy_high`: **PASS**
- `intact_group_accuracy_high`: **PASS**
- `intact_continuation_recall_high`: **PASS**
- `intact_replacement_specificity_high`: **PASS**
- `intact_unresolved_accuracy_high`: **PASS**
- `intact_fork_exact`: **PASS**
- `snapshot_control_worse`: **PASS**
- `causal_only_fails_causal_mimic`: **PASS**
- `memory_only_fails_memory_clone`: **PASS**
- `metacognition_refinement_matters`: **PASS**
- `transfer_cut_preserves_task_accuracy`: **PASS**
- `transfer_cut_costs_more`: **PASS**
- `binding_cut_harms_task`: **PASS**
- `joint_cut_worse`: **PASS**
- `intact_task_accuracy_high`: **PASS**
- `intact_regret_low`: **PASS**
- `superior_replacement_selected`: **PASS**
- `wrong_transfer_absent_intact`: **PASS**
- `receipt_chains_all_valid`: **PASS**
- `runtime_has_no_rewards_or_labels`: **PASS**
- `multigeneration_lineages_all_pass`: **PASS**
- `multigeneration_reaches_generation_five`: **PASS**
- `multigeneration_parent_chains_valid`: **PASS**

## Interpretation

The intact controller estimates coordinate transports from active probes, tests whether the predecessor causal boundary survives those transports, checks autobiographical and commitment compatibility, explicitly represents forks and unresolved evidence, and then binds that adjudication to memory transport or fresh model reconstruction before an external task is selected.

## Claim boundary

This matched synthetic study tests whether a persistent causal self-model can infer and use continuity through representation remapping, memory compression, component change, forks, copy traps, and evidence loss without successor identity labels. It does not test phenomenal consciousness, sentience, valence, moral status, subjective experience, or open-world autonomous agency.
