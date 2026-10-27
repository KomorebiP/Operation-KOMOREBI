# RRCT v0.43 Whole-Loop Causal Closure Report

**Cohort:** `frozen_holdout`

**Seeds:** 359411978, 725556465, 759191530, 820618202

**Frozen endpoints met:** `True`

## Matched intervention results

| Mode | Accuracy | Mean regret | Mean samples / candidate | Refinement rate | Authorized by self-model |
|---|---:|---:|---:|---:|---:|
| intact | 1.000000 | 0.000000 | 16.000 | 0.750000 | 1.000000 |
| memory_cut | 1.000000 | 0.000000 | 20.000 | 1.000000 | 1.000000 |
| boundary_cut | 0.250000 | 0.519076 | 4.000 | 0.000000 | 0.000000 |
| metacognition_cut | 0.661458 | 0.192255 | 4.000 | 0.000000 | 1.000000 |
| feedback_cut | 1.000000 | 0.000000 | 16.000 | 0.750000 | 1.000000 |
| provenance_cut | 0.445312 | 0.362634 | 16.375 | 0.773438 | 1.000000 |
| planner_binding_cut | 0.250000 | 0.519076 | 16.833 | 0.802083 | 0.000000 |
| joint_cut | 0.250000 | 0.519076 | 4.000 | 0.000000 | 0.000000 |

## Frozen endpoint adjudication

- `all_receipt_chains_valid`: **PASS**
- `no_evaluator_labels_enter_receipts`: **PASS**
- `future_outcomes_unknown_at_commit`: **PASS**
- `intact_accuracy_at_least_0_98`: **PASS**
- `intact_mean_regret_at_most_0_01`: **PASS**
- `intact_accepts_superior_replacement`: **PASS**
- `memory_cut_recovers_accuracy`: **PASS**
- `memory_cut_uses_more_evidence`: **PASS**
- `metacognition_cut_loses_accuracy`: **PASS**
- `boundary_cut_loses_accuracy`: **PASS**
- `provenance_cut_loses_accuracy`: **PASS**
- `planner_binding_cut_loses_accuracy`: **PASS**
- `joint_cut_loses_accuracy`: **PASS**
- `intact_regret_below_metacognition_cut`: **PASS**
- `intact_regret_below_boundary_cut`: **PASS**
- `intact_regret_below_provenance_cut`: **PASS**
- `intact_regret_below_planner_binding_cut`: **PASS**
- `all_feedback_challenges_pass`: **PASS**
- `runtime_has_no_survival_or_identity_reward`: **PASS**

## Interpretation

The intact controller binds one temporally grounded identity episode, one learned causal boundary, an uncertainty-guided evidence decision, an external-task plan, the authorized action, and the resulting calibration update into one cross-validated receipt chain. The surgical cuts test whether those links are functionally consequential rather than merely inspectable metadata.

## Claim boundary

This synthetic matched intervention study tests whether one persistent identity-bound causal self-model jointly changes attribution, evidence acquisition, planning, action authorization, and post-outcome calibration. It does not test phenomenal consciousness, sentience, valence, moral status, or an intrinsic desire to persist.
