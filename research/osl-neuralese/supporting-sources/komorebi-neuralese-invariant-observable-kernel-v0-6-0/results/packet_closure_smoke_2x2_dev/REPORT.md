# Packet-closure training block

- Profile: `smoke`
- Study: `prospective_developmental_fresh_seed_paired_2x2`
- Execution: `FAIL`
- Assay: `PASS`
- Mechanism: `NOT_EVALUATED`
- Primary D4 capability: `NOT_EVALUATED`
- Causal attribution: `NOT_EVALUATED`
- Secondary cross-family transfer: `NOT_EVALUATED`
- Descriptive ambient-Q attribution: `NOT_EVALUATED`
- Full developmental claim: `NOT_EVALUATED`

Scientific failures are retained. The clean paired 2x2 crosses raw Euclidean-normalized operators with hard O(12)-polar operators and matched supervised versus anonymous composition-plus-exact-return (CR) objectives. All cells share initialization and both accepted and proposal episode streams.

## Arm outcomes

Metrics use prefix 256, depth 64, and null-loop repeat 2.

| Arm | Packet | Margin p10 | D4 deep | Xfer min | Null retain | Switch gain/acc | Hard defect | Raw smin/smax | State patch/control | Operator patch/control |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `euclidean_supervised` | 0 | -0.6216 | 0.1562 | 0.09375 | 0 | 7.312/0.1875 | — | — | 0.09375/0.1562 | 0.2188/0.09375 |
| `euclidean_cr` | 0 | -0.6234 | 0.25 | 0.03125 | 0 | 10.99/0.125 | — | — | 0.1875/0.1875 | 0.1562/0.03125 |
| `polar_supervised` | 0 | -0.5817 | 0.125 | 0.09375 | 0 | 1/0.125 | 3.844e-06 | 0.001207 | 0.1875/0.09375 | 0.1562/0.125 |
| `polar_cr` | 0 | -0.5802 | 0.1875 | 0.0625 | 0 | 1/0.2188 | 3.402e-06 | 0.0004793 | 0.1562/0.03125 | 0.125/0.2188 |

## Paired 2x2 contrasts

Positive values favor the named first condition. The interaction is the difference in the CR effect between polar and raw architectures.

| Metric | CR given polar | Polar given supervised | Interaction |
|---|---:|---:|---:|
| `packet_membership` | 0 | 0 | 0 |
| `packet_margin_p10` | 0.001453 | 0.03994 | 0.003282 |
| `d4_accuracy` | 0.0625 | -0.03125 | -0.03125 |
| `cross_family_minimum_accuracy` | -0.03125 | 0 | 0.03125 |
| `structured_minimum_accuracy` | -0.03125 | 0 | 0.03125 |
| `null_retention` | 0 | 0 | 0 |
| `switched_max_gain` | -5.862e-07 | -6.312 | -3.675 |
| `switched_word_accuracy` | 0.09375 | -0.0625 | 0.1562 |
| `feshbach_return_fraction` | -0.004632 | 0.03284 | 0.003453 |
| `state_patch_margin` | 0.03125 | 0.1562 | -0.03125 |
| `operator_patch_margin` | -0.125 | -0.09375 | -0.125 |
| `ambient_q_ablation_drop` | 0.08333 | -0.07292 | 0.08333 |
| `ambient_q_specific_excess_drop` | 0.0625 | -0.03125 | 0.04167 |

## Execution gates

| Gate | Status | Criterion |
|---|---|---|
| `E01_preregistration_profile_match` | FAIL | contract schema/version/profile exactly match embedded implementation |
| `E02_all_training_runs_completed` | PASS | == 4 |
| `E03_all_evaluations_completed` | PASS | == 4 |
| `E04_checkpoint_seal_complete` | PASS | == 4 checkpoint receipts |
| `E05_frozen_checkpoint_reload` | PASS | == 4 hash-verified disk reloads |

## Assay gates

| Gate | Status | Criterion |
|---|---|---|
| `A01_paired_initialization_and_stream` | PASS | identical full/shared initialization, accepted episode-stream, and terminal-proposal-stream digests within every seed |
| `A02_construction_bank_shared` | PASS | one construction digest and exactly 20 horizon-4 construction words |
| `A03_checkpoint_audit_firewall` | PASS | no heldout/evaluation bank content in any checkpoint |
| `A04_relation_group_holdout` | PASS | 170 exhaustive horizon-8 words in two whole reserved action groups; split verified |
| `A05_checkpoint_before_evaluation_bank` | PASS | checkpoint seal timestamp precedes evaluation-bank materialization |
| `A06_exact_episode_contracts` | PASS | all bank targets, intermediates, and slot mappings exact |
| `A07_nonvacuous_exact_feshbach_split` | PASS | retained rank == 8 and nuisance rank == 4 for every evaluated checkpoint |
| `A08_switched_bank_contract` | PASS | exactly all 256 length-8 words for pilot; declared deterministic bank with configured contexts otherwise |
| `A09_terminal_endpoint_group_firewall` | PASS | every run uses the frozen identity/r2 endpoint-rejection policy; accepted count equals steps*batch and proposal/rejection counts close exactly |
| `A10_hard_polar_isometry` | PASS | both polar arms pass exact O(12) matrix and finite-bank projective-gain implementation checks for every seed |
| `A11_raw_prepolar_singular_diagnostic` | PASS | raw pre-polar relative singular values are recorded for both polar arms; conditioning below 1e-4 is a warning, not a closure failure |
| `A12_ambient_control_geometry` | PASS | all ambient assays have exact ranks 8/4, stable projectors, and rank/energy-matched random controls within 1e-8 |

## Mechanism gates

| Gate | Status | Criterion |
|---|---|---|
| `M01_heldout_packet_membership` | NOT_EVALUABLE | >= 0.90 at every audited prefix and in both reserved groups per polar_cr pilot seed |
| `M02_heldout_margin_p10` | NOT_EVALUABLE | > 0 at every audited prefix and in both reserved groups per polar_cr pilot seed |
| `M03_null_loop_packet_retention` | NOT_EVALUABLE | >= 0.90 for every relation and repeat through 32 per polar_cr pilot seed |
| `M04_switched_projective_gain` | NOT_EVALUABLE | hard-polar exhaustive length-8 maximum gain lies in [0.999, 1.001] per pilot seed |
| `M05_switched_domain_defined` | NOT_EVALUABLE | defined fraction == 1 per polar_cr pilot seed |
| `M06_switched_word_accuracy` | NOT_EVALUABLE | exhaustive length-8 switched-word behavioral accuracy >= 0.95 per polar_cr pilot seed |

## Primary D4 capability gates

| Gate | Status | Criterion |
|---|---|---|
| `C01_primary_d4_depth_curve` | NOT_EVALUABLE | polar_cr per-seed D4 accuracy >= 0.98@128, 0.90@256, 0.75@512 |

## Causal attribution gates

| Gate | Status | Criterion |
|---|---|---|
| `T01_complete_paired_2x2` | PASS | all four paired raw/polar x supervised/CR cells available |
| `T02_causal_state_patch_specificity` | NOT_EVALUABLE | polar_cr state patch >= 0.90 and matched random control <= 0.40 per pilot seed |
| `T03_causal_operator_patch_specificity` | NOT_EVALUABLE | polar_cr operator patch >= 0.90 and matched random control <= 0.40 per pilot seed |

## Secondary cross-family transfer gates

| Gate | Status | Criterion |
|---|---|---|
| `S01_zero_shot_cross_family_depth_curve` | NOT_EVALUABLE | descriptive secondary: polar_cr per-seed C8 and mixed-cycle accuracy >= 0.98@128, 0.90@256, 0.75@512 |

## Descriptive ambient-Q attribution gates

| Gate | Status | Criterion |
|---|---|---|
| `D01_specific_ambient_complement_use` | NOT_EVALUABLE | descriptive only: every polar_cr family supports a Q-specific performance drop over the energy/rank-matched random control; failure does not invalidate closure |

## Audit boundary

The terminal sampler rejects every loss-bearing D4 word whose complete induced action is identity or r². The horizon-8 evaluation bank was materialized only after all available checkpoints were serialized and hashed. It exhaustively contains the 170 nonempty words through length eight in those two reserved action groups. Checkpoints contain only the horizon-4 construction words plus aggregate terminal-firewall counts and digests, never rejected or evaluation words.

The Feshbach and causal ambient audits use the exact rank-eight anchor plane and its rank-four complement. Q energy alone is not evidence of use: the descriptive attribution requires a performance loss under Q ablation beyond an exactly rank- and energy-matched random control. A negative ambient-Q result does not invalidate packet closure.

Hard polar isometry is an architectural implementation assay, not evidence that stability was learned. Raw pre-polar singular conditioning is retained as a warning diagnostic and is not a closure gate.

## Claim boundary

A successful primary pilot would establish finite-depth packet preservation, exact hard-polar switched control, D4 depth extrapolation, and causal state/operator execution in this explicit table-conditioned architecture. Cross-family zero-shot transfer and ambient-Q use are reported separately and cannot be hidden inside the primary closure claim. The experiment would not establish spontaneous Neuralese, an infinite quotient, universal stability, architecture-independent emergence, awareness, or consciousness.
